"""Instrumentation helpers for EventStore-backed lifecycle events."""

from __future__ import annotations

import asyncio
import inspect
import time
from contextvars import Token
from collections.abc import Coroutine
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, TypeVar, cast
from uuid import uuid4

from css.modules.hooks.interceptors import HookContext, get_interceptor_registry

from .domain_event import DomainEvent
from .emitter import get_event_bus
from .otel_context import OtelSpanInstrumentor, correlation_id_ctx, get_correlation_id

P = ParamSpec("P")
R = TypeVar("R")
_correlation_ctx = correlation_id_ctx


def _resolve_correlation_id() -> tuple[str, Token[str] | None]:
    existing = get_correlation_id()
    if existing:
        return existing, None
    correlation_id = str(uuid4())
    return correlation_id, correlation_id_ctx.set(correlation_id)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


async def _emit_domain_event(
    *,
    namespace: str,
    stage: str,
    correlation_id: str,
    function_name: str,
    started_at: str,
    duration_ms: float | None,
    error_type: str | None,
    metadata: dict[str, Any],
    data: dict[str, Any],
) -> None:
    from . import get_event_store

    get_event_store().append(
        DomainEvent(
            kind=f"{namespace}.{stage}",
            aggregate_type="instrument",
            aggregate_id=correlation_id,
            metadata={
                "correlation_id": correlation_id,
                "function": function_name,
                "started_at": started_at,
                "duration_ms": duration_ms,
                "error_type": error_type,
                **metadata,
            },
            data=data,
        )
    )


def _run_bus_emit_sync(event_type: str, payload: dict[str, Any]) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(get_event_bus().emit(event_type, payload))
        return
    loop.create_task(get_event_bus().emit(event_type, payload))


def _run_async_sync(coro: Coroutine[Any, Any, None]) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
        return
    loop.create_task(coro)


def _wrap_sync(
    namespace: str,
    fn: Callable[P, R],
    metadata: dict[str, Any],
) -> Callable[P, R]:
    function_name = f"{fn.__module__}.{fn.__qualname__}"

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started_at = _now_iso()
        started_monotonic = time.monotonic()
        correlation_id = str(uuid4())
        span = OtelSpanInstrumentor.start_span(
            f"{namespace}.{function_name}",
            attributes={"correlation_id": correlation_id},
        )

        _run_async_sync(
            _emit_domain_event(
                namespace=namespace,
                stage="started",
                correlation_id=correlation_id,
                function_name=function_name,
                started_at=started_at,
                duration_ms=0.0,
                error_type=None,
                metadata=metadata,
                data={"args_count": len(args), "kwargs_keys": sorted(kwargs.keys())},
            )
        )
        _run_bus_emit_sync(f"{namespace}.start", {**metadata, "started_at": started_monotonic})

        try:
            result = fn(*args, **kwargs)
        except BaseException as exc:
            duration_ms = round((time.monotonic() - started_monotonic) * 1000, 2)
            OtelSpanInstrumentor.record_exception(span, exc)
            OtelSpanInstrumentor.end_span(span, status=type(exc).__name__)
            _run_async_sync(
                _emit_domain_event(
                    namespace=namespace,
                    stage="failed",
                    correlation_id=correlation_id,
                    function_name=function_name,
                    started_at=started_at,
                    duration_ms=duration_ms,
                    error_type=type(exc).__name__,
                    metadata=metadata,
                    data={"error": str(exc)},
                )
            )
            _run_bus_emit_sync(
                f"{namespace}.error",
                {
                    **metadata,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                    "duration_ms": duration_ms,
                },
            )
            raise

        OtelSpanInstrumentor.end_span(span, status="OK")
        duration_ms = round((time.monotonic() - started_monotonic) * 1000, 2)
        _run_async_sync(
            _emit_domain_event(
                namespace=namespace,
                stage="completed",
                correlation_id=correlation_id,
                function_name=function_name,
                started_at=started_at,
                duration_ms=duration_ms,
                error_type=None,
                metadata=metadata,
                data={"result_type": type(result).__name__},
            )
        )
        _run_bus_emit_sync(f"{namespace}.complete", {**metadata, "duration_ms": duration_ms})
        return result

    return wrapper


def _wrap_async(
    namespace: str,
    fn: Callable[P, Awaitable[R]],
    metadata: dict[str, Any],
) -> Callable[P, Awaitable[R]]:
    function_name = f"{fn.__module__}.{fn.__qualname__}"

    @wraps(fn)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started_at = _now_iso()
        started_monotonic = time.monotonic()
        context = HookContext(
            namespace=namespace,
            input={"args": list(cast(tuple[object, ...], args)), "kwargs": dict(cast(dict[str, object], kwargs))},
            metadata={"instrument": True, **metadata},
        )
        context = await get_interceptor_registry().run_pre(context)
        call_args = cast(tuple[Any, ...], context.get_args())
        call_kwargs = cast(dict[str, Any], context.get_kwargs())
        span = OtelSpanInstrumentor.start_span(
            f"{namespace}.{function_name}",
            attributes={"correlation_id": context.correlation_id},
        )

        await _emit_domain_event(
            namespace=namespace,
            stage="started",
            correlation_id=context.correlation_id,
            function_name=function_name,
            started_at=started_at,
            duration_ms=0.0,
            error_type=None,
            metadata=metadata,
            data={"args_count": len(call_args), "kwargs_keys": sorted(call_kwargs.keys())},
        )
        await get_event_bus().emit(f"{namespace}.start", {**metadata, "started_at": started_monotonic})

        try:
            result = await fn(*call_args, **call_kwargs)
        except BaseException as exc:
            context.error = str(exc)
            context.duration_ms = round((time.monotonic() - started_monotonic) * 1000, 2)
            OtelSpanInstrumentor.record_exception(span, exc)
            OtelSpanInstrumentor.end_span(span, status=type(exc).__name__)
            context = await get_interceptor_registry().run_post(context)
            await _emit_domain_event(
                namespace=namespace,
                stage="failed",
                correlation_id=context.correlation_id,
                function_name=function_name,
                started_at=started_at,
                duration_ms=context.duration_ms,
                error_type=type(exc).__name__,
                metadata=metadata,
                data={"error": str(exc)},
            )
            await get_event_bus().emit(
                f"{namespace}.error",
                {
                    **metadata,
                    "error": context.error,
                    "error_type": type(exc).__name__,
                    "duration_ms": context.duration_ms,
                },
            )
            raise

        OtelSpanInstrumentor.end_span(span, status="OK")
        context.output = cast(object, result)
        context.duration_ms = round((time.monotonic() - started_monotonic) * 1000, 2)
        context = await get_interceptor_registry().run_post(context)
        await _emit_domain_event(
            namespace=namespace,
            stage="completed",
            correlation_id=context.correlation_id,
            function_name=function_name,
            started_at=started_at,
            duration_ms=context.duration_ms,
            error_type=None,
            metadata=metadata,
            data={"result_type": type(result).__name__},
        )
        await get_event_bus().emit(f"{namespace}.complete", {**metadata, "duration_ms": context.duration_ms})
        return cast(R, context.output)

    return wrapper


class _InstrumentBlock:
    def __init__(self, namespace: str, metadata: dict[str, Any]) -> None:
        self.namespace = namespace
        self.metadata = metadata
        self._started_monotonic = 0.0
        self._started_at = ""
        self._context: HookContext | None = None
        self._payload: dict[str, Any] = {}

    def __call__(self, fn: Callable[P, R] | Callable[P, Awaitable[R]]) -> Callable[P, Any]:
        if inspect.iscoroutinefunction(fn):
            return _wrap_async(self.namespace, cast(Callable[P, Awaitable[R]], fn), dict(self.metadata))
        return _wrap_sync(self.namespace, cast(Callable[P, R], fn), dict(self.metadata))

    async def __aenter__(self) -> dict[str, Any]:
        self._started_monotonic = time.monotonic()
        self._started_at = _now_iso()
        self._payload = {**self.metadata, "started_at": self._started_monotonic}
        self._context = HookContext(
            namespace=self.namespace,
            input={"payload": self._payload},
            metadata={"instrument": True, **self.metadata},
        )
        self._context = await get_interceptor_registry().run_pre(self._context)
        payload_obj = self._context.input.get("payload")
        if isinstance(payload_obj, dict):
            self._payload = payload_obj

        await _emit_domain_event(
            namespace=self.namespace,
            stage="started",
            correlation_id=self._context.correlation_id,
            function_name="contextmanager",
            started_at=self._started_at,
            duration_ms=0.0,
            error_type=None,
            metadata=self.metadata,
            data={"payload_keys": sorted(self._payload.keys())},
        )
        await get_event_bus().emit(f"{self.namespace}.start", self._payload)
        return self._payload

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        _tb: object,
    ) -> bool:
        if self._context is None:
            return False

        duration_ms = round((time.monotonic() - self._started_monotonic) * 1000, 2)
        if exc is not None:
            self._context.error = str(exc)
            self._context.duration_ms = duration_ms
            self._context = await get_interceptor_registry().run_post(self._context)
            await _emit_domain_event(
                namespace=self.namespace,
                stage="failed",
                correlation_id=self._context.correlation_id,
                function_name="contextmanager",
                started_at=self._started_at,
                duration_ms=self._context.duration_ms,
                error_type=type(exc).__name__,
                metadata=self.metadata,
                data={"error": str(exc)},
            )
            await get_event_bus().emit(
                f"{self.namespace}.error",
                {
                    **self._payload,
                    "error": self._context.error,
                    "error_type": type(exc).__name__,
                    "duration_ms": self._context.duration_ms,
                    "metadata": self._context.metadata,
                },
            )
            return False

        self._context.output = self._payload
        self._context.duration_ms = duration_ms
        self._context = await get_interceptor_registry().run_post(self._context)
        output_payload = self._context.output
        if isinstance(output_payload, dict):
            self._payload = output_payload
        self._payload["duration_ms"] = self._context.duration_ms
        self._payload["metadata"] = self._context.metadata

        await _emit_domain_event(
            namespace=self.namespace,
            stage="completed",
            correlation_id=self._context.correlation_id,
            function_name="contextmanager",
            started_at=self._started_at,
            duration_ms=self._context.duration_ms,
            error_type=None,
            metadata=self.metadata,
            data={"payload_keys": sorted(self._payload.keys())},
        )
        await get_event_bus().emit(f"{self.namespace}.complete", self._payload)
        return False


def instrument(namespace: str, **metadata: Any) -> _InstrumentBlock:
    """Return a handle usable as both decorator and async context manager."""
    return _InstrumentBlock(namespace, dict(metadata))


def instrument_decorator(namespace: str, **metadata: Any) -> Callable[[Callable[P, R]], Callable[P, Any]]:
    """Backward-compatible alias for decorator usage."""
    block = instrument(namespace, **metadata)

    def decorator(fn: Callable[P, R]) -> Callable[P, Any]:
        return block(fn)

    return decorator


