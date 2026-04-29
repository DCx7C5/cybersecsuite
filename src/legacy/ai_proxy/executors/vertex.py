"""
Google Vertex AI executor — AnthropicVertex-backed executor.

Requires: pip install anthropic[vertex]
Env vars: VERTEX_PROJECT_ID, VERTEX_REGION (default: us-east5)
          GOOGLE_APPLICATION_CREDENTIALS (service account JSON path)

Register as a provider with api_format=ApiFormat.VERTEX.
"""


import json
import logging
import os
import time
from typing import Any, AsyncIterator

from ai_proxy.executors.base import BaseExecutor
from core.types import ExecutorResult
from core.registries.providers import ProviderConfig

logger = logging.getLogger("ai_proxy.executor.vertex")


class VertexSdkExecutor(BaseExecutor):
    """
    Anthropic executor backed by AnthropicVertex.

    Handles Google Cloud service account auth automatically.
    """

    def __init__(self, provider: ProviderConfig) -> None:
        super().__init__(provider)
        self._sdk = None

    def _get_sdk(self):
        if self._sdk is None:
            try:
                from anthropic import AnthropicVertex  # type: ignore[attr-defined]
            except ImportError as exc:
                raise ImportError(
                    "anthropic[vertex] is required for Vertex executor. "
                    "Run: pip install 'anthropic[vertex]'"
                ) from exc

            project_id = (
                self.provider.extra.get("vertex_project_id")
                or os.getenv("VERTEX_PROJECT_ID", "")
            )
            region = (
                self.provider.extra.get("vertex_region")
                or os.getenv("VERTEX_REGION", "us-east5")
            )
            self._sdk = AnthropicVertex(
                project_id=project_id,
                region=region,
            )
        return self._sdk

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        return f"vertex/{model}"

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
                status_code=502, error=f"Vertex connection error: {exc}",
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
