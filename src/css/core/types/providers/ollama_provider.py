"""Ollama provider base class for local LLM support."""

from typing import Any, AsyncIterator, Optional

from ..base import BaseMessage, Tool, ModelMetadata, StreamChunk, ProviderType
from .base_providers import LocalProviderBase


class OllamaProviderBase(LocalProviderBase):
    """Base class for Ollama local provider integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout_seconds: int = 120,
        max_retries: int = 3,
        local_model_path: Optional[str] = None,
        auto_discover_models: bool = True,
        model_discovery_endpoint: str = "/api/tags",
        chat_endpoint: str = "/api/chat",
    ):
        """Initialize Ollama provider.

        Args:
            api_key: Optional API key (Ollama typically doesn't use).
            base_url: Base URL for Ollama instance. Defaults to localhost:11434.
            timeout_seconds: Request timeout in seconds.
            max_retries: Maximum retry attempts.
            local_model_path: Path to Ollama binary (optional check).
            auto_discover_models: Auto-discover available models on init.
            model_discovery_endpoint: Endpoint for model discovery.
            chat_endpoint: Endpoint for chat completions.
        """
        super().__init__(
            provider_id=ProviderType.OLLAMA,
            api_key=api_key,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            local_model_path=local_model_path,
            check_binary_on_init=False,  # Ollama doesn't need binary check
        )
        self.model_discovery_endpoint = model_discovery_endpoint
        self.chat_endpoint = chat_endpoint
        self.auto_discover_models = auto_discover_models
        self._discovered_models: Optional[list[ModelMetadata]] = None

    def _default_base_url(self) -> str:
        """Default base URL for Ollama local instance."""
        return "http://localhost:11434"

    def _get_binary_name(self) -> str:
        """Binary name for Ollama."""
        return "ollama"

    async def get_models(self) -> list[ModelMetadata]:
        """Discover available Ollama models.

        Fetches list of available models from Ollama's /api/tags endpoint
        and returns them as ModelMetadata objects.

        Returns:
            List of available models.

        Raises:
            ConnectionError: If unable to reach Ollama server.
            RuntimeError: If model discovery fails.
        """
        if self._discovered_models is not None:
            return self._discovered_models

        # Call get_models endpoint (implemented by subclass)
        if not self.session:
            raise ConnectionError("No aiohttp session available")

        url = f"{self.base_url}{self.model_discovery_endpoint}"
        try:
            async with self.session.get(url, timeout=self.timeout_seconds) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Parse response and convert to ModelMetadata
                    models = await self._parse_model_list(data)
                    self._discovered_models = models
                    return models
                raise RuntimeError(f"Model discovery failed: {resp.status}")
        except Exception as e:
            raise RuntimeError(f"Failed to discover Ollama models: {e}")

    async def _parse_model_list(self, data: dict[str, Any]) -> list[ModelMetadata]:
        """Parse Ollama model list response into ModelMetadata objects.

        Override in subclass to customize parsing.

        Args:
            data: Response from /api/tags endpoint.

        Returns:
            List of ModelMetadata objects.
        """
        models = []
        if "models" in data:
            for model_info in data["models"]:
                model_name = model_info.get("name", "unknown")
                models.append(
                    ModelMetadata(
                        id=model_name,
                        provider=ProviderType.OLLAMA,
                        display_name=model_name,
                        context_window=4096,  # Default, override in subclass
                        max_output_tokens=2048,  # Default, override in subclass
                        streaming=True,
                    )
                )
        return models

    async def call_llm(
        self,
        model_id: str,
        messages: list[BaseMessage],
        tools: Optional[list[Tool]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        streaming: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        """Call Ollama LLM.

        This is a stub that must be implemented by subclass.
        Subclass should handle actual HTTP calls to Ollama chat endpoint.

        Args:
            model_id: Model identifier.
            messages: Conversation messages.
            tools: Optional tools/functions.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            system_prompt: System prompt.
            streaming: Whether to stream response.
            **kwargs: Additional provider-specific parameters.

        Yields:
            StreamChunk objects.

        Raises:
            NotImplementedError: This is a stub.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement call_llm()"
        )


__all__ = ["OllamaProviderBase"]
