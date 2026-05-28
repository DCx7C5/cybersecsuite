"""W3C trace context extraction and correlation_id ContextVar."""

from collections.abc import Mapping
from contextvars import ContextVar
from typing import Any
from uuid import uuid4

import msgspec

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")


def set_correlation_id(value: str | None = None) -> str:
    """Set and return the correlation_id for the current context.

    If *value* is None or empty, generates a new UUID hex string.
    """
    if value:
        correlation_id_ctx.set(value)
        return value
    new_id = uuid4().hex
    correlation_id_ctx.set(new_id)
    return new_id


def get_correlation_id() -> str:
    """Return the current correlation_id or empty string if unset."""
    return correlation_id_ctx.get()


def clear_correlation_id() -> None:
    """Reset the correlation_id to empty."""
    correlation_id_ctx.set("")


class Traceparent(msgspec.Struct, frozen=True, kw_only=True):
    version: str
    trace_id: str
    parent_id: str
    trace_flags: str


class TraceContextExtractor:
    """Parse W3C ``traceparent`` headers into a correlation_id."""

    @staticmethod
    def extract(headers: Mapping[str, str]) -> Traceparent | None:
        raw = headers.get("traceparent", "")
        if not raw or "-" not in raw:
            return None
        parts = raw.strip().split("-")
        if len(parts) < 4:
            return None
        return Traceparent(
            version=parts[0],
            trace_id=parts[1],
            parent_id=parts[2],
            trace_flags=parts[3],
        )

    @staticmethod
    def extract_correlation_id(headers: Mapping[str, str]) -> str:
        trace = TraceContextExtractor.extract(headers)
        if trace is not None:
            return trace.trace_id
        return ""


class OtelSpanInstrumentor:
    """Creates child OTEL spans per instrumented call. Safe no-op when OTEL unavailable."""

    _tracer: Any | None = None

    @classmethod
    def _tracer_or_none(cls) -> Any | None:
        if cls._tracer is not None:
            return cls._tracer
        try:
            from opentelemetry import trace as otel_trace
            cls._tracer = otel_trace.get_tracer("css.core.events", "0.1.0")
        except Exception:
            cls._tracer = None
        return cls._tracer

    @classmethod
    def start_span(cls, name: str, attributes: dict[str, Any] | None = None) -> Any | None:
        tracer = cls._tracer_or_none()
        if tracer is None:
            return None
        return tracer.start_span(name, attributes=attributes or {})

    @classmethod
    def end_span(cls, span: Any | None, status: str = "OK") -> None:
        if span is None:
            return
        if status not in ("OK", "UNSET"):
            try:
                from opentelemetry.trace import Status, StatusCode
                span.set_status(Status(StatusCode.ERROR, description=status))
            except Exception:
                pass
        span.end()

    @classmethod
    def record_exception(cls, span: Any | None, exc: BaseException | None = None) -> None:
        if span is None:
            return
        span.record_exception(exc)
