"""Async bulk writer with buffering for OpenObserve.

Usage:
    await bulk_index("telemetry", [{"metric_name": "...", "value_ms": 12.3, ...}])

Documents are auto-stamped with @timestamp and bulk-sent to the daily stream.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from openobserve.client import get_client, OPENOBSERVE_ORG
from openobserve.streams import stream_name

_FLUSH_INTERVAL = 5.0  # seconds
_FLUSH_THRESHOLD = 100  # docs per stream before forced flush

_buffer: dict[str, list[dict[str, Any]]] = defaultdict(list)
_lock = asyncio.Lock()
_flush_task: asyncio.Task | None = None


async def bulk_index(base: str, docs: list[dict[str, Any]]) -> None:
    """Buffer docs for bulk indexing into `cybersecsuite-{base}-YYYY.MM.DD` stream."""
    if not docs:
        return
    stream = stream_name(base)
    now = datetime.now(timezone.utc).isoformat()
    stamped = [{"@timestamp": now, **d} for d in docs]

    async with _lock:
        _buffer[stream].extend(stamped)
        should_flush = len(_buffer[stream]) >= _FLUSH_THRESHOLD

    if should_flush:
        await _flush_stream(base)


async def _flush_stream(base: str) -> None:
    stream = stream_name(base)
    async with _lock:
        docs = _buffer.pop(stream, [])
    if not docs:
        return
    try:
        client = get_client()
        org = OPENOBSERVE_ORG
        await client.post(f"/api/{org}/{base}/_json", json=docs)
    except Exception:
        pass


async def flush_all() -> None:
    """Flush all buffered streams. Call on graceful shutdown."""
    async with _lock:
        streams = list(_buffer.keys())
    for stream in streams:
        base = stream.split("-")[-3]  # extract "telemetry" from cybersecsuite-telemetry-YYYY.MM.DD
        await _flush_stream(base)


def start_flush_loop() -> None:
    """Start background flush task. Call once during app lifespan startup."""
    global _flush_task

    async def _loop() -> None:
        while True:
            await asyncio.sleep(_FLUSH_INTERVAL)
            await flush_all()

    if _flush_task is None or _flush_task.done():
        _flush_task = asyncio.ensure_future(_loop())


def stop_flush_loop() -> None:
    """Cancel the background flush loop. Call during app shutdown after flush_all()."""
    global _flush_task
    if _flush_task and not _flush_task.done():
        _flush_task.cancel()
        _flush_task = None