"""Ollama client — wrapper for local Ollama HTTP API with streaming support."""

from typing import Optional, List, AsyncIterator
import logging

from src.core.types.api_services import BaseApiServiceClient, StreamChunk, Message, Tool, ModelMetadata
from src.core.types.ollama import OllamaModel, OllamaConfig, OllamaExecutionContext


logger = logging.getLogger(__name__)


class OllamaClient(BaseApiServiceClient):
    """
    Ollama LLM client for local model inference.
    
    Wraps the local Ollama HTTP API (typically http://localhost:11434).
    Supports model discovery, streaming responses, and execution context tracking.
    
    Features:
    - Auto-discovery of locally installed models
    - Streaming and buffered response modes
    - Execution context tracking (timing, token counts)
    - Automatic model loading if not resident
    - Fallback graceful handling
    
    Example:
        client = OllamaClient(base_url='http://localhost:11434')
        async with client:
            models = await client.get_models()
            chunks = await client.call_llm('llama2', messages=[...])
    """
    
    def __init__(
        self,
        base_url: str = 'http://localhost:11434',
        timeout_seconds: int = 300,
        enable_model_auto_load: bool = True,
        config: Optional[OllamaConfig] = None,
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (default: localhost:11434)
            timeout_seconds: Request timeout in seconds
            enable_model_auto_load: If True, auto-load models if not resident
            config: Optional OllamaConfig for capability settings
        """
        super().__init__(base_url=base_url)
        pass
    
    def _default_base_url(self) -> str:
        """Return default Ollama base URL."""
        pass
    
    async def get_models(self) -> List[ModelMetadata]:
        """
        Get list of available models from local Ollama.
        
        Calls /api/tags endpoint to discover locally installed models.
        Includes capability detection and model metadata.
        
        Returns:
            List of ModelMetadata with per-model feature flags
        
        Raises:
            OllamaConnectionError: If cannot reach Ollama server
        """
        pass
    
    async def call_llm(
        self,
        model_id: str,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = True,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        """
        Call Ollama model with streaming support.
        
        Always returns an async iterator of chunks.
        For buffered responses, yields a single complete chunk.
        
        Args:
            model_id: Model name (e.g., 'llama2', 'neural-chat')
            messages: Conversation messages
            tools: Optional tools/function definitions
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Max tokens in response
            system_prompt: Optional system context
            streaming: If True, stream chunks; if False, return complete response
            **kwargs: Additional Ollama parameters
        
        Returns:
            AsyncIterator[StreamChunk] — always iterable (streaming or buffered)
        
        Raises:
            OllamaModelNotFoundError: If model not found locally
            OllamaModelLoadError: If model fails to load
            StreamingError: If streaming fails
        """
        pass
    
    async def supports_feature(self, model_metadata: ModelMetadata, feature: str) -> bool:
        """
        Check if model supports a specific feature.
        
        Feature support determined by:
        1. Model capabilities (from discovery)
        2. Ollama version constraints
        3. Model architecture constraints
        
        Args:
            model_metadata: Model metadata with capability flags
            feature: Feature to check (e.g., 'vision', 'tool_use')
        
        Returns:
            True if feature is supported, False otherwise
        """
        pass
    
    async def get_execution_context(self) -> OllamaExecutionContext:
        """
        Get execution context after last model call.
        
        Includes timing data, token counts, and performance metrics.
        
        Returns:
            OllamaExecutionContext with load_duration_ms, eval_count, etc.
        """
        pass
    
    async def ensure_model_loaded(self, model_id: str) -> bool:
        """
        Ensure model is loaded into memory.
        
        If not already resident, pulls and loads the model.
        
        Args:
            model_id: Model name to load
        
        Returns:
            True if model is loaded, False if not available
        
        Raises:
            OllamaConnectionError: If cannot reach server
        """
        pass
