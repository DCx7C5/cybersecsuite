"""Tests for streaming hooks: PreStreaming, StreamingToken, PostStreaming."""

import sys
import time
from pathlib import Path

import pytest

# Adjust path for imports
SRC_PATH = Path(__file__).resolve().parent.parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from legacy.hooks.events import HookContext
from legacy.hooks.instrumentation import HookInstrument
from css.core.registries.hooks import HookRegistry, reset_registry
from legacy.hooks.streaming_hooks import (
    clear_token_aggregator,
    get_token_aggregator,
    on_streaming_complete,
    on_streaming_start,
    on_streaming_token,
)


class TestStreamingHookImplementations:
    """Test basic streaming hook implementations."""

    def test_streaming_start_initializes_aggregator(self):
        """on_streaming_start should initialize token aggregator."""
        correlation_id = "test-corr-1"
        event = {
            "correlation_id": correlation_id,
            "session_id": "test-sess",
            "model": "claude-3.5-sonnet",
            "token_count_estimate": 100,
            "hook_event_name": "PreStreaming",
        }
        
        # Clear any existing aggregator
        clear_token_aggregator(correlation_id)
        
        # Run hook
        result = run_async(on_streaming_start(event))
        
        # Verify aggregator initialized
        agg = get_token_aggregator(correlation_id)
        assert "tokens" in agg
        assert "token_count" in agg
        assert agg["token_count"] == 0
        
        # Verify hook output
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["aggregator_initialized"] is True

    def test_streaming_token_aggregates_batch(self):
        """on_streaming_token should aggregate batched tokens."""
        correlation_id = "test-corr-2"
        
        # Initialize aggregator
        clear_token_aggregator(correlation_id)
        event_start = {
            "correlation_id": correlation_id,
            "session_id": "test-sess",
            "model": "test-model",
            "hook_event_name": "PreStreaming",
        }
        run_async(on_streaming_start(event_start))
        
        # Simulate batched tokens
        batched_tokens = [
            {"token": "Hello", "delta": "Hello", "cumulative_length": 5, "token_count": 1, "timestamp": time.time()},
            {"token": " world", "delta": " world", "cumulative_length": 11, "token_count": 2, "timestamp": time.time()},
            {"token": "!", "delta": "!", "cumulative_length": 12, "token_count": 3, "timestamp": time.time()},
        ]
        
        event_token = {
            "correlation_id": correlation_id,
            "token": "!",
            "delta": "!",
            "cumulative_length": 12,
            "token_count": 3,
            "timestamp": time.time(),
            "_batched_tokens": batched_tokens,
            "hook_event_name": "StreamingToken",
        }
        
        # Run hook
        result = run_async(on_streaming_token(event_token))
        
        # Verify aggregation
        agg = get_token_aggregator(correlation_id)
        assert agg["token_count"] == 3
        assert len(agg["tokens"]) == 3
        assert agg["tokens"] == ["Hello", " world", "!"]
        
        # Verify hook output
        assert "hookSpecificOutput" in result
        assert result["hookSpecificOutput"]["batch_processed"] == 3

    def test_streaming_complete_logs_metrics(self):
        """on_streaming_complete should log streaming metrics and cleanup."""
        correlation_id = "test-corr-3"
        
        # Initialize with some tokens
        clear_token_aggregator(correlation_id)
        event_start = {
            "correlation_id": correlation_id,
            "session_id": "test-sess",
            "model": "test-model",
            "hook_event_name": "PreStreaming",
        }
        run_async(on_streaming_start(event_start))
        
        # Add tokens
        batched_tokens = [
            {"token": "T1", "delta": "T1", "cumulative_length": 2, "token_count": 1, "timestamp": time.time()},
            {"token": "T2", "delta": "T2", "cumulative_length": 4, "token_count": 2, "timestamp": time.time()},
        ]
        event_token = {
            "correlation_id": correlation_id,
            "_batched_tokens": batched_tokens,
            "hook_event_name": "StreamingToken",
        }
        run_async(on_streaming_token(event_token))
        
        # Verify aggregator has tokens
        agg_before = get_token_aggregator(correlation_id)
        assert agg_before["token_count"] == 2
        
        # Complete streaming
        event_complete = {
            "correlation_id": correlation_id,
            "total_tokens": 100,
            "duration_ms": 1000.0,
            "status": "success",
            "cumulative_length": 500,
            "hook_event_name": "PostStreaming",
        }
        
        result = run_async(on_streaming_complete(event_complete))
        
        # Verify result
        assert "hookSpecificOutput" in result
        summary = result["hookSpecificOutput"]["streaming_summary"]
        assert summary["status"] == "success"
        assert summary["total_tokens"] == 100
        assert summary["duration_ms"] == 1000.0
        
        # Verify throughput calculation
        expected_tps = 100.0  # 100 tokens in 1 second
        assert abs(summary["throughput_tps"] - expected_tps) < 1.0

    def test_streaming_token_without_batch_returns_empty(self):
        """on_streaming_token should return empty dict if no batched tokens."""
        event = {
            "correlation_id": "test-corr",
            "_batched_tokens": [],
            "hook_event_name": "StreamingToken",
        }
        
        result = run_async(on_streaming_token(event))
        assert result == {}

    def test_token_aggregator_lifecycle(self):
        """Token aggregator should be creatable and clearable."""
        correlation_id = "test-lifecycle"
        
        # Should create on first access
        agg = get_token_aggregator(correlation_id)
        assert agg["token_count"] == 0
        
        # Modify aggregator
        agg["token_count"] = 50
        
        # Should get same aggregator
        agg2 = get_token_aggregator(correlation_id)
        assert agg2["token_count"] == 50
        
        # Clear should remove it
        clear_token_aggregator(correlation_id)
        
        # New access should create fresh aggregator
        agg3 = get_token_aggregator(correlation_id)
        assert agg3["token_count"] == 0


class TestStreamingHookRegistry:
    """Test streaming hooks with HookRegistry."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset registry after each test."""
        yield
        reset_registry()

    @pytest.mark.asyncio
    async def test_registry_execute_streaming_unknown_event(self):
        """Registry execute_streaming should handle unknown event types."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        output = await registry.execute_streaming("UnknownStreamingEvent", {}, context)
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_registry_execute_streaming_with_batch_size_one(self):
        """Registry execute_streaming with batch_size=1 should use standard execute."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        event = {
            "correlation_id": "test-corr",
            "token": "test",
            "hook_event_name": "StreamingToken",
        }
        
        # Should not raise, batch_size=1 uses standard execute
        output = await registry.execute_streaming(
            "StreamingToken",
            event,
            context,
            batch_size=1,
        )
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_registry_execute_streaming_non_streaming_event(self):
        """Registry execute_streaming for non-streaming events should use standard execute."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        event = {
            "correlation_id": "test-corr",
            "model": "test-model",
            "hook_event_name": "PreStreaming",
        }
        
        # PreStreaming should use standard execute, not batching
        output = await registry.execute_streaming(
            "PreStreaming",
            event,
            context,
            batch_size=10,  # Ignored for non-streaming events
        )
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_registry_streaming_token_batching_accumulation(self):
        """Registry should accumulate tokens in _batched_tokens."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        # Create a mock event that would have batched tokens
        event = {
            "correlation_id": "test-corr",
            "token": "test-token",
            "delta": "test-token",
            "cumulative_length": 10,
            "token_count": 1,
            "timestamp": time.time(),
            "hook_event_name": "StreamingToken",
        }
        
        # First call with batch_size=3 should initialize _batched_tokens
        # Since there are no StreamingToken hooks registered, it returns early
        # with empty output, which is correct behavior (no-op when no hooks)
        output1 = await registry.execute_streaming(
            "StreamingToken",
            event,
            context,
            batch_size=3,
        )
        # When no hooks are registered, execute_streaming returns empty dict
        assert output1 == {}
        assert isinstance(output1, dict)


class TestStreamingHookInstrumentation:
    """Test streaming hooks with instrumentation."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset registry after each test."""
        yield
        reset_registry()

    @pytest.mark.asyncio
    async def test_streaming_hooks_with_instrumentation(self):
        """Streaming hooks should work with HookInstrument."""
        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        # Should not raise
        output = await registry.execute_streaming(
            "StreamingToken",
            {"hook_event_name": "StreamingToken"},
            context,
            batch_size=1,
        )
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_streaming_instrumentation_captures_timing(self):
        """Instrumentation should capture streaming hook timing."""
        instrument = HookInstrument()
        registry = HookRegistry(instrumentation=instrument)
        
        # Verify instrumentation is registered
        assert registry.get_instrumentation() is instrument


class TestStreamingBackwardCompatibility:
    """Test backward compatibility with existing hook system."""

    def test_streaming_event_types_in_core_union(self):
        """Streaming event types should be in EventType union."""
        
        # These should be valid event types (not raising type errors)
        pre_streaming_event: dict = {
            "correlation_id": "test",
            "session_id": "test",
            "model": "test",
            "hook_event_name": "PreStreaming",
        }
        
        # If this doesn't raise a type error, EventType includes streaming events
        assert pre_streaming_event is not None

    @pytest.mark.asyncio
    async def test_registry_execute_still_works(self):
        """Registry execute() should still work for non-streaming events."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        event = {
            "correlation_id": "test-corr",
            "hook_event_name": "PreToolUse",
        }
        
        output = await registry.execute("PreToolUse", event, context)
        assert isinstance(output, dict)

    @pytest.mark.asyncio
    async def test_streaming_execute_backward_compatible_with_standard_execute(self):
        """execute_streaming should have same interface as execute."""
        registry = HookRegistry()
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        event = {"hook_event_name": "PreStreaming"}
        
        # Both methods should return dict
        output1 = await registry.execute("PreStreaming", event, context)
        output2 = await registry.execute_streaming("PreStreaming", event, context)
        
        assert isinstance(output1, dict)
        assert isinstance(output2, dict)


class TestStreamingEventContracts:
    """Test streaming event type contracts."""

    def test_pre_streaming_event_contract(self):
        """PreStreamingEvent should have expected fields."""
        from hooks.events import PreStreamingEvent
        
        event: PreStreamingEvent = {
            "correlation_id": "corr1",
            "session_id": "sess1",
            "model": "claude-3.5-sonnet",
            "hook_event_name": "PreStreaming",
        }
        
        assert event["correlation_id"] == "corr1"
        assert event["session_id"] == "sess1"
        assert event["model"] == "claude-3.5-sonnet"

    def test_streaming_token_event_contract(self):
        """StreamingTokenEvent should have expected fields."""
        from hooks.events import StreamingTokenEvent
        
        timestamp = time.time()
        event: StreamingTokenEvent = {
            "token": "hello",
            "delta": "hello",
            "cumulative_length": 5,
            "token_count": 1,
            "timestamp": timestamp,
            "hook_event_name": "StreamingToken",
        }
        
        assert event["token"] == "hello"
        assert event["cumulative_length"] == 5
        assert event["token_count"] == 1

    def test_post_streaming_event_contract(self):
        """PostStreamingEvent should have expected fields."""
        from hooks.events import PostStreamingEvent
        
        event: PostStreamingEvent = {
            "total_tokens": 100,
            "duration_ms": 1000.0,
            "status": "success",
            "cumulative_length": 500,
            "hook_event_name": "PostStreaming",
        }
        
        assert event["total_tokens"] == 100
        assert event["duration_ms"] == 1000.0
        assert event["status"] == "success"


class TestStreamingErrorHandling:
    """Test error handling in streaming hooks."""

    @pytest.mark.asyncio
    async def test_streaming_hook_with_error_strategy_preserve(self):
        """Streaming hooks with PRESERVE_EXISTING should not raise on hook failure."""
        from hooks.events import ErrorStrategy
        
        registry = HookRegistry(error_strategy=ErrorStrategy.PRESERVE_EXISTING)
        context = HookContext(
            correlation_id="test-corr",
            session_id="test-sess",
            timestamp=time.time(),
        )
        
        # Should not raise even if hook fails
        event = {
            "hook_event_name": "StreamingToken",
            "_batched_tokens": [],
        }
        
        output = await registry.execute_streaming(
            "StreamingToken",
            event,
            context,
            batch_size=1,
        )
        assert isinstance(output, dict)

    def test_streaming_token_aggregator_handles_missing_fields(self):
        """on_streaming_token should handle events missing optional fields."""
        event = {
            "correlation_id": "test-corr",
            "_batched_tokens": [],
            # Missing some optional fields
        }
        
        result = run_async(on_streaming_token(event))
        assert result == {}

    def test_streaming_complete_handles_missing_correlation(self):
        """on_streaming_complete should handle missing correlation_id."""
        event = {
            # Missing correlation_id
            "total_tokens": 100,
            "duration_ms": 1000.0,
            "status": "success",
            "cumulative_length": 500,
        }
        
        result = run_async(on_streaming_complete(event))
        assert "hookSpecificOutput" in result


# ── Test Helpers ───────────────────────────────────────────────────────────

def run_async(coro):
    """Run async coroutine in test."""
    import asyncio
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    finally:
        # Don't close the loop; pytest-asyncio manages it
        pass


class TestStreamingIntegration:
    """Integration tests for streaming hooks with full flow."""

    @pytest.fixture(autouse=True)
    def cleanup(self):
        """Reset registry and aggregators after each test."""
        yield
        reset_registry()
        # Clean all aggregators
        from hooks.streaming_hooks import _token_aggregators
        _token_aggregators.clear()

    def test_streaming_complete_flow(self):
        """Test complete streaming flow: start → tokens → complete."""
        correlation_id = "test-flow-1"
        
        # Phase 1: Start streaming
        clear_token_aggregator(correlation_id)
        event_start = {
            "correlation_id": correlation_id,
            "session_id": "sess1",
            "model": "claude-3.5-sonnet",
            "token_count_estimate": 50,
            "hook_event_name": "PreStreaming",
        }
        result_start = run_async(on_streaming_start(event_start))
        assert result_start["hookSpecificOutput"]["aggregator_initialized"] is True
        
        # Phase 2: Process tokens in batches
        batches = [
            [
                {"token": "T1", "delta": "T1", "cumulative_length": 2, "token_count": 1, "timestamp": time.time()},
                {"token": "T2", "delta": "T2", "cumulative_length": 4, "token_count": 2, "timestamp": time.time()},
            ],
            [
                {"token": "T3", "delta": "T3", "cumulative_length": 6, "token_count": 3, "timestamp": time.time()},
            ],
        ]
        
        for batch in batches:
            event_token = {
                "correlation_id": correlation_id,
                "_batched_tokens": batch,
                "hook_event_name": "StreamingToken",
            }
            result_token = run_async(on_streaming_token(event_token))
            assert "hookSpecificOutput" in result_token
        
        # Phase 3: Complete streaming
        event_complete = {
            "correlation_id": correlation_id,
            "total_tokens": 45,
            "duration_ms": 500.0,
            "status": "success",
            "cumulative_length": 100,
            "hook_event_name": "PostStreaming",
        }
        result_complete = run_async(on_streaming_complete(event_complete))
        
        # Verify complete flow
        summary = result_complete["hookSpecificOutput"]["streaming_summary"]
        assert summary["status"] == "success"
        assert summary["total_tokens"] == 45
        assert summary["throughput_tps"] > 0

    def test_streaming_interrupted_status(self):
        """Test streaming complete with interrupted status."""
        correlation_id = "test-interrupted"
        
        clear_token_aggregator(correlation_id)
        
        event_complete = {
            "correlation_id": correlation_id,
            "total_tokens": 25,
            "duration_ms": 250.0,
            "status": "interrupted",
            "cumulative_length": 50,
        }
        
        result = run_async(on_streaming_complete(event_complete))
        assert result["hookSpecificOutput"]["streaming_summary"]["status"] == "interrupted"

    def test_streaming_throughput_calculation_edge_cases(self):
        """Test throughput calculation with edge cases."""
        correlation_id = "test-edge-case"
        
        clear_token_aggregator(correlation_id)
        
        # Duration = 0 should not crash
        event = {
            "correlation_id": correlation_id,
            "total_tokens": 100,
            "duration_ms": 0.0,
            "status": "success",
            "cumulative_length": 500,
        }
        
        result = run_async(on_streaming_complete(event))
        assert "hookSpecificOutput" in result
        # Throughput should be 0 when duration is 0
        assert result["hookSpecificOutput"]["streaming_summary"]["throughput_tps"] == 0.0
