"""Domain event types for Phase 6 CQRS EventStore."""

from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

import msgspec


class DomainEvent(msgspec.Struct, frozen=True, kw_only=True):
    """Immutable domain event for audit trail and replay.

    All domain mutations are represented as events and persisted to EventStore.
    Events are the source of truth; read models are derived from event streams.
    """

    kind: str
    aggregate_type: str
    aggregate_id: str
    id: str = msgspec.field(default_factory=lambda: str(uuid4()))
    data: dict[str, Any] = msgspec.field(default_factory=dict)
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    timestamp: datetime = msgspec.field(default_factory=lambda: datetime.now(UTC))
    version: int = 1

    @property
    def event_key(self) -> str:
        """Unique key for deduplication."""
        return f"{self.aggregate_type}:{self.aggregate_id}:{self.id}"


# ── Domain event factories ──────────────────────────────────────────────────────


def event_team_spawned(team_id: str, team_name: str, members: list[str]) -> DomainEvent:
    """Team spawned event."""
    return DomainEvent(
        kind="team.spawned",
        aggregate_type="team",
        aggregate_id=team_id,
        data={
            "name": team_name,
            "members": members,
            "count": len(members),
        },
    )


def event_team_shutdown(team_id: str, reason: str | None = None) -> DomainEvent:
    """Team shutdown event."""
    return DomainEvent(
        kind="team.shutdown",
        aggregate_type="team",
        aggregate_id=team_id,
        data={"reason": reason or "graceful_shutdown"},
    )


def event_task_delegated(task_id: str, team_id: str, task_def: dict) -> DomainEvent:
    """Task delegated to team event."""
    return DomainEvent(
        kind="task.delegated",
        aggregate_type="task",
        aggregate_id=task_id,
        data={
            "team_id": team_id,
            "definition": task_def,
        },
    )


def event_task_completed(
    task_id: str,
    result: Any,
    duration_ms: float,
) -> DomainEvent:
    """Task completed event."""
    return DomainEvent(
        kind="task.completed",
        aggregate_type="task",
        aggregate_id=task_id,
        data={
            "result": result,
            "duration_ms": duration_ms,
        },
    )


def event_task_failed(
    task_id: str,
    error: str,
    duration_ms: float,
) -> DomainEvent:
    """Task failed event."""
    return DomainEvent(
        kind="task.failed",
        aggregate_type="task",
        aggregate_id=task_id,
        data={
            "error": error,
            "duration_ms": duration_ms,
        },
    )


def event_permission_granted(
    resource_id: str,
    principal_id: str,
    action: str,
) -> DomainEvent:
    """Permission granted event."""
    return DomainEvent(
        kind="permission.granted",
        aggregate_type="permission",
        aggregate_id=f"{resource_id}:{principal_id}",
        data={
            "resource_id": resource_id,
            "principal_id": principal_id,
            "action": action,
        },
    )

