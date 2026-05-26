"""Planner value models."""

from __future__ import annotations

from datetime import datetime
import msgspec

from .enums import PlanStepStatus


class PlanStep(msgspec.Struct, frozen=True, kw_only=True):
    """A single executable planning step."""

    step_id: str
    description: str
    status: PlanStepStatus = PlanStepStatus.PENDING
    result: str = ""
    depends_on: list[str] = msgspec.field(default_factory=list)


class PlannerSession(msgspec.Struct, frozen=True, kw_only=True):
    """Plan session and progress state."""

    session_id: str
    objective: str
    created_at: datetime = msgspec.field(default_factory=datetime.now)
    updated_at: datetime = msgspec.field(default_factory=datetime.now)
    steps: list[PlanStep] = msgspec.field(default_factory=list)

    def progress(self) -> dict[str, int]:
        counts = {status.value: 0 for status in PlanStepStatus}
        for step in self.steps:
            counts[step.status.value] += 1
        return counts
