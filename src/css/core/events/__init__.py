"""Core event system exports."""

from .command_bus import (
    AgentCommand,
    Command,
    CommandBus,
    CommandHandler,
    CompleteTaskCommand,
    CreateTaskCommand,
    CreateTeamCommand,
    SpawnAgentCommand,
    TaskCommand,
    TeamCommand,
)
from .domain_event import (
    DomainEvent,
    event_permission_granted,
    event_task_completed,
    event_task_delegated,
    event_task_failed,
    event_team_shutdown,
    event_team_spawned,
)
from .event_bus import EventBus, event_bus
from .hooks import HookRegistry, hook_registry, on_event
from .otel_bridge import EventStoreObserver, OtelBridge
from .projections import (
    AuditTrailProjection,
    PermissionsProjection,
    Projection,
    ProjectionManager,
)
from .store import EventStore
from .types import (
    ALL_EVENT_TYPES,
    EVENT_TYPES_PHASE3,
    EVENT_TYPES_PHASE5,
    EVENT_TYPES_PHASE6,
    EVENT_TYPES_PHASE14,
)
from .exceptions import EventError, HookRegistrationError, HookTimeoutError, EventBusError

__all__ = [
    "DomainEvent",
    "event_team_spawned",
    "event_team_shutdown",
    "event_task_delegated",
    "event_task_completed",
    "event_task_failed",
    "event_permission_granted",
    "EventStore",
    "Command",
    "TeamCommand",
    "TaskCommand",
    "AgentCommand",
    "CreateTeamCommand",
    "CreateTaskCommand",
    "CompleteTaskCommand",
    "SpawnAgentCommand",
    "CommandHandler",
    "CommandBus",
    "Projection",
    "PermissionsProjection",
    "AuditTrailProjection",
    "ProjectionManager",
    "OtelBridge",
    "EventStoreObserver",
    "EventBus",
    "event_bus",
    "HookRegistry",
    "hook_registry",
    "on_event",
    "ALL_EVENT_TYPES",
    "EVENT_TYPES_PHASE3",
    "EVENT_TYPES_PHASE5",
    "EVENT_TYPES_PHASE6",
    "EVENT_TYPES_PHASE14",
    "EventError",
    "HookRegistrationError",
    "HookTimeoutError",
    "EventBusError",
]
