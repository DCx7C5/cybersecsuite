"""Core event system exports."""

from typing import cast

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
from .emitter import EventEmitterMixin, NamespacedEventEmitter, emit_event, emit_events, event, get_event_bus
from .instrument import instrument, instrument_decorator
from .otel_context import (
    TraceContextExtractor,
    clear_correlation_id,
    correlation_id_ctx,
    get_correlation_id,
    set_correlation_id,
)
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

# Hook re-exports omitted here — import directly from css.modules.hooks to
# avoid a circular import: css.core.events → css.modules.hooks.registry →
# css.core.events.emitter → css.core.events (partial).

event_store: EventStore | None = None
otel_bridge: OtelBridge | None = None
event_store_observer: EventStoreObserver | None = None

def configure_event_runtime() -> tuple[EventStore, OtelBridge, EventStoreObserver]:
    """Initialize event runtime singletons once and return them."""
    global event_store, otel_bridge, event_store_observer
    if event_store is None:
        event_store = EventStore()
    if otel_bridge is None:
        otel_bridge = OtelBridge()
    if event_store_observer is None:
        event_store_observer = EventStoreObserver(event_store=event_store, otel_bridge=otel_bridge)
    return event_store, otel_bridge, event_store_observer

def shutdown_event_runtime() -> None:
    """Reset event runtime singletons."""
    global event_store, otel_bridge, event_store_observer
    event_store = None
    otel_bridge = None
    event_store_observer = None

def get_event_store() -> EventStore:
    """Get the canonical EventStore singleton."""
    configure_event_runtime()
    return cast(EventStore, event_store)

def get_otel_bridge() -> OtelBridge:
    """Get the canonical OtelBridge singleton."""
    configure_event_runtime()
    return cast(OtelBridge, otel_bridge)
