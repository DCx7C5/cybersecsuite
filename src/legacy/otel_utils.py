"""Shared OTEL utilities for reducing duplication across instrumentation modules.

This module provides reusable patterns for:
- Async/sync span wrappers
- Time tracking and baseline checks
- Exception handling in spans
- Common metric recording patterns
"""


import time
import logging
from typing import Any, Callable, Optional, TypeVar
from functools import wraps

from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.span import Span

logger = logging.getLogger("otel.utils")

T = TypeVar("T")


class AsyncSpanContext:
    """Async context manager for creating and managing OTEL spans."""
    
    def __init__(
        self,
        tracer: Any,
        span_name: str,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """Initialize async span context.
        
        Args:
            tracer: OTEL tracer instance
            span_name: Name for the span
            attributes: Initial attributes to set on span
        """
        self.tracer = tracer
        self.span_name = span_name
        self.attributes = attributes or {}
        self.span: Optional[Span] = None
        self.start_time_ms = 0.0
    
    async def __aenter__(self) -> Span:
        """Async entry: create and start span."""
        self.span = self.tracer.start_span(self.span_name)
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        self.start_time_ms = time.time() * 1000
        return self.span
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async exit: record exception and end span."""
        if exc_type:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()
    
    def get_duration_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return (time.time() * 1000) - self.start_time_ms


class SyncSpanContext:
    """Sync context manager for creating and managing OTEL spans."""
    
    def __init__(
        self,
        tracer: Any,
        span_name: str,
        attributes: Optional[dict[str, Any]] = None,
    ):
        """Initialize sync span context.
        
        Args:
            tracer: OTEL tracer instance
            span_name: Name for the span
            attributes: Initial attributes to set on span
        """
        self.tracer = tracer
        self.span_name = span_name
        self.attributes = attributes or {}
        self.span: Optional[Span] = None
        self.start_time_ms = 0.0
    
    def __enter__(self) -> Span:
        """Sync entry: create and start span."""
        self.span = self.tracer.start_span(self.span_name)
        for key, value in self.attributes.items():
            self.span.set_attribute(key, value)
        self.start_time_ms = time.time() * 1000
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Sync exit: record exception and end span."""
        if exc_type:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()
    
    def get_duration_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        return (time.time() * 1000) - self.start_time_ms


def make_async_span_wrapper(
    tracer: Any,
    span_name_fn: Callable[..., str],
    attributes_fn: Optional[Callable[..., dict[str, Any]]] = None,
) -> Callable:
    """Create an async function wrapper that creates OTEL spans.
    
    Args:
        tracer: OTEL tracer instance
        span_name_fn: Function to generate span name from function args
        attributes_fn: Optional function to generate attributes from args
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            span_name = span_name_fn(*args, **kwargs)
            attributes = attributes_fn(*args, **kwargs) if attributes_fn else {}
            
            with SyncSpanContext(tracer, span_name, attributes):
                try:
                    result = await func(*args, **kwargs)
                    return result
                except Exception:
                    raise
        
        return wrapper
    return decorator


def make_sync_span_wrapper(
    tracer: Any,
    span_name_fn: Callable[..., str],
    attributes_fn: Optional[Callable[..., dict[str, Any]]] = None,
) -> Callable:
    """Create a sync function wrapper that creates OTEL spans.
    
    Args:
        tracer: OTEL tracer instance
        span_name_fn: Function to generate span name from function args
        attributes_fn: Optional function to generate attributes from args
    
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            span_name = span_name_fn(*args, **kwargs)
            attributes = attributes_fn(*args, **kwargs) if attributes_fn else {}
            
            with SyncSpanContext(tracer, span_name, attributes):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception:
                    raise
        
        return wrapper
    return decorator


def record_operation_with_baseline(
    duration_ms: float,
    metric: Any,
    baseline_ms: float,
    operation: str,
    attributes: Optional[dict[str, str]] = None,
    logger_obj: Optional[logging.Logger] = None,
) -> None:
    """Record operation metric and check baseline.
    
    Args:
        duration_ms: Operation duration in milliseconds
        metric: OTEL metric (histogram) to record to
        baseline_ms: Baseline P95 in milliseconds
        operation: Operation name (for logging)
        attributes: Attributes for metric recording
        logger_obj: Logger instance (for warnings)
    """
    attributes = attributes or {}
    metric.record(duration_ms, attributes)
    
    threshold_ms = baseline_ms * 1.15  # 15% over baseline
    if duration_ms > threshold_ms:
        msg = (
            f"{operation} slow: {duration_ms:.1f}ms "
            f"(baseline P95: {baseline_ms}ms, threshold: {threshold_ms:.0f}ms)"
        )
        if logger_obj:
            logger_obj.warning(msg)
        else:
            logger.warning(msg)


def extract_error_type(exc: Exception) -> str:
    """Extract clean error type name from exception."""
    return exc.__class__.__name__


# Export for public API
__all__ = [
    "AsyncSpanContext",
    "SyncSpanContext",
    "make_async_span_wrapper",
    "make_sync_span_wrapper",
    "record_operation_with_baseline",
    "extract_error_type",
]
