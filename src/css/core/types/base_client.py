"""Abstract base for all API service providers.

Imports msgspec.Struct versions from messages.py (Phase 6 P1).
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from aiohttp import ClientSession

from css.core.config import ProviderDefaults
from .enums import ProviderType
from .base_messages import BaseMessage, Tool, ModelMetadata, StreamChunk, LLMResponse


from css.core.logger import getLogger
logger = getLogger(__name__)


class StreamingHandler:
    """Mixin for providers that parse streaming responses."""
    
    async def _parse_stream_chunk(self, line: str) -> StreamChunk | None:
        """Parse a single line from stream. Override in provider subclass."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement _parse_stream_chunk()")


class BaseApiServiceClient(ABC):
    """Abstract base for all API service providers."""
    
    def __init__(
        self,
        provider_id: ProviderType,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = ProviderDefaults.TIMEOUT_SECONDS,
        max_retries: int = ProviderDefaults.MAX_RETRIES,
    ):
        self.provider_id = provider_id
        self.api_key = api_key
        self.base_url = base_url or self._default_base_url()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._session: ClientSession | None = None
    
    def _default_base_url(self) -> str:
        """Override in subclass to provide default base URL."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement _default_base_url()")
    
    @property
    def session(self) -> ClientSession | None:
        """Lazy-initialize aiohttp session."""
        if self._session is None:
            self._session = ClientSession()
        return self._session
    
    async def __aenter__(self):
        """Context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit — cleanup session."""
        if self._session:
            await self._session.close()
    
    @abstractmethod
    async def get_models(self) -> list[ModelMetadata]:
        """Get available models for this provider (with per-model feature flags)."""
        pass
    
    @abstractmethod
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
        """
        Call LLM with streaming support.
        
        Always returns an async iterator of chunks. For buffered responses,
        yields a single complete chunk instead of streaming multiple chunks.
        """
        pass
    
    async def call_llm_buffered(
        self,
        model_id: str,
        messages: list[BaseMessage],
        tools: list[Tool] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Buffered call: accumulate all chunks and return complete response."""
        chunks = []
        async for chunk in await self.call_llm(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            streaming=True,
            **kwargs,
        ):
            if chunk.type == "content_block_delta" and chunk.content:
                chunks.append(chunk.content)
            elif chunk.type == "message_stop":
                return LLMResponse(
                    text="".join(chunks),
                    stop_reason=chunk.stop_reason or "stop",
                    usage=chunk.metadata.get("usage", {}),
                )
        return LLMResponse(text="".join(chunks), stop_reason="eof")
    
    @staticmethod
    def _ensure_auth_header(
        headers: dict[str, str],
        api_key: str,
        header_name: str = "Authorization",
        prefix: str = "Bearer",
    ) -> dict[str, str]:
        """Ensure auth header is set."""
        if api_key:
            if prefix:
                headers[header_name] = f"{prefix} {api_key}"
            else:
                headers[header_name] = api_key
        return headers
    
    def supports_feature(self, model_metadata: ModelMetadata, feature: str) -> bool:
        """Check if model supports a feature (per-model gating, not provider-wide)."""
        feature_map = {
            "streaming": model_metadata.streaming,
            "vision": model_metadata.vision,
            "tool_use": model_metadata.tool_use,
            "prompt_caching": model_metadata.prompt_caching,
            "batch_api": model_metadata.batch_api,
            "structured_output": model_metadata.structured_output,
            "extended_thinking": model_metadata.extended_thinking,
            "files_api": model_metadata.files_api,
            "tool_use_caching": model_metadata.tool_use_caching,
        }
        return feature_map.get(feature, False)
