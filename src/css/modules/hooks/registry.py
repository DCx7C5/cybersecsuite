"""Event hook registry owned by modules/hooks.

Hooks consume events from ``css.core.events.event_bus``.
"""

import asyncio
import fnmatch
import inspect
from collections.abc import Awaitable, Callable
from functools import partial
from typing import TypeAlias, override

from css.core.logger import getLogger
from css.core.types.base_registry import BaseRegistry
from css.core.types.meta import singleton
from .base import BaseHookClass

logger = getLogger(__name__)

HookResult: TypeAlias = object | None
HookHandler: TypeAlias = Callable[[str, object], HookResult | Awaitable[HookResult]]


def _get_event_bus():
    from css.core.events.emitter import get_event_bus
    return get_event_bus()

HookRegistration = BaseHookClass


class _HookBinding:
    """Runtime hook binding with callable handler."""

    def __init__(self, pattern: str, handler: HookHandler, priority: int) -> None:
        self.pattern = pattern
        self.handler = handler
        self.priority = priority


@singleton(auto_instantiate=True)
class HookRegistry(BaseRegistry[HookRegistration]):
    """Pattern hook registry with chained execution and non-blocking dispatch."""

    _initialized: bool = False

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self._bindings: list[_HookBinding] = []
        self._bound_events: set[str] = set()
        self._timeout_seconds = 5.0

    def register(self, pattern: str, handler: HookHandler, *, priority: int = 50) -> None:
        """Register a hook and bind bus dispatcher(s) for the pattern."""
        self._bindings.append(_HookBinding(pattern=pattern, handler=handler, priority=priority))
        self._bind_dispatcher()

    def on(self, pattern: str, *, priority: int = 50) -> Callable[[HookHandler], HookHandler]:
        """Decorator form for hook registration."""

        def decorator(func: HookHandler) -> HookHandler:
            self.register(pattern, func, priority=priority)
            return func

        return decorator

    async def run_chain(self, event_type: str, payload: object) -> object:
        """Run matching handlers in priority order for one emitted event."""
        current_payload = payload
        for binding in self._matching_bindings(event_type):
            current_payload = await self._call_handler(binding.handler, event_type, current_payload)
        return current_payload

    def list_patterns(self) -> list[str]:
        """List distinct hook patterns."""
        return sorted({binding.pattern for binding in self._bindings})

    @override
    async def get(self, identifier: str) -> HookRegistration | None:
        for binding in sorted(self._bindings, key=lambda item: item.priority):
            if binding.pattern == identifier:
                return HookRegistration(pattern=binding.pattern, priority=binding.priority)
        return None

    @override
    async def list(
        self,
        predicate: Callable[[HookRegistration], bool] | None = None,
    ) -> list[HookRegistration]:
        items = [
            HookRegistration(pattern=binding.pattern, priority=binding.priority)
            for binding in sorted(self._bindings, key=lambda item: (item.pattern, item.priority))
        ]
        if predicate is None:
            return items
        return [item for item in items if predicate(item)]

    @override
    async def invalidate(self, identifier: str | None = None) -> None:
        if identifier is None:
            self._bindings.clear()
            self._unbind_all_dispatchers()
            return

        self._bindings = [binding for binding in self._bindings if binding.pattern != identifier]
        if not self._bindings:
            self._unbind_all_dispatchers()

    @override
    async def reload(self) -> None:
        """No persisted source yet; ensure dispatcher bind state is coherent."""
        if self._bindings:
            self._bind_dispatcher()
        else:
            self._unbind_all_dispatchers()

    def _bind_dispatcher(self) -> None:
        """Bind one wildcard dispatcher to capture all emitted events."""
        if "*" in self._bound_events:
            return
        _get_event_bus().register("*", self._dispatch)
        self._bound_events.add("*")

    def _unbind_all_dispatchers(self) -> None:
        event_bus = _get_event_bus()
        for event_name in list(self._bound_events):
            event_bus.unregister(event_name, self._dispatch)
        self._bound_events.clear()

    def _matching_bindings(self, event_type: str) -> list[_HookBinding]:
        matches = [binding for binding in self._bindings if fnmatch.fnmatch(event_type, binding.pattern)]
        matches.sort(key=lambda item: item.priority)
        return matches

    async def _dispatch(self, event_type: str, payload: object) -> None:
        task = asyncio.create_task(self.run_chain(event_type, payload))
        task.add_done_callback(partial(self._log_dispatch_failure, event_type=event_type))

    @staticmethod
    def _log_dispatch_failure(task: asyncio.Task[object], *, event_type: str) -> None:
        if task.cancelled():
            return
        error = task.exception()
        if error is not None:
            logger.warning("hook chain failed for %s: %s", event_type, error)

    async def _call_handler(self, handler: HookHandler, event_type: str, payload: object) -> object:
        try:
            result = await asyncio.wait_for(
                self._invoke_handler(handler, event_type, payload),
                timeout=self._timeout_seconds,
            )
        except asyncio.CancelledError:
            raise
        except BaseException as error:
            logger.warning("hook handler failed for %s: %s", event_type, error)
            return payload

        return payload if result is None else result

    @staticmethod
    async def _invoke_handler(handler: HookHandler, event_type: str, payload: object) -> HookResult:
        if inspect.iscoroutinefunction(handler):
            return await handler(event_type, payload)
        result = await asyncio.to_thread(handler, event_type, payload)
        if inspect.isawaitable(result):
            return await result
        return result


class _HookRegistryHandle:
    """Lazy handle to singleton HookRegistry (no eager instance construction)."""

    def __getattr__(self, attribute: str) -> object:
        return getattr(HookRegistry(), attribute)


hook_registry = _HookRegistryHandle()


def on_event(pattern: str, *, priority: int = 50) -> Callable[[HookHandler], HookHandler]:
    """Decorator shortcut for registering event hooks."""
    return HookRegistry().on(pattern, priority=priority)


__all__ = [
    "HookRegistry",
    "HookRegistration",
    "hook_registry",
    "on_event",
]
