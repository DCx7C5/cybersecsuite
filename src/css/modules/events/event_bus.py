"""Event bus — centralized event emission and handling."""

from typing import Any, Callable, Dict, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class EventBus:
    """Simple event bus for Phase 3 — emits events to registered handlers.
    
    Note: Phase 6 will replace this with CQRS/EventStore architecture.
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    async def emit(self, event_type: str, payload: Any) -> None:
        """Emit an event to all registered handlers."""
        if event_type not in self._handlers:
            return

        handlers = self._handlers[event_type]
        tasks = [self._safe_call(handler, event_type, payload) for handler in handlers]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_call(self, handler: Callable, event_type: str, payload: Any) -> None:
        """Safely call a handler, catching exceptions."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event_type, payload)
            else:
                handler(event_type, payload)
        except Exception as e:
            logger.error(f"Error in event handler for {event_type}: {e}", exc_info=True)

    def register(self, event_type: str, handler: Callable) -> None:
        """Register a handler for an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def unregister(self, event_type: str, handler: Callable) -> None:
        """Unregister a handler for an event type."""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)


# Global singleton
event_bus = EventBus()
