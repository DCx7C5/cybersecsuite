from collections.abc import AsyncIterator, Awaitable
from inspect import isawaitable
from typing import Any, cast

from css.core.sdks.adapters.browser_relay import BrowserRelayAdapter
from css.core.sdks.adapters.deepseek import DeepSeekAdapter
from css.core.sdks.registry import SDKRegistry
from css.core.types.base_client import BaseApiServiceClient
from css.core.types.base_messages import LLMResponse
from css.core.utils.token_counter import estimate_message_tokens
from css.core.models import get_model_registry

_BROWSER_RELAY_PROVIDER_IDS = {
    "browser-relay",
    "browser_relay",
    "browser-plugin",
    "browser_plugin",
}
_DEEPSEEK_PROVIDER_IDS = {
    "deepseek",
    "deepseek-ai",
    "deepseek_ai",
}


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
        self._register_builtin_sdks()

    @staticmethod
    def _normalize_provider_id(provider_id: str) -> str:
        normalized = provider_id.strip().lower()
        if normalized in _DEEPSEEK_PROVIDER_IDS:
            return "deepseek"
        return normalized

    def _register_builtin_sdks(self) -> None:
        if "deepseek" not in self._registry.list_registered():
            self._registry.register("deepseek", DeepSeekAdapter)

    async def get_sdk(
        self,
        provider_id: str,
        **kwargs: Any,
    ) -> BaseApiServiceClient:
        normalized_provider_id = self._normalize_provider_id(provider_id)
        return await self._registry.get(normalized_provider_id, **kwargs)

    async def call(
        self,
        provider_id: str,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        normalized_provider_id = self._normalize_provider_id(provider_id)
        if normalized_provider_id in _BROWSER_RELAY_PROVIDER_IDS:
            adapter = BrowserRelayAdapter()
            return await adapter.call_llm(
                model_id=model_id,
                messages=messages,
                **kwargs,
            )

        sdk = await self._registry.get(normalized_provider_id, **kwargs)
        stream_or_future = sdk.call_llm(
            model_id=model_id,
            messages=messages,
            **kwargs,
        )
        if isawaitable(stream_or_future):
            return await cast(Awaitable[AsyncIterator[Any]], stream_or_future)
        return cast(AsyncIterator[Any], stream_or_future)

    async def call_buffered(
        self,
        provider_id: str,
        model_id: str,
        messages: list[Any],
        **kwargs: Any,
    ) -> LLMResponse:
        normalized_provider_id = self._normalize_provider_id(provider_id)
        if normalized_provider_id in _BROWSER_RELAY_PROVIDER_IDS:
            adapter = BrowserRelayAdapter()
            return await adapter.call_llm_buffered(
                model_id=model_id,
                messages=messages,
                **kwargs,
            )

        sdk = await self._registry.get(normalized_provider_id, **kwargs)
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
