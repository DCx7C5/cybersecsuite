"""
Microsoft Azure AI Foundry executor — AnthropicFoundry (no extra deps needed).

Wraps AsyncAnthropicFoundry to route Claude requests through Azure AI Foundry.

Required env vars:
  AZURE_API_KEY     — Azure API key or leave unset to use azure_ad_token_provider
  AZURE_ENDPOINT    — Azure AI Foundry endpoint URL (set as provider base_url)
  AZURE_RESOURCE    — Azure resource name (optional, for resource-scoped routing)
"""
from __future__ import annotations

import logging
import os
from typing import Any

import anthropic

from ai_proxy.executors.anthropic_sdk import AnthropicSdkExecutor

logger = logging.getLogger("ai_proxy.executor.foundry")


class FoundrySdkExecutor(AnthropicSdkExecutor):
    """
    Executor backed by AsyncAnthropicFoundry for Azure AI Foundry deployments.

    Inherits streaming + completion logic from AnthropicSdkExecutor;
    only overrides the SDK client construction to use the Foundry client.
    """

    def _get_sdk(self) -> anthropic.AsyncAnthropicFoundry:  # type: ignore[override]
        if self._sdk is None:
            api_key = self.provider.get_api_key() or os.getenv("AZURE_API_KEY") or "none"
            base_url = self.provider.base_url or os.getenv("AZURE_ENDPOINT")
            resource = os.getenv("AZURE_RESOURCE")

            kwargs: dict[str, Any] = {
                "api_key": api_key,
                "max_retries": self.provider.max_retries,
                "timeout": anthropic.Timeout(
                    total=float(self.provider.timeout_seconds),
                    connect=10.0,
                    read=float(self.provider.timeout_seconds),
                    write=30.0,
                ),
            }
            if base_url:
                kwargs["base_url"] = base_url
            if resource:
                kwargs["resource"] = resource

            self._sdk = anthropic.AsyncAnthropicFoundry(**kwargs)
            logger.debug("Using AsyncAnthropicFoundry executor (Azure AI Foundry)")
        return self._sdk  # type: ignore[return-value]

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        base = self.provider.base_url or os.getenv("AZURE_ENDPOINT", "")
        return f"{base}/messages"
