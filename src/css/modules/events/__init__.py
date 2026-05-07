"""Events module exports."""

from .store import EventStore
from .types import (
    DomainEvent,
    event_permission_granted,
    event_task_completed,
    event_task_delegated,
    event_task_failed,
    event_team_shutdown,
    event_team_spawned,
)
# Phase 6 T6.3: Command pattern for event sourcing
from .command_bus import (
    Command,
    CommandBus,
    CommandHandler,
    CreateTeamCommand,
    CreateTaskCommand,
    CompleteTaskCommand,
    SpawnAgentCommand,
)
# Phase 6 T6.5: Read projections from event stream
from .projections import (
    Projection,
    PermissionsProjection,
    AuditTrailProjection,
    ProjectionManager,
)
# Phase 6 T6.5: OTel observability bridge
from .otel_bridge import (
    OtelBridge,
    EventStoreObserver,
)

__all__ = [
    "DomainEvent",
    "EventStore",
    "event_team_spawned",
    "event_team_shutdown",
    "event_task_delegated",
    "event_task_completed",
    "event_task_failed",
    "event_permission_granted",
    # Command pattern
    "Command",
    "CommandBus",
    "CommandHandler",
    "CreateTeamCommand",
    "CreateTaskCommand",
    "CompleteTaskCommand",
    "SpawnAgentCommand",
    # Read projections
    "Projection",
    "PermissionsProjection",
    "AuditTrailProjection",
    "ProjectionManager",
    # OTel observability
    "OtelBridge",
    "EventStoreObserver",
]
