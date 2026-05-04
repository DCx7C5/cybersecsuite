"""Headers for cloud API providers (OpenAI, Anthropic, etc.)."""

from dataclasses import dataclass, field
from typing import Optional

from ...base.base_header import BaseHeader


@dataclass
class APIHeader(BaseHeader):
    """Base header for cloud API providers."""

    api_key_required: bool = True
    auth_scheme: str = "Bearer"
    rate_limit_requests_per_minute: int = 60
    rate_limit_tokens_per_minute: int = 90000
    timeout_seconds: int = 120
    max_retries: int = 3
    retry_backoff_factor: float = 2.0
    custom_headers: dict[str, str] = field(default_factory=dict)


@dataclass
class OpenAIHeader(APIHeader):
    """Headers for OpenAI API provider."""

    api_version: str = "2024-02"
    base_url: str = "https://api.openai.com/v1"
    organization_id: Optional[str] = None


@dataclass
class AnthropicHeader(APIHeader):
    """Headers for Anthropic API provider."""

    api_version: str = "2024-06-15"
    base_url: str = "https://api.anthropic.com"
    beta_features: list[str] = field(default_factory=list)


@dataclass
class GeminiHeader(APIHeader):
    """Headers for Google Gemini API provider."""

    api_version: str = "v1beta"
    base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    project_id: Optional[str] = None


@dataclass
class GroqHeader(APIHeader):
    """Headers for Groq API provider."""

    api_version: str = "openai"
    base_url: str = "https://api.groq.com/openai/v1"
    rate_limit_requests_per_minute: int = 30


@dataclass
class MistralHeader(APIHeader):
    """Headers for Mistral API provider."""

    api_version: str = "v0.0.11"
    base_url: str = "https://api.mistral.ai/v1"


@dataclass
class CohereHeader(APIHeader):
    """Headers for Cohere API provider."""

    api_version: str = "2024-02-29"
    base_url: str = "https://api.cohere.ai/v1"


@dataclass
class PerplexityHeader(APIHeader):
    """Headers for Perplexity API provider."""

    api_version: str = "openai"
    base_url: str = "https://api.perplexity.ai"
    rate_limit_requests_per_minute: int = 60


__all__ = [
    "APIHeader",
    "OpenAIHeader",
    "AnthropicHeader",
    "GeminiHeader",
    "GroqHeader",
    "MistralHeader",
    "CohereHeader",
    "PerplexityHeader",
]
