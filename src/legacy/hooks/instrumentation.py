"""Hook execution timing and error tracking instrumentation.

This module provides lightweight performance instrumentation for hook execution
WITHOUT adding significant latency. It captures:
- Execution timing (using time.perf_counter for accuracy)
- Success/failure status
- Error messages
- Per-hook aggregated statistics

Key Design:
    - Zero behavioral changes: results unchanged, errors still fire-and-forget
    - Minimal overhead: <1ms per hook call (target is <2ms for no-op hooks)
    - Optional: can be disabled or enabled per-registry
    - Metrics collection: append-only for thread safety
    - Aggregation: lazy computation (stats computed on-demand)

Performance Budgets:
    - no_op: <2ms (hooks that do nothing)
    - validated_sync: <10ms (simple validation hooks)
    - io_bound: <50ms (file I/O, network calls)
"""

import logging
import time
from dataclasses import dataclass, field
from statistics import mean, quantiles
from typing import Any, Callable, Optional, Tuple

logger = logging.getLogger(__name__)


# ── Performance Budgets ────────────────────────────────────────────────────

PERFORMANCE_BUDGETS = {
    "no_op": 2.0,              # <2ms for hooks that do nothing
    "validated_sync": 10.0,    # <10ms for validated sync hooks
    "io_bound": 50.0,          # <50ms for file I/O hooks
}


# ── Hook Metrics ───────────────────────────────────────────────────────────

@dataclass
class HookMetrics:
    """Metrics captured for a single hook execution.
    
    Attributes:
        hook_name: Name of the hook that was executed
        event_type: Event type (e.g., "PreToolUse", "PostToolUse")
        duration_ms: Wall-clock execution time in milliseconds
        success: True if hook executed without raising
        error_message: Exception message if success=False, else None
        timestamp: Unix timestamp when execution completed
    """
    hook_name: str
    event_type: str
    duration_ms: float
    success: bool
    error_message: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


# ── Hook Instrumentation ───────────────────────────────────────────────────

class HookInstrument:
    """Lightweight hook execution timing and error tracking.
    
    Features:
        - Captures execution timing using perf_counter (high precision)
        - Records success/failure status
        - Logs errors WITHOUT raising (fire-and-forget semantics preserved)
        - Computes per-hook statistics on demand
        - Detects hooks exceeding performance budgets
        - Generates performance reports
    
    Usage:
        instrument = HookInstrument()
        result, metrics = await instrument.instrument_hook_call(
            "my_hook", "PreToolUse", hook_func, arg1, arg2
        )
    """
    
    def __init__(self):
        """Initialize empty metrics collection."""
        self.metrics: list[HookMetrics] = []
        self._lock = None  # For future thread safety if needed
    
    async def instrument_hook_call(
        self,
        hook_name: str,
        event_type: str,
        hook_func: Callable,
        *args,
        **kwargs,
    ) -> Tuple[Any, HookMetrics]:
        """Execute hook with timing capture.
        
        Args:
            hook_name: Name of the hook (for logging/metrics)
            event_type: Event type being processed
            hook_func: Coroutine function to call
            *args: Positional arguments to hook
            **kwargs: Keyword arguments to hook
        
        Returns:
            (result, metrics) tuple where:
            - result: Return value from hook (or None if error)
            - metrics: HookMetrics instance with timing/status
        
        Behavior:
            - Timing measured using perf_counter for accuracy
            - Exceptions caught and logged, not raised
            - Success=True only if NO exception occurred
            - Error message captured for debugging
        """
        start_time = time.perf_counter()
        result = None
        error_msg = None
        success = True
        
        try:
            result = await hook_func(*args, **kwargs)
        except Exception as exc:
            success = False
            error_msg = str(exc)[:500]  # Truncate very long error messages
            logger.exception(
                f"Hook {hook_name} (event {event_type}) raised exception: {exc}",
                extra={"hook": hook_name, "event": event_type},
            )
        finally:
            elapsed = time.perf_counter() - start_time
            duration_ms = elapsed * 1000.0
        
        # Create metrics record
        metrics = HookMetrics(
            hook_name=hook_name,
            event_type=event_type,
            duration_ms=duration_ms,
            success=success,
            error_message=error_msg,
            timestamp=time.time(),
        )
        
        # Append to metrics (thread-safe append in CPython)
        self.metrics.append(metrics)
        
        return result, metrics
    
    def get_slow_hooks(
        self,
        threshold_ms: float = 10.0,
    ) -> list[HookMetrics]:
        """Get metrics for hooks exceeding performance threshold.
        
        Args:
            threshold_ms: Duration threshold in milliseconds
        
        Returns:
            List of HookMetrics for hooks exceeding threshold
        """
        return [m for m in self.metrics if m.duration_ms > threshold_ms]
    
    def get_stats(self) -> dict[str, Any]:
        """Compute aggregated statistics per hook.
        
        Returns:
            Dictionary mapping hook names to stats dicts:
            {
                "hook_name": {
                    "count": int,
                    "success": int,
                    "failures": int,
                    "min_ms": float,
                    "max_ms": float,
                    "avg_ms": float,
                    "p95_ms": float,
                    "p99_ms": float,
                }
            }
        
        Note:
            - p95/p99 computed only if count >= 3
            - Returns {} if no metrics collected
        """
        if not self.metrics:
            return {}
        
        # Group by hook name
        by_hook: dict[str, list[HookMetrics]] = {}
        for m in self.metrics:
            if m.hook_name not in by_hook:
                by_hook[m.hook_name] = []
            by_hook[m.hook_name].append(m)
        
        stats = {}
        for hook_name, hook_metrics in by_hook.items():
            durations = [m.duration_ms for m in hook_metrics]
            success_count = sum(1 for m in hook_metrics if m.success)
            failure_count = len(hook_metrics) - success_count
            
            # Compute quantiles if we have enough data
            p95_ms = None
            p99_ms = None
            if len(durations) >= 3:
                try:
                    quantiles_result = quantiles(durations, n=100)
                    p95_ms = quantiles_result[94]  # 95th percentile (index 94 of 0-99)
                    p99_ms = quantiles_result[98]  # 99th percentile (index 98 of 0-99)
                except Exception as exc:
                    logger.warning(f"Failed to compute quantiles for {hook_name}: {exc}")
            
            stats[hook_name] = {
                "count": len(hook_metrics),
                "success": success_count,
                "failures": failure_count,
                "min_ms": min(durations),
                "max_ms": max(durations),
                "avg_ms": round(mean(durations), 3),
                "p95_ms": round(p95_ms, 3) if p95_ms is not None else None,
                "p99_ms": round(p99_ms, 3) if p99_ms is not None else None,
            }
        
        return stats
    
    def generate_report(self) -> dict[str, Any]:
        """Generate performance report suitable for export/logging.
        
        Returns:
            Dictionary with structure:
            {
                "summary": {
                    "total_calls": int,
                    "success_count": int,
                    "failure_count": int,
                    "time_period": "..."
                },
                "per_hook": {
                    "hook_name": {
                        "count": int,
                        "avg_ms": float,
                        "min_ms": float,
                        "max_ms": float,
                        "p95_ms": float,
                        "budget_ok": bool,
                    }
                },
                "slow_hooks": [
                    {
                        "hook": str,
                        "avg_ms": float,
                        "budget_ms": float,
                        "violations": int,
                    }
                ]
            }
        """
        if not self.metrics:
            return {
                "summary": {
                    "total_calls": 0,
                    "success_count": 0,
                    "failure_count": 0,
                },
                "per_hook": {},
                "slow_hooks": [],
            }
        
        # Overall summary
        success_count = sum(1 for m in self.metrics if m.success)
        failure_count = len(self.metrics) - success_count
        
        # Per-hook stats
        stats = self.get_stats()
        per_hook = {}
        
        for hook_name, hook_stats in stats.items():
            # Determine performance budget
            budget_ms = PERFORMANCE_BUDGETS.get("validated_sync", 10.0)
            avg_ms = hook_stats["avg_ms"]
            budget_ok = avg_ms <= budget_ms
            
            per_hook[hook_name] = {
                "count": hook_stats["count"],
                "avg_ms": avg_ms,
                "min_ms": hook_stats["min_ms"],
                "max_ms": hook_stats["max_ms"],
                "p95_ms": hook_stats["p95_ms"],
                "budget_ms": budget_ms,
                "budget_ok": budget_ok,
            }
        
        # Identify slow hooks (exceeding budget on average)
        slow_hooks = []
        for hook_name, hook_stats in stats.items():
            budget_ms = PERFORMANCE_BUDGETS.get("validated_sync", 10.0)
            avg_ms = hook_stats["avg_ms"]
            
            if avg_ms > budget_ms:
                violations = sum(
                    1 for m in self.metrics
                    if m.hook_name == hook_name and m.duration_ms > budget_ms
                )
                slow_hooks.append({
                    "hook": hook_name,
                    "avg_ms": avg_ms,
                    "budget_ms": budget_ms,
                    "violations": violations,
                })
        
        # Sort slow hooks by severity
        slow_hooks.sort(key=lambda x: x["avg_ms"], reverse=True)
        
        return {
            "summary": {
                "total_calls": len(self.metrics),
                "success_count": success_count,
                "failure_count": failure_count,
            },
            "per_hook": per_hook,
            "slow_hooks": slow_hooks,
        }
    
    def clear_metrics(self) -> None:
        """Clear all collected metrics (for test isolation).
        
        Warning:
            This discards all historical metrics. Use with care in production.
        """
        self.metrics.clear()
    
    def get_metrics_count(self) -> int:
        """Get total number of metrics collected."""
        return len(self.metrics)
    
    def get_metrics_by_hook(self, hook_name: str) -> list[HookMetrics]:
        """Get all metrics for a specific hook.
        
        Args:
            hook_name: Name of hook to filter by
        
        Returns:
            List of HookMetrics for the hook
        """
        return [m for m in self.metrics if m.hook_name == hook_name]
    
    def get_metrics_by_event(self, event_type: str) -> list[HookMetrics]:
        """Get all metrics for a specific event type.
        
        Args:
            event_type: Event type to filter by
        
        Returns:
            List of HookMetrics for the event
        """
        return [m for m in self.metrics if m.event_type == event_type]


# ── Global Instrumentation Singleton ───────────────────────────────────────

_global_instrument: Optional[HookInstrument] = None


def get_instrumentation() -> HookInstrument:
    """Get or create the global hook instrumentation instance.
    
    Returns:
        The global HookInstrument instance
    
    Note:
        Instrumentation is created once and cached. Subsequent calls
        return the same instance.
    """
    global _global_instrument
    if _global_instrument is None:
        _global_instrument = HookInstrument()
    return _global_instrument


def reset_instrumentation() -> None:
    """Reset the global instrumentation instance (for testing).
    
    Warning:
        This creates a new instance, discarding all metrics.
    """
    global _global_instrument
    _global_instrument = None
