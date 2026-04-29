"""Async bulk writer with buffering for OpenObserve (T016).

Usage:
    await bulk_index("telemetry", [{"metric_name": "...", "value_ms": 12.3, ...}])
    await emit_event("qol_metrics", "qol.injection", {"tokens": 42})
    await emit_metric("qol", "injection_latency_ms", 5.2, {"agent": "cybersec"})

Documents are auto-stamped with @timestamp and bulk-sent to the daily stream.
Metrics are emitted with graceful degradation if OpenObserve unavailable (T020).
"""



import asyncio
import json
import logging
import os
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from openobserve.client import get_client, OPENOBSERVE_ORG
from openobserve.streams import stream_name

logger = logging.getLogger("openobserve.writer")

_FLUSH_INTERVAL = 5.0  # seconds
_FLUSH_THRESHOLD = 100  # legacy_docs per stream before forced flush
_RETRY_MAX_ATTEMPTS = 3
_RETRY_BASE_DELAY_MS = 100
_ENABLED = os.environ.get("OPENOBSERVE_ENABLED", "true").lower() in ("true", "1", "yes")

_buffer: dict[str, list[dict[str, Any]]] = defaultdict(list)
_lock = asyncio.Lock()
_flush_task: asyncio.Task | None = None

# Emission statistics (T016)
_stats = {
    "events_sent": 0,
    "events_failed": 0,
    "bytes_sent": 0,
}


async def bulk_index(base: str, docs: list[dict[str, Any]]) -> None:
    """Buffer legacy_docs for bulk indexing into `cybersecsuite-{base}-YYYY.MM.DD` stream."""
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


async def emit_event(
    stream: str,
    event_type: str,
    data: dict[str, Any],
    retry_attempts: int = _RETRY_MAX_ATTEMPTS,
) -> bool:
    """Emit a single event to OpenObserve with retry logic (T016/T020).

    Args:
        stream: stream name (e.g., "qol_metrics")
        event_type: event classification (e.g., "qol.injection")
        data: event data dict
        retry_attempts: number of retry attempts on failure

    Returns:
        True if sent successfully, False otherwise.
        Always returns gracefully; never raises.
    """
    if not _ENABLED:
        return False

    event = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **data,
    }

    for attempt in range(1, retry_attempts + 1):
        try:
            client = get_client()
            if client is None:
                logger.debug("OpenObserve client unavailable, skipping event emission")
                _stats["events_failed"] += 1
                return False

            # POST to /api/default/{org}/events/{stream}
            endpoint = f"/api/default/{OPENOBSERVE_ORG}/events/{stream}"
            payload = json.dumps(event)
            response = await client.post(
                endpoint,
                content=payload,
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )

            if response.status_code in (200, 201):
                _stats["events_sent"] += 1
                _stats["bytes_sent"] += len(payload)
                logger.debug("Event emitted to OpenObserve: %s/%s", stream, event_type)
                return True

            if response.status_code >= 500 and attempt < retry_attempts:
                delay_ms = _RETRY_BASE_DELAY_MS * (2 ** (attempt - 1))
                await asyncio.sleep(delay_ms / 1000.0)
                continue

            logger.warning(
                "OpenObserve emission failed (status %d): %s/%s",
                response.status_code,
                stream,
                event_type,
            )
            _stats["events_failed"] += 1
            return False

        except asyncio.CancelledError:
            raise
        except Exception as e:
            if attempt < retry_attempts:
                delay_ms = _RETRY_BASE_DELAY_MS * (2 ** (attempt - 1))
                await asyncio.sleep(delay_ms / 1000.0)
                continue
            logger.debug("OpenObserve emission error: %s", e, exc_info=True)
            _stats["events_failed"] += 1
            return False

    return False


async def emit_metric(
    stream: str,
    metric_name: str,
    value: float,
    tags: dict[str, str] | None = None,
) -> bool:
    """Emit a metric point to OpenObserve (T016).

    Args:
        stream: stream name (e.g., "qol_metrics")
        metric_name: metric name (e.g., "injection_latency_ms")
        value: numeric value
        tags: optional labels dict

    Returns:
        True if emitted successfully, False otherwise.
    """
    data = {"metric_name": metric_name, "value": value}
    if tags:
        data.update(tags)
    return await emit_event(stream, metric_name, data)


def get_writer_stats() -> dict[str, Any]:
    """Return current emission statistics (T016)."""
    return _stats.copy()


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