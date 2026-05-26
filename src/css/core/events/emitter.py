"""Reusable event emission helpers.

Prefer composition (NamespacedEventEmitter) over inheritance for event emission.
An optional mixin is provided for class-based components that want convenience.
"""

import inspect
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from functools import wraps
from typing import TYPE_CHECKING, ParamSpec, TypeVar, cast

from css.core.types.base_emitter import BaseEmitterClass

if TYPE_CHECKING:
    from .event_bus import EventBus

P = ParamSpec("P")
TResult = TypeVar("TResult")


def get_event_bus() -> "EventBus":
    """Return the typed global EventBus singleton."""
    from .event_bus import event_bus as raw_event_bus

    return cast("EventBus", raw_event_bus)


async def emit_event(event_type: str, payload: Mapping[str, object] | None = None) -> None:
    """Emit one event with an immutable-friendly payload mapping."""
    await get_event_bus().emit(event_type, dict(payload or {}))


async def emit_events(
    event_types: Sequence[str],
    payload: Mapping[str, object] | None = None,
) -> None:
    """Emit many events in-order with the same payload."""
    bus = get_event_bus()
    body = dict(payload or {})
    for event_type in event_types:
        await bus.emit(event_type, body)


class NamespacedEventEmitter:
    """Event emitter that prefixes local names with a namespace."""

    def __init__(self, namespace: str):
        self._namespace = namespace.strip(".")

    def _qualify(self, event_type: str) -> str:
        if not self._namespace:
            return event_type
        if event_type.startswith(f"{self._namespace}."):
            return event_type
        return f"{self._namespace}.{event_type}"

    async def emit(
        self,
        event_type: str,
        payload: Mapping[str, object] | None = None,
    ) -> None:
        await emit_event(self._qualify(event_type), payload)

    async def emit_many(
        self,
        event_types: Sequence[str],
        payload: Mapping[str, object] | None = None,
    ) -> None:
        await emit_events([self._qualify(event_type) for event_type in event_types], payload)


EventEmitterMixin = BaseEmitterClass


def _as_emitter(call_args: tuple[object, ...]) -> BaseEmitterClass | None:
    if not call_args:
        return None
    candidate = call_args[0]
    if isinstance(candidate, BaseEmitterClass):
        return candidate
    return None


def _resolve_event_name(event_name: str, call_args: tuple[object, ...]) -> str:
    emitter = _as_emitter(call_args)
    if emitter is not None:
        return emitter.qualify_event_name(event_name)
    return event_name


def _event_enabled_for_call(event_name: str, call_args: tuple[object, ...]) -> bool:
    emitter = _as_emitter(call_args)
    if emitter is not None:
        declared = emitter.declared_events()
        if declared and not emitter.event_registered(event_name):
            return False
    return True


def _callable_name(func: object) -> str:
    module_name_obj = getattr(func, "__module__", "")
    module_name = module_name_obj if isinstance(module_name_obj, str) else ""
    qualname_obj = getattr(func, "__qualname__", "")
    qualname = qualname_obj if isinstance(qualname_obj, str) else ""
    name_obj = getattr(func, "__name__", "")
    name = name_obj if isinstance(name_obj, str) else ""
    fn = qualname or name or "anonymous"
    return f"{module_name}.{fn}" if module_name else fn


def _lifecycle_decorator(
    event_name: str | None = None,
    *,
    emit_pre: bool,
    emit_post: bool,
    emit_completed: bool,
    emit_failed: bool,
) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
    def decorate(func: Callable[P, Awaitable[TResult]]) -> Callable[P, Awaitable[TResult]]:
        if not inspect.iscoroutinefunction(func):
            raise TypeError("event decorators require async functions/methods")

        default_event_name = event_name or _callable_name(func).split(".")[-1]
        function_name = _callable_name(func)

        @wraps(func)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> TResult:
            from css.modules.hooks.interceptors import (
                HookBlockedError,
                HookContext,
                interceptor_registry,
            )

            arg_tuple = cast(tuple[object, ...], args)
            resolved_event = _resolve_event_name(default_event_name, arg_tuple)
            enabled = _event_enabled_for_call(resolved_event, arg_tuple)
            started = time.monotonic()
            context = HookContext(
                namespace=resolved_event,
                input={
                    "args": list(arg_tuple),
                    "kwargs": dict(cast(dict[str, object], kwargs)),
                },
                metadata={
                    "function": function_name,
                    "decorator": "event",
                },
            )

            context = await interceptor_registry.run_pre(context)
            call_args = context.get_args()
            call_kwargs = context.get_kwargs()

            payload: dict[str, object] = {
                "event": resolved_event,
                "function": function_name,
                "args_count": len(call_args),
                "kwargs_keys": tuple(sorted(call_kwargs.keys())),
                "correlation_id": context.correlation_id,
                "metadata": context.metadata,
            }

            if enabled and emit_pre:
                await emit_event(f"{resolved_event}.pre", payload)

            try:
                result = await cast(
                    Callable[..., Awaitable[TResult]],
                    func,
                )(*call_args, **call_kwargs)
            except HookBlockedError as error:
                context.error = str(error)
                context.duration_ms = round((time.monotonic() - started) * 1000, 2)
                context = await interceptor_registry.run_post(context)
                if enabled and emit_failed:
                    failed_payload = dict(payload)
                    failed_payload["duration_ms"] = context.duration_ms
                    failed_payload["error"] = context.error
                    failed_payload["error_type"] = type(error).__name__
                    failed_payload["metadata"] = context.metadata
                    await emit_event(f"{resolved_event}.failed", failed_payload)
                raise
            except BaseException as error:
                context.error = str(error)
                context.duration_ms = round((time.monotonic() - started) * 1000, 2)
                context = await interceptor_registry.run_post(context)
                if enabled and emit_failed:
                    failed_payload = dict(payload)
                    failed_payload["duration_ms"] = context.duration_ms
                    failed_payload["error"] = context.error
                    failed_payload["error_type"] = type(error).__name__
                    failed_payload["metadata"] = context.metadata
                    await emit_event(f"{resolved_event}.failed", failed_payload)
                raise

            context.output = cast(object, result)
            context.duration_ms = round((time.monotonic() - started) * 1000, 2)
            context = await interceptor_registry.run_post(context)

            success_payload = dict(payload)
            success_payload["duration_ms"] = context.duration_ms
            success_payload["result_type"] = type(result).__name__
            success_payload["metadata"] = context.metadata

            if enabled and emit_post:
                await emit_event(f"{resolved_event}.post", success_payload)
            if enabled and emit_completed:
                await emit_event(f"{resolved_event}.completed", success_payload)

            if context.output is not None:
                return cast(TResult, context.output)
            return result

        return wrapped

    return decorate


class _EventDecoratorSet:
    """Decorator set for lifecycle-triggered event emission."""

    def pre(
        self,
        event_name: str | None = None,
    ) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
        return _lifecycle_decorator(
            event_name,
            emit_pre=True,
            emit_post=False,
            emit_completed=False,
            emit_failed=False,
        )

    def post(
        self,
        event_name: str | None = None,
    ) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
        return _lifecycle_decorator(
            event_name,
            emit_pre=False,
            emit_post=True,
            emit_completed=False,
            emit_failed=False,
        )

    def past(
        self,
        event_name: str | None = None,
    ) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
        """Alias for post() to match requested decorator naming."""
        return self.post(event_name)

    def on_completed(
        self,
        event_name: str | None = None,
    ) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
        return _lifecycle_decorator(
            event_name,
            emit_pre=False,
            emit_post=False,
            emit_completed=True,
            emit_failed=False,
        )

    def on_failed(
        self,
        event_name: str | None = None,
    ) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
        return _lifecycle_decorator(
            event_name,
            emit_pre=False,
            emit_post=False,
            emit_completed=False,
            emit_failed=True,
        )

    def all(
        self,
        event_name: str | None = None,
    ) -> Callable[[Callable[P, Awaitable[TResult]]], Callable[P, Awaitable[TResult]]]:
        return _lifecycle_decorator(
            event_name,
            emit_pre=True,
            emit_post=True,
            emit_completed=True,
            emit_failed=True,
        )


event = _EventDecoratorSet()
