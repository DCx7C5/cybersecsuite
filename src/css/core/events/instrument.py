"""Instrumentation helpers — emit tool/agent events to the event bus.

Provides a lightweight async context manager ``instrument()`` that emits
``*.start``, ``*.complete``, and ``*.error`` events around any operation.

Usage::

    from .instrument import instrument

    async with instrument("tool.call", tool_id="openai:code_interpreter", agent_id="a1"):
        result = await execute_tool(...)
"""


import time
import logging
from contextlib import asynccontextmanager
from typing import Any
from collections.abc import AsyncIterator

from .event_bus import event_bus

logger = logging.getLogger(__name__)


@asynccontextmanager
async def instrument(
    event_prefix: str,
    **payload_fields: Any,
) -> AsyncIterator[dict[str, Any]]:
    """Async context manager that emits ``{prefix}.start``, ``{prefix}.complete``,
    or ``{prefix}.error`` events around the wrapped block.

    Args:
        event_prefix: Base event name, e.g. ``"tool.call"`` or ``"agent.run"``.
        **payload_fields: Extra key/value pairs included in every event payload.

    Yields:
        A mutable ``payload`` dict. The wrapped code may add keys to it;
        those keys will appear in the ``.complete`` event.

    Example::

        async with instrument("tool.call", tool_id="openai:code_interpreter") as p:
            p["result"] = await execute_tool(tool_id, params)
    """
    start = time.monotonic()
    payload: dict[str, Any] = {**payload_fields, "started_at": start}

    await event_bus.emit(f"{event_prefix}.start", payload)

    try:
        yield payload
    except Exception as exc:
        elapsed = time.monotonic() - start
        error_payload = {
            **payload,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": round(elapsed * 1000, 2),
        }
        logger.warning("instrument[%s] error: %s", event_prefix, exc)
        await event_bus.emit(f"{event_prefix}.error", error_payload)
        raise
    else:
        elapsed = time.monotonic() - start
        payload["duration_ms"] = round(elapsed * 1000, 2)
        await event_bus.emit(f"{event_prefix}.complete", payload)


__all__ = ["instrument"]
