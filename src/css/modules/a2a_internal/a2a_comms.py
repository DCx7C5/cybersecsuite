from css.core.logger import getLogger
import msgspec
from typing import Any
from datetime import UTC, datetime

from css.modules.a2a_google.enums import MessageRole, TaskState
from css.modules.a2a_google.types import (
    Message as A2AMessage,
    Part,
    Task,
    TaskArtifact,
    TaskStatus,
    TextPart,
)
from css.core.redis.messaging import Message as InternalMessage

from .dispatcher import MessageDispatcher

log = getLogger(__name__)

class DelegationMessage(msgspec.Struct, frozen=True, kw_only=True):
    """Typed IPC payload for team task delegation."""

    task_id: str
    data: Any


class ResultMessage(msgspec.Struct, frozen=True, kw_only=True):
    """Typed IPC payload for task message forwarding."""

    task_id: str
    message: dict[str, Any]


class A2ACommunicator(msgspec.Struct, frozen=True, kw_only=True):
    """High-level async interface for A2A protocol messaging.

    Translates between:
    - **Google A2A protocol** (external: ``Task``, ``Message``, ``TaskState``, ``Part`` union)
    - **Internal Redis dispatch** (internal: ``InternalMessage`` pubsub)

    Handles task lifecycle: ``SUBMITTED`` → ``WORKING`` → ``COMPLETED`` / ``FAILED``.

    ``agent_id`` is the canonical agents identifier (e.g. ``"research:analyst"``).
    ``dispatcher`` routes internal messages; ``task_store`` tracks task state.
    """

    agent_id: str
    dispatcher: MessageDispatcher
    task_store: dict[str, Task] = msgspec.field(default_factory=dict)

    async def create_task(self, task_id: str, message: A2AMessage, session_id: str | None = None) -> Task:
        """Create a new A2A task in SUBMITTED state."""
        task = Task(
            id=task_id,
            session_id=session_id,
            status=TaskStatus(state=TaskState.SUBMITTED),
            history=[message],
            artifacts=[],
            metadata={"agent_id": self.agent_id},
        )
        self.task_store[task_id] = task
        log.debug("A2A task %r created (SUBMITTED)", task_id)
        return task

    async def set_working(self, task_id: str, message: A2AMessage | None = None) -> Task:
        """Transition a task to WORKING state."""
        if task_id not in self.task_store:
            raise ValueError(f"Task {task_id!r} not found")
        task = self.task_store[task_id]
        task.status = TaskStatus(state=TaskState.WORKING, message=message)
        if message and message not in task.history:
            task.history.append(message)
        log.debug("A2A task %r → WORKING", task_id)
        return task

    async def set_completed(
        self,
        task_id: str,
        artifact: TaskArtifact | None = None,
        final_message: A2AMessage | None = None,
    ) -> Task:
        """Complete a task with optional artifact and final message."""
        if task_id not in self.task_store:
            raise ValueError(f"Task {task_id!r} not found")
        task = self.task_store[task_id]
        task.status = TaskStatus(state=TaskState.COMPLETED, message=final_message)
        if final_message and final_message not in task.history:
            task.history.append(final_message)
        if artifact:
            task.artifacts.append(artifact)
        log.debug("A2A task %r → COMPLETED with %d artifact(s)", task_id, len(task.artifacts or []))
        return task

    async def set_failed(self, task_id: str, error_message: str) -> Task:
        """Fail a task with an error message."""
        if task_id not in self.task_store:
            raise ValueError(f"Task {task_id!r} not found")
        task = self.task_store[task_id]
        error_msg = A2AMessage(
            role=MessageRole.AGENT,
            parts=[TextPart(text=f"Error: {error_message}")],
        )
        task.status = TaskStatus(state=TaskState.FAILED, message=error_msg)
        task.history.append(error_msg)
        log.error("A2A task %r → FAILED: %s", task_id, error_message)
        return task

    async def add_artifact(self, task_id: str, artifact: TaskArtifact) -> Task:
        """Add an output artifact to a task."""
        if task_id not in self.task_store:
            raise ValueError(f"Task {task_id!r} not found")
        task = self.task_store[task_id]
        task.artifacts.append(artifact)
        log.debug("A2A task %r: artifact added (%s)", task_id, artifact.name or "unnamed")
        return task

    async def get_task(self, task_id: str) -> Task:
        """Retrieve task by ID."""
        if task_id not in self.task_store:
            raise ValueError(f"Task {task_id!r} not found")
        return self.task_store[task_id]

    async def send_agent_message(
        self,
        task_id: str,
        text: str,
        parts: list[Part] | None = None,
    ) -> A2AMessage:
        """Send an agents response message back into a task."""
        if parts is None:
            parts = [TextPart(text=text)]
        msg = A2AMessage(role=MessageRole.AGENT, parts=parts)

        task = self.task_store.get(task_id)
        if task:
            task.history.append(msg)
            log.debug("A2A task %r: agents message appended (%d parts)", task_id, len(parts))

        return msg

    async def dispatch_to_team(
        self,
        task_id: str,
        team_members: list[str],
        payload: Any,
    ) -> None:
        """Broadcast an internal dispatch to team members for task collaboration.

        Converts A2A task context into internal ``InternalMessage`` for routing.
        """
        if task_id not in self.task_store:
            raise ValueError(f"Task {task_id!r} not found")

        for member_id in team_members:
            delegation = DelegationMessage(task_id=task_id, data=payload)
            msg = InternalMessage(
                from_id=self.agent_id,
                to_id=member_id,
                type="a2a_task",
                payload=msgspec.to_builtins(delegation),
                routing_mode="direct",
            )
            await self.dispatcher.send(msg)
            log.debug("A2A task %r: dispatched to %r", task_id, member_id)

class A2ACommunicationGroup(msgspec.Struct, frozen=True, kw_only=True):
    """A2A protocol group for multi-agents collaboration.

    Manages a named team of agents responding to A2A protocol requests,
    internally coordinated via Redis pubsub.

    ``name`` is the team identifier (e.g. ``"forensics_team"``).
    ``members`` stores agents IDs (e.g. ``["research:orchestrator", "research:analyst"]``).
    """

    name: str
    members: list[str] = msgspec.field(default_factory=list)
    dispatcher: MessageDispatcher | None = None
    a2a_communicator: A2ACommunicator | None = None

    def _require_dispatcher(self) -> MessageDispatcher:
        if self.dispatcher is None:
            raise RuntimeError(f"A2ACommunicationGroup {self.name!r} has no dispatcher set")
        return self.dispatcher

    def _require_a2a_communicator(self) -> A2ACommunicator:
        if self.a2a_communicator is None:
            raise RuntimeError(f"A2ACommunicationGroup {self.name!r} has no A2ACommunicator set")
        return self.a2a_communicator

    async def add_member(self, agent_id: str) -> None:
        """Add an agents to the team (idempotent)."""
        if agent_id not in self.members:
            self.members.append(agent_id)
            log.debug("A2A group [%s]: added member %r (%d total)", self.name, agent_id, len(self.members))

    async def remove_member(self, agent_id: str) -> None:
        """Remove an agents from the team (no-op if not present)."""
        try:
            self.members.remove(agent_id)
            log.debug("A2A group [%s]: removed member %r (%d remaining)", self.name, agent_id, len(self.members))
        except ValueError:
            pass

    async def broadcast_task(
        self,
        task_id: str,
        message: A2AMessage,
        from_agent: str | None = None,
    ) -> None:
        """Broadcast an A2A task message to all team members.

        Internally routes via Redis; externally seen as multi-agents task execution.
        """
        dispatcher = self._require_dispatcher()
        sender = from_agent or self.name

        for member_id in list(self.members):
            result_payload = ResultMessage(task_id=task_id, message=msgspec.to_builtins(message))
            msg = InternalMessage(
                from_id=sender,
                to_id=member_id,
                type="a2a_task_broadcast",
                payload=msgspec.to_builtins(result_payload),
                routing_mode="direct",
            )
            await dispatcher.send(msg)
            log.debug("A2A group [%s]: task %r broadcast to %r", self.name, task_id, member_id)

    async def send_task_to_member(
        self,
        agent_id: str,
        task_id: str,
        message: A2AMessage,
        from_agent: str | None = None,
    ) -> None:
        """Send a specific A2A task to one team member."""
        if agent_id not in self.members:
            raise ValueError(f"{agent_id!r} is not a member of group {self.name!r}")

        dispatcher = self._require_dispatcher()
        sender = from_agent or self.name

        result_payload = ResultMessage(task_id=task_id, message=msgspec.to_builtins(message))
        msg = InternalMessage(
            from_id=sender,
            to_id=agent_id,
            type="a2a_task_direct",
            payload=msgspec.to_builtins(result_payload),
            routing_mode="direct",
        )
        await dispatcher.send(msg)
        log.debug("A2A group [%s]: task %r sent to %r", self.name, task_id, agent_id)

    async def get_members(self) -> list[str]:
        """Return a snapshot of current team members."""
        return list(self.members)

    async def get_team_status(self) -> dict[str, Any]:
        """Return team overview: name, member count, team health."""
        return {
            "name": self.name,
            "member_count": len(self.members),
            "members": list(self.members),
            "timestamp": datetime.now(UTC).isoformat(),
        }
