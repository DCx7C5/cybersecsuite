"""
API Services Module — 25 LLM and service providers.

Each provider lives in src/api_services/{provider_name}/ and exports an *ApiService class
that inherits from BaseApiServiceClient (in src/core/api_service_client/).
"""

# Tier 1: Major cloud providers
from .anthropic import AnthropicApiService
from .openai import OpenAIApiService
from .gemini import GeminiApiService

# Tier 1.5: High-quality alternatives
from .deepseek import DeepSeekApiService
from .groq import GroqApiService
from .mistral import MistralApiService
from .xai import xAIApiService
from .together import TogetherApiService
from .perplexity import PerplexityApiService

# Tier 2: Routing / Multi-provider
from .openrouter import OpenRouterApiService

# Tier 2.5: Specialized services
from .nvidia import NvidiaApiService
from .cerebras import CerebrasApiService
from .sambanova import SambanovaApiService
from .deepinfra import DeepinfraApiService
from .cohere import CohereApiService
from .ai21 import AI21ApiService
from .huggingface import HuggingfaceApiService
from .nscale import NscaleApiService
from .lambda_api import LambdaApiService

# Tier 3: Utility services
from .github import GithubApiService
from .cloudflare import CloudflareApiService
from .fireworks import FireworksApiService
from .opencode import OpencodeApiService

# Local providers
from .ollama import OllamaApiService

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
    "NscaleApiService",
    "LambdaApiService",
    "PROVIDERS",
    "get_service",
]
