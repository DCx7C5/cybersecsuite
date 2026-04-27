"""MCP Tool OpenTelemetry instrumentation.

Provides tracing for MCP tool execution:
- Tool invocation and dispatch
- External MCP loading
- Tool execution time and results
- Error tracking

Service Name: cybersecsuite-mcp
"""
from __future__ import annotations

import logging
from typing import Any, Callable, Optional
from functools import wraps

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.span import Span
from opentelemetry.metrics import Counter, Histogram

logger = logging.getLogger("csmcp.otel")

# Initialize tracer and meter
_tracer = trace.get_tracer(__name__)
_meter = metrics.get_meter(__name__)

# Performance baselines (milliseconds)
BASELINE_TOOL_EXECUTION_P95_MS = 2000
BASELINE_EXTERNAL_LOAD_P95_MS = 1000

# Create metrics
tool_execution_duration = _meter.create_histogram(
    name="mcp.tool.duration",
    description="MCP tool execution time (ms)",
    unit="ms",
)

external_mcp_load_duration = _meter.create_histogram(
    name="mcp.load_external.duration",
    description="External MCP loading time (ms)",
    unit="ms",
)

tool_invocations = _meter.create_counter(
    name="mcp.tool.invocations",
    description="Total MCP tool invocations",
)

tool_errors = _meter.create_counter(
    name="mcp.tool.errors",
    description="Total MCP tool errors",
)

external_mcp_loads = _meter.create_counter(
    name="mcp.load_external.attempts",
    description="External MCP loading attempts",
)

tool_input_size = _meter.create_histogram(
    name="mcp.tool.input_size_bytes",
    description="MCP tool input size (bytes)",
    unit="By",
)

tool_output_size = _meter.create_histogram(
    name="mcp.tool.output_size_bytes",
    description="MCP tool output size (bytes)",
    unit="By",
)


class MCPTracingContext:
    """Context for MCP tracing."""
    
    def __init__(self, tool_name: str, request_id: Optional[str] = None):
        self.tool_name = tool_name
        self.request_id = request_id
        self.span: Optional[Span] = None
    
    def __enter__(self) -> Span:
        """Start a span for this tool."""
        self.span = _tracer.start_span(f"mcp.tool.{self.tool_name}")
        if self.request_id:
            self.span.set_attribute("request_id", self.request_id)
        self.span.set_attribute("tool_name", self.tool_name)
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the span, recording errors if any."""
        if exc_type:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR, str(exc_val)))
            tool_errors.add(1, {"tool": self.tool_name})
        else:
            self.span.set_status(Status(StatusCode.OK))
        self.span.end()


def trace_tool_execution(func: Callable) -> Callable:
    """Decorator for tracing MCP tool execution."""
    @wraps(func)
    async def wrapper(tool_name: str, tool_input: Any, *args, **kwargs) -> Any:
        import time
        import json
        
        # Calculate input size
        try:
            input_size = len(json.dumps(tool_input).encode("utf-8"))
        except:
            input_size = 0
        
        with _tracer.start_as_current_span(f"mcp.tool.{tool_name}") as span:
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("tool.input_size", input_size)
            
            start_ms = time.time() * 1000
            try:
                result = await func(tool_name, tool_input, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                # Calculate output size
                try:
                    output_size = len(json.dumps(result).encode("utf-8"))
                except:
                    output_size = 0
                
                span.set_attribute("tool.status", "success")
                span.set_attribute("tool.duration_ms", duration)
                span.set_attribute("tool.output_size", output_size)
                
                tool_execution_duration.record(duration, {"tool": tool_name})
                tool_input_size.record(input_size, {"tool": tool_name})
                tool_output_size.record(output_size, {"tool": tool_name})
                tool_invocations.add(1, {"tool": tool_name, "status": "success"})
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("tool.status", "error")
                span.set_attribute("tool.duration_ms", duration)
                span.set_attribute("tool.error", str(exc))
                
                tool_execution_duration.record(duration, {"tool": tool_name})
                tool_input_size.record(input_size, {"tool": tool_name})
                tool_errors.add(1, {"tool": tool_name})
                tool_invocations.add(1, {"tool": tool_name, "status": "error"})
                
                raise
        
        return wrapper


def trace_external_mcp_load(func: Callable) -> Callable:
    """Decorator for tracing external MCP loading."""
    @wraps(func)
    async def wrapper(mcp_name: str, *args, **kwargs) -> Any:
        import time
        
        with _tracer.start_as_current_span(f"mcp.load_external.{mcp_name}") as span:
            span.set_attribute("mcp.name", mcp_name)
            
            start_ms = time.time() * 1000
            try:
                result = await func(mcp_name, *args, **kwargs)
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.set_attribute("mcp.load_status", "success")
                span.set_attribute("mcp.load_duration_ms", duration)
                
                external_mcp_load_duration.record(duration, {"mcp": mcp_name})
                external_mcp_loads.add(1, {"mcp": mcp_name, "status": "success"})
                
                return result
            except Exception as exc:
                end_ms = time.time() * 1000
                duration = end_ms - start_ms
                
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                span.set_attribute("mcp.load_status", "error")
                span.set_attribute("mcp.load_duration_ms", duration)
                
                external_mcp_load_duration.record(duration, {"mcp": mcp_name})
                external_mcp_loads.add(1, {"mcp": mcp_name, "status": "error"})
                
                raise
        
        return wrapper


def check_tool_baseline(duration_ms: float, tool_name: str) -> None:
    """Check if tool execution meets baseline."""
    if duration_ms > BASELINE_TOOL_EXECUTION_P95_MS * 1.15:  # 15% over baseline
        logger.warning(
            f"MCP tool {tool_name} slow: {duration_ms:.1f}ms "
            f"(baseline P95: {BASELINE_TOOL_EXECUTION_P95_MS}ms)"
        )


def check_external_load_baseline(duration_ms: float, mcp_name: str) -> None:
    """Check if external MCP load meets baseline."""
    if duration_ms > BASELINE_EXTERNAL_LOAD_P95_MS * 1.15:  # 15% over baseline
        logger.warning(
            f"External MCP {mcp_name} slow to load: {duration_ms:.1f}ms "
            f"(baseline P95: {BASELINE_EXTERNAL_LOAD_P95_MS}ms)"
        )


# Export for public API
__all__ = [
    "MCPTracingContext",
    "trace_tool_execution",
    "trace_external_mcp_load",
    "check_tool_baseline",
    "check_external_load_baseline",
    "_tracer",
    "_meter",
]
