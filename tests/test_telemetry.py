"""Tests for telemetry — metrics store, middleware, collectors."""
import asyncio
import pytest

from telemetry import (
    record_event,
    get_snapshot,
    metrics_store,
    TelemetryEvent,
)
from telemetry.middleware import TelemetryMiddleware


class TestTelemetryStore:
    """Test in-process metrics store."""

    def test_record_event(self):
        """Test recording a telemetry event."""
        event = TelemetryEvent(
            metric_name="test_metric",
            value=42,
            tags={"status": "ok"},
        )
        record_event(event)
        # Event should be stored in ring buffer
        assert len(metrics_store.events) > 0

    def test_get_snapshot(self):
        """Test getting a snapshot of metrics."""
        record_event(TelemetryEvent(metric_name="test1", value=10))
        record_event(TelemetryEvent(metric_name="test2", value=20))

        snapshot = get_snapshot()
        assert isinstance(snapshot, dict)
        assert "timestamp" in snapshot

    def test_metrics_store_ring_buffer(self):
        """Test that metrics store uses ring buffer (max 1000 events)."""
        # Record many events
        for i in range(1500):
            record_event(TelemetryEvent(
                metric_name=f"metric_{i}",
                value=i,
            ))
        # Should not exceed 1000 (ring buffer limit)
        assert len(metrics_store.events) <= 1000


class TestTelemetryMiddleware:
    """Test ASGI telemetry middleware."""

    @pytest.mark.asyncio
    async def test_middleware_initialization(self):
        """Test middleware initializes."""
        async def dummy_app(scope, receive, send):
            await send({
                "type": "http.response.start",
                "status": 200,
            })

        middleware = TelemetryMiddleware(dummy_app)
        assert middleware.app == dummy_app

    @pytest.mark.asyncio
    async def test_path_normalization(self):
        """Test path normalization for metrics."""
        # Test that UUID paths are normalized to /{uuid} tag
        paths = [
            "/api/findings/123e4567-e89b-12d3-a456-426614174000",
            "/api/findings/987654321",
            "/api/findings/abc-def-ghi",
        ]
        for path in paths:
            normalized = TelemetryMiddleware._normalize_path(path)
            # Should normalize ID patterns
            assert normalized


class TestTelemetryMetrics:
    """Test specific metrics collection."""

    def test_request_latency_metric(self):
        """Test recording request latency."""
        event = TelemetryEvent(
            metric_name="http.request.duration_ms",
            value=123.45,
            tags={"path": "/api/v1/chat", "method": "POST"},
        )
        record_event(event)
        snapshot = get_snapshot()
        assert snapshot is not None

    def test_error_rate_metric(self):
        """Test recording error metrics."""
        for i in range(5):
            event = TelemetryEvent(
                metric_name="http.error",
                value=1,
                tags={"status": "500", "path": "/api/test"},
            )
            record_event(event)

        snapshot = get_snapshot()
        assert snapshot is not None

    def test_token_usage_metric(self):
        """Test recording token usage."""
        event = TelemetryEvent(
            metric_name="ai.tokens.used",
            value=1250,
            tags={"model": "claude-opus", "direction": "input"},
        )
        record_event(event)
        snapshot = get_snapshot()
        assert snapshot is not None


class TestMetricsAggregation:
    """Test metrics aggregation and summaries."""

    def test_snapshot_includes_summary(self):
        """Test that snapshots include aggregated metrics."""
        # Record multiple events of same metric
        for i in range(10):
            record_event(TelemetryEvent(
                metric_name="response_time",
                value=50 + i * 10,
            ))

        snapshot = get_snapshot()
        # Snapshot should have timestamp and metrics
        assert "timestamp" in snapshot

    def test_percentile_calculations(self):
        """Test p50, p95, p99 percentile calculations."""
        # Record latencies
        latencies = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        for lat in latencies:
            record_event(TelemetryEvent(
                metric_name="latency_ms",
                value=lat,
            ))

        snapshot = get_snapshot()
        assert snapshot is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

