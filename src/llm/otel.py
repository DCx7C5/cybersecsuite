"""OpenTelemetry setup for the LLM layer.

Call `setup_otel()` once during ASGI lifespan startup (or at process init).
Afterwards use `get_tracer()` / `get_meter()` everywhere.
"""
from __future__ import annotations

import base64
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

_tracer = None
_meter = None


def setup_otel(
    endpoint: str | None = None,
    service_name: str | None = None,
    sample_ratio: float = 1.0,
) -> None:
    """Configure OTLP exporter pointing at OpenObserve and instrument httpx."""
    global _tracer, _meter

    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

    svc = service_name or os.environ.get("OTEL_SERVICE_NAME", "cybersecsuite-llm")
    ep = endpoint or os.environ.get(
        "OPENOBSERVE_OTLP_ENDPOINT", "http://localhost:5080/api/default"
    )
    headers = {"Authorization": "Basic " + _basic_auth()}

    sampler = TraceIdRatioBased(sample_ratio) if sample_ratio < 1.0 else None
    tp_kwargs = {"sampler": sampler} if sampler else {}
    tp = TracerProvider(**tp_kwargs)
    tp.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{ep}/v1/traces", headers=headers))
    )
    trace.set_tracer_provider(tp)

    mr = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{ep}/v1/metrics", headers=headers)
    )
    mp = MeterProvider(metric_readers=[mr])
    metrics.set_meter_provider(mp)

    try:
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        HTTPXClientInstrumentor().instrument()
    except Exception:
        pass  # optional instrumentation

    _tracer = trace.get_tracer(svc)
    _meter = metrics.get_meter(svc)


def get_tracer():
    """Return the module-level tracer, initialising a no-op one if needed."""
    if _tracer is not None:
        return _tracer
    from opentelemetry import trace
    return trace.get_tracer("cybersecsuite-llm")


def get_meter():
    """Return the module-level meter, initialising a no-op one if needed."""
    if _meter is not None:
        return _meter
    from opentelemetry import metrics
    return metrics.get_meter("cybersecsuite-llm")


def _basic_auth() -> str:
    u = os.environ.get("OPENOBSERVE_EMAIL", "admin@cybersec.local")
    p = os.environ.get("OPENOBSERVE_PASSWORD", "cYb3rS3c!")
    return base64.b64encode(f"{u}:{p}".encode()).decode()
