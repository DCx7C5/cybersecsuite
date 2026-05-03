"""
Issue #5: LocalSDK Base Class

Provides a unified base class for all local LLM implementations.
Enables consistent error handling, retry logic, and streaming support across all local SDKs.

Subclasses: OllamaApiService, NScaleApiService, and future local providers.
"""

import logging
from typing import AsyncIterator, Optional, List
from abc import ABC, abstractmethod

from ...api_services import (
    BaseApiServiceClient,
    StreamChunk,
    BaseMessage,
    Tool,
    ModelMetadata,
    ProviderType,
)
from core.exceptions import GatewayError
from core.retry import RetryOrchestrator, RetryConfig

logger = logging.getLogger(__name__)


class LocalSDKBase(BaseApiServiceClient, ABC):
    """
    Abstract base class for all local LLM SDKs.
    
    Local SDKs are characterized by:
    - Running on local machine or private network (not cloud API)
    - HTTP API interface (OpenAI-compatible or native)
    - No built-in retry (so we use WRAP strategy)
    - Variable model availability (model discovery needed)
    - Lower latency but less stable than cloud providers
    
    Provides:
    - Unified error handling (Issue #3)
    - Retry orchestration (Issue #2)
    - Streaming support (AsyncIterator[StreamChunk])
    - Model discovery and capability tracking
    
    Example subclasses:
    - OllamaApiService: Ollama HTTP API
    - NScaleApiService: NScale local inference
    - LocalVLLMService: vLLM OpenAI-compatible API
    - LocalOllamaService: Alternative Ollama wrapper
    """
    
    def __init__(
        self,
        provider_id: ProviderType,
        base_url: str,
        timeout_seconds: int = 120,
        max_retries: int = 3,
        api_key: Optional[str] = None,
        enable_model_auto_load: bool = True,
    ):
        """
        Initialize LocalSDK base.
        
        Args:
            provider_id: Local provider type (OLLAMA, NSCALE, etc.)
            base_url: Base URL for local API
            timeout_seconds: Request timeout
            max_retries: Max retries for transient failures
            api_key: Optional API key (local SDKs typically don't use)
            enable_model_auto_load: Auto-load models if available
        """
        super().__init__(
            provider_id=provider_id,
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        
        self.enable_model_auto_load = enable_model_auto_load
        self.retry_orchestrator = RetryOrchestrator(
            RetryConfig(
                max_retries=max_retries,
                base_delay_ms=100,  # Local APIs usually respond quickly
            )
        )
        self._cached_models: Optional[List[ModelMetadata]] = None
    
    async def get_models(self) -> List[ModelMetadata]:
        """
        Discover available models.
        
        Must be implemented by subclasses to call their model discovery endpoint.
        Results are cached to avoid repeated queries.
        
        Returns:
            List of ModelMetadata for available models
        
        Raises:
            GatewayError: If you cannot reach server
            AuthError: If authentication fails
        """
        if self._cached_models is not None:
            return self._cached_models
        
        async def fetch_models() -> List[ModelMetadata]:
            fetched = await self._fetch_available_models()
            self._cached_models = fetched
            return fetched
        
        result = await self.retry_orchestrator.execute_with_retry(
            api_call=fetch_models,
            provider_id=self.provider_id,
        )
        
        if not result.success:
            if result.error:
                mapped_error = self.retry_orchestrator.map_error_to_unified(
                    result.error, self.provider_id
                )
                raise mapped_error
            raise GatewayError("Unknown error fetching models")
        
        models = result.result
        if models is None:
            raise GatewayError("Model fetch returned None")
        return models
    
    @abstractmethod
    async def _fetch_available_models(self) -> List[ModelMetadata]:
        """
        Fetch available models from local SDK.
        
        Subclasses must implement provider-specific model discovery.
        Called by get_models() which handles caching and retry.
        
        Returns:
            List of ModelMetadata
        
        Raises:
            GatewayError: If cannot reach server
        """
        pass
    
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
    ) -> AsyncIterator[StreamChunk]:
        """
        Call local LLM model (Issue #5).
        
        Returns AsyncIterator[StreamChunk] for both streaming and buffered modes:
        - streaming=True: yields multiple chunks as they arrive
        - streaming=False: buffers complete response and yields as single final chunk
        
        Both paths go through:
        1. Model validation (if autoload enabled)
        2. Request preparation (formatting messages, tools)
        3. Retry orchestrator (Issue #2)
        4. Error mapping (Issue #3)
        5. Streaming/buffering
        
        Args:
            model_id: Model name (provider-specific format)
            messages: Conversation messages
            tools: Optional tools/function definitions
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            system_prompt: Optional system context
            streaming: If True, stream chunks; if False, buffer complete response
            **kwargs: Provider-specific parameters
        
        Yields:
            StreamChunk objects in both streaming and buffered modes
        
        Raises:
            GatewayError: If server unavailable or error occurs
        """
        # Ensure model is available if auto-load enabled
        if self.enable_model_auto_load:
            loaded = await self._ensure_model_loaded(model_id)
            if not loaded:
                raise GatewayError(
                    f"Model '{model_id}' not found and could not be loaded"
                )
        
        # Prepare request (subclass-specific)
        call_body = await self._prepare_call_body(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            streaming=streaming,
            **kwargs,
        )
        
        # Execute with retry
        async def make_call() -> AsyncIterator[StreamChunk]:
            """Execute the call and return the iterator of chunks."""
            return await self._execute_call(call_body, streaming)
        
        result = await self.retry_orchestrator.execute_with_retry(
            api_call=make_call,
            provider_id=self.provider_id,
        )
        
        if not result.success:
            if result.error:
                mapped_error = self.retry_orchestrator.map_error_to_unified(
                    result.error, self.provider_id
                )
                raise mapped_error
            raise GatewayError("Unknown error executing call")
        
        # result.result is now AsyncIterator[StreamChunk]
        response = result.result
        if response is not None:
            async for response_chunk in response:
                yield response_chunk
    
    @abstractmethod
    async def _prepare_call_body(
        self,
        model_id: str,
        messages: List[BaseMessage],
        tools: Optional[List[Tool]],
        temperature: float,
        max_tokens: Optional[int],
        system_prompt: Optional[str],
        streaming: bool,
        **kwargs,
    ) -> dict:
        """
        Prepare API call body in provider-specific format.
        
        Subclasses implement provider-specific request formatting.
        
        Returns:
            Dict to be sent to API endpoint
        """
        pass
    
    @abstractmethod
    async def _execute_call(
        self,
        call_body: dict,
        streaming: bool,
    ) -> AsyncIterator[StreamChunk]:
        """
        Execute prepared call body.
        
        Subclasses implement provider-specific HTTP calls and response parsing.
        
        ALWAYS returns AsyncIterator[StreamChunk]:
        - streaming=True: yields chunks as they arrive from provider
        - streaming=False: buffers complete response, yields as single final chunk
        
        Buffered responses should be wrapped as StreamChunk:
        ```python
        yield StreamChunk(
            type="message_delta",
            content=response.text,
            metadata={
                "stop_reason": response.stop_reason,
                "usage": response.usage,
            }
        )
        ```
        """
        pass
    
    async def _ensure_model_loaded(self, model_id: str) -> bool:
        """
        Ensure model is loaded into memory.
        
        Override in subclasses if model autoloading is supported.
        Default implementation returns True (assume model exists).
        
        Args:
            model_id: Model name
        
        Returns:
            True if model is loaded, False if not available
        
        Raises:
            GatewayError: If cannot reach server
        """
        # Default: assume model exists (subclasses can override)
        return True
    
    def _format_error_response(self, error_msg: str) -> StreamChunk:
        """
        Format error as StreamChunk for consistent error handling.
        
        Allows streaming handlers to treat errors consistently.
        """
        return StreamChunk(
            type="error",
            metadata={"error": error_msg}
        )
    
    async def health_check(self) -> bool:
        """
        Check if local SDK is healthy and reachable.
        
        Override in subclasses to implement provider-specific health checks.
        Default: Try to connect to base_url.
        
        Returns:
            True if healthy, False otherwise
        """
        session = self.session
        if session is None:
            logger.warning(f"No session available for {self.provider_id}")
            return False
        
        try:
            async with session.get(
                self.base_url,
                timeout=5,
            ) as resp:
                return resp.status < 500
        except Exception as e:
            logger.warning(f"Health check failed for {self.provider_id}: {e}")
            return False
    
    def clear_model_cache(self):
        """Clear cached model list."""
        self._cached_models = None
