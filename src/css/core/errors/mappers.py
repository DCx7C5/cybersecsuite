"""
Concrete error mappers: Provider-specific error mapping.

Maps each provider's SDK errors to the unified 5-type error hierarchy.
"""

from collections.abc import Callable
from typing import override

import grpc

from css.core.exceptions import (
    AuthError,
    GatewayError,
    RateLimitError,
    TimeoutError,
    UnknownError,
)
from css.core.base.enums import ProviderType
from css.core.base.error_mapper import BaseErrorMapper


class AnthropicErrorMapper(BaseErrorMapper):
    """Map Anthropic SDK errors to unified types using provider-specific patterns."""

    @staticmethod
    @override
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        return BaseErrorMapper.map_error(error, provider="anthropic")


class OpenAIErrorMapper(BaseErrorMapper):
    """Map OpenAI SDK errors to unified types using provider-specific patterns."""

    @staticmethod
    @override
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        return BaseErrorMapper.map_error(error, provider="openai")


class OllamaErrorMapper(BaseErrorMapper):
    """Map Ollama errors (usually aiohttp exceptions) to unified types."""

    @staticmethod
    @override
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        return BaseErrorMapper.map_error(error, provider="ollama")


class GeminiErrorMapper(BaseErrorMapper):
    """Map Google Gemini errors to unified types."""

    @staticmethod
    @override
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        return BaseErrorMapper.map_error(error, provider="gemini")


class GroqErrorMapper(BaseErrorMapper):
    """Map Groq errors to unified types."""

    @staticmethod
    @override
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        return BaseErrorMapper.map_error(error, provider="groq")


class XAIErrorMapper(BaseErrorMapper):
    """Map xAI gRPC errors to unified types with status-aware handling."""

    @staticmethod
    @override
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        if isinstance(error, grpc.RpcError):
            status_code = error.code()
            if status_code in (grpc.StatusCode.UNAUTHENTICATED, grpc.StatusCode.PERMISSION_DENIED):
                return AuthError(str(error), provider="xai", original_error=error)
            if status_code == grpc.StatusCode.RESOURCE_EXHAUSTED:
                return RateLimitError(str(error), provider="xai", original_error=error)
            if status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
                return TimeoutError(str(error), provider="xai", original_error=error)
            if status_code in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.INTERNAL):
                return GatewayError(str(error), provider="xai", original_error=error)
            return UnknownError(str(error), provider="xai", original_error=error)
        return BaseErrorMapper.map_error(error, provider="xai")


ERROR_MAPPERS: dict[ProviderType, Callable[[Exception], Exception]] = {
    ProviderType.ANTHROPIC: AnthropicErrorMapper.map_error,
    ProviderType.OPENAI: OpenAIErrorMapper.map_error,
    ProviderType.OLLAMA: OllamaErrorMapper.map_error,
    ProviderType.GEMINI: GeminiErrorMapper.map_error,
    ProviderType.GROQ: GroqErrorMapper.map_error,
    ProviderType.XAI: XAIErrorMapper.map_error,
}


def map_provider_error(provider_id: ProviderType, error: Exception) -> Exception:
    """
    Map any provider error to unified type.

    Uses provider-specific mappers when available, falls back to BaseErrorMapper
    for consistent error handling across all REST providers.

    Args:
        provider_id: Provider type
        error: Original exception from SDK

    Returns:
        Mapped exception (UnifiedLLMError subclass)
    """
    mapper = ERROR_MAPPERS.get(provider_id)
    if mapper:
        return mapper(error)

    provider_name = provider_id.value if provider_id else "unknown"
    return BaseErrorMapper.map_error(error, provider=provider_name)
