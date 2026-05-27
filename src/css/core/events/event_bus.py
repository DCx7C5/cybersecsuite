import asyncio
import fnmatch
import inspect
from collections.abc import Awaitable, Callable
from typing import Any, TypeAlias

from css.core.logger import getLogger
from css.core.types.base_meta import AsyncSafeSingletonMeta

logger = getLogger(__name__)

EventHandler: TypeAlias = Callable[[str, object], object | Awaitable[object]]


class EventBus(metaclass=AsyncSafeSingletonMeta):
    """Simple event bus for Phase 3 — emits events to registered handlers.
    
    Note: Phase 6 will replace this with CQRS/EventStore architecture.
    """

    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = {}

    async def emit(self, event_type: str, payload: Any) -> None:
        """Emit an event to all registered handlers."""
        handlers = self._matching_handlers(event_type)
        if not handlers:
            return

        tasks = [self._safe_call(handler, event_type, payload) for handler in handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _matching_handlers(self, event_type: str) -> list[EventHandler]:
        """Return unique handlers matching an emitted event type.

        Supports exact matches and glob-style patterns registered as keys.
        """
        matches: list[EventHandler] = []
        seen: set[int] = set()

        for registered_event, handlers in self._handlers.items():
            if not self._matches_event(registered_event, event_type):
                continue
            for handler in handlers:
                marker = id(handler)
                if marker in seen:
                    continue
                seen.add(marker)
                matches.append(handler)

        return matches

    @staticmethod
    def _matches_event(registered_event: str, emitted_event: str) -> bool:
        if registered_event == emitted_event:
            return True
        if any(ch in registered_event for ch in ("*", "?", "[")):
            return fnmatch.fnmatch(emitted_event, registered_event)
        return False

    async def _safe_call(self, handler: EventHandler, event_type: str, payload: object) -> None:
        """Safely call a handler, catching exceptions."""
        try:
            if inspect.iscoroutinefunction(handler):
                await handler(event_type, payload)
            else:
                result = handler(event_type, payload)
                if inspect.isawaitable(result):
                    await result
        except asyncio.CancelledError:
            raise
        except BaseException as error:
            logger.error(
                "Error in event handler for %s: %s",
                event_type,
                error,
                exc_info=True,
            )

    def register(self, event_type: str, handler: EventHandler) -> None:
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unregister(self, event_type: str, handler: EventHandler) -> None:
        """Unregister a handler for an event type."""
        if event_type in self._handlers:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)


# Module-level singleton accessor — EventBus uses AsyncSafeSingletonMeta,
# so EventBus() always returns the same instance.
event_bus = EventBus()
