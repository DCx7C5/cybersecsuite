"""Worker State Machine OpenTelemetry instrumentation.

Provides tracing for worker lifecycle:
- Worker state transitions
- Execution time per state
- Pause/resume tracking
- Failure/retry metrics

Service Name: cybersecsuite-worker
"""


import logging
from typing import Any, Optional, Callable
from functools import wraps
import time

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger("db.worker.otel")

# Initialize tracer and meter
_tracer = trace.get_tracer(__name__)
_meter = metrics.get_meter(__name__)

# Performance baselines (milliseconds)
BASELINE_RUNNING_P95_MS = 10000  # 10 seconds average task time
BASELINE_PAUSED_P95_MS = 5000

# Create metrics
state_transition_duration = _meter.create_histogram(
    name="worker.transition.duration",
    description="Worker state transition time (ms)",
    unit="ms",
)

state_duration = _meter.create_histogram(
    name="worker.state.duration",
    description="Time spent in worker state (ms)",
    unit="ms",
)

transition_count = _meter.create_counter(
    name="worker.transition.count",
    description="Total worker state transitions",
)

transition_errors = _meter.create_counter(
    name="worker.transition.errors",
    description="Failed worker state transitions",
)

workers_by_state = _meter.create_counter(
    name="worker.state.current",
    description="Current workers in each state",
)

pause_resume_count = _meter.create_counter(
    name="worker.pause_resume.count",
    description="Worker pause/resume events",
)

failure_count = _meter.create_counter(
    name="worker.failure.count",
    description="Worker failures",
)


def trace_state_transition(func: Callable) -> Callable:
    """Decorator for tracing worker state transitions."""
    @wraps(func)
    async def wrapper(self, to_state: str, reason: str = "", metadata: Optional[dict] = None, *args, **kwargs) -> Any:
        worker_id = getattr(self, 'worker_id', 'unknown')
        span_name = f"worker.transition.{to_state}"
        
        with _tracer.start_as_current_span(span_name) as span:
            span.set_attribute("worker.id", worker_id)
            span.set_attribute("worker.to_state", to_state)
            span.set_attribute("worker.reason", reason)
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        span.set_attribute(f"worker.metadata.{key}", value)
            
            start_ms = time.time() * 1000
            try:
                result = await func(self, to_state, reason, metadata, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                # Extract from_state from result or try to get it
                from_state = getattr(result, 'from_state', 'unknown') if hasattr(result, 'from_state') else 'unknown'
                span.set_attribute("worker.from_state", from_state)
                span.set_attribute("worker.duration_ms", duration)
                span.set_status(Status(StatusCode.OK))
                
                state_transition_duration.record(duration, {
                    "worker_id": worker_id,
                    "from_state": from_state,
                    "to_state": to_state,
                    "reason": reason or "unknown"
                })
                transition_count.add(1, {
                    "from_state": from_state,
                    "to_state": to_state,
                    "status": "success"
                })
                
                # Track pause/resume events
                if to_state == "paused":
                    pause_resume_count.add(1, {"event": "pause", "reason": reason or "unknown"})
                elif from_state == "paused" and to_state == "running":
                    pause_resume_count.add(1, {"event": "resume", "reason": reason or "unknown"})
                
                # Track failures
                if to_state == "failed":
                    failure_count.add(1, {"reason": reason or "unknown"})
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("worker.error", exc.__class__.__name__)
                span.set_attribute("worker.duration_ms", duration)
                
                transition_errors.add(1, {
                    "to_state": to_state,
                    "error": exc.__class__.__name__
                })
                transition_count.add(1, {
                    "to_state": to_state,
                    "status": "error"
                })
                
                raise
    
    return wrapper


def trace_state_query(func: Callable) -> Callable:
    """Decorator for tracing worker state queries."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs) -> Any:
        func_name = func.__name__
        span_name = f"worker.query.{func_name}"
        
        with _tracer.start_as_current_span(span_name) as span:
            start_ms = time.time() * 1000
            try:
                result = await func(self, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.set_attribute("worker.query_type", func_name)
                span.set_attribute("worker.duration_ms", duration)
                span.set_status(Status(StatusCode.OK))
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("worker.error", exc.__class__.__name__)
                
                raise
    
    return wrapper


def record_worker_state(state: str, count: int) -> None:
    """Record current count of workers in a state."""
    workers_by_state.add(count, {"state": state})


def check_transition_baseline(duration_ms: float, from_state: str, to_state: str) -> None:
    """Check if transition meets baseline."""
    if to_state == "running" and duration_ms > BASELINE_RUNNING_P95_MS * 1.15:
        logger.warning(
            f"Worker transition to running slow: "
            f"{duration_ms:.1f}ms (baseline P95: {BASELINE_RUNNING_P95_MS}ms)"
        )
    elif to_state == "paused" and duration_ms > BASELINE_PAUSED_P95_MS * 1.15:
        logger.warning(
            f"Worker transition to paused slow: "
            f"{duration_ms:.1f}ms (baseline P95: {BASELINE_PAUSED_P95_MS}ms)"
        )


# Export for public API
__all__ = [
    "trace_state_transition",
    "trace_state_query",
    "record_worker_state",
    "check_transition_baseline",
    "_tracer",
    "_meter",
    "state_transition_duration",
    "state_duration",
    "transition_count",
    "transition_errors",
    "pause_resume_count",
    "failure_count",
]
