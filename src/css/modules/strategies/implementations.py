"""Concrete response strategy implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from css.core.a2a.enums import ResponseInjectionStrategy


@dataclass
class DirectStrategy:
    """Return assistant output without extra context wrapping."""

    def apply(self, user_query: str, assistant_output: str, context: dict[str, Any] | None = None) -> str:
        return assistant_output


@dataclass
class PrependContextStrategy:
    """Prepend selected context before assistant output."""

    def apply(self, user_query: str, assistant_output: str, context: dict[str, Any] | None = None) -> str:
        if not context:
            return assistant_output
        context_block = context.get("prepend", "")
        if not context_block:
            return assistant_output
        return f"{context_block}\n\n{assistant_output}"


@dataclass
class ChainStrategy:
    """Attach chain metadata for multi-step responses."""

    def apply(self, user_query: str, assistant_output: str, context: dict[str, Any] | None = None) -> str:
        if not context:
            return assistant_output
        trace = context.get("trace", [])
        if not trace:
            return assistant_output
        trace_lines = "\n".join(f"- {step}" for step in trace)
        return f"{assistant_output}\n\nReasoning trace:\n{trace_lines}"


@dataclass
class BalancedStrategy:
    """Round-robin provider selection for balanced distribution."""

    _cursor: int = 0

    def choose_provider(self, providers: list[str]) -> str:
        if not providers:
            return "ollama"
        idx = self._cursor % len(providers)
        self._cursor = (self._cursor + 1) % len(providers)
        return providers[idx]


@dataclass
class CostOptimizedStrategy:
    """Select provider with the lowest estimated per-token cost."""

    def choose_provider(self, providers: list[str], cost_map: dict[str, float] | None = None) -> str:
        if not providers:
            return "ollama"
        costs = cost_map or {}
        return min(providers, key=lambda provider: costs.get(provider, 1.0))


@dataclass
class LatencyOptimizedStrategy:
    """Select provider with the lowest observed latency."""

    def choose_provider(
        self,
        providers: list[str],
        latency_map: dict[str, float] | None = None,
    ) -> str:
        if not providers:
            return "ollama"
        latencies = latency_map or {}
        return min(providers, key=lambda provider: latencies.get(provider, 9999.0))


def get_strategy(strategy: ResponseInjectionStrategy):
    """Resolve concrete strategy implementation from enum value."""
    if strategy == ResponseInjectionStrategy.INJECT:
        return DirectStrategy()
    if strategy == ResponseInjectionStrategy.CHAIN:
        return ChainStrategy()
    return PrependContextStrategy()
