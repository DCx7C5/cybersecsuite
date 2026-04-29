"""
Anthropic SDK Executor — wraps AsyncAnthropic for typed errors, retries, and request ID capture.

Replaces the raw-httpx AnthropicExecutor for ApiFormat.ANTHROPIC providers.

Set CCS_AIOHTTP=1 to use the aiohttp backend for higher-concurrency workloads.
Requires: pip install anthropic[aiohttp]
"""


import json
import logging
import os
import time
from typing import Any, AsyncIterator

import anthropic

from ai_proxy.executors.base import BaseExecutor, ExecutorResult
from core.registries.providers import ProviderConfig

logger = logging.getLogger("ai_proxy.executor.anthropic_sdk")

# Anthropic typed error → HTTP status code mapping
_STATUS_MAP: dict[type[anthropic.APIError], int] = {
    anthropic.BadRequestError: 400,
    anthropic.AuthenticationError: 401,
    anthropic.PermissionDeniedError: 403,
    anthropic.NotFoundError: 404,
    anthropic.UnprocessableEntityError: 422,
    anthropic.RateLimitError: 429,
    anthropic.InternalServerError: 500,
    anthropic.APITimeoutError: 504,
}


class AnthropicSdkExecutor(BaseExecutor):
    """
    Anthropic executor backed by the official AsyncAnthropic SDK.

    Gains over raw httpx:
    - Typed error classes with status codes
    - Built-in exponential-backoff retry (SDK-level)
    - request_id capture via with_raw_response for tracing
    - Proper streaming via messages.stream() context manager
    - Thinking (extended thinking) parameter support
    """

    def __init__(self, provider: ProviderConfig) -> None:
        super().__init__(provider)
        self._sdk: anthropic.AsyncAnthropic | None = None

    def _get_sdk(self) -> anthropic.AsyncAnthropic:
        if self._sdk is None:
            api_key = self.provider.get_api_key() or "none"
            kwargs: dict[str, Any] = {
                "api_key": api_key,
                "base_url": self.provider.base_url,
                "max_retries": self.provider.max_retries,
                "timeout": anthropic.Timeout(
                    total=float(self.provider.timeout_seconds),
                    connect=10.0,
                    read=float(self.provider.timeout_seconds),
                    write=30.0,
                ),
            }
            # Optional aiohttp backend for high-concurrency asgi deployments
            if os.getenv("CCS_AIOHTTP"):
                try:
                    from anthropic import DefaultAioHttpClient  # type: ignore[attr-defined]
                    kwargs["http_client"] = DefaultAioHttpClient()
                    logger.debug("Using aiohttp backend for Anthropic executor")
                except ImportError:
                    logger.warning(
                        "CCS_AIOHTTP=1 but anthropic[aiohttp] is not installed; "
                        "falling back to httpx. Run: pip install 'anthropic[aiohttp]'"
                    )
            self._sdk = anthropic.AsyncAnthropic(**kwargs)
        return self._sdk

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        return f"{self.provider.base_url}/messages"

    async def execute(
        self,
        body: dict[str, Any],
        model: str,
        stream: bool = False,
        endpoint: str = "chat/completions",
    ) -> ExecutorResult:
        """Execute against Anthropic using the native SDK."""
        start = time.monotonic()
        sdk = self._get_sdk()
        kwargs = _extract_kwargs(body, model)

        try:
            if stream:
                return await self._stream(sdk, kwargs, model, start)
            return await self._complete(sdk, kwargs, model, start)

        except anthropic.APITimeoutError as exc:
            return ExecutorResult(
                status_code=504,
                error=f"Request timed out: {exc}",
                latency_ms=(time.monotonic() - start) * 1000,
                provider_id=self.provider.id,
                model_id=model,
            )
        except anthropic.APIConnectionError as exc:
            return ExecutorResult(
                status_code=502,
                error=f"Connection error: {exc}",
                latency_ms=(time.monotonic() - start) * 1000,
                provider_id=self.provider.id,
                model_id=model,
            )
        except anthropic.APIStatusError as exc:
            status = _STATUS_MAP.get(type(exc), exc.status_code)
            return ExecutorResult(
                status_code=status,
                error=exc.message,
                latency_ms=(time.monotonic() - start) * 1000,
                provider_id=self.provider.id,
                model_id=model,
                request_id=exc.request_id,
            )
        except anthropic.APIError as exc:
            return ExecutorResult(
                status_code=500,
                error=str(exc),
                latency_ms=(time.monotonic() - start) * 1000,
                provider_id=self.provider.id,
                model_id=model,
            )

    async def _complete(
        self,
        sdk: anthropic.AsyncAnthropic,
        kwargs: dict[str, Any],
        model: str,
        start: float,
    ) -> ExecutorResult:
        # Use with_raw_response for reliable x-request-id capture from headers
        raw = await sdk.messages.with_raw_response.create(**kwargs)
        message = raw.parse()
        latency = (time.monotonic() - start) * 1000
        request_id: str | None = raw.headers.get("x-request-id")
        return ExecutorResult(
            status_code=200,
            body=message.model_dump(),
            latency_ms=latency,
            provider_id=self.provider.id,
            model_id=model,
            request_id=request_id,
        )

    async def _stream(
        self,
        sdk: anthropic.AsyncAnthropic,
        kwargs: dict[str, Any],
        model: str,
        start: float,
    ) -> ExecutorResult:
        # Use messages.stream() context manager for structured event access
        # and access to get_final_message() / request_id helpers
        latency = (time.monotonic() - start) * 1000

        async def _sse_bytes() -> AsyncIterator[bytes]:
            async with sdk.messages.stream(**kwargs) as s:
                async for event in s:
                    event_type = event.type
                    data = json.dumps(
                        event.model_dump(exclude_unset=True),
                        separators=(",", ":"),
                    )
                    yield f"event: {event_type}\ndata: {data}\n\n".encode()
            yield b"data: [DONE]\n\n"

        return ExecutorResult(
            status_code=200,
            stream=_sse_bytes(),
            latency_ms=latency,
            provider_id=self.provider.id,
            model_id=model,
        )

    async def close(self) -> None:
        await super().close()
        if self._sdk is not None:
            await self._sdk.close()
            self._sdk = None


# ── helpers ──────────────────────────────────────────────────────────────────

def _extract_kwargs(body: dict[str, Any], model: str) -> dict[str, Any]:
    """Pull Anthropic-format fields from translated request body."""
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": body.get("messages", []),
        "max_tokens": body.get("max_tokens") or 4096,
    }
    for opt in ("system", "temperature", "top_p", "tools", "stop_sequences", "tool_choice"):
        if body.get(opt) is not None:
            kwargs[opt] = body[opt]

    # Extended thinking support: pass through if caller sends thinking config
    # Expected body format: {"thinking": {"type": "enabled", "budget_tokens": 8000}}
    if body.get("thinking") is not None:
        kwargs["thinking"] = body["thinking"]

    # betas list for beta features (e.g. interleaved-thinking-2025-05-14)
    if body.get("betas") is not None:
        kwargs["betas"] = body["betas"]

    return kwargs
