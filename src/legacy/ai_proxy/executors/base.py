"""
Executor layer — dispatch requests to upstream LLM providers.

This module now re-exports core types from core.types for consistency.
The BaseExecutor and get_executor implementations remain here.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

import httpx

from core.registries.providers import ProviderConfig, ApiFormat, AuthType
from core.types import ExecutorResult

logger = logging.getLogger("ai_proxy.executor")

# Retry config
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0
RETRY_MAX_DELAY = 30.0
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class BaseExecutor(ABC):
    """Abstract base for provider executors."""

    def __init__(self, provider: ProviderConfig):
        self.provider = provider
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.provider.timeout_seconds, connect=10.0),
                follow_redirects=True,
                http2=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        ...

    def build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream, application/json",
        }
        api_key = self.provider.get_api_key()
        if api_key:
            headers[self.provider.auth_header] = f"{self.provider.auth_prefix}{api_key}"
        return headers

    def transform_request(self, body: dict[str, Any]) -> dict[str, Any]:
        """Hook for provider-specific request transforms."""
        return body

    async def execute(
        self,
        body: dict[str, Any],
        model: str,
        stream: bool = False,
        endpoint: str = "chat/completions",
    ) -> ExecutorResult:
        """Execute request with retry logic."""
        url = self.build_url(model, endpoint)
        headers = self.build_headers()
        transformed = self.transform_request(body)
        last_error: str | None = None

        for attempt in range(self.provider.max_retries):
            start = time.monotonic()
            try:
                client = await self._get_client()

                if stream:
                    return await self._execute_stream(client, url, headers, transformed, model, start)
                else:
                    return await self._execute_json(client, url, headers, transformed, model, start)

            except httpx.HTTPStatusError as exc:
                latency = (time.monotonic() - start) * 1000
                status = exc.response.status_code
                last_error = f"HTTP {status}: {exc.response.text[:500]}"

                if status in RETRYABLE_STATUS_CODES and attempt < self.provider.max_retries - 1:
                    retry_after = exc.response.headers.get("retry-after")
                    delay = float(retry_after) if retry_after else min(
                        RETRY_BASE_DELAY * (2 ** attempt), RETRY_MAX_DELAY
                    )
                    logger.warning(
                        "Retryable %d from %s (attempt %d/%d), waiting %.1fs",
                        status, self.provider.id, attempt + 1, self.provider.max_retries, delay,
                    )
                    await asyncio.sleep(delay)
                    continue

                return ExecutorResult(
                    status_code=status, error=last_error, latency_ms=latency,
                    provider_id=self.provider.id, model_id=model,
                )

            except (httpx.ConnectError, httpx.ReadTimeout, httpx.WriteTimeout) as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < self.provider.max_retries - 1:
                    delay = min(RETRY_BASE_DELAY * (2 ** attempt), RETRY_MAX_DELAY)
                    logger.warning(
                        "Connection error from %s (attempt %d/%d): %s",
                        self.provider.id, attempt + 1, self.provider.max_retries, last_error,
                    )
                    await asyncio.sleep(delay)
                    continue

                return ExecutorResult(
                    status_code=502, error=last_error, latency_ms=0,
                    provider_id=self.provider.id, model_id=model,
                )

        return ExecutorResult(
            status_code=502, error=last_error or "Max retries exhausted",
            provider_id=self.provider.id, model_id=model,
        )

    async def _execute_json(
        self, client: httpx.AsyncClient, url: str, headers: dict, body: dict, model: str, start: float,
    ) -> ExecutorResult:
        resp = await client.post(url, json=body, headers=headers)
        latency = (time.monotonic() - start) * 1000
        resp.raise_for_status()
        return ExecutorResult(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            body=resp.json(),
            latency_ms=latency,
            provider_id=self.provider.id,
            model_id=model,
        )

    async def _execute_stream(
        self, client: httpx.AsyncClient, url: str, headers: dict, body: dict, model: str, start: float,
    ) -> ExecutorResult:
        req = client.build_request("POST", url, json=body, headers=headers)
        resp = await client.send(req, stream=True)
        latency = (time.monotonic() - start) * 1000

        if resp.status_code >= 400:
            error_body = await resp.aread()
            await resp.aclose()
            return ExecutorResult(
                status_code=resp.status_code,
                error=error_body.decode("utf-8", errors="replace")[:500],
                latency_ms=latency,
                provider_id=self.provider.id,
                model_id=model,
            )

        async def _stream_lines():
            try:
                async for line in resp.aiter_lines():
                    yield (line + "\n").encode("utf-8")
            finally:
                await resp.aclose()

        return ExecutorResult(
            status_code=resp.status_code,
            headers=dict(resp.headers),
            stream=_stream_lines(),
            latency_ms=latency,
            provider_id=self.provider.id,
            model_id=model,
        )


class DefaultExecutor(BaseExecutor):
    """Executor for OpenAI-compatible providers (most providers)."""

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        return f"{self.provider.base_url}/{endpoint}"


class GeminiExecutor(BaseExecutor):
    """Executor for Google Gemini REST API."""

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        api_key = self.provider.get_api_key() or ""
        return (
            f"{self.provider.base_url}/models/{model}:generateContent"
            f"?key={api_key}"
        )

    def build_headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}


class AnthropicExecutor(BaseExecutor):
    """Anthropic executor — delegates to the SDK-backed implementation."""

    def build_url(self, model: str, endpoint: str = "chat/completions") -> str:
        return f"{self.provider.base_url}/messages"

    def build_headers(self) -> dict[str, str]:
        headers = super().build_headers()
        headers["anthropic-version"] = "2023-06-01"
        return headers


def get_executor(provider: ProviderConfig) -> BaseExecutor:
    """Factory — return the correct executor for a provider."""
    if provider.auth_type == AuthType.BROWSER:
        from ai_proxy.executors.playwright import PlaywrightExecutor
        return PlaywrightExecutor(provider)
    if provider.api_format == ApiFormat.GEMINI:
        return GeminiExecutor(provider)
    if provider.api_format == ApiFormat.ANTHROPIC:
        from ai_proxy.executors.anthropic_sdk import AnthropicSdkExecutor
        return AnthropicSdkExecutor(provider)
    if provider.api_format == ApiFormat.BEDROCK:
        from ai_proxy.executors.bedrock import BedrockSdkExecutor
        return BedrockSdkExecutor(provider)
    if provider.api_format == ApiFormat.VERTEX:
        from ai_proxy.executors.vertex import VertexSdkExecutor
        return VertexSdkExecutor(provider)
    if provider.api_format == ApiFormat.FOUNDRY:
        from ai_proxy.executors.foundry import FoundrySdkExecutor
        return FoundrySdkExecutor(provider)
    return DefaultExecutor(provider)
