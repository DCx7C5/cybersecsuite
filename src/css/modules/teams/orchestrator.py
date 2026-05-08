"""Team orchestrator wired to internal CSS A2A delegation flow."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from css.modules.a2a_internal.a2a_comms import A2ACommunicator
from css.modules.a2a_internal.dispatcher import MessageDispatcher


def _state_name(task: Any) -> str:
    state = getattr(getattr(task, "status", None), "state", None)
    if hasattr(state, "value"):
        return str(state.value).lower()
    return str(state).lower()


@dataclass
class TeamOrchestrator:
    """Delegates tasks to team members via A2A communicator + dispatcher."""

    team_id: str
    members: list[str]
    dispatcher: MessageDispatcher
    timeout_seconds: float = 30.0
    poll_interval_seconds: float = 0.2
    communicator: A2ACommunicator | None = None
    _rr_cursor: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        if self.communicator is None:
            self.communicator = A2ACommunicator(
                agent_id=f"team:{self.team_id}",
                dispatcher=self.dispatcher,
            )

    def _select_available_member(self) -> str:
        if not self.members:
            raise ValueError(f"No members available for team {self.team_id}")
        idx = self._rr_cursor % len(self.members)
        self._rr_cursor = (self._rr_cursor + 1) % len(self.members)
        return self.members[idx]

    async def delegate(self, task: dict[str, Any]) -> dict[str, Any]:
        """Delegate one task to the selected team member and await completion."""
        member_id = self._select_available_member()
        task_id = str(task.get("task_id") or uuid4())
        session_id = str(task.get("session_id", ""))
        user_text = str(task.get("text") or task.get("query") or task.get("title") or "delegated task")

        # 1) Create A2A task envelope
        await self.communicator.create_task(
            task_id=task_id,
            message={"role": "user", "parts": [{"text": user_text}]},
            session_id=session_id or None,
        )
        # 2) Dispatch through internal dispatcher to chosen member
        await self.communicator.dispatch_to_team(
            task_id=task_id,
            team_members=[member_id],
            payload=task,
        )
        # 3) Await completion signal in task store
        completed_task = await self._await_completion(task_id)
        return {
            "task_id": task_id,
            "member_id": member_id,
            "status": _state_name(completed_task),
            "artifacts_count": len(getattr(completed_task, "artifacts", []) or []),
        }

    async def _await_completion(self, task_id: str) -> Any:
        deadline = asyncio.get_running_loop().time() + self.timeout_seconds
        while asyncio.get_running_loop().time() < deadline:
            task = await self.communicator.get_task(task_id)
            state = _state_name(task)
            if state.endswith("completed") or state == "completed":
                return task
            if state.endswith("failed") or state == "failed":
                return task
            await asyncio.sleep(self.poll_interval_seconds)
        raise TimeoutError(f"Timed out waiting for delegated task completion: {task_id}")

