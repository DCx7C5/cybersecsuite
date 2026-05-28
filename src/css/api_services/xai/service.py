"""xAI (Grok) API service provider."""

from css.core.logger import getLogger
import json
import os
from types import TracebackType
from typing import override, Any, Self
from collections.abc import AsyncIterator
from pathlib import Path
import msgspec
from xai_sdk import AsyncClient

from css.core.base import (
    BaseMessage,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    Tool,
    LLMResponse,
)
from css.core.exceptions import LLMApiServiceError
from css.core.base.client import BaseApiServiceClient, BaseStreamingHandler
from css.core.errors.mappers import map_provider_error
from css.core.config import ProviderDefaults
from css.core.settings import config as settings_config
from css.core.base.providers import decode_provider_spec_file

logger = getLogger(__name__)


class xAIApiService(BaseApiServiceClient, BaseStreamingHandler):
    """xAI (Grok) API service with streaming support.
    
    Supports both OpenAI-compatible fallback and native gRPC AsyncClient from xai-sdk.
    AsyncClient lifecycle is managed lazily with timeout and channel configuration.
    """
    
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
        self._async_client: AsyncClient | None = None
        self._timeout_seconds = timeout_seconds
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
    
    async def _ensure_async_client(self) -> AsyncClient:
        """Lazily initialize native xAI AsyncClient on first use."""
        if self._async_client is not None:
            return self._async_client
        
        if not self._use_native_sdk:
            raise LLMApiServiceError(
                message="Native xAI SDK is not enabled. Use OpenAI-compatible fallback instead.",
                provider_name="xai",
            )
        
        try:
            self._async_client = AsyncClient(
                api_key=self.api_key,
                timeout=self._timeout_seconds,
            )
            logger.debug(f"xAI native AsyncClient initialized with {self._timeout_seconds}s timeout")
            return self._async_client
        except Exception as error:
            # Map any initialization errors through error mapper
            mapped_error = map_provider_error(ProviderType.XAI, error)
            logger.error(f"Failed to initialize xAI AsyncClient: {mapped_error}")
            raise mapped_error
    
    async def _close_async_client(self) -> None:
        """Close and cleanup native xAI AsyncClient."""
        if self._async_client is not None:
            try:
                if hasattr(self._async_client, 'close'):
                    await self._async_client.close()
                elif hasattr(self._async_client, '__aexit__'):
                    await self._async_client.__aexit__(None, None, None)
                logger.debug("xAI native AsyncClient closed")
            except Exception as error:
                mapped_error = map_provider_error(ProviderType.XAI, error)
                logger.error(f"Error closing xAI AsyncClient: {mapped_error}")
            finally:
                self._async_client = None
    
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
        **kwargs: object,
    ) -> AsyncIterator[StreamChunk]:
        """Call xAI with native SDK or OpenAI-compatible fallback.
        
        If use_native_sdk is True, uses the gRPC AsyncClient from xai-sdk.
        Otherwise falls back to OpenAI-compatible REST API.
        """
        if self._use_native_sdk:
            if not self._allow_openai_compat_fallback:
                try:
                    await self._ensure_async_client()
                    # Use native SDK stream (implementation pending: xai-sdk-chat-stream-bridge)
                    # For now, fall through to fallback to avoid breaking existing behavior
                    logger.warning(
                        "Native xAI SDK AsyncClient is initialized but native call flow is not yet complete. "
                        "Falling back to OpenAI-compatible API."
                    )
                except LLMApiServiceError:
                    if not self._allow_openai_compat_fallback:
                        raise
                    logger.info("Native xAI SDK unavailable, using OpenAI-compatible fallback")
        
        # OpenAI-compatible fallback (current implementation)
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
    
    @override
    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self
    
    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        """Async context manager exit with cleanup."""
        await self._close_async_client()
        await super().__aexit__(exc_type, exc_val, exc_tb)
        return False
