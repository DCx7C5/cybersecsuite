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


def get_strategy(strategy: ResponseInjectionStrategy):
    """Resolve concrete strategy implementation from enum value."""
    if strategy == ResponseInjectionStrategy.INJECT:
        return DirectStrategy()
    if strategy == ResponseInjectionStrategy.CHAIN:
        return ChainStrategy()
    return PrependContextStrategy()
