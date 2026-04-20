"""
Token Counter Service — pre-request token estimation via Anthropic SDK.

Wraps client.messages.count_tokens() to count tokens before sending,
enabling smarter routing decisions and pre-flight budget checks.
"""
from __future__ import annotations

import logging
from typing import Any

import anthropic

from ai_proxy.providers.registry import get_provider

logger = logging.getLogger("ai_proxy.token_counter")


class TokenCounter:
    """Count tokens for an Anthropic-format request using the official SDK."""

    def __init__(self) -> None:
        self._clients: dict[str, anthropic.AsyncAnthropic] = {}

    def _get_client(self, provider_id: str = "anthropic") -> anthropic.AsyncAnthropic | None:
        if provider_id in self._clients:
            return self._clients[provider_id]

        provider = get_provider(provider_id)
        if not provider:
            return None

        api_key = provider.get_api_key()
        if not api_key:
            return None

        client = anthropic.AsyncAnthropic(
            api_key=api_key,
            base_url=provider.base_url,
            max_retries=1,
        )
        self._clients[provider_id] = client
        return client

    async def count(
        self,
        model: str,
        messages: list[dict[str, Any]],
        system: str | None = None,
        tools: list[dict[str, Any]] | None = None,
        provider_id: str = "anthropic",
    ) -> int | None:
        """
        Count tokens for the given request parameters.

        Returns input_tokens count, or None if counting is unavailable.
        """
        client = self._get_client(provider_id)
        if not client:
            logger.debug("No Anthropic client for provider %s, skipping token count", provider_id)
            return None

        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system
            if tools:
                kwargs["tools"] = tools

            response = await client.messages.count_tokens(**kwargs)
            return response.input_tokens

        except anthropic.APIError as exc:
            logger.warning("Token counting failed: %s", exc)
            return None

    async def close(self) -> None:
        for client in self._clients.values():
            await client.close()
        self._clients.clear()


# Global singleton
token_counter = TokenCounter()
