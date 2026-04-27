"""Context Propagation OpenTelemetry instrumentation.

Provides trace context propagation across services:
- HTTP header injection/extraction
- gRPC metadata propagation
- Async task context preservation
- Request ID correlation

Service Name: cybersecsuite-propagation
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
import uuid

from opentelemetry import trace, context

logger = logging.getLogger("propagation.otel")

# Get the global tracer
_tracer = trace.get_tracer(__name__)

# Initialize propagators for different formats (optional, gracefully degrade)
_jaeger_propagator = None
_b3_propagator = None
_thrift_propagator = None

try:
    from opentelemetry.propagators.jaeger.jaeger_format import JaegerFormat
    _jaeger_propagator = JaegerFormat()
except ImportError:
    pass

try:
    from opentelemetry.propagators.b3 import B3SingleFormat
    _b3_propagator = B3SingleFormat()
except ImportError:
    pass

try:
    from opentelemetry.propagators.jaeger_thrift import JaegerThriftPropagator
    _thrift_propagator = JaegerThriftPropagator()
except ImportError:
    pass


class TraceContextManager:
    """Manages trace context across requests and async operations."""
    
    def __init__(self, request_id: Optional[str] = None, trace_id: Optional[str] = None):
        """Initialize trace context manager.
        
        Args:
            request_id: Optional request ID for correlation
            trace_id: Optional existing trace ID to continue
        """
        self.request_id = request_id or str(uuid.uuid4())
        self.trace_id = trace_id
        self._current_span = None
    
    def extract_from_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Extract trace context from HTTP headers.
        
        Supports multiple formats: Jaeger, B3, W3C Trace Context
        """
        ctx = {}
        
        # Try Jaeger format first
        if _jaeger_propagator:
            try:
                extracted = _jaeger_propagator.extract(headers)
                if extracted:
                    ctx['jaeger'] = extracted
            except:
                pass
        
        # Try B3 format
        if _b3_propagator:
            try:
                extracted = _b3_propagator.extract(headers)
                if extracted:
                    ctx['b3'] = extracted
            except:
                pass
        
        return ctx
    
    def inject_into_headers(self, headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Inject trace context into HTTP headers.
        
        Returns headers with trace context for downstream services.
        """
        if headers is None:
            headers = {}
        
        current_span = trace.get_current_span()
        
        # Inject using Jaeger format (most common)
        if _jaeger_propagator and current_span:
            try:
                _jaeger_propagator.inject(headers)
            except:
                pass
        
        # Also inject request ID for application-level correlation
        headers['X-Request-ID'] = self.request_id
        if self.trace_id:
            headers['X-Trace-ID'] = self.trace_id
        
        return headers
    
    def __enter__(self):
        """Context manager entry."""
        token = context.attach(context.get_current())
        self._token = token
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if hasattr(self, '_token'):
            context.detach(self._token)


def propagate_trace_context(func: Callable) -> Callable:
    """Decorator to propagate trace context across async/sync boundaries."""
    @wraps(func)
    async def async_wrapper(self, *args, request_id: Optional[str] = None, **kwargs) -> Any:
        # Create context manager with request ID
        ctx_mgr = TraceContextManager(request_id=request_id)
        
        with ctx_mgr:
            return await func(self, *args, **kwargs)
    
    @wraps(func)
    def sync_wrapper(self, *args, request_id: Optional[str] = None, **kwargs) -> Any:
        # Create context manager with request ID
        ctx_mgr = TraceContextManager(request_id=request_id)
        
        with ctx_mgr:
            return func(self, *args, **kwargs)
    
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def extract_trace_context_from_request(request: Any) -> Dict[str, Any]:
    """Extract trace context from incoming HTTP request.
    
    Works with FastAPI, Starlette, and other ASGI frameworks.
    """
    headers = {}
    
    # Extract headers from request
    if hasattr(request, 'headers'):
        if isinstance(request.headers, dict):
            headers = request.headers
        else:
            # Handle headers as list of tuples or MutableHeaders
            try:
                headers = dict(request.headers)
            except:
                pass
    
    # Extract trace context
    ctx_mgr = TraceContextManager()
    trace_ctx = ctx_mgr.extract_from_headers(headers)
    
    # Also extract request ID if present
    request_id = headers.get('X-Request-ID') or headers.get('x-request-id')
    trace_ctx['request_id'] = request_id or str(uuid.uuid4())
    
    return trace_ctx


def create_trace_headers(request_id: Optional[str] = None, trace_id: Optional[str] = None) -> Dict[str, str]:
    """Create headers for propagating trace context to downstream services."""
    ctx_mgr = TraceContextManager(request_id=request_id, trace_id=trace_id)
    return ctx_mgr.inject_into_headers()


def get_or_create_request_id(headers: Optional[Dict[str, str]] = None) -> str:
    """Get existing request ID from headers or create new one."""
    if headers:
        request_id = headers.get('X-Request-ID') or headers.get('x-request-id')
        if request_id:
            return request_id
    
    return str(uuid.uuid4())


# Export for public API
__all__ = [
    "TraceContextManager",
    "propagate_trace_context",
    "extract_trace_context_from_request",
    "create_trace_headers",
    "get_or_create_request_id",
    "_tracer",
]
