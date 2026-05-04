"""Headers for local LLM providers."""

from dataclasses import dataclass, field

from ...base.base_header import BaseHeader


@dataclass
class LocalHeader(BaseHeader):
    """Base header for local LLM providers."""

    api_key_required: bool = False
    base_url: str = "http://localhost:11434"
    timeout_seconds: int = 120
    max_retries: int = 3
    auto_start_service: bool = False
    model_discovery_enabled: bool = True
    model_cache_hours: int = 24
    resource_limits: dict[str, int] = field(default_factory=dict)


@dataclass
class OllamaLocalHeader(LocalHeader):
    """Headers for Ollama local provider."""

    base_url: str = "http://localhost:11434"
    model_discovery_endpoint: str = "/api/tags"
    chat_endpoint: str = "/api/chat"
    embeddings_endpoint: str = "/api/embeddings"
    generate_endpoint: str = "/api/generate"
    pull_endpoint: str = "/api/pull"
    show_endpoint: str = "/api/show"


@dataclass
class NScaleLocalHeader(LocalHeader):
    """Headers for NScale local provider."""

    base_url: str = "http://localhost:8000"
    model_discovery_endpoint: str = "/v1/models"
    chat_endpoint: str = "/v1/chat/completions"


@dataclass
class VLLMLocalHeader(LocalHeader):
    """Headers for vLLM (OpenAI-compatible) local provider."""

    base_url: str = "http://localhost:8000"
    model_discovery_endpoint: str = "/v1/models"
    chat_endpoint: str = "/v1/chat/completions"
    completions_endpoint: str = "/v1/completions"


__all__ = [
    "LocalHeader",
    "OllamaLocalHeader",
    "NScaleLocalHeader",
    "VLLMLocalHeader",
]
