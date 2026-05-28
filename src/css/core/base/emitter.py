"""Base class for event-emitting components."""

from collections.abc import Mapping, Sequence


class BaseEmitterClass:
    """Base class that gives subclasses first-class event emission."""

    event_namespace: str = ""
    _registered_events: set[str] = set()

    @classmethod
    def qualify_event_name(cls, event_name: str) -> str:
        """Qualify event names with class namespace when configured."""
        namespace = cls.event_namespace.strip(".")
        if not namespace:
            return event_name
        if event_name.startswith(f"{namespace}."):
            return event_name
        return f"{namespace}.{event_name}"

    @classmethod
    def register_events(cls, *event_names: str) -> None:
        """Manually register event names that this subclass is allowed to emit."""
        declared = set(getattr(cls, "_registered_events", set()))
        for event_name in event_names:
            declared.add(cls.qualify_event_name(event_name))
        cls._registered_events = declared

    @classmethod
    def declared_events(cls) -> set[str]:
        """Return manually registered event names for this class."""
        return set(getattr(cls, "_registered_events", set()))

    @classmethod
    def event_registered(cls, event_name: str) -> bool:
        """Check whether an event is manually registered for this class."""
        return cls.qualify_event_name(event_name) in cls.declared_events()

    async def emit(
        self,
        event_name: str,
        payload: Mapping[str, object] | None = None,
    ) -> None:
        """Emit one namespaced event."""
        from css.core.events.emitter import emit_event

        await emit_event(self.qualify_event_name(event_name), payload)

    async def emit_many(
        self,
        event_names: Sequence[str],
        payload: Mapping[str, object] | None = None,
    ) -> None:
        """Emit many namespaced events in order."""
        from css.core.events.emitter import emit_events

        await emit_events([self.qualify_event_name(name) for name in event_names], payload)
