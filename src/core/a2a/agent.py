"""
A2A Agent base class.
Subclass this to implement a custom A2A-compatible agent.
"""


import abc
from typing import AsyncIterator, Optional

from a2a.models import (
    Task, AgentCard,
    Message, TaskArtifact, TextPart,
)
from a2a.enums import TaskState, MessageRole, PartType
from a2a.task_store import TaskStore


class BaseA2AAgent(abc.ABC):
    """
    Abstract base for A2A agents.

    Subclass and implement `execute()` (or `stream()` for streaming).
    """

    def __init__(self, card: AgentCard, store: Optional[TaskStore] = None) -> None:
        self.card = card
        self.store = store or TaskStore()

    @abc.abstractmethod
    async def execute(self, task: Task, message: Message) -> None:
        """
        Process a task message.

        Update task status and artifacts via self.store.
        Must call update_status(COMPLETED | FAILED) before returning.
        """

    async def stream(
        self, task: Task, message: Message
    ) -> AsyncIterator[Task]:
        """
        Stream task updates.  Override for full streaming support.

        Default behaviour: yields a WORKING status immediately (so SSE clients
        know work has started), then awaits ``execute()``, then yields the
        final task state.  Skill handlers that call ``run_agent_query()``
        produce their full output before returning, so there is only one
        substantive data chunk; the WORKING yield provides early feedback.

        Note: incremental SDK text chunks (partial TextBlocks) require each
        skill handler to become an async generator that calls ``stream_query()``
        from ``agent.streaming``.  That refactor is tracked as Phase 3.
        """
        working = self.store.update_status(task.id, TaskState.WORKING) or task
        yield working
        await self.execute(task, message)
        yield self.store.get(task.id) or task

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _extract_text(message: Message) -> str:
        """Extract all text parts from a message and join them."""
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
        return " ".join(parts)

    def _reply(self, task_id: str, text: str, state: TaskState = TaskState.COMPLETED) -> Task | None:
        """Convenience: update task with a text reply."""
        msg = Message(
            role=MessageRole.AGENT,
            parts=[TextPart(type=PartType.TEXT, text=text)],
        )
        return self.store.update_status(task_id, state, msg)

    def _add_text_artifact(self, task_id: str, text: str, name: str = "result") -> Task | None:
        """Convenience: add a text artifact."""
        artifact = TaskArtifact(
            name=name,
            parts=[TextPart(type=PartType.TEXT, text=text)],
        )
        return self.store.add_artifact(task_id, artifact)

    def _fail(self, task_id: str, reason: str) -> Task | None:
        """Convenience: mark task as failed."""
        return self._reply(task_id, reason, TaskState.FAILED)

