"""Gemini API service provider."""

import json
import logging
import os
from typing import Any, AsyncIterator, Optional

from core.types import (
    BaseApiServiceClient,
    Message,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    StreamingHandler,
    Tool,
    LLMResponse,
)

logger = logging.getLogger(__name__)


class GeminiApiService(BaseApiServiceClient, StreamingHandler):
    """Google Gemini API service with streaming support."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
    ):
        super().__init__(
            provider_id=ProviderType.GEMINI,
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
    
    def _default_base_url(self) -> str:
        return "https://generativelanguage.googleapis.com"
    
    async def get_models(self) -> list[ModelMetadata]:
        """Fetch available Gemini models from API."""
        # TODO: Call Google models endpoint
        return []
    
    async def call_llm(
        self,
        model_id: str,
        messages: list[Message],
        tools: Optional[list[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk] | LLMResponse:
        """Call Gemini with proprietary API format."""
        formatted_messages = self._format_messages(messages)
        
        call_body = {
            "contents": formatted_messages,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens or 4096,
            },
        }
        
        if system_prompt:
            call_body["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        
        if tools:
            call_body["tools"] = self._format_tools(tools)
        
        if streaming:
            return self._stream_response(model_id, call_body)
        else:
            return await self._buffered_response(model_id, call_body)
    
    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
        """Parse Gemini stream chunk (JSON per line)."""
        if not line:
            return None
        
        try:
            data = json.loads(line)
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    text = parts[0].get("text", "")
                    if text:
                        return StreamChunk(
                            type="content_block_delta",
                            content=text,
                        )
            
            if data.get("usageMetadata"):
                return StreamChunk(type="message_stop")
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        
        return None
    
    async def _stream_response(
        self,
        model_id: str,
        call_body: dict[str, Any],
    ) -> AsyncIterator[StreamChunk]:
        """Stream response."""
        url = f"{self.base_url}/v1beta/models/{model_id}:streamGenerateContent"
        params = {"key": self.api_key}
        headers = {"Content-Type": "application/json"}
        
        try:
            async with self.session.post(
                url,
                json=call_body,
                headers=headers,
                params=params,
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
        model_id: str,
        call_body: dict[str, Any],
    ) -> LLMResponse:
        """Buffer response."""
        url = f"{self.base_url}/v1beta/models/{model_id}:generateContent"
        params = {"key": self.api_key}
        headers = {"Content-Type": "application/json"}
        
        async with self.session.post(
            url,
            json=call_body,
            headers=headers,
            params=params,
        ) as resp:
            data = await resp.json()
            text = ""
            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                for part in parts:
                    if "text" in part:
                        text += part["text"]
            
            return LLMResponse(
                text=text,
                stop_reason="stop",
                usage=data.get("usageMetadata", {}),
            )
    
    @staticmethod
    def _format_messages(messages: list[Message]) -> list[dict[str, Any]]:
        """Format messages for Gemini."""
        formatted = []
        for msg in messages:
            if msg.role != MessageRole.SYSTEM:
                role = "user" if msg.role == MessageRole.USER else "model"
                formatted.append({"role": role, "parts": [{"text": msg.content}]})
        return formatted
    
    @staticmethod
    def _format_tools(tools: list[Tool]) -> dict[str, Any]:
        """Format tools for Gemini."""
        return {
            "functionDeclarations": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                }
                for tool in tools
            ]
        }
