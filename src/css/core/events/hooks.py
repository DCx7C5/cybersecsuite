"""Hook registry — register event handlers using decorators."""

from css.core.logger import getLogger
from typing import Any, TypeVar
from collections.abc import Callable

from .event_bus import event_bus

logger = getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class HookRegistry:
    """Registry for event hooks — allows decorating functions to handle events."""

    def __init__(self, bus=None):
        self.bus = bus or event_bus
        self._hooks = {}

    def on(self, event_type: str) -> Callable[[F], F]:
        """Decorator to register a function as an event handler.
        
        @hook_registry.on("event.type")
        async def my_handler(event_type: str, payload: dict):
            pass
        """
        def decorator(func: F) -> F:
            self.bus.register(event_type, func)
            if event_type not in self._hooks:
                self._hooks[event_type] = []
            self._hooks[event_type].append(func)
            return func
        return decorator


# Global singleton
hook_registry = HookRegistry(event_bus)


def on_event(event_type: str) -> Callable[[F], F]:
    """Convenience decorator for @on_event("event.type").
    
    @on_event("event.type")
    async def my_handler(event_type: str, payload: dict):
        pass
    """
    return hook_registry.on(event_type)
