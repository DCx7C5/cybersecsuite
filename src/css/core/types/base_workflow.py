"""Base workflow entity types — abstract contracts for team and task modules.

Team and Task are workflow/orchestration entities (distinct from domain entities
like BaseAgent/BaseSkill). Modules extend these base dataclasses and add their
own domain-specific fields, status enums, and state machine methods.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BaseTeam:
    """Abstract base for team entities.

    Modules (modules/teams) extend this with:
    - Domain status enum (TeamStatus)
    - Orchestrator pool state
    - Task queue counters
    - Lifecycle transitions (activate, pause, resume, complete)
    """

    team_id: int
    team_name: str
    session_id: int


@dataclass
class BaseTeamScope:
    """Abstract base for immutable team context snapshots."""

    team_id: int
    team_name: str
    session_id: int
    max_orchestrators: int = 0
    current_orchestrators: int = 0
    completed_tasks: int = 0


@dataclass
class BaseTask:
    """Abstract base for task entities.

    Modules (modules/tasks) extend this with:
    - Domain status enum (TaskStatus)
    - Priority levels
    - Retry logic
    - State machine transitions (queue, execute, complete, fail, pause, cancel)
    """

    id: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class BaseTaskScope:
    """Abstract base for immutable task context snapshots."""

    id: str
    metadata: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "BaseTeam",
    "BaseTeamScope",
    "BaseTask",
    "BaseTaskScope",
]
