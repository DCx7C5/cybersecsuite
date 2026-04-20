"""
AWS Bedrock executor — AnthropicBedrock-backed executor.

Requires: pip install anthropic[bedrock]
Env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION (or BEDROCK_REGION)

Register as a provider with api_format=ApiFormat.BEDROCK.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, AsyncIterator

from ai_proxy.executors.base import BaseExecutor, ExecutorResult
from ai_proxy.providers.registry import ProviderConfig

logger = logging.getLogger("ai_proxy.executor.bedrock")


class BedrockSdkExecutor(BaseExecutor):
    """
    Anthropic executor backed by AnthropicBedrock.

    Handles AWS SigV4 auth automatically via boto3 credentials chain.
    """

    def __init__(self, provider: ProviderConfig) -> None:
        super().__init__(provider)
        self._sdk = None

    def _get_sdk(self):
        if self._sdk is None:
            try:
                from anthropic import AnthropicBedrock  # type: ignore[attr-defined]
            except ImportError as exc:
                raise ImportError(
                    "anthropic[bedrock] is required for Bedrock executor. "
                    "Run: pip install 'anthropic[bedrock]'"
                ) from exc

            region = (
                self.provider.extra.get("aws_region")
                or os.getenv("BEDROCK_REGION")
                or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            )
            kwargs: dict[str, Any] = {
                "aws_region": region,
                "max_retries": self.provider.max_retries,
            }
            # Allow explicit key override (env fallback handled by SDK)
            if self.provider.extra.get("aws_access_key_id"):
                kwargs["aws_access_key"] = self.provider.extra["aws_access_key_id"]
            if self.provider.extra.get("aws_secret_access_key"):
                kwargs["aws_secret_key"] = self.provider.extra["aws_secret_access_key"]

            self._sdk = AnthropicBedrock(**kwargs)
        return self._sdk

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        return f"bedrock/{model}"

    async def execute(
        self,
        body: dict[str, Any],
        model: str,
        stream: bool = False,
        endpoint: str = "chat/completions",
    ) -> ExecutorResult:
        import anthropic

        start = time.monotonic()
        try:
            sdk = self._get_sdk()
        except ImportError as exc:
            return ExecutorResult(
                status_code=501,
                error=str(exc),
                provider_id=self.provider.id,
                model_id=model,
            )

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": body.get("messages", []),
            "max_tokens": body.get("max_tokens") or 4096,
        }
        for opt in ("system", "temperature", "top_p", "tools"):
            if body.get(opt) is not None:
                kwargs[opt] = body[opt]

        try:
            if stream:
                sdk_stream = await sdk.messages.create(**kwargs, stream=True)
                latency = (time.monotonic() - start) * 1000

                async def _sse() -> AsyncIterator[bytes]:
                    async with sdk_stream as s:
                        async for event in s:
                            data = json.dumps(event.model_dump(exclude_unset=True), separators=(",", ":"))
                            yield f"event: {event.type}\ndata: {data}\n\n".encode()
                    yield b"data: [DONE]\n\n"

                return ExecutorResult(
                    status_code=200,
                    stream=_sse(),
                    latency_ms=latency,
                    provider_id=self.provider.id,
                    model_id=model,
                )

            message = await sdk.messages.create(**kwargs)
            latency = (time.monotonic() - start) * 1000
            return ExecutorResult(
                status_code=200,
                body=message.model_dump(),
                latency_ms=latency,
                provider_id=self.provider.id,
                model_id=model,
                request_id=getattr(message, "_request_id", None),
            )

        except anthropic.APIConnectionError as exc:
            return ExecutorResult(
                status_code=502, error=f"Bedrock connection error: {exc}",
                latency_ms=(time.monotonic() - start) * 1000,
                provider_id=self.provider.id, model_id=model,
            )
        except anthropic.APIStatusError as exc:
            return ExecutorResult(
                status_code=exc.status_code, error=exc.message,
                latency_ms=(time.monotonic() - start) * 1000,
                provider_id=self.provider.id, model_id=model,
                request_id=exc.request_id,
            )

    async def close(self) -> None:
        await super().close()
        if self._sdk is not None:
            try:
                await self._sdk.close()
            except Exception:
                pass
            self._sdk = None
