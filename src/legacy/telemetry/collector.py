"""Background task that snapshots MetricsStore every 15 s and keeps history."""


import asyncio
from collections import deque
from typing import Any

from telemetry import get_snapshot

_HISTORY_MAX = 100
_INTERVAL_S = 15


class TelemetryCollector:
    """Polls MetricsStore on a fixed cadence and maintains a rolling snapshot history."""

    def __init__(self, interval: float = _INTERVAL_S, history_max: int = _HISTORY_MAX) -> None:
        self._interval = interval
        self._history_max = history_max
        self._history: deque[dict[str, Any]] = deque(maxlen=history_max)
        self._task: asyncio.Task | None = None

    # ── lifecycle ────────────────────────────────────────────────────────────

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.ensure_future(self._run())

    def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()

    # ── query ────────────────────────────────────────────────────────────────

    def get_history(self, metric: str, n: int = 20) -> list[float]:
        """Return the last n values for a specific metric (for sparklines)."""
        values: list[float] = []
        for snap in self._history:
            entry = snap.get(metric)
            if entry:
                values.append(entry.get("mean", 0.0))
        return values[-n:]

    def latest_snapshot(self) -> dict[str, Any]:
        if self._history:
            return self._history[-1]
        return {}

    def all_history(self) -> list[dict[str, Any]]:
        return list(self._history)

    # ── internal ─────────────────────────────────────────────────────────────

    async def _run(self) -> None:
        while True:
            try:
                snap = await get_snapshot()
                self._history.append(snap)
            except Exception:
                pass
            await asyncio.sleep(self._interval)


# Module-level singleton — start with collector.start() in app lifespan
collector = TelemetryCollector()
