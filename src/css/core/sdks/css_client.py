from collections.abc import AsyncIterator
from typing import Any

from css.core.sdks.registry import SDKRegistry
from css.core.types.base_client import BaseApiServiceClient
from css.core.types.base_messages import LLMResponse
from css.core.utils.token_counter import estimate_message_tokens
from css.core.models import get_model_registry


class CSSLLMClient:
    """Unified LLM client that routes to registered SDK adapters.

    Usage:
        client = CSSLLMClient()
        sdk = await client.get_sdk("openai", api_key="sk-...")
        async for chunk in await sdk.call_llm(model_id="gpt-4", messages=[...]):
            print(chunk.content)
    """

    def __init__(self) -> None:
        self._registry: SDKRegistry = SDKRegistry()
        self._model_registry = get_model_registry()

    async def get_sdk(
        self,
        provider_id: str,
        **kwargs: Any,
    ) -> BaseApiServiceClient:
        return await self._registry.get(provider_id, **kwargs)

    async def call(
        self,
        provider_id: str,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        sdk = await self._registry.get(provider_id, **kwargs)
        return await sdk.call_llm(
            model_id=model_id,
            messages=messages,
            **kwargs,
        )

    async def call_buffered(
        self,
        provider_id: str,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        sdk = await self._registry.get(provider_id, **kwargs)
        return await sdk.call_llm_buffered(
            model_id=model_id,
            messages=messages,
            **kwargs,
        )

    async def estimate_tokens(
        self,
        model_id: str,
        messages: list[dict[str, Any]],
    ) -> int:
        """Estimate token count for messages using the model's tokenizer.

        Attempts to use the provider SDK's tokenizer if available.
        Falls back to heuristic estimation if not supported.

        Args:
            model_id: Model identifier (e.g., 'gpt-4', 'claude-opus')
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Estimated token count
        """
        # Try provider-specific token counting first
        try:
            # Check if model has a documented token count method
            # (e.g., via OpenAI's encoding or Anthropic's token counter)
            # For now, use heuristic fallback
            pass
        except Exception:
            pass

        # Fallback to heuristic token counting
        return estimate_message_tokens(messages)

    def clear_cache(self, provider_id: str | None = None) -> None:
        self._registry.clear_cache(provider_id)

    def list_registered(self) -> list[str]:
        return self._registry.list_registered()


UniversalLLMClient = CSSLLMClient
