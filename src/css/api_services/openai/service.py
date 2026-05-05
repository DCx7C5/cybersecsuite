"""OpenAI API service provider."""

import json
import logging
import os
from typing import Any, AsyncIterator, Optional

import aiohttp

from css.core.types import (
    BaseMessage,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    StreamingHandler,
    Tool,
    LLMResponse,
)
from css.core.types.providers import APIProviderBase
from css.core.config import ProviderDefaults

logger = logging.getLogger(__name__)


class OpenAIApiService(APIProviderBase, StreamingHandler):
    """OpenAI API service with streaming support."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = ProviderDefaults.TIMEOUT_SECONDS,
        max_retries: int = ProviderDefaults.MAX_RETRIES,
    ):
        super().__init__(
            provider_id=ProviderType.OPENAI,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or self._default_base_url(),
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self._session: Optional[aiohttp.AsyncClient] = None

    def _default_base_url(self) -> str:
        return "https://api.openai.com/v1"

    async def get_models(self) -> list[ModelMetadata]:
        """Get available models for this provider."""
        return [
            ModelMetadata(
                id="gpt-4o",
                provider=ProviderType.OPENAI,
                display_name="GPT-4o",
                context_window=128000,
                max_output_tokens=4096,
                streaming=True,
                vision=True,
                tool_use=True,
                batch_api=True,
                structured_output=True,
                files_api=True,
                input_cost_per_mtok=5.0,
                output_cost_per_mtok=15.0,
            ),
            ModelMetadata(
                id="gpt-4-turbo",
                provider=ProviderType.OPENAI,
                display_name="GPT-4 Turbo",
                context_window=128000,
                max_output_tokens=4096,
                streaming=True,
                vision=True,
                tool_use=True,
                batch_api=True,
                structured_output=True,
                files_api=True,
                input_cost_per_mtok=10.0,
                output_cost_per_mtok=30.0,
            ),
            ModelMetadata(
                id="gpt-3.5-turbo",
                provider=ProviderType.OPENAI,
                display_name="GPT-3.5 Turbo",
                context_window=16384,
                max_output_tokens=4096,
                streaming=True,
                tool_use=True,
                batch_api=True,
                structured_output=True,
                files_api=True,
                input_cost_per_mtok=0.5,
                output_cost_per_mtok=1.5,
            ),
        ]

    async def call_llm(
        self,
        model_id: str,
        messages: list[BaseMessage],
        tools: Optional[list[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk] | LLMResponse:
        """Call OpenAI with streaming support."""
        formatted_messages = self._format_messages(messages, system_prompt)

        call_body = {
            "model": model_id,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 4096,
        }

        if tools:
            call_body["tools"] = self._format_tools(tools)

        if streaming:
            return self._stream_response(call_body)
        else:
            return await self._buffered_response(call_body)

    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
        """Parse SSE line."""
        if not line.startswith("data: "):
            return None

        data_str = line[6:]
        if data_str == "[DONE]":
            return StreamChunk(type="message_stop")

        try:
            data = json.loads(data_str)
            choice = data.get("choices", [{}])[0]
            delta = choice.get("delta", {})

            if "content" in delta:
                return StreamChunk(
                    type="content_block_delta",
                    content=delta["content"],
                )

            if choice.get("finish_reason"):
                return StreamChunk(
                    type="message_stop",
                    stop_reason=choice["finish_reason"],
                )
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        return None

    async def _stream_response(
        self, call_body: dict[str, Any],
    ) -> AsyncIterator[StreamChunk]:
        """Stream response."""
        call_body["stream"] = True
        headers = self._ensure_auth_header(
            {"Content-Type": "application/json"},
            self.api_key or "",
            "Bearer",
        )

        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=call_body,
                headers=headers,
            ) as resp:
                if resp.status != 200:
                    yield StreamChunk(type="error", metadata={"error": f"HTTP {resp.status}"})
                    return

                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if not decoded:
                        continue

                    chunk = await self._parse_stream_chunk(decoded)
                    if chunk:
                        yield chunk
        except Exception as e:
            yield StreamChunk(type="error", metadata={"error": str(e)})

    async def _buffered_response(
        self, call_body: dict[str, Any],
    ) -> LLMResponse:
        """Buffer response."""
        call_body["stream"] = False
        headers = self._ensure_auth_header(
            {"Content-Type": "application/json"},
            self.api_key or "",
            "Bearer",
        )

        async with self.session.post(
            f"{self.base_url}/chat/completions",
            json=call_body,
            headers=headers,
        ) as resp:
            data = await resp.json()
            text = ""
            for choice in data.get("choices", []):
                if choice.get("message", {}).get("content"):
                    text += choice["message"]["content"]

            return LLMResponse(
                text=text,
                stop_reason=data.get("choices", [{}])[0].get("finish_reason", "stop"),
                usage=data.get("usage", {}),
            )

    @staticmethod
    def _format_messages(
        messages: list[BaseMessage],
        system_prompt: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """Format messages."""
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
                formatted.append({"role": msg.role.value, "content": msg.content})
        return formatted

    @staticmethod
    def _format_tools(tools: list[Tool]) -> list[dict[str, Any]]:
        """Format tools."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in tools
        ]

    @property
    def session(self) -> aiohttp.AsyncClient:
        """Get or create httpx session."""
        if self._session is None or self._session.is_closed:
            self._session = aiohttp.AsyncClient(timeout=aiohttp.TimeoutConfig(timeout=self.timeout_seconds))
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.is_closed:
            await self._session.aclose()
