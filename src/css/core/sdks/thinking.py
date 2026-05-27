"""ThinkingConfig — Extended thinking/reasoning configuration for LLM providers.

Providers with extended thinking capabilities:
- Anthropic: extended_thinking with optional budget_tokens
- OpenAI: reasoning with optional thinking_budget
- Other: Ignored for providers without native support

This module provides a provider-neutral contract for thinking/reasoning parameters.
Translation to provider-specific formats is delegated to adapter implementations
(src/css/core/sdks/adapters/anthropic.py, openai.py, etc.).
"""

from typing import Literal
import msgspec


class ThinkingConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Configuration for LLM extended thinking/reasoning capabilities."""

    budget_tokens: int | None = None
    effort: Literal["low", "medium", "high"] | None = None

    def __post_init__(self):
        if self.budget_tokens is not None and self.budget_tokens <= 0:
            raise ValueError(
                f"budget_tokens must be positive, got {self.budget_tokens}"
            )
        if self.effort is not None and self.effort not in {"low", "medium", "high"}:
            raise ValueError(f"effort must be one of low|medium|high, got {self.effort}")
