from collections.abc import AsyncIterator
from typing import Any

from css.core.sdks.registry import SDKRegistry
from css.core.types.base_client import BaseApiServiceClient
from css.core.types.base_messages import LLMResponse


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

    def clear_cache(self, provider_id: str | None = None) -> None:
        self._registry.clear_cache(provider_id)

    def list_registered(self) -> list[str]:
        return self._registry.list_registered()


UniversalLLMClient = CSSLLMClient
