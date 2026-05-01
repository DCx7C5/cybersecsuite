"""Ollama-specific types for local LLM support.

Ollama is treated as a special case in Phase 0.0+ to ensure feature parity
with cloud LLM providers (streaming, vision, tools, etc.).

This module is part of the Ollama provider package and should be imported from:
  from api_services.ollama import OllamaConfig, OllamaModel, OllamaCapabilities
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OllamaModel(BaseModel):
    """Metadata for a local Ollama model."""

    name: str = Field(..., description="Model name (e.g., 'llama2', 'mistral')")
    full_name: str = Field(..., description="Full identifier with tag (e.g., 'llama2:7b')")
    size_gb: float = Field(default=0.0, description="Model size in GB")
    parameters: int = Field(default=0, description="Number of parameters")
    quantization: Optional[str] = Field(default=None, description="Quantization level (e.g., 'Q4_0')")
    description: Optional[str] = Field(default=None)
    modified_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = False


class OllamaCapabilities(BaseModel):
    """Capabilities supported by a specific Ollama model."""

    model_name: str = Field(..., description="Which model these apply to")
    supports_streaming: bool = Field(default=True, description="Can stream responses")
    supports_vision: bool = Field(default=False, description="Can process images")
    supports_tool_use: bool = Field(default=False, description="Can use tools/functions")
    supports_json_mode: bool = Field(default=False, description="Can output structured JSON")
    supports_embeddings: bool = Field(default=False, description="Can generate embeddings")
    context_window: int = Field(default=2048, description="Max context window")
    max_tokens: int = Field(default=512, description="Max output tokens")
    discovered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        use_enum_values = False


class OllamaConfig(BaseModel):
    """Configuration for connecting to local Ollama instance."""

    base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server base URL",
    )
    timeout_seconds: int = Field(default=120, description="Request timeout")
    max_retries: int = Field(default=3, description="Retry attempts on failure")
    model_discovery_endpoint: str = Field(
        default="/api/tags",
        description="Endpoint to discover available models",
    )
    model_info_endpoint: str = Field(
        default="/api/show",
        description="Endpoint to get model details",
    )
    chat_endpoint: str = Field(
        default="/api/chat",
        description="Endpoint for chat completions",
    )
    embeddings_endpoint: str = Field(
        default="/api/embeddings",
        description="Endpoint for generating embeddings",
    )

    # Auto-discovery settings
    auto_discover_models: bool = Field(default=True, description="Discover available models on startup")
    discovery_timeout_seconds: int = Field(default=10, description="Max time to wait for model discovery")
    cache_models_for_hours: int = Field(default=24, description="How long to cache model list")

    # Feature detection
    detect_capabilities: bool = Field(
        default=True,
        description="Auto-detect model capabilities (vision, tools, etc.)",
    )

    class Config:
        """Pydantic config."""

        extra = "allow"  # Allow forward-compatible fields


class OllamaExecutionContext(BaseModel):
    """Execution context specific to Ollama models.

    Tracks streaming, interruptions, and local resource usage.
    """

    model_name: str = Field(..., description="Which Ollama model was used")
    provider: str = Field(default="ollama", description="Always 'ollama'")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(default=None)
    tokens_generated: int = Field(default=0, description="Output tokens")
    tokens_prompted: int = Field(default=0, description="Input tokens")
    total_duration_ms: float = Field(default=0.0, description="Total execution time")
    load_duration_ms: float = Field(default=0.0, description="Time to load model into memory")
    prompt_eval_count: int = Field(default=0, description="Tokens evaluated in prompt")
    eval_count: int = Field(default=0, description="Tokens generated")
    streamed: bool = Field(default=True, description="Was this response streamed?")
    interrupted: bool = Field(default=False, description="Was streaming interrupted?")
    error: Optional[str] = Field(default=None, description="Error message if failed")

    class Config:
        """Pydantic config."""

        use_enum_values = False

    def set_completed(self, **timing_data) -> None:
        """Mark execution as completed with timing data.

        Ollama returns timing data that we capture here.
        """
        self.ended_at = datetime.utcnow()
        for key, value in timing_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_failed(self, error: str) -> None:
        """Mark execution as failed."""
        self.ended_at = datetime.utcnow()
        self.error = error

    def get_tokens_per_second(self) -> float:
        """Calculate generation speed."""
        if self.eval_count == 0 or self.total_duration_ms == 0:
            return 0.0
        return (self.eval_count / self.total_duration_ms) * 1000


class OllamaHealthCheck(BaseModel):
    """Health check result for Ollama instance."""

    is_healthy: bool = Field(default=False, description="Is Ollama running and responsive?")
    is_reachable: bool = Field(default=False, description="Can we reach the server?")
    models_available: int = Field(default=0, description="Number of models on disk")
    models_loaded: int = Field(default=0, description="Number of models in memory")
    last_check_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = Field(default=None, description="Error message if health check failed")

    class Config:
        """Pydantic config."""

        use_enum_values = False


__all__ = [
    "OllamaModel",
    "OllamaConfig",
    "OllamaCapabilities",
    "OllamaExecutionContext",
    "OllamaHealthCheck",
]
