"""In-process metrics store with ring-buffer per key and percentile summaries."""
from __future__ import annotations

import asyncio
import math
import statistics
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

_RING_MAX = 1000


@dataclass
class TelemetryEvent:
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    ts: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MetricSummary:
    count: int
    mean: float
    p50: float
    p95: float
    p99: float
    rps: float  # events per second over the window


class MetricsStore:
    """Thread-safe, in-process ring-buffer metrics store."""

    def __init__(self, ring_max: int = _RING_MAX) -> None:
        self._ring_max = ring_max
        self._lock = asyncio.Lock()
        self._rings: dict[str, deque[TelemetryEvent]] = {}

    async def record(self, event: TelemetryEvent) -> None:
        async with self._lock:
            ring = self._rings.setdefault(event.name, deque(maxlen=self._ring_max))
            ring.append(event)

    async def get_summary(self, name: str) -> MetricSummary | None:
        async with self._lock:
            ring = self._rings.get(name)
            if not ring:
                return None
            values = [e.value for e in ring]
            timestamps = [e.ts.timestamp() for e in ring]

        count = len(values)
        if count == 0:
            return None

        sorted_vals = sorted(values)
        mean = statistics.mean(values)
        p50 = _percentile(sorted_vals, 50)
        p95 = _percentile(sorted_vals, 95)
        p99 = _percentile(sorted_vals, 99)

        # rps = events / window duration
        window = max(timestamps) - min(timestamps) if len(timestamps) > 1 else 1.0
        rps = count / window if window > 0 else float(count)

        return MetricSummary(count=count, mean=mean, p50=p50, p95=p95, p99=p99, rps=rps)

    async def get_snapshot(self) -> dict[str, Any]:
        """Return summaries for all tracked metrics."""
        async with self._lock:
            names = list(self._rings.keys())

        result: dict[str, Any] = {}
        for name in names:
            summary = await self.get_summary(name)
            if summary:
                result[name] = {
                    "count": summary.count,
                    "mean": round(summary.mean, 4),
                    "p50": round(summary.p50, 4),
                    "p95": round(summary.p95, 4),
                    "p99": round(summary.p99, 4),
                    "rps": round(summary.rps, 4),
                }
        return result

    async def keys(self) -> list[str]:
        async with self._lock:
            return list(self._rings.keys())


def _percentile(sorted_values: list[float], p: int) -> float:
    n = len(sorted_values)
    if n == 0:
        return 0.0
    idx = (p / 100) * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_values[lo]
    frac = idx - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac
