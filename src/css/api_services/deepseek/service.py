"""DeepSeek API service provider."""

from css.core.logger import getLogger
import json
import os
from typing import Any
from collections.abc import AsyncIterator

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
from css.core.types.base_client import BaseApiServiceClient
from css.core.config import ProviderDefaults

logger = getLogger(__name__)


class DeepSeekApiService(BaseApiServiceClient, StreamingHandler):
    """DeepSeek API service with streaming support."""
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = ProviderDefaults.TIMEOUT_SECONDS,
        max_retries: int = ProviderDefaults.MAX_RETRIES,
    ):
        super().__init__(
            provider_id=ProviderType.DEEPSEEK,
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
    
    def _default_base_url(self) -> str:
        return "https://api.deepseek.com/v1"
    
    async def get_models(self) -> list[ModelMetadata]:
        """Get available models for this provider."""
        return [
            ModelMetadata(
                id="deepseek-chat",
                provider=ProviderType.DEEPSEEK,
                display_name="DeepSeek Chat",
                context_window=4096,
                max_output_tokens=4096,
                streaming=True,
                vision=True,
                tool_use=True,
                structured_output=True,
            ),
            ModelMetadata(
                id="deepseek-coder",
                provider=ProviderType.DEEPSEEK,
                display_name="DeepSeek Coder",
                context_window=4096,
                max_output_tokens=4096,
                streaming=True,
                tool_use=True,
                structured_output=True,
            ),
        ]
    
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
    ) -> AsyncIterator[StreamChunk] | LLMResponse:
        """Call DeepSeek with OpenAI-compatible streaming."""
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
    
    async def _parse_stream_chunk(self, line: str) -> StreamChunk | None:
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

            # DeepSeek-R1 non-standard field: reasoning chain-of-thought
            reasoning = delta.get("reasoning_content")
            if reasoning:
                return StreamChunk(
                    type="content_block_delta",
                    content=reasoning,
                    metadata={"content_type": "reasoning"},
                )

            if "content" in delta and delta["content"]:
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
        self,
        call_body: dict[str, Any],
    ) -> AsyncIterator[StreamChunk]:
        """Stream response."""
        call_body["stream"] = True
        headers = self._ensure_auth_header(
            {"Content-Type": "application/json"},
            self.api_key or "",
            "Authorization",
            "Bearer",
        )
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=call_body,
                headers=headers,
            ) as resp:
                if resp.status != 200:
                    yield StreamChunk(
                        type="error",
                        metadata={"error": f"HTTP {resp.status}"},
                    )
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
        self,
        call_body: dict[str, Any],
    ) -> LLMResponse:
        """Buffer response."""
        call_body["stream"] = False
        headers = self._ensure_auth_header(
            {"Content-Type": "application/json"},
            self.api_key or "",
            "Authorization",
            "Bearer",
        )
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            json=call_body,
            headers=headers,
        ) as resp:
            data = await resp.json()
            text = ""
            reasoning = ""
            for choice in data.get("choices", []):
                msg = choice.get("message", {})
                if msg.get("content"):
                    text += msg["content"]
                # DeepSeek-R1 non-standard reasoning chain-of-thought
                if msg.get("reasoning_content"):
                    reasoning += msg["reasoning_content"]

            metadata: dict[str, Any] = {}
            if reasoning:
                metadata["reasoning"] = reasoning

            return LLMResponse(
                text=text,
                stop_reason=data["choices"][0].get("finish_reason", "stop") if data.get("choices") else "stop",
                usage={**data.get("usage", {}), **({"reasoning": reasoning} if reasoning else {})},
            )
    
    @staticmethod
    def _format_messages(
        messages: list[BaseMessage],
        system_prompt: str | None = None,
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
