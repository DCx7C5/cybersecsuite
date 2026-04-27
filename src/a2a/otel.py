"""A2A JSON-RPC OpenTelemetry instrumentation.

Provides tracing for A2A server operations:
- JSON-RPC method dispatch
- Task lifecycle (send, get, cancel)
- SSE streaming
- Performance baselines

Service Name: cybersecsuite-a2a
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional
from functools import wraps

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.span import Span
from opentelemetry.metrics import Counter, Histogram

logger = logging.getLogger("a2a.otel")

# Initialize tracer and meter
_tracer = trace.get_tracer(__name__)
_meter = metrics.get_meter(__name__)

# Performance baselines (milliseconds)
BASELINE_JSONRPC_P95_MS = 500
BASELINE_TASK_SEND_P95_MS = 300
BASELINE_TASK_GET_P95_MS = 100
BASELINE_SSE_STREAM_P95_MS = 100

# Create metrics
jsonrpc_method_duration = _meter.create_histogram(
    name="a2a.jsonrpc.duration",
    description="JSON-RPC method execution time (ms)",
    unit="ms",
)

task_send_duration = _meter.create_histogram(
    name="a2a.task.send.duration",
    description="Task send operation duration (ms)",
    unit="ms",
)

task_get_duration = _meter.create_histogram(
    name="a2a.task.get.duration",
    description="Task get operation duration (ms)",
    unit="ms",
)

task_cancel_duration = _meter.create_histogram(
    name="a2a.task.cancel.duration",
    description="Task cancel operation duration (ms)",
    unit="ms",
)

sse_stream_duration = _meter.create_histogram(
    name="a2a.sse.stream.duration",
    description="SSE stream connection duration (ms)",
    unit="ms",
)

jsonrpc_errors = _meter.create_counter(
    name="a2a.jsonrpc.errors",
    description="Total JSON-RPC errors",
)

task_counter = _meter.create_counter(
    name="a2a.task.total",
    description="Total tasks processed by action",
)

active_sessions = _meter.create_gauge(
    name="a2a.sessions.active",
    description="Active A2A sessions",
)


class A2ATracingContext:
    """Context for A2A tracing."""
    
    def __init__(self, method: str, request_id: Optional[str] = None):
        self.method = method
        self.request_id = request_id
        self.span: Optional[Span] = None
    
    def __enter__(self) -> Span:
        """Start a span for this operation."""
        self.span = _tracer.start_span(f"a2a.{self.method}")
        if self.request_id:
            self.span.set_attribute("request_id", self.request_id)
        self.span.set_attribute("method", self.method)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the span, recording errors if any."""
        if exc_type:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            jsonrpc_errors.add(1, {"method": self.method})
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()


def trace_jsonrpc_method(method_name: str) -> Callable:
    """Decorator for tracing JSON-RPC method handlers."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            request_id = kwargs.get("request_id") or getattr(args[0], "request_id", None)
            
            with _tracer.start_as_current_span(f"jsonrpc.{method_name}") as span:
                span.set_attribute("jsonrpc.method", method_name)
                if request_id:
                    span.set_attribute("jsonrpc.request_id", str(request_id))
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("jsonrpc.status", "success")
                    task_counter.add(1, {"action": method_name, "status": "success"})
                    return result
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    task_counter.add(1, {"action": method_name, "status": "error"})
                    jsonrpc_errors.add(1, {"method": method_name})
                    raise
        
        return wrapper
    return decorator


def trace_task_operation(operation_type: str, metric_name: str) -> Callable:
    """Decorator for tracing task operations (send, get, cancel)."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import time
            task_id = kwargs.get("task_id") or getattr(args[0], "task_id", None)
            
            with _tracer.start_as_current_span(f"tasks.{operation_type}") as span:
                span.set_attribute("task.operation", operation_type)
                if task_id:
                    span.set_attribute("task.id", str(task_id))
                
                start_ms = time.time() * 1000
                try:
                    result = await func(*args, **kwargs)
                    end_ms = time.time() * 1000
                    duration = end_ms - start_ms
                    
                    span.set_attribute("task.status", "success")
                    span.set_attribute("task.duration_ms", duration)
                    
                    # Record histogram metric
                    metric = globals()[metric_name]
                    metric.record(duration, {"operation": operation_type})
                    task_counter.add(1, {"action": operation_type, "status": "success"})
                    
                    return result
                except Exception as exc:
                    end_ms = time.time() * 1000
                    duration = end_ms - start_ms
                    
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    span.set_attribute("task.status", "error")
                    span.set_attribute("task.duration_ms", duration)
                    
                    metric = globals()[metric_name]
                    metric.record(duration, {"operation": operation_type})
                    task_counter.add(1, {"action": operation_type, "status": "error"})
                    
                    raise
        
        return wrapper
    return decorator


def trace_sse_stream() -> Callable:
    """Decorator for tracing SSE streaming operations."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            import time
            task_id = kwargs.get("task_id") or getattr(args[0], "task_id", None)
            
            with _tracer.start_as_current_span("sse.stream") as span:
                if task_id:
                    span.set_attribute("task.id", str(task_id))
                
                start_ms = time.time() * 1000
                try:
                    result = await func(*args, **kwargs)
                    end_ms = time.time() * 1000
                    duration = end_ms - start_ms
                    
                    span.set_attribute("sse.status", "success")
                    span.set_attribute("sse.duration_ms", duration)
                    sse_stream_duration.record(duration, {"status": "success"})
                    
                    return result
                except Exception as exc:
                    end_ms = time.time() * 1000
                    duration = end_ms - start_ms
                    
                    span.record_exception(exc)
                    span.set_status(Status(StatusCode.ERROR, str(exc)))
                    span.set_attribute("sse.status", "error")
                    span.set_attribute("sse.duration_ms", duration)
                    sse_stream_duration.record(duration, {"status": "error"})
                    
                    raise
        
        return wrapper
    return decorator


# Performance baseline checks
def check_jsonrpc_baseline(duration_ms: float, method: str) -> None:
    """Check if JSON-RPC operation meets baseline."""
    if duration_ms > BASELINE_JSONRPC_P95_MS * 1.15:  # 15% over baseline
        logger.warning(
            f"JSON-RPC {method} slow: {duration_ms:.1f}ms "
            f"(baseline P95: {BASELINE_JSONRPC_P95_MS}ms)"
        )


def check_task_baseline(duration_ms: float, operation: str) -> None:
    """Check if task operation meets baseline."""
    baselines = {
        "send": BASELINE_TASK_SEND_P95_MS,
        "get": BASELINE_TASK_GET_P95_MS,
        "cancel": 50,  # Fast
    }
    
    baseline = baselines.get(operation, 100)
    if duration_ms > baseline * 1.15:  # 15% over baseline
        logger.warning(
            f"Task {operation} slow: {duration_ms:.1f}ms "
            f"(baseline P95: {baseline}ms)"
        )


# Export for public API
__all__ = [
    "A2ATracingContext",
    "trace_jsonrpc_method",
    "trace_task_operation",
    "trace_sse_stream",
    "check_jsonrpc_baseline",
    "check_task_baseline",
    "_tracer",
    "_meter",
]
