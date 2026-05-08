"""Planer module enums."""

from enum import Enum


class PlanStepStatus(str, Enum):
    """Execution status for one plan step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


__all__ = ["PlanStepStatus"]
