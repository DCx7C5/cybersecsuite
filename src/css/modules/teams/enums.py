"""Team enums — status and orchestrator modes."""

from enum import Enum


class TeamStatus(str, Enum):
    """Team lifecycle states."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class OrchestratorMode(str, Enum):
    """Orchestrator selection strategies for task distribution."""
    ROUND_ROBIN = "round-robin"
    LEAST_BUSY = "least-busy"
    WEIGHTED = "weighted"
