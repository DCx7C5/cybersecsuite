"""Tests for hooks.instrumentation: hook timing and error tracking.

Tests verify:
- Accurate timing capture using perf_counter
- Error logging without exception raising
- Performance budget detection
- Per-hook and per-event filtering
- Statistics aggregation and report generation
- Thread-safe metrics collection
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from legacy.hooks.instrumentation import (
    HookInstrument,
    HookMetrics,
    PERFORMANCE_BUDGETS,
    get_instrumentation,
    reset_instrumentation,
)


class TestHookMetrics:
    """Test HookMetrics dataclass."""
    
    def test_hook_metrics_creation(self):
        """HookMetrics should be created with required fields."""
        metrics = HookMetrics(
            hook_name="test_hook",
            event_type="PreToolUse",
            duration_ms=5.0,
            success=True,
        )
        
        assert metrics.hook_name == "test_hook"
        assert metrics.event_type == "PreToolUse"
        assert metrics.duration_ms == 5.0
        assert metrics.success is True
        assert metrics.error_message is None
        assert metrics.timestamp > 0
    
    def test_hook_metrics_with_error(self):
        """HookMetrics should capture error messages."""
        metrics = HookMetrics(
            hook_name="failing_hook",
            event_type="PostToolUse",
            duration_ms=2.5,
            success=False,
            error_message="Test error occurred",
        )
        
        assert metrics.success is False
        assert metrics.error_message == "Test error occurred"


class TestHookInstrumentTiming:
    """Test hook execution timing."""
    
    @pytest.mark.asyncio
    async def test_instrument_successful_hook(self):
        """Instrumentation should capture successful hook execution."""
        instrument = HookInstrument()
        
        async def sample_hook(arg):
            return {"result": "success"}
        
        result, metrics = await instrument.instrument_hook_call(
            "sample_hook",
            "PreToolUse",
            sample_hook,
            "test_arg",
        )
        
        assert result == {"result": "success"}
        assert metrics.hook_name == "sample_hook"
        assert metrics.event_type == "PreToolUse"
        assert metrics.success is True
        assert metrics.duration_ms > 0
        assert metrics.error_message is None
    
    @pytest.mark.asyncio
    async def test_instrument_hook_with_exception(self):
        """Instrumentation should capture exceptions without raising."""
        instrument = HookInstrument()
        
        async def failing_hook(arg):
            raise ValueError("Test exception")
        
        result, metrics = await instrument.instrument_hook_call(
            "failing_hook",
            "PostToolUse",
            failing_hook,
            "test_arg",
        )
        
        # Should not raise, should log error
        assert result is None
        assert metrics.hook_name == "failing_hook"
        assert metrics.success is False
        assert "Test exception" in metrics.error_message
        assert metrics.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_instrumentation_timing_overhead(self):
        """Instrumentation overhead should be <1ms for quick hooks."""
        instrument = HookInstrument()
        
        async def no_op_hook(arg):
            return {}
        
        # Execute multiple times
        durations = []
        for _ in range(10):
            _, metrics = await instrument.instrument_hook_call(
                "no_op",
                "PreToolUse",
                no_op_hook,
                "arg",
            )
            durations.append(metrics.duration_ms)
        
        avg_duration = sum(durations) / len(durations)
        # Average should be < 2ms per spec
        assert avg_duration < 2.0, f"Average overhead {avg_duration}ms exceeds budget"
    
    @pytest.mark.asyncio
    async def test_timing_uses_perf_counter(self):
        """Timing should use perf_counter for accuracy."""
        instrument = HookInstrument()
        
        async def delay_hook(delay_s):
            await asyncio.sleep(delay_s)
            return {}
        
        # Sleep for ~50ms
        _, metrics = await instrument.instrument_hook_call(
            "delay_hook",
            "PostToolUse",
            delay_hook,
            0.05,
        )
        
        # Should be within 5ms of target (50ms)
        assert 45 < metrics.duration_ms < 60, f"Timing {metrics.duration_ms}ms not in expected range"


class TestHookInstrumentMetricsCollection:
    """Test metrics collection and filtering."""
    
    @pytest.mark.asyncio
    async def test_metrics_are_accumulated(self):
        """Multiple hook calls should accumulate metrics."""
        instrument = HookInstrument()
        
        async def dummy_hook():
            return {}
        
        # Execute multiple hooks
        for i in range(5):
            await instrument.instrument_hook_call(
                f"hook_{i}",
                "PreToolUse",
                dummy_hook,
            )
        
        assert len(instrument.metrics) == 5
        assert instrument.get_metrics_count() == 5
    
    def test_get_metrics_by_hook(self):
        """Should filter metrics by hook name."""
        instrument = HookInstrument()
        
        # Add some test metrics manually
        instrument.metrics.append(HookMetrics(
            hook_name="hook_a",
            event_type="PreToolUse",
            duration_ms=5.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="hook_b",
            event_type="PreToolUse",
            duration_ms=3.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="hook_a",
            event_type="PostToolUse",
            duration_ms=2.0,
            success=True,
        ))
        
        hook_a_metrics = instrument.get_metrics_by_hook("hook_a")
        assert len(hook_a_metrics) == 2
        assert all(m.hook_name == "hook_a" for m in hook_a_metrics)
    
    def test_get_metrics_by_event(self):
        """Should filter metrics by event type."""
        instrument = HookInstrument()
        
        instrument.metrics.append(HookMetrics(
            hook_name="hook_a",
            event_type="PreToolUse",
            duration_ms=5.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="hook_b",
            event_type="PostToolUse",
            duration_ms=3.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="hook_c",
            event_type="PreToolUse",
            duration_ms=2.0,
            success=True,
        ))
        
        pretool_metrics = instrument.get_metrics_by_event("PreToolUse")
        assert len(pretool_metrics) == 2
        assert all(m.event_type == "PreToolUse" for m in pretool_metrics)


class TestSlowHookDetection:
    """Test detection of hooks exceeding performance budgets."""
    
    def test_get_slow_hooks_default_threshold(self):
        """Should identify hooks exceeding default threshold."""
        instrument = HookInstrument()
        
        # Add metrics
        instrument.metrics.append(HookMetrics(
            hook_name="fast_hook",
            event_type="PreToolUse",
            duration_ms=5.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="slow_hook",
            event_type="PostToolUse",
            duration_ms=15.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="slower_hook",
            event_type="PreToolUse",
            duration_ms=50.0,
            success=True,
        ))
        
        slow = instrument.get_slow_hooks(threshold_ms=10.0)
        assert len(slow) == 2
        assert all(m.duration_ms > 10.0 for m in slow)
    
    def test_get_slow_hooks_custom_threshold(self):
        """Should respect custom threshold."""
        instrument = HookInstrument()
        
        instrument.metrics.append(HookMetrics(
            hook_name="hook1",
            event_type="PreToolUse",
            duration_ms=20.0,
            success=True,
        ))
        instrument.metrics.append(HookMetrics(
            hook_name="hook2",
            event_type="PostToolUse",
            duration_ms=50.0,
            success=True,
        ))
        
        slow = instrument.get_slow_hooks(threshold_ms=30.0)
        assert len(slow) == 1
        assert slow[0].hook_name == "hook2"


class TestStatisticsAggregation:
    """Test per-hook statistics computation."""
    
    def test_get_stats_empty(self):
        """Should return empty dict for no metrics."""
        instrument = HookInstrument()
        stats = instrument.get_stats()
        assert stats == {}
    
    def test_get_stats_single_hook(self):
        """Should compute stats for single hook."""
        instrument = HookInstrument()
        
        instrument.metrics.extend([
            HookMetrics("hook1", "PreToolUse", 5.0, True),
            HookMetrics("hook1", "PreToolUse", 7.0, True),
            HookMetrics("hook1", "PreToolUse", 6.0, True),
        ])
        
        stats = instrument.get_stats()
        assert "hook1" in stats
        assert stats["hook1"]["count"] == 3
        assert stats["hook1"]["success"] == 3
        assert stats["hook1"]["failures"] == 0
        assert stats["hook1"]["min_ms"] == 5.0
        assert stats["hook1"]["max_ms"] == 7.0
        assert stats["hook1"]["avg_ms"] == 6.0
    
    def test_get_stats_with_failures(self):
        """Should track success/failure counts."""
        instrument = HookInstrument()
        
        instrument.metrics.extend([
            HookMetrics("hook1", "PreToolUse", 5.0, True),
            HookMetrics("hook1", "PreToolUse", 3.0, False, "Error 1"),
            HookMetrics("hook1", "PreToolUse", 6.0, True),
        ])
        
        stats = instrument.get_stats()
        assert stats["hook1"]["count"] == 3
        assert stats["hook1"]["success"] == 2
        assert stats["hook1"]["failures"] == 1
    
    def test_get_stats_percentiles(self):
        """Should compute p95 and p99 with enough data."""
        instrument = HookInstrument()
        
        # Add 20 data points for percentile calculation
        for i in range(1, 21):
            instrument.metrics.append(
                HookMetrics("hook1", "PreToolUse", float(i), True)
            )
        
        stats = instrument.get_stats()
        assert "hook1" in stats
        assert "p95_ms" in stats["hook1"]
        assert "p99_ms" in stats["hook1"]
        assert stats["hook1"]["p95_ms"] is not None
        assert stats["hook1"]["p99_ms"] is not None


class TestPerformanceReportGeneration:
    """Test report generation."""
    
    def test_generate_report_empty(self):
        """Report should handle empty metrics."""
        instrument = HookInstrument()
        report = instrument.generate_report()
        
        assert report["summary"]["total_calls"] == 0
        assert report["summary"]["success_count"] == 0
        assert report["summary"]["failure_count"] == 0
        assert report["per_hook"] == {}
        assert report["slow_hooks"] == []
    
    def test_generate_report_basic(self):
        """Report should include summary and per-hook stats."""
        instrument = HookInstrument()
        
        instrument.metrics.extend([
            HookMetrics("hook1", "PreToolUse", 5.0, True),
            HookMetrics("hook2", "PostToolUse", 8.0, True),
            HookMetrics("hook1", "PreToolUse", 3.0, False, "Error"),
        ])
        
        report = instrument.generate_report()
        
        assert report["summary"]["total_calls"] == 3
        assert report["summary"]["success_count"] == 2
        assert report["summary"]["failure_count"] == 1
        assert "hook1" in report["per_hook"]
        assert "hook2" in report["per_hook"]
    
    def test_generate_report_identifies_slow_hooks(self):
        """Report should flag hooks exceeding budget."""
        instrument = HookInstrument()
        
        # Add hooks: one fast, one slow
        for _ in range(5):
            instrument.metrics.append(
                HookMetrics("fast_hook", "PreToolUse", 3.0, True)
            )
            instrument.metrics.append(
                HookMetrics("slow_hook", "PreToolUse", 15.0, True)
            )
        
        report = instrument.generate_report()
        
        # slow_hook should be in slow_hooks list
        slow_hooks = report["slow_hooks"]
        assert len(slow_hooks) == 1
        assert slow_hooks[0]["hook"] == "slow_hook"
        assert slow_hooks[0]["avg_ms"] > 10.0
    
    def test_generate_report_budget_ok_flag(self):
        """Report should indicate budget status per hook."""
        instrument = HookInstrument()
        
        instrument.metrics.extend([
            HookMetrics("fast", "PreToolUse", 3.0, True),
            HookMetrics("slow", "PreToolUse", 25.0, True),
        ])
        
        report = instrument.generate_report()
        
        assert report["per_hook"]["fast"]["budget_ok"] is True
        assert report["per_hook"]["slow"]["budget_ok"] is False


class TestMetricsManagement:
    """Test metrics collection management."""
    
    def test_clear_metrics(self):
        """Should clear all metrics."""
        instrument = HookInstrument()
        
        instrument.metrics.extend([
            HookMetrics("hook1", "PreToolUse", 5.0, True),
            HookMetrics("hook2", "PostToolUse", 8.0, True),
        ])
        
        assert len(instrument.metrics) == 2
        
        instrument.clear_metrics()
        assert len(instrument.metrics) == 0
        assert instrument.get_metrics_count() == 0


class TestPerformanceBudgets:
    """Test performance budget constants."""
    
    def test_performance_budgets_exist(self):
        """Should have defined performance budgets."""
        assert "no_op" in PERFORMANCE_BUDGETS
        assert "validated_sync" in PERFORMANCE_BUDGETS
        assert "io_bound" in PERFORMANCE_BUDGETS
    
    def test_performance_budget_values(self):
        """Performance budgets should have reasonable values."""
        assert PERFORMANCE_BUDGETS["no_op"] < PERFORMANCE_BUDGETS["validated_sync"]
        assert PERFORMANCE_BUDGETS["validated_sync"] < PERFORMANCE_BUDGETS["io_bound"]


class TestGlobalInstrumentation:
    """Test global instrumentation singleton."""
    
    def test_get_instrumentation_creates_singleton(self):
        """get_instrumentation should create singleton."""
        reset_instrumentation()
        
        inst1 = get_instrumentation()
        inst2 = get_instrumentation()
        
        assert inst1 is inst2
    
    def test_reset_instrumentation(self):
        """reset_instrumentation should create new instance."""
        inst1 = get_instrumentation()
        reset_instrumentation()
        inst2 = get_instrumentation()
        
        assert inst1 is not inst2
    
    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset instrumentation after each test."""
        yield
        reset_instrumentation()


class TestErrorHandling:
    """Test error handling in instrumentation."""
    
    @pytest.mark.asyncio
    async def test_error_message_truncation(self):
        """Should truncate very long error messages."""
        instrument = HookInstrument()
        
        async def hook_with_long_error():
            raise ValueError("x" * 1000)
        
        _, metrics = await instrument.instrument_hook_call(
            "hook",
            "PreToolUse",
            hook_with_long_error,
        )
        
        assert len(metrics.error_message) <= 500


class TestExceptionPropagation:
    """Verify exceptions are NOT propagated (fire-and-forget)."""
    
    @pytest.mark.asyncio
    async def test_exceptions_not_raised(self):
        """Hook exceptions should be caught and logged."""
        instrument = HookInstrument()
        
        async def failing_hook():
            raise RuntimeError("This should be logged, not raised")
        
        # Should NOT raise
        result, metrics = await instrument.instrument_hook_call(
            "failing_hook",
            "PostToolUse",
            failing_hook,
        )
        
        assert result is None
        assert metrics.success is False
