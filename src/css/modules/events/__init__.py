"""Event system module — event bus and hook registry for Phase 3.

This is a Phase 3 placeholder. Phase 6 will replace this with a full CQRS/EventStore
architecture with PostgreSQL + Redis Streams + OTEL instrumentation.

For now, provides basic EventBus (Singleton) and hook registration capability.
"""

from .event_bus import EventBus
from .hooks import HookRegistry, hook_registry, on_event
from .types import ALL_EVENT_TYPES, EVENT_TYPES_PHASE3, EVENT_TYPES_PHASE6, EVENT_TYPES_PHASE14
from .exceptions import EventError, HookRegistrationError, HookTimeoutError, EventBusError

__all__ = [
    # Event bus (Singleton)
    "EventBus",
    
    # Hooks
    "HookRegistry",
    "hook_registry",
    "on_event",
    
    # Types
    "ALL_EVENT_TYPES",
    "EVENT_TYPES_PHASE3",
    "EVENT_TYPES_PHASE6",
    "EVENT_TYPES_PHASE14",
    
    # Exceptions
    "EventError",
    "HookRegistrationError",
    "HookTimeoutError",
    "EventBusError",
]
