"""Instrumentation helpers — emit domain events around operations.

Provides ``instrument()`` as both:
- An async context manager (existing usage)::

    async with instrument("tool.call", tool_id="code_interpreter"):
        result = await execute_tool(...)

- A decorator for sync/async functions::

    @instrument_decorator("tool.call")
    async def my_tool(query: str) -> str: ...
"""

import asyncio
import functools
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Any, TypeVar, cast

from css.core.logger import getLogger

from .domain_event import DomainEvent
from .emitter import get_event_bus
from .store import EventStore

logger = getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _emit_domain_event(
    store: EventStore,
    kind: str,
    aggregate_type: str,
    aggregate_id: str,
    data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
) -> None:
    event = DomainEvent(
        kind=kind,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        data=data,
        metadata=metadata or {},
    )
    store.append(event)


def _get_store() -> EventStore:
    from css.core.events import get_event_store
    return get_event_store()


def _wrap_sync(
    fn: Callable[..., Any],
    event_prefix: str,
    **default_metadata: Any,
) -> Callable[..., Any]:
    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        store = _get_store()
        corr_id = str(id(fn))
        started_at = time.monotonic()
        fn_name = fn.__name__
        aggregate_id = kwargs.get("request_id") or kwargs.get("tool_id") or fn_name

        _emit_domain_event(
            store,
            kind=f"{event_prefix}.started",
            aggregate_type=event_prefix,
            aggregate_id=aggregate_id,
            data={"correlation_id": corr_id, "function": fn_name, "started_at": started_at},
            metadata=default_metadata,
        )

        try:
            result = fn(*args, **kwargs)
            duration_ms = round((time.monotonic() - started_at) * 1000, 2)
            _emit_domain_event(
                store,
                kind=f"{event_prefix}.completed",
                aggregate_type=event_prefix,
                aggregate_id=aggregate_id,
                data={
                    "correlation_id": corr_id,
                    "function": fn_name,
                    "duration_ms": duration_ms,
                    "started_at": started_at,
                },
                metadata=default_metadata,
            )
            return result
        except BaseException as exc:
            duration_ms = round((time.monotonic() - started_at) * 1000, 2)
            _emit_domain_event(
                store,
                kind=f"{event_prefix}.failed",
                aggregate_type=event_prefix,
                aggregate_id=aggregate_id,
                data={
                    "correlation_id": corr_id,
                    "function": fn_name,
                    "duration_ms": duration_ms,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "started_at": started_at,
                },
                metadata=default_metadata,
            )
            raise

    return wrapper


def _wrap_async(
    fn: Callable[..., Any],
    event_prefix: str,
    **default_metadata: Any,
) -> Callable[..., Any]:
    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        store = _get_store()
        corr_id = str(id(fn))
        started_at = time.monotonic()
        fn_name = fn.__name__
        aggregate_id = kwargs.get("request_id") or kwargs.get("tool_id") or fn_name

        _emit_domain_event(
            store,
            kind=f"{event_prefix}.started",
            aggregate_type=event_prefix,
            aggregate_id=aggregate_id,
            data={"correlation_id": corr_id, "function": fn_name, "started_at": started_at},
            metadata=default_metadata,
        )

        try:
            result = await fn(*args, **kwargs)
            duration_ms = round((time.monotonic() - started_at) * 1000, 2)
            _emit_domain_event(
                store,
                kind=f"{event_prefix}.completed",
                aggregate_type=event_prefix,
                aggregate_id=aggregate_id,
                data={
                    "correlation_id": corr_id,
                    "function": fn_name,
                    "duration_ms": duration_ms,
                    "started_at": started_at,
                },
                metadata=default_metadata,
            )
            return result
        except BaseException as exc:
            duration_ms = round((time.monotonic() - started_at) * 1000, 2)
            _emit_domain_event(
                store,
                kind=f"{event_prefix}.failed",
                aggregate_type=event_prefix,
                aggregate_id=aggregate_id,
                data={
                    "correlation_id": corr_id,
                    "function": fn_name,
                    "duration_ms": duration_ms,
                    "error_type": type(exc).__name__,
                    "error": str(exc),
                    "started_at": started_at,
                },
                metadata=default_metadata,
            )
            raise

    return wrapper


@asynccontextmanager
async def instrument(
    event_prefix: str,
    **payload_fields: Any,
) -> AsyncIterator[dict[str, Any]]:
    """Async context manager emitting ``{prefix}.started`` / ``.completed`` / ``.failed``.

    Can also be used as a decorator::

        @instrument("tool.call")
        async def my_tool(...): ...
    """
    start = time.monotonic()
    payload: dict[str, Any] = {**payload_fields, "started_at": start}

    await get_event_bus().emit(f"{event_prefix}.start", payload)

    try:
        yield payload
    except BaseException as exc:
        elapsed = time.monotonic() - start
        error_payload = {
            **payload,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": round(elapsed * 1000, 2),
        }
        await get_event_bus().emit(f"{event_prefix}.error", error_payload)
        raise
    else:
        elapsed = time.monotonic() - start
        payload["duration_ms"] = round(elapsed * 1000, 2)
        await get_event_bus().emit(f"{event_prefix}.complete", payload)


def instrument_decorator(
    event_prefix: str,
    **metadata: Any,
) -> Callable[[F], F]:
    """Decorator variant of ``instrument()``.

    Usage::

        @instrument_decorator("tool.call")
        async def query_llm(prompt: str) -> str: ...
    """
    def decorator(fn: F) -> F:
        if asyncio.iscoroutinefunction(fn):
            return cast(F, _wrap_async(fn, event_prefix, **metadata))
        return cast(F, _wrap_sync(fn, event_prefix, **metadata))
    return decorator


__all__ = ["instrument", "instrument_decorator"]
