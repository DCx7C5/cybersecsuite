"""Task module enums — status, priority, routing."""

from enum import Enum


class TaskStatus(str, Enum):
    """Task lifecycle status."""
    PENDING = "pending"
    QUEUED = "queued"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TaskPriority(str, Enum):
    """Task execution priority."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class TaskRoutingStrategy(str, Enum):
    """Task routing strategy for TeamMembers."""
    ROUND_ROBIN = "round_robin"
    LEAST_BUSY = "least_busy"
    WEIGHTED = "weighted"
    AFFINITY = "affinity"


__all__ = ["TaskStatus", "TaskPriority", "TaskRoutingStrategy"]
