"""Async bulk writer with buffering for OpenSearch.

Usage:
    await bulk_index("telemetry", [{"metric_name": "...", "value_ms": 12.3, ...}])

Documents are auto-stamped with @timestamp and bulk-sent to the daily index.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from opensearch.client import get_client
from opensearch.indices import daily_index

_FLUSH_INTERVAL = 5.0   # seconds
_FLUSH_THRESHOLD = 100  # docs per index before forced flush

# buffer: {index_name: [doc, ...]}
_buffer: dict[str, list[dict[str, Any]]] = defaultdict(list)
_lock = asyncio.Lock()
_flush_task: asyncio.Task | None = None


async def bulk_index(base: str, docs: list[dict[str, Any]]) -> None:
    """Buffer docs for bulk indexing into `cybersecsuite-{base}-YYYY.MM.DD`."""
    if not docs:
        return
    index = daily_index(base)
    now = datetime.now(timezone.utc).isoformat()
    stamped = [{"@timestamp": now, **d} for d in docs]

    async with _lock:
        _buffer[index].extend(stamped)
        should_flush = len(_buffer[index]) >= _FLUSH_THRESHOLD

    if should_flush:
        await _flush_index(index)


async def _flush_index(index: str) -> None:
    async with _lock:
        docs = _buffer.pop(index, [])
    if not docs:
        return
    actions: list[dict[str, Any]] = []
    for doc in docs:
        actions.append({"index": {"_index": index}})
        actions.append(doc)
    try:
        client = get_client()
        await client.bulk(body=actions, refresh=False)
    except Exception:
        # Non-fatal — telemetry loss is acceptable
        pass


async def flush_all() -> None:
    """Flush all buffered indices. Call on graceful shutdown."""
    async with _lock:
        indices = list(_buffer.keys())
    for index in indices:
        await _flush_index(index)


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
