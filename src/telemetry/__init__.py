"""Telemetry package — module-level singleton and convenience helpers."""
from __future__ import annotations

from telemetry.store import MetricSummary, MetricsStore, TelemetryEvent

metrics_store = MetricsStore()


async def record_event(
    name: str,
    value: float,
    labels: dict[str, str] | None = None,
) -> None:
    await metrics_store.record(TelemetryEvent(name=name, value=value, labels=labels or {}))


async def get_snapshot() -> dict:
    return await metrics_store.get_snapshot()


__all__ = [
    "metrics_store",
    "record_event",
    "get_snapshot",
    "TelemetryEvent",
    "MetricSummary",
    "MetricsStore",
]
