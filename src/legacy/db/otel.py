"""Database OpenTelemetry instrumentation for Tortoise ORM.

Provides tracing for database operations:
- Query execution and duration
- Connection pooling metrics
- Transaction tracking
- Slow query detection

Service Name: cybersecsuite-db
"""


import logging
from typing import Any, Optional, Callable
from functools import wraps
import time
import re

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode

logger = logging.getLogger("db.otel")

# Initialize tracer and meter
_tracer = trace.get_tracer(__name__)
_meter = metrics.get_meter(__name__)

# Performance baselines (milliseconds)
BASELINE_QUERY_P95_MS = 100
BASELINE_TRANSACTION_P95_MS = 500

# Create metrics
query_duration = _meter.create_histogram(
    name="db.query.duration",
    description="Database query execution time (ms)",
    unit="ms",
)

transaction_duration = _meter.create_histogram(
    name="db.transaction.duration",
    description="Database transaction execution time (ms)",
    unit="ms",
)

query_count = _meter.create_counter(
    name="db.query.count",
    description="Total database queries",
)

query_errors = _meter.create_counter(
    name="db.query.errors",
    description="Total database query errors",
)

transaction_count = _meter.create_counter(
    name="db.transaction.count",
    description="Total database transactions",
)

connection_pool_size = _meter.create_counter(
    name="db.connection.pool_size",
    description="Database connection pool size",
)

slow_query_count = _meter.create_counter(
    name="db.query.slow",
    description="Slow database queries (over 150% of baseline)",
)


def _normalize_sql(sql: str) -> str:
    """Normalize SQL for better span names and grouping."""
    # Remove parameters and normalize spacing
    normalized = re.sub(r'\s+', ' ', sql.strip())
    # Extract operation type (SELECT, INSERT, UPDATE, DELETE, etc.)
    match = re.match(r'^(\w+)\s+', normalized)
    return match.group(1).upper() if match else "QUERY"


def _extract_table_name(sql: str) -> Optional[str]:
    """Extract table name from SQL query."""
    patterns = [
        r'FROM\s+`?(\w+)`?',
        r'INTO\s+`?(\w+)`?',
        r'UPDATE\s+`?(\w+)`?',
        r'DELETE\s+FROM\s+`?(\w+)`?',
    ]
    
    sql_upper = sql.upper()
    for pattern in patterns:
        match = re.search(pattern, sql_upper)
        if match:
            return match.group(1).lower()
    return None


def trace_query(func: Callable) -> Callable:
    """Decorator for tracing individual database queries."""
    @wraps(func)
    async def async_wrapper(sql: str, *args, **kwargs) -> Any:
        op_type = _normalize_sql(sql)
        table_name = _extract_table_name(sql)
        span_name = f"db.query.{op_type.lower()}"
        if table_name:
            span_name += f".{table_name}"
        
        with _tracer.start_as_current_span(span_name) as span:
            span.set_attribute("db.operation", op_type)
            if table_name:
                span.set_attribute("db.table", table_name)
            span.set_attribute("db.sql_length", len(sql))
            
            start_ms = time.time() * 1000
            try:
                result = await func(sql, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.set_attribute("db.duration_ms", duration)
                span.set_status(Status(StatusCode.OK))
                
                query_duration.record(duration, {"operation": op_type, "table": table_name or "unknown"})
                query_count.add(1, {"operation": op_type})
                
                if duration > BASELINE_QUERY_P95_MS * 1.5:
                    slow_query_count.add(1, {"operation": op_type})
                    logger.warning(
                        f"Slow query: {op_type} on {table_name or 'unknown'} "
                        f"({duration:.1f}ms, baseline P95: {BASELINE_QUERY_P95_MS}ms)"
                    )
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("db.error", exc.__class__.__name__)
                span.set_attribute("db.duration_ms", duration)
                
                query_duration.record(duration, {"operation": op_type, "table": table_name or "unknown"})
                query_errors.add(1, {"operation": op_type, "error": exc.__class__.__name__})
                query_count.add(1, {"operation": op_type})
                
                raise
    
    @wraps(func)
    def sync_wrapper(sql: str, *args, **kwargs) -> Any:
        op_type = _normalize_sql(sql)
        table_name = _extract_table_name(sql)
        span_name = f"db.query.{op_type.lower()}"
        if table_name:
            span_name += f".{table_name}"
        
        with _tracer.start_as_current_span(span_name) as span:
            span.set_attribute("db.operation", op_type)
            if table_name:
                span.set_attribute("db.table", table_name)
            span.set_attribute("db.sql_length", len(sql))
            
            start_ms = time.time() * 1000
            try:
                result = func(sql, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.set_attribute("db.duration_ms", duration)
                span.set_status(Status(StatusCode.OK))
                
                query_duration.record(duration, {"operation": op_type, "table": table_name or "unknown"})
                query_count.add(1, {"operation": op_type})
                
                if duration > BASELINE_QUERY_P95_MS * 1.5:
                    slow_query_count.add(1, {"operation": op_type})
                    logger.warning(
                        f"Slow query: {op_type} on {table_name or 'unknown'} "
                        f"({duration:.1f}ms, baseline P95: {BASELINE_QUERY_P95_MS}ms)"
                    )
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("db.error", exc.__class__.__name__)
                span.set_attribute("db.duration_ms", duration)
                
                query_duration.record(duration, {"operation": op_type, "table": table_name or "unknown"})
                query_errors.add(1, {"operation": op_type, "error": exc.__class__.__name__})
                query_count.add(1, {"operation": op_type})
                
                raise
    
    # Return appropriate wrapper based on whether the original function is async
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def trace_transaction(func: Callable) -> Callable:
    """Decorator for tracing database transactions."""
    @wraps(func)
    async def async_wrapper(name: Optional[str] = None, *args, **kwargs) -> Any:
        span_name = f"db.transaction.{name}" if name else "db.transaction"
        
        with _tracer.start_as_current_span(span_name) as span:
            if name:
                span.set_attribute("db.transaction_name", name)
            
            start_ms = time.time() * 1000
            try:
                result = await func(name, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.set_attribute("db.duration_ms", duration)
                span.set_status(Status(StatusCode.OK))
                
                transaction_duration.record(duration, {"transaction": name or "unknown"})
                transaction_count.add(1, {"status": "success"})
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("db.error", exc.__class__.__name__)
                span.set_attribute("db.duration_ms", duration)
                
                transaction_duration.record(duration, {"transaction": name or "unknown"})
                transaction_count.add(1, {"status": "error"})
                
                raise
    
    @wraps(func)
    def sync_wrapper(name: Optional[str] = None, *args, **kwargs) -> Any:
        span_name = f"db.transaction.{name}" if name else "db.transaction"
        
        with _tracer.start_as_current_span(span_name) as span:
            if name:
                span.set_attribute("db.transaction_name", name)
            
            start_ms = time.time() * 1000
            try:
                result = func(name, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.set_attribute("db.duration_ms", duration)
                span.set_status(Status(StatusCode.OK))
                
                transaction_duration.record(duration, {"transaction": name or "unknown"})
                transaction_count.add(1, {"status": "success"})
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("db.error", exc.__class__.__name__)
                span.set_attribute("db.duration_ms", duration)
                
                transaction_duration.record(duration, {"transaction": name or "unknown"})
                transaction_count.add(1, {"status": "error"})
                
                raise
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def check_query_baseline(duration_ms: float, operation: str, table: Optional[str] = None) -> None:
    """Check if query meets baseline."""
    if duration_ms > BASELINE_QUERY_P95_MS * 1.15:  # 15% over baseline
        logger.warning(
            f"Database query slow: {operation} on {table or 'unknown'} "
            f"({duration_ms:.1f}ms, baseline P95: {BASELINE_QUERY_P95_MS}ms)"
        )


def check_transaction_baseline(duration_ms: float, transaction_name: Optional[str] = None) -> None:
    """Check if transaction meets baseline."""
    if duration_ms > BASELINE_TRANSACTION_P95_MS * 1.15:  # 15% over baseline
        logger.warning(
            f"Database transaction slow: {transaction_name or 'unnamed'} "
            f"({duration_ms:.1f}ms, baseline P95: {BASELINE_TRANSACTION_P95_MS}ms)"
        )


# Export for public API
__all__ = [
    "trace_query",
    "trace_transaction",
    "check_query_baseline",
    "check_transaction_baseline",
    "_tracer",
    "_meter",
    "query_duration",
    "transaction_duration",
    "query_count",
    "query_errors",
    "transaction_count",
    "slow_query_count",
]
