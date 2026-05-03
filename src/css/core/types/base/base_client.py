"""Abstract base for all API service providers."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Optional

from aiohttp import ClientSession


logger = logging.getLogger(__name__)



@dataclass
class BaseMessage:
    """A message in the conversation."""
    role: MessageRole
    content: str


@dataclass
class Tool:
    """A tools available to the model."""
    name: str
    description: str
    input_schema: dict[str, Any]


@dataclass
class ModelMetadata:
    """Metadata about a model with per-model feature flags."""
    id: str
    provider: ProviderType
    display_name: str
    context_window: int
    max_output_tokens: int
    # Per-model feature flags (not provider-wide)
    streaming: bool = True
    vision: bool = False
    tool_use: bool = False
    prompt_caching: bool = False
    batch_api: bool = False
    structured_output: bool = False
    extended_thinking: bool = False
    files_api: bool = False
    tool_use_caching: bool = False
    # Cost
    input_cost_per_mtok: float = 0.0
    output_cost_per_mtok: float = 0.0


@dataclass
class StreamChunk:
    """A chunk from a streaming response."""
    type: str  # "content_block_delta", "message_stop", "error"
    content: Optional[str] = None
    stop_reason: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMResponse:
    """A complete LLM response (buffered)."""
    text: str
    stop_reason: str = "stop"
    usage: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutorResult:
    """Result from an execution/API call to a provider."""
    status_code: int = 200
    headers: dict[str, str] = field(default_factory=dict)
    body: Optional[dict[str, Any]] = None
    stream: Optional[AsyncIterator[bytes]] = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    provider_id: str = ""
    model_id: str = ""
    request_id: Optional[str] = None

    @property
    def ok(self) -> bool:
        """Check if status code is successful (2xx range)."""
        return 200 <= self.status_code < 300


class ErrorStrategy(str, Enum):
    """Strategy for handling errors in hook and service execution."""
    PRESERVE_EXISTING = "preserve"
    LOG = "log"
    WARN = "warn"


class StreamingHandler:
    """Mixin for providers that parse streaming responses."""
    
    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
        """Parse a single line from stream. Override in provider subclass."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement _parse_stream_chunk()")


class BaseApiServiceClient(ABC):
    """Abstract base for all API service providers."""
    
    def __init__(
        self,
        provider_id: ProviderType,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
    ):
        self.provider_id = provider_id
        self.api_key = api_key
        self.base_url = base_url or self._default_base_url()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self._session: Optional[ClientSession] = None
    
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
        tools: Optional[list[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
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
        tools: Optional[list[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
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


__all__ = [
    "ProviderType",
    "MessageRole",
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    "ErrorStrategy",
    "StreamingHandler",
    "BaseApiServiceClient",
]
