"""Anthropic API service provider."""

from css.core.logger import getLogger
import os
from typing import override,  Any
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic
from css.core.types import (
    BaseMessage,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    Tool,
    LLMResponse,
)
from css.core.types.base_client import BaseApiServiceClient, BaseStreamingHandler
from css.core.config import ProviderDefaults


logger = getLogger(__name__)


class AnthropicApiService(BaseApiServiceClient, BaseStreamingHandler):
    """Anthropic API service with streaming support."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = ProviderDefaults.TIMEOUT_SECONDS,
        max_retries: int = ProviderDefaults.MAX_RETRIES,
    ):
        super().__init__(
            provider_id=ProviderType.ANTHROPIC,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    @override
    def _default_base_url(self) -> str:
        return "https://api.anthropic.com/v1"

    @override
    async def get_models(self) -> list[ModelMetadata]:
        """Get available models for this provider."""
        return [
            ModelMetadata(
                id="claude-3-5-sonnet-20241022",
                provider=ProviderType.ANTHROPIC,
                display_name="Claude 3.5 Sonnet",
                context_window=200000,
                max_output_tokens=16384,
                streaming=True,
                vision=True,
                tool_use=True,
                prompt_caching=True,
                structured_output=True,
                input_cost_per_mtok=3.0,
                output_cost_per_mtok=15.0,
            ),
            ModelMetadata(
                id="claude-3-opus-20250219",
                provider=ProviderType.ANTHROPIC,
                display_name="Claude 3 Opus",
                context_window=200000,
                max_output_tokens=4096,
                streaming=True,
                vision=True,
                tool_use=True,
                prompt_caching=True,
                structured_output=True,
                extended_thinking=True,
                input_cost_per_mtok=15.0,
                output_cost_per_mtok=75.0,
            ),
            ModelMetadata(
                id="claude-3-sonnet-20240229",
                provider=ProviderType.ANTHROPIC,
                display_name="Claude 3 Sonnet",
                context_window=200000,
                max_output_tokens=4096,
                streaming=True,
                vision=True,
                tool_use=True,
                prompt_caching=True,
                structured_output=True,
                input_cost_per_mtok=3.0,
                output_cost_per_mtok=15.0,
            ),
            ModelMetadata(
                id="claude-3-haiku-20240307",
                provider=ProviderType.ANTHROPIC,
                display_name="Claude 3 Haiku",
                context_window=200000,
                max_output_tokens=4096,
                streaming=True,
                vision=True,
                tool_use=True,
                prompt_caching=True,
                structured_output=True,
                input_cost_per_mtok=0.25,
                output_cost_per_mtok=1.25,
            ),
        ]

    @override
    async def call_llm(
        self,
        model_id: str,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """Call Anthropic with streaming support."""
        client = AsyncAnthropic(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout_seconds,
        )

        formatted_messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
            if msg.role != MessageRole.SYSTEM
        ]

        call_body = {
            "model": model_id,
            "messages": formatted_messages,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
        }

        if system_prompt:
            call_body["system"] = system_prompt

        if tools:
            call_body["tools"] = self._format_tools(tools)

        if streaming:
            return self._stream_response(client, call_body)
        else:
            return self._buffered_call_to_stream(self._buffered_response(client, call_body))

    async def _stream_response(
        self,
        client: Any,
        call_body: dict[str, Any],
    ) -> AsyncIterator[StreamChunk]:
        """Stream response via Anthropic SDK."""
        async with await client.messages.stream(**call_body) as stream:
            async for event in stream:
                if event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield StreamChunk(
                            type="content_block_delta",
                            content=event.delta.text,
                        )
                elif event.type == "message_stop":
                    yield StreamChunk(
                        type="message_stop",
                        stop_reason="stop",
                    )

    async def _buffered_response(
        self,
        client: Any,
        call_body: dict[str, Any],
    ) -> LLMResponse:
        """Buffer Anthropic response and normalize to LLMResponse."""
        response = await client.messages.create(**call_body)
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text

        return LLMResponse(
            text=text,
            stop_reason=response.stop_reason or "stop",
            usage={"usage": response.usage.model_dump() if hasattr(response, "usage") else {}},
        )

    @override
    async def _parse_stream_chunk(self, line: str) -> StreamChunk | None:
        """Not used for Anthropic SDK (uses event stream)."""
        return None

    @staticmethod
    def _format_tools(tools: list[Tool]) -> list[dict[str, Any]]:
        """Format tools for Anthropic."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]
