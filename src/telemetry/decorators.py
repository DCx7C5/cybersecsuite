"""Async decorators for timing and counting functions via MetricsStore."""
from __future__ import annotations

import functools
import time
from collections.abc import Callable, Coroutine
from typing import Any

from telemetry import record_event


def timed(name: str) -> Callable:
    """Wrap an async function, recording its duration_ms to the metrics store."""

    def decorator(fn: Callable[..., Coroutine[Any, Any, Any]]) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            t0 = time.perf_counter()
            try:
                return await fn(*args, **kwargs)
            finally:
                await record_event(f"{name}.duration_ms", (time.perf_counter() - t0) * 1000)

        return wrapper

    return decorator


def counted(name: str) -> Callable:
    """Wrap an async function, incrementing a counter on every call."""

    def decorator(fn: Callable[..., Coroutine[Any, Any, Any]]) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            await record_event(f"{name}.calls", 1.0)
            return await fn(*args, **kwargs)

        return wrapper

    return decorator
