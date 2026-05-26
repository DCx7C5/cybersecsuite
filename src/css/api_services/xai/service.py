"""xAI (Grok) API service provider."""

from css.core.logger import getLogger
import json
import os
from typing import override,  Any
from collections.abc import AsyncIterator
from pathlib import Path
import msgspec

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
from css.core.exceptions import LLMApiServiceError
from css.core.types.base_client import BaseApiServiceClient
from css.core.config import ProviderDefaults
from css.core.settings import config as settings_config
from css.core.types.providers import decode_provider_spec_file

logger = getLogger(__name__)


class XAINativeSDKFallbackRequiredError(LLMApiServiceError):
    """Raised when native xAI SDK is enabled but compatibility fallback is disabled."""


class xAIApiService(BaseApiServiceClient, StreamingHandler):
    """xAI (Grok) API service with streaming support."""
    
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = ProviderDefaults.TIMEOUT_SECONDS,
        max_retries: int = ProviderDefaults.MAX_RETRIES,
        use_native_sdk: bool | None = None,
        allow_openai_compat_fallback: bool | None = None,
    ):
        self._use_native_sdk = (
            use_native_sdk if use_native_sdk is not None else settings_config.XAI_SDK_ENABLED
        )
        self._allow_openai_compat_fallback = (
            allow_openai_compat_fallback
            if allow_openai_compat_fallback is not None
            else settings_config.XAI_SDK_FALLBACK_OPENAI_COMPAT
        )
        super().__init__(
            provider_id=ProviderType.XAI,
            api_key=api_key or os.getenv("XAI_API_KEY"),
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        if self._use_native_sdk and self._allow_openai_compat_fallback:
            logger.info(
                "xAI native SDK flag enabled; OpenAI-compatible fallback remains active until native bridge is complete"
            )
    
    @override
    def _default_base_url(self) -> str:
        spec_file = Path(__file__).with_name("spec.yaml")
        try:
            spec = decode_provider_spec_file(spec_file)
            return spec.base_url
        except FileNotFoundError as error:
            raise LLMApiServiceError(
                message="Missing xAI provider spec.yaml",
                provider_name="xai",
                context={"spec_path": str(spec_file)},
            ) from error
        except OSError as error:
            raise LLMApiServiceError(
                message="Failed reading xAI provider spec.yaml",
                provider_name="xai",
                context={"spec_path": str(spec_file)},
            ) from error
        except RuntimeError as error:
            raise LLMApiServiceError(
                message="xAI provider spec decode requires msgspec YAML support",
                provider_name="xai",
                context={"spec_path": str(spec_file)},
            ) from error
        except msgspec.ValidationError as error:
            raise LLMApiServiceError(
                message="Invalid xAI provider spec.yaml schema",
                provider_name="xai",
                context={"spec_path": str(spec_file)},
            ) from error
    
    @override
    async def get_models(self) -> list[ModelMetadata]:
        """Get available models for this provider."""
        # stub: fetch from xAI /models endpoint (see tracker 'provider-types-dynamic')
        ...

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
        """Call xAI with OpenAI-compatible streaming."""
        if self._use_native_sdk and not self._allow_openai_compat_fallback:
            raise XAINativeSDKFallbackRequiredError(
                message=(
                    "XAI_SDK_ENABLED is true, but native xAI SDK call flow is not yet wired "
                    "and compatibility fallback is disabled. Set XAI_SDK_FALLBACK_OPENAI_COMPAT=true."
                ),
                provider_name="xai",
            )
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
            return self._buffered_call_to_stream(self._buffered_response(call_body))
    
    @override
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
