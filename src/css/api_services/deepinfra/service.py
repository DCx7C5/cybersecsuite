"""DeepInfra API service provider."""

import json
import logging
import os
from typing import Any, AsyncIterator, Optional

from css.core.types import (
    BaseApiServiceClient,
    BaseMessage,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    StreamingHandler,
    Tool,
    LLMResponse,
)

logger = logging.getLogger(__name__)


class DeepInfraApiService(BaseApiServiceClient, StreamingHandler):
    """DeepInfra API service with streaming support."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
    ):
        super().__init__(
            provider_id=ProviderType.DEEPINFRA,
            api_key=api_key or os.getenv("DEEPINFRA_API_KEY"),
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
    
    def _default_base_url(self) -> str:
        return "https://api.deepinfra.com/v1/openai"
    
    async def get_models(self) -> list[ModelMetadata]:
        """Fetch available DeepInfra models from API."""
        # TODO: Call DeepInfra models endpoint
        return []
    
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
        """Call DeepInfra with OpenAI-compatible streaming."""
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
            for choice in data.get("choices", []):
                if choice.get("message", {}).get("content"):
                    text += choice["message"]["content"]
            
            return LLMResponse(
                text=text,
                stop_reason=data["choices"][0].get("finish_reason", "stop") if data.get("choices") else "stop",
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
