"""
Issue #4: Ollama Backward Compatibility Layer

Maintains compatibility with legacy OllamaClient while supporting new streaming architecture.
Enables existing code to work with new AsyncIterator[StreamChunk] return type.

Architecture:
- OllamaApiService: New implementation (currently in service.py)
- OllamaClientCompat: Wraps legacy OllamaClient for compatibility
- Both return AsyncIterator[StreamChunk] consistently
"""

import logging
from typing import AsyncIterator, Optional, List

from css.core.types.api_services import (
    BaseApiServiceClient,
    StreamChunk,
    BaseMessage,
    Tool,
    ModelMetadata,
    ProviderType,
)
from css.core.exceptions import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    GatewayError,
    AuthError,
)
from css.core.retry import RetryOrchestrator, RetryConfig
from css.core.config import ProviderDefaults

logger = logging.getLogger(__name__)


class OllamaClientCompat(BaseApiServiceClient):
    """
    Backward compatibility wrapper for legacy OllamaClient.
    
    Wraps the old OllamaClient implementation while exposing new interface:
    - Returns AsyncIterator[StreamChunk] consistently
    - Integrates error mapping (Issue #3)
    - Integrates retry logic (Issue #2)
    - Handles both streaming and buffered modes
    
    Migration path:
    1. Old code using OllamaClient continues to work
    2. New code uses OllamaApiService directly
    3. Eventually deprecate this wrapper in Phase 0.3
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout_seconds: int = ProviderDefaults.TIMEOUT_SECONDS,
        enable_model_auto_load: bool = True,
        max_retries: int = ProviderDefaults.MAX_RETRIES,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Ollama compatibility wrapper.
        
        Args:
            base_url: Ollama server URL
            timeout_seconds: Request timeout
            enable_model_auto_load: Auto-load models if needed
            max_retries: Max retries for transient failures
            api_key: Optional API key (Ollama typically doesn't need one)
        """
        super().__init__(
            provider_id=ProviderType.OLLAMA,
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        
        self.enable_model_auto_load = enable_model_auto_load
        self.retry_orchestrator = RetryOrchestrator(
            RetryConfig(max_retries=max_retries)
        )
        self._cached_models: Optional[List[ModelMetadata]] = None
    
    def _default_base_url(self) -> str:
        """Return default Ollama base URL."""
        return "http://localhost:11434/v1"
    
    async def get_models(self) -> List[ModelMetadata]:
        """
        Get available models from local Ollama.
        
        Calls /api/tags endpoint and returns list of ModelMetadata.
        Results are cached to avoid repeated queries.
        
        Returns:
            List of ModelMetadata for locally installed models
        
        Raises:
            OllamaConnectionError: If cannot reach Ollama server
        """
        if self._cached_models is not None:
            return self._cached_models
        
        async def fetch_models():
            """Fetch models from Ollama /api/tags endpoint."""
            try:
                async with self.session.get(
                    f"{self.base_url.replace('/v1', '')}/api/tags",
                    timeout=self.timeout_seconds,
                ) as resp:
                    if resp.status != 200:
                        raise OllamaConnectionError(
                            f"Failed to fetch models: HTTP {resp.status}"
                        )
                    
                    data = await resp.json()
                    models = []
                    
                    for model_info in data.get("models", []):
                        model_name = model_info.get("name", "")
                        if model_name:
                            models.append(
                                ModelMetadata(
                                    name=model_name,
                                    provider=ProviderType.OLLAMA,
                                    capabilities={},
                                    metadata={
                                        "digest": model_info.get("digest"),
                                        "size": model_info.get("size"),
                                        "modified_at": model_info.get("modified_at"),
                                    }
                                )
                            )
                    
                    return models
            except OllamaConnectionError:
                raise
            except Exception as e:
                raise OllamaConnectionError(f"Error fetching models: {str(e)}")
        
        # Use retry orchestrator for resilience
        result = await self.retry_orchestrator.execute_with_retry(
            api_call=fetch_models,
            provider_id=ProviderType.OLLAMA,
        )
        
        if not result.success:
            raise OllamaConnectionError(f"Failed to fetch models: {result.error}")
        
        self._cached_models = result.result
        return self._cached_models
    
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
        Call Ollama model with streaming support (Issue #4).
        
        Returns AsyncIterator[StreamChunk] consistently, supporting both:
        - Streaming mode: yields chunks as they arrive
        - Buffered mode: yields complete response as single chunk
        
        Args:
            model_id: Model name (e.g., 'llama2', 'neural-chat')
            messages: Conversation messages
            tools: Optional tools/function definitions
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            system_prompt: Optional system context
            streaming: If True, stream; if False, buffer
            **kwargs: Additional Ollama parameters
        
        Returns:
            AsyncIterator[StreamChunk] — always iterable
        
        Raises:
            OllamaModelNotFoundError: If model not found
            OllamaModelLoadError: If model fails to load
            GatewayError: If server unavailable
            AuthError: If authentication fails
        """
        # Ensure model is loaded if auto-load enabled
        if self.enable_model_auto_load:
            loaded = await self._ensure_model_loaded(model_id)
            if not loaded:
                raise OllamaModelNotFoundError(
                    f"Model '{model_id}' not found and could not be loaded"
                )
        
        # Prepare request
        formatted_messages = self._format_messages(messages, system_prompt)
        call_body = {
            "model": model_id,
            "messages": formatted_messages,
            "temperature": temperature,
            "stream": streaming,
        }
        
        if max_tokens:
            call_body["num_predict"] = max_tokens
        
        if tools:
            call_body["tools"] = self._format_tools(tools)
        
        # Make call with retry
        async def make_call():
            return await self._stream_or_buffer(call_body, streaming)
        
        result = await self.retry_orchestrator.execute_with_retry(
            api_call=make_call,
            provider_id=ProviderType.OLLAMA,
        )
        
        if not result.success:
            # Map error to unified type and raise
            mapped_error = self.retry_orchestrator.map_error_to_unified(
                result.error, ProviderType.OLLAMA
            )
            raise mapped_error
        
        # result.result is AsyncIterator[StreamChunk]
        async for chunk in result.result:
            yield chunk
    
    async def _stream_or_buffer(
        self,
        call_body: dict,
        streaming: bool,
    ) -> AsyncIterator[StreamChunk]:
        """
        Execute API call with streaming or buffering.
        
        Returns AsyncIterator[StreamChunk] for consistency.
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=call_body,
                headers=headers,
                timeout=self.timeout_seconds,
            ) as resp:
                if resp.status == 401:
                    raise AuthError("Ollama authentication failed")
                elif resp.status == 404:
                    raise OllamaModelNotFoundError("Model not found")
                elif resp.status >= 500:
                    raise GatewayError(f"Ollama server error: {resp.status}")
                elif resp.status != 200:
                    raise GatewayError(f"Ollama request failed: HTTP {resp.status}")
                
                if streaming:
                    async for chunk in self._stream_chunks(resp):
                        yield chunk
                else:
                    data = await resp.json()
                    chunk = self._parse_buffered_response(data)
                    yield chunk
        
        except (AuthError, GatewayError, OllamaModelNotFoundError):
            raise
        except Exception as e:
            raise GatewayError(f"Ollama call failed: {str(e)}")
    
    async def _stream_chunks(self, resp) -> AsyncIterator[StreamChunk]:
        """Parse streaming response."""
        
        try:
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if not decoded:
                    continue
                
                chunk = await self._parse_stream_chunk(decoded)
                if chunk:
                    yield chunk
        except Exception as e:
            yield StreamChunk(
                type="error",
                metadata={"error": str(e)}
            )
    
    async def _parse_stream_chunk(self, line: str) -> Optional[StreamChunk]:
        """Parse SSE line to StreamChunk."""
        import json
        
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
    
    def _parse_buffered_response(self, data: dict) -> StreamChunk:
        """Parse buffered response to complete StreamChunk."""
        
        text = ""
        for choice in data.get("choices", []):
            if choice.get("message", {}).get("content"):
                text += choice["message"]["content"]
        
        return StreamChunk(
            type="message_delta",
            content=text,
            metadata={
                "stop_reason": data["choices"][0].get("finish_reason", "stop")
                if data.get("choices") else "stop",
                "usage": data.get("usage", {}),
            }
        )
    
    async def _ensure_model_loaded(self, model_id: str) -> bool:
        """
        Ensure model is loaded into memory.
        
        If not already resident, pulls and loads the model.
        
        Args:
            model_id: Model name to load
        
        Returns:
            True if model is loaded, False if not available
        
        Raises:
            GatewayError: If cannot reach server
        """
        try:
            # Call /api/pull to load model
            async with self.session.post(
                f"{self.base_url.replace('/v1', '')}/api/pull",
                json={"name": model_id},
                timeout=self.timeout_seconds,
            ) as resp:
                if resp.status == 200:
                    return True
                elif resp.status == 404:
                    return False
                else:
                    raise GatewayError(f"Model load failed: HTTP {resp.status}")
        except Exception as e:
            raise GatewayError(f"Could not load model: {str(e)}")
    
    @staticmethod
    def _format_messages(
        messages: List[BaseMessage],
        system_prompt: Optional[str] = None,
    ) -> List[dict]:
        """Format messages for Ollama API."""
        formatted = []
        if system_prompt:
            formatted.append({"role": "system", "content": system_prompt})
        
        for msg in messages:
            formatted.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        return formatted
    
    @staticmethod
    def _format_tools(tools: List[Tool]) -> List[dict]:
        """Format tools for Ollama API."""
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
