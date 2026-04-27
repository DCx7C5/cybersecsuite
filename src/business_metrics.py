"""Business Metrics OpenTelemetry instrumentation.

Provides tracing for business-level metrics:
- Token usage (prompt, completion, total)
- API costs
- Cache hit/miss rates
- Tool latencies by name
- Threat intelligence lookups
- Findings processing

Service Name: cybersecsuite-business
"""


import logging
from typing import Optional
from dataclasses import dataclass

from opentelemetry import metrics

logger = logging.getLogger("business.otel")

# Initialize meter
_meter = metrics.get_meter(__name__)

# Token Metrics
token_prompt_usage = _meter.create_histogram(
    name="business.tokens.prompt",
    description="Prompt tokens used",
    unit="1",
)

token_completion_usage = _meter.create_histogram(
    name="business.tokens.completion",
    description="Completion tokens used",
    unit="1",
)

token_total_usage = _meter.create_counter(
    name="business.tokens.total",
    description="Total tokens used",
    unit="1",
)

# Cost Metrics
api_cost = _meter.create_counter(
    name="business.cost.api",
    description="API costs in USD",
    unit="$",
)

cache_cost_savings = _meter.create_counter(
    name="business.cache.savings",
    description="Estimated savings from cache hits (USD)",
    unit="$",
)

# Cache Metrics
cache_hits = _meter.create_counter(
    name="business.cache.hits",
    description="Cache hit count",
)

cache_misses = _meter.create_counter(
    name="business.cache.misses",
    description="Cache miss count",
)

cache_evictions = _meter.create_counter(
    name="business.cache.evictions",
    description="Cache eviction count",
)

# Tool Metrics
tool_invocations = _meter.create_counter(
    name="business.tool.invocations",
    description="Tool invocations by name",
)

tool_latency = _meter.create_histogram(
    name="business.tool.latency",
    description="Tool latency by name (ms)",
    unit="ms",
)

tool_errors = _meter.create_counter(
    name="business.tool.errors",
    description="Tool errors by name",
)

# Threat Intelligence Metrics
threat_intel_lookups = _meter.create_counter(
    name="business.threat_intel.lookups",
    description="Threat intelligence lookups",
)

threat_intel_cache_hits = _meter.create_counter(
    name="business.threat_intel.cache_hits",
    description="Threat intelligence cache hits",
)

# Findings Processing Metrics
findings_created = _meter.create_counter(
    name="business.findings.created",
    description="Findings created",
)

findings_updated = _meter.create_counter(
    name="business.findings.updated",
    description="Findings updated",
)

findings_archived = _meter.create_counter(
    name="business.findings.archived",
    description="Findings archived",
)

# Cases Metrics
cases_created = _meter.create_counter(
    name="business.cases.created",
    description="Cases created",
)

cases_completed = _meter.create_counter(
    name="business.cases.completed",
    description="Cases completed",
)

cases_duration = _meter.create_histogram(
    name="business.cases.duration",
    description="Case duration from creation to completion (ms)",
    unit="ms",
)

# Worker Metrics
workers_active = _meter.create_counter(
    name="business.workers.active",
    description="Active workers",
)

workers_completed = _meter.create_counter(
    name="business.workers.completed",
    description="Completed workers",
)

workers_failed = _meter.create_counter(
    name="business.workers.failed",
    description="Failed workers",
)

worker_duration = _meter.create_histogram(
    name="business.worker.duration",
    description="Worker execution duration (ms)",
    unit="ms",
)


@dataclass
class TokenUsage:
    """Token usage data."""
    prompt_tokens: int
    completion_tokens: int
    
    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def record_token_usage(usage: TokenUsage, model: str = "unknown") -> None:
    """Record token usage."""
    token_prompt_usage.record(usage.prompt_tokens, {"model": model})
    token_completion_usage.record(usage.completion_tokens, {"model": model})
    token_total_usage.add(usage.total_tokens, {"model": model})


def record_api_cost(amount_usd: float, api_name: str = "unknown") -> None:
    """Record API cost."""
    api_cost.add(amount_usd, {"api": api_name})


def record_cache_hit(cache_name: str = "unknown", saved_usd: Optional[float] = None) -> None:
    """Record cache hit."""
    cache_hits.add(1, {"cache": cache_name})
    if saved_usd:
        cache_cost_savings.add(saved_usd, {"cache": cache_name})


def record_cache_miss(cache_name: str = "unknown") -> None:
    """Record cache miss."""
    cache_misses.add(1, {"cache": cache_name})


def record_cache_eviction(cache_name: str = "unknown") -> None:
    """Record cache eviction."""
    cache_evictions.add(1, {"cache": cache_name})


def record_tool_invocation(tool_name: str, latency_ms: float, success: bool = True) -> None:
    """Record tool invocation."""
    tool_invocations.add(1, {"tool": tool_name, "status": "success" if success else "error"})
    tool_latency.record(latency_ms, {"tool": tool_name})
    if not success:
        tool_errors.add(1, {"tool": tool_name})


def record_threat_intel_lookup(lookup_type: str = "unknown", cached: bool = False) -> None:
    """Record threat intelligence lookup."""
    threat_intel_lookups.add(1, {"type": lookup_type})
    if cached:
        threat_intel_cache_hits.add(1, {"type": lookup_type})


def record_finding_created(severity: str = "unknown") -> None:
    """Record finding creation."""
    findings_created.add(1, {"severity": severity})


def record_finding_updated(severity: str = "unknown") -> None:
    """Record finding update."""
    findings_updated.add(1, {"severity": severity})


def record_finding_archived(reason: str = "unknown") -> None:
    """Record finding archival."""
    findings_archived.add(1, {"reason": reason})


def record_case_created(case_type: str = "unknown") -> None:
    """Record case creation."""
    cases_created.add(1, {"type": case_type})


def record_case_completed(case_type: str = "unknown", duration_ms: float = 0) -> None:
    """Record case completion."""
    cases_completed.add(1, {"type": case_type})
    if duration_ms > 0:
        cases_duration.record(duration_ms, {"type": case_type})


def record_worker_active(worker_type: str = "unknown") -> None:
    """Record active worker."""
    workers_active.add(1, {"type": worker_type})


def record_worker_completed(worker_type: str = "unknown", duration_ms: float = 0) -> None:
    """Record completed worker."""
    workers_completed.add(1, {"type": worker_type})
    if duration_ms > 0:
        worker_duration.record(duration_ms, {"type": worker_type})


def record_worker_failed(worker_type: str = "unknown", reason: str = "unknown") -> None:
    """Record failed worker."""
    workers_failed.add(1, {"type": worker_type, "reason": reason})


# Export for public API
__all__ = [
    "TokenUsage",
    "record_token_usage",
    "record_api_cost",
    "record_cache_hit",
    "record_cache_miss",
    "record_cache_eviction",
    "record_tool_invocation",
    "record_threat_intel_lookup",
    "record_finding_created",
    "record_finding_updated",
    "record_finding_archived",
    "record_case_created",
    "record_case_completed",
    "record_worker_active",
    "record_worker_completed",
    "record_worker_failed",
]
