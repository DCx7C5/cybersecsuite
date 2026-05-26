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
    """Configuration for LLM extended thinking/reasoning capabilities.
    
    Provider-neutral contract for thinking parameters. Adapters translate
    these values to provider-specific formats (budget_tokens, thinking_budget, etc.)
    
    Attributes:
        budget_tokens: Maximum tokens for reasoning/thinking (optional).
            Anthropic: extended_thinking budget_tokens parameter
            OpenAI: reasoning thinking_budget parameter
            Must be positive if specified.
        effort: Reasoning effort level (optional).
            Supported values: 'low', 'medium', 'high'
            Adapters may ignore this value or use it as a heuristic.
            Default behavior: adapter determines based on model capabilities
    
    Examples:
        # Full thinking with high effort
        config = ThinkingConfig(budget_tokens=10000, effort="high")
        
        # Limited thinking on specific provider
        config = ThinkingConfig(budget_tokens=5000)
        
        # Low-effort reasoning
        config = ThinkingConfig(effort="low")
    """
    
    budget_tokens: int | None = None
    effort: Literal["low", "medium", "high"] | None = None
    
    def __post_init__(self):
        """Validate budget_tokens is positive if specified."""
        if self.budget_tokens is not None and self.budget_tokens <= 0:
            raise ValueError(
                f"budget_tokens must be positive, got {self.budget_tokens}"
            )
