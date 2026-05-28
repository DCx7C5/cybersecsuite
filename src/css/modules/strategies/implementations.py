"""Concrete response strategy implementations."""


from typing import Any

from css.modules.a2a_google.enums import ResponseInjectionStrategy
from css.core.base import BaseMessage


class DirectStrategy:
    """Return assistant output without extra context wrapping."""

    def apply(self, user_query: str, assistant_output: str, context: dict[str, Any] | None = None) -> str:
        return assistant_output


class PrependContextStrategy:
    """Prepend selected context before assistant output."""

    def apply(self, user_query: str, assistant_output: str, context: dict[str, Any] | None = None) -> str:
        if not context:
            return assistant_output
        context_block = context.get("prepend", "")
        if not context_block:
            return assistant_output
        return f"{context_block}\n\n{assistant_output}"


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


class BalancedStrategy:
    """Round-robin provider selection for balanced distribution."""

    def __init__(self) -> None:
        self._cursor = 0

    def choose_provider(self, providers: list[str]) -> str:
        if not providers:
            return "ollama"
        idx = self._cursor % len(providers)
        self._cursor = (self._cursor + 1) % len(providers)
        return providers[idx]


class CostOptimizedStrategy:
    """Select provider with the lowest estimated per-token cost."""

    def choose_provider(self, providers: list[str], cost_map: dict[str, float] | None = None) -> str:
        if not providers:
            return "ollama"
        costs = cost_map or {}
        return min(providers, key=lambda provider: costs.get(provider, 1.0))


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


class TokenAwareStrategy:
    """Select provider based on message token count and provider context window limits.

    Routes to providers capable of handling the estimated token count. Falls back
    to providers with larger context windows when message size exceeds limits.

    Uses CSSLLMClient.estimate_tokens() for heuristic token counting.
    """

    async def choose_provider(
        self,
        providers: list[str],
        messages: list[BaseMessage] | None = None,
        provider_limits: dict[str, int] | None = None,
        default_model: str = "gpt-4",
    ) -> str:
        """Choose provider based on token count and context window limits.

        Args:
            providers: List of available provider IDs
            messages: Message list to estimate tokens for
            provider_limits: Context window size per provider (tokens)
                            e.g., {"openai/gpt-4": 128000, "mistral": 32000}
            default_model: Model ID to use for token estimation

        Returns:
            Selected provider ID
        """
        if not providers:
            return "ollama"

        if not messages:
            # No message context — use first provider
            return providers[0]

        # Estimate total token count
        try:
            from css.core.sdks.css_client import CSSLLMClient
            
            client = CSSLLMClient()
            # Convert BaseMessage to dict format for estimation
            msg_dicts = [
                {"role": m.role, "content": m.content}
                for m in messages
            ]
            token_count = await client.estimate_tokens(default_model, msg_dicts)
        except Exception:
            # If estimation fails, use first provider (graceful degradation)
            return providers[0]

        # If no limits provided, use first provider
        if not provider_limits:
            return providers[0]

        # Find providers that can handle the token count
        suitable_providers = [
            p for p in providers
            if provider_limits.get(p, 128000) >= token_count
        ]

        # Return first suitable provider, or largest-context provider as fallback
        if suitable_providers:
            return suitable_providers[0]

        # Fallback: return provider with largest context window
        return max(providers, key=lambda p: provider_limits.get(p, 128000))


def get_strategy(strategy: ResponseInjectionStrategy):
    """Resolve concrete strategy implementation from enum value."""
    if strategy == ResponseInjectionStrategy.INJECT:
        return DirectStrategy()
    if strategy == ResponseInjectionStrategy.CHAIN:
        return ChainStrategy()
    return PrependContextStrategy()
