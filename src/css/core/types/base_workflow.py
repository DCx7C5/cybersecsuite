"""Base workflow entity types — abstract contracts for task modules.

Task is a workflow/orchestration entity (distinct from domain entities
like BaseAgent/BaseSkill). Modules extend these base dataclasses and add their
own domain-specific fields, status enums, and state machine methods.

Note: Team types live entirely within modules/teams — no core base needed.
"""
import msgspec

class BaseTask(msgspec.Struct):
    """Abstract base for task entities.

    Modules (modules/tasks) extend this with:
    - Domain status enum (TaskStatus)
    - Priority levels
    - Retry logic
    - State machine transitions (queue, execute, complete, fail, pause, cancel)
    """

    id: str
    metadata: dict[str, object] = msgspec.field(default_factory=dict)

class BaseTaskScope(msgspec.Struct):
    """Abstract base for immutable task context snapshots."""

    id: str
    metadata: dict[str, object] = msgspec.field(default_factory=dict)

__all__ = [
    "BaseTask",
    "BaseTaskScope",
]
