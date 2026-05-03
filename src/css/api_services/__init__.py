"""
API Services Module — 25 LLM and service providers.

Each provider lives in src/api_services/{provider_name}/ and exports an *ApiService class
that inherits from BaseApiServiceClient (in src/core/api_service_client/).
"""

# Tier 1: Major cloud providers
from css.api_services.anthropic import AnthropicApiService
from css.api_services.openai import OpenAIApiService
from css.api_services.gemini import GeminiApiService

# Tier 1.5: High-quality alternatives
from css.api_services.deepseek import DeepSeekApiService
from css.api_services.groq import GroqApiService
from css.api_services.mistral import MistralApiService
from css.api_services.xai import xAIApiService
from css.api_services.together import TogetherApiService
from css.api_services.perplexity import PerplexityApiService

# Tier 2: Routing / Multi-provider
from css.api_services.openrouter import OpenRouterApiService

# Tier 2.5: Specialized services
from css.api_services.nvidia import NvidiaApiService
from css.api_services.cerebras import CerebrasApiService
from css.api_services.sambanova import SambanovaApiService
from css.api_services.deepinfra import DeepinfraApiService
from css.api_services.cohere import CohereApiService
from css.api_services.ai21 import AI21ApiService
from css.api_services.huggingface import HuggingfaceApiService
from css.api_services.nscale import NscaleApiService
from css.api_services.lambda_api import LambdaApiService

# Tier 3: Utility services
from css.api_services.github import GithubApiService
from css.api_services.cloudflare import CloudflareApiService
from css.api_services.fireworks import FireworksApiService
from css.api_services.opencode import OpencodeApiService

# Local providers
from css.api_services.ollama import OllamaApiService, OllamaClientCompat

# Error mapping (Issue #3)
from css.api_services.error_mappers import (
    map_provider_error,
    AnthropicErrorMapper,
    OpenAIErrorMapper,
    OllamaErrorMapper,
    GeminiErrorMapper,
    GroqErrorMapper,
)

# Provider registry
PROVIDERS = {
    "anthropic": AnthropicApiService,
    "openai": OpenAIApiService,
    "deepseek": DeepSeekApiService,
    "groq": GroqApiService,
    "gemini": GeminiApiService,
    "mistral": MistralApiService,
    "xai": xAIApiService,
    "nvidia": NvidiaApiService,
    "openrouter": OpenRouterApiService,
    "cerebras": CerebrasApiService,
    "together": TogetherApiService,
    "github": GithubApiService,
    "cloudflare": CloudflareApiService,
    "fireworks": FireworksApiService,
    "opencode": OpencodeApiService,
    "cohere": CohereApiService,
    "perplexity": PerplexityApiService,
    "sambanova": SambanovaApiService,
    "deepinfra": DeepinfraApiService,
    "ai21": AI21ApiService,
    "huggingface": HuggingfaceApiService,
    "ollama": OllamaApiService,
    "nscale": NscaleApiService,
    "lambda": LambdaApiService,
}


def get_service(provider_name: str, **kwargs):
    """Get API service instance for provider."""
    service_class = PROVIDERS.get(provider_name)
    if not service_class:
        raise ValueError(f"Unknown provider: {provider_name}")
    return service_class(**kwargs)


__all__ = [
    "AnthropicApiService",
    "OpenAIApiService",
    "DeepSeekApiService",
    "GroqApiService",
    "GeminiApiService",
    "MistralApiService",
    "xAIApiService",
    "NvidiaApiService",
    "OpenRouterApiService",
    "CerebrasApiService",
    "TogetherApiService",
    "GithubApiService",
    "CloudflareApiService",
    "FireworksApiService",
    "OpencodeApiService",
    "CohereApiService",
    "PerplexityApiService",
    "SambanovaApiService",
    "DeepinfraApiService",
    "AI21ApiService",
    "HuggingfaceApiService",
    "OllamaApiService",
    "OllamaClientCompat",
    "NscaleApiService",
    "LambdaApiService",
    "PROVIDERS",
    "get_service",
    # Error mapping (Issue #3)
    "map_provider_error",
    "AnthropicErrorMapper",
    "OpenAIErrorMapper",
    "OllamaErrorMapper",
    "GeminiErrorMapper",
    "GroqErrorMapper",
]
