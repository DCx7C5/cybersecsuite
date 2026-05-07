"""Planner value models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class PlanStepStatus(str, Enum):
    """Execution status for one plan step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PlanStep:
    """A single executable planning step."""

    step_id: str
    description: str
    status: PlanStepStatus = PlanStepStatus.PENDING
    result: str = ""
    depends_on: list[str] = field(default_factory=list)


@dataclass
class PlannerSession:
    """Plan session and progress state."""

    session_id: str
    objective: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    steps: list[PlanStep] = field(default_factory=list)

    def progress(self) -> dict[str, int]:
        counts = {status.value: 0 for status in PlanStepStatus}
        for step in self.steps:
            counts[step.status.value] += 1
        return counts
