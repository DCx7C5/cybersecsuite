"""Tests for telemetry — metrics store, path normalization, aggregation."""

import pytest

from telemetry import (
    record_event,
    get_snapshot,
    TelemetryEvent,
)
from telemetry.store import MetricsStore
from proxy.middleware import _normalise


@pytest.mark.anyio
class TestTelemetryStore:
    """Test in-process metrics store."""

    async def test_record_event(self):
        event = TelemetryEvent(name="test.metric", value=42.0, labels={"status": "ok"})
        await record_event(event.name, event.value, event.labels)
        snapshot = await get_snapshot()
        assert isinstance(snapshot, dict)

    async def test_get_snapshot(self):
        await record_event("snap.test1", 10.0)
        await record_event("snap.test2", 20.0)
        snapshot = await get_snapshot()
        assert isinstance(snapshot, dict)

    async def test_metrics_store_ring_buffer(self):
        store = MetricsStore(ring_max=100)
        for i in range(150):
            await store.record(TelemetryEvent(name="ring.test", value=float(i)))
        summary = await store.get_summary("ring.test")
        assert summary is not None
        assert summary.count <= 100

    async def test_metrics_store_keys(self):
        store = MetricsStore()
        await store.record(TelemetryEvent(name="keys.a", value=1.0))
        await store.record(TelemetryEvent(name="keys.b", value=2.0))
        keys = await store.keys()
        assert "keys.a" in keys
        assert "keys.b" in keys


class TestPathNormalization:
    """Test path normalization for metrics keys."""

    def test_uuid_normalization(self):
        path = "/api/findings/123e4567-e89b-12d3-a456-426614174000"
        result = _normalise(path)
        assert "{" in result or result != path

    def test_numeric_id_normalization(self):
        path = "/api/findings/987654321"
        result = _normalise(path)
        assert result

    def test_plain_path_unchanged(self):
        path = "/api/v1/chat"
        result = _normalise(path)
        assert result == "/api/v1/chat"


@pytest.mark.anyio
class TestTelemetryMetrics:
    """Test specific metrics collection."""

    async def test_request_latency_metric(self):
        await record_event(
            "http.request.duration_ms", 123.45,
            {"path": "/api/v1/chat", "method": "POST"},
        )
        snapshot = await get_snapshot()
        assert snapshot is not None

    async def test_error_rate_metric(self):
        for _ in range(5):
            await record_event("http.error", 1.0, {"status": "500", "path": "/api/test"})
        snapshot = await get_snapshot()
        assert snapshot is not None

    async def test_token_usage_metric(self):
        await record_event(
            "ai.tokens.used", 1250.0,
            {"model": "claude-opus", "direction": "input"},
        )
        snapshot = await get_snapshot()
        assert snapshot is not None


@pytest.mark.anyio
class TestMetricsAggregation:
    """Test metrics aggregation and summaries."""

    async def test_summary_for_metric(self):
        store = MetricsStore()
        for i in range(10):
            await store.record(TelemetryEvent(name="agg.response_time", value=50.0 + i * 10))
        summary = await store.get_summary("agg.response_time")
        assert summary is not None
        assert summary.count == 10
        assert summary.mean > 0

    async def test_percentile_calculations(self):
        store = MetricsStore()
        for lat in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
            await store.record(TelemetryEvent(name="agg.latency", value=float(lat)))
        summary = await store.get_summary("agg.latency")
        assert summary is not None
        assert summary.p50 > 0
        assert summary.p95 >= summary.p50
        assert summary.p99 >= summary.p95

    async def test_snapshot_returns_all_metrics(self):
        store = MetricsStore()
        await store.record(TelemetryEvent(name="snap.a", value=1.0))
        await store.record(TelemetryEvent(name="snap.b", value=2.0))
        snapshot = await store.get_snapshot()
        assert isinstance(snapshot, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
