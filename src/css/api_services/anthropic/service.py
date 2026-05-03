"""Anthropic API service provider."""

import logging
import os
from typing import Any, AsyncIterator, Optional, List

from css.core.types import (
    BaseApiServiceClient,
    StreamingHandler,
    ProviderType,
    ModelMetadata,
    BaseMessage,
    Tool,
    StreamChunk,
    LLMResponse,
    MessageRole
)

logger = logging.getLogger(__name__)


class AnthropicApiService(BaseApiServiceClient, StreamingHandler):
    """Anthropic API service with streaming support."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
    ):
        super().__init__(
            provider_id=ProviderType.ANTHROPIC,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
    
    def _default_base_url(self) -> str:
        return "https://api.anthropic.com/v1"
    
    async def get_models(self) -> List[ModelMetadata]:
        """Fetch available Anthropic models from API."""
        # TODO: Call Anthropic API endpoint (if available) or use models endpoint
        # For now: placeholder that will be populated at integration test time
        return []
    
    async def call_llm(
        self,
        model_id: str,
        messages: List[BaseMessage],
        tools: Optional[List[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk] | LLMResponse:
        """Call Anthropic with streaming support."""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")
        
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
    
    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
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
