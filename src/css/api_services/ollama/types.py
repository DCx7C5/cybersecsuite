"""Ollama-specific types for local LLM support.

Ollama is treated as a special case in Phase 0.0+ to ensure feature parity
with cloud LLM providers (streaming, vision, tools, etc.).

This module is part of the Ollama provider package and should be imported from:
  from css.api_services.ollama import OllamaConfig, OllamaModel, OllamaCapabilities
"""

from datetime import datetime, timezone

import msgspec


class OllamaModel(msgspec.Struct, frozen=True):
    """Metadata for a local Ollama model."""

    name: str
    full_name: str
    size_gb: float = 0.0
    parameters: int = 0
    quantization: str | None = None
    description: str | None = None
    modified_at: datetime = datetime.now(timezone.utc)


class OllamaCapabilities(msgspec.Struct, frozen=True):
    """Capabilities supported by a specific Ollama model."""

    model_name: str
    supports_streaming: bool = True
    supports_vision: bool = False
    supports_tool_use: bool = False
    supports_json_mode: bool = False
    supports_embeddings: bool = False
    context_window: int = 2048
    max_tokens: int = 512
    discovered_at: datetime = datetime.now(timezone.utc)


class OllamaConfig(msgspec.Struct, frozen=True):
    """Configuration for connecting to local Ollama instance."""

    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 120
    max_retries: int = 3
    model_discovery_endpoint: str = "/api/tags"
    model_info_endpoint: str = "/api/show"
    chat_endpoint: str = "/api/chat"
    embeddings_endpoint: str = "/api/embeddings"

    auto_discover_models: bool = True
    discovery_timeout_seconds: int = 10
    cache_models_for_hours: int = 24

    detect_capabilities: bool = True


class OllamaExecutionContext(msgspec.Struct):
    """Execution context specific to Ollama models.

    Tracks streaming, interruptions, and local resource usage.
    """

    model_name: str
    provider: str = "ollama"
    started_at: datetime = datetime.now(timezone.utc)
    ended_at: datetime | None = None
    tokens_generated: int = 0
    tokens_prompted: int = 0
    total_duration_ms: float = 0.0
    load_duration_ms: float = 0.0
    prompt_eval_count: int = 0
    eval_count: int = 0
    streamed: bool = True
    interrupted: bool = False
    error: str | None = None

    def set_completed(self, **timing_data) -> None:
        """Mark execution as completed with timing data.

        Ollama returns timing data that we capture here.
        """
        self.ended_at = datetime.now(timezone.utc)
        for key, value in timing_data.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_failed(self, error: str) -> None:
        """Mark execution as failed."""
        self.ended_at = datetime.now(timezone.utc)
        self.error = error

    def get_tokens_per_second(self) -> float:
        """Calculate generation speed."""
        if self.eval_count == 0 or self.total_duration_ms == 0:
            return 0.0
        return (self.eval_count / self.total_duration_ms) * 1000


class OllamaHealthCheck(msgspec.Struct, frozen=True):
    """Health check result for Ollama instance."""

    is_healthy: bool = False
    is_reachable: bool = False
    models_available: int = 0
    models_loaded: int = 0
    last_check_at: datetime = datetime.now(timezone.utc)
    error: str | None = None


__all__ = [
    "OllamaModel",
    "OllamaConfig",
    "OllamaCapabilities",
    "OllamaExecutionContext",
    "OllamaHealthCheck",
]
