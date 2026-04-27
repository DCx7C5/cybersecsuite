"""Basic streaming hook implementations.

This module provides simple, production-ready streaming hooks for:
- PreStreaming: Initialize streaming context
- StreamingToken: Aggregate/batch tokens
- PostStreaming: Log streaming metrics

These hooks integrate with HookInstrument for timing and can be extended
for real-world use cases (e.g., real-time monitoring, filtering).
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


# ── Token Aggregator State ─────────────────────────────────────────────────
# In production, this would be stored in a database or cache.
# For testing/demo, we use a simple module-level dict.

_token_aggregators: dict[str, dict[str, Any]] = {}


def get_token_aggregator(correlation_id: str) -> dict[str, Any]:
    """Get or create token aggregator for correlation ID.
    
    Args:
        correlation_id: Request correlation ID
    
    Returns:
        Dict with 'tokens': [] and 'start_time': float
    """
    if correlation_id not in _token_aggregators:
        _token_aggregators[correlation_id] = {
            "tokens": [],
            "start_time": None,
            "token_count": 0,
        }
    return _token_aggregators[correlation_id]


def clear_token_aggregator(correlation_id: str) -> None:
    """Clear aggregator for correlation ID.
    
    Args:
        correlation_id: Request correlation ID
    """
    if correlation_id in _token_aggregators:
        del _token_aggregators[correlation_id]


# ── Streaming Hooks ────────────────────────────────────────────────────────

async def on_streaming_start(event: dict[str, Any]) -> dict[str, Any]:
    """Log streaming start and initialize token aggregator.
    
    Args:
        event: PreStreamingEvent dict with:
            - correlation_id: Request correlation ID
            - session_id: CyberSecSuite session ID
            - model: Model identifier
            - token_count_estimate: Estimated tokens (optional)
    
    Returns:
        HookOutput dict (empty or with metadata)
    """
    correlation_id = event.get("correlation_id", "unknown")
    session_id = event.get("session_id", "unknown")
    model = event.get("model", "unknown")
    estimate = event.get("token_count_estimate")
    
    # Initialize token aggregator
    agg = get_token_aggregator(correlation_id)
    agg["start_time"] = None
    agg["tokens"] = []
    agg["token_count"] = 0
    
    logger.info(
        f"Streaming started: model={model}, session={session_id}, "
        f"correlation={correlation_id}, estimated_tokens={estimate}",
        extra={
            "event": "StreamingStarted",
            "model": model,
            "correlation_id": correlation_id,
            "session_id": session_id,
        }
    )
    
    return {
        "hookSpecificOutput": {
            "aggregator_initialized": True,
            "correlation_id": correlation_id,
        }
    }


async def on_streaming_token(event: dict[str, Any]) -> dict[str, Any]:
    """Aggregate tokens and batch them for efficient processing.
    
    This hook is called for each token. Batching is handled by registry.
    
    Args:
        event: StreamingTokenEvent dict with:
            - token: Token content (str)
            - delta: Incremental content (str)
            - cumulative_length: Total characters so far (int)
            - token_count: Tokens processed (int)
            - timestamp: When token arrived (float)
            - _batched_tokens: List of accumulated tokens (from registry batching)
    
    Returns:
        HookOutput dict with aggregation metadata
    """
    correlation_id = event.get("correlation_id", "unknown")
    batched = event.get("_batched_tokens", [])
    
    if not batched:
        return {}
    
    agg = get_token_aggregator(correlation_id)
    
    # Accumulate tokens from batch
    for token_data in batched:
        agg["tokens"].append(token_data["token"])
        agg["token_count"] += 1
    
    # Log aggregation (at batch boundary)
    batch_len = len(batched)
    total_so_far = agg["token_count"]
    
    logger.debug(
        f"Streaming token batch: batch_size={batch_len}, total_tokens={total_so_far}, "
        f"correlation={correlation_id}",
        extra={
            "event": "StreamingTokenBatch",
            "batch_size": batch_len,
            "total_tokens": total_so_far,
            "correlation_id": correlation_id,
        }
    )
    
    return {
        "hookSpecificOutput": {
            "batch_processed": batch_len,
            "total_tokens": total_so_far,
        }
    }


async def on_streaming_complete(event: dict[str, Any]) -> dict[str, Any]:
    """Log streaming completion and metrics.
    
    Args:
        event: PostStreamingEvent dict with:
            - total_tokens: Total tokens in stream (int)
            - duration_ms: Total streaming duration (float)
            - status: Completion status (str)
            - cumulative_length: Total characters (int)
            - correlation_id: Request correlation ID (optional)
    
    Returns:
        HookOutput dict with streaming summary
    """
    correlation_id = event.get("correlation_id", "unknown")
    total_tokens = event.get("total_tokens", 0)
    duration_ms = event.get("duration_ms", 0.0)
    status = event.get("status", "unknown")
    cumulative_length = event.get("cumulative_length", 0)
    
    # Get aggregator stats if available
    agg = get_token_aggregator(correlation_id)
    aggregated_count = agg.get("token_count", 0)
    
    # Compute throughput
    throughput_tps = (total_tokens / (duration_ms / 1000.0)) if duration_ms > 0 else 0.0
    
    logger.info(
        f"Streaming completed: status={status}, tokens={total_tokens}, "
        f"duration_ms={duration_ms:.0f}, throughput={throughput_tps:.1f} t/s, "
        f"correlation={correlation_id}",
        extra={
            "event": "StreamingCompleted",
            "status": status,
            "total_tokens": total_tokens,
            "duration_ms": round(duration_ms),
            "throughput_tps": round(throughput_tps, 1),
            "cumulative_length": cumulative_length,
            "correlation_id": correlation_id,
            "aggregated_tokens": aggregated_count,
        }
    )
    
    # Clean up aggregator
    clear_token_aggregator(correlation_id)
    
    return {
        "hookSpecificOutput": {
            "streaming_summary": {
                "status": status,
                "total_tokens": total_tokens,
                "duration_ms": round(duration_ms, 1),
                "throughput_tps": round(throughput_tps, 1),
                "cumulative_length": cumulative_length,
            },
            "aggregated_tokens": aggregated_count,
        }
    }
