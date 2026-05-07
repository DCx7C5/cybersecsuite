"""
Error mappers: Convert provider-specific errors to unified 5-type hierarchy.

Issue #3: Error Code Mapping — Map all SDK errors to standard types:
  - AuthError: 401, 403, invalid credentials
  - RateLimitError: 429, quota exceeded
  - TimeoutError: Connection timeout, read timeout
  - GatewayError: 5xx, service unavailable
  - UnknownError: Everything else (fallback)
"""

import re
from collections.abc import Callable
from css.core.exceptions import (
    AuthError,
    RateLimitError,
    TimeoutError,
    GatewayError,
    UnknownError,
)
from css.core.types import ProviderType


class ErrorMapper:
    """Base error mapper with common patterns."""
    
    @staticmethod
    def extract_status_code(error_message: str) -> int | None:
        """Extract HTTP status code from error message."""
        match = re.search(r'\b([4-5]\d{2})\b', error_message)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def extract_retry_after(error_message: str) -> float | None:
        """Extract retry-after seconds from error message."""
        # Look for patterns like "retry-after: 60" or "retry_after_seconds: 30"
        match = re.search(r'retry[_-]after[:\s]+(\d+)', error_message, re.IGNORECASE)
        return float(match.group(1)) if match else None


class BaseErrorMapper(ErrorMapper):
    """Generic error mapper for aiohttp and REST-based providers.
    
    Maps HTTP status codes and common error patterns to 5 unified error types:
    - AuthError: 401, 403, authentication failures
    - RateLimitError: 429, quota exceeded
    - TimeoutError: Connection timeouts, read timeouts
    - GatewayError: 5xx errors, service unavailable
    - UnknownError: All other errors (fallback)
    
    Used by all 19 REST providers as a fallback when provider-specific mappers
    aren't available or for consistent error handling across the platform.
    """
    
    # Pattern keywords for each error type (provider-agnostic)
    AUTH_PATTERNS = {
        'authentication', 'unauthorized', 'forbidden', 'invalid_api_key',
        'invalid api key', 'auth', 'api key', 'token invalid', 'credentials'
    }
    
    RATE_LIMIT_PATTERNS = {
        'rate limit', 'rate-limited', 'rate_limited', 'quota', 'quota_exceeded',
        'quota exceeded', 'throttle', 'too many requests', 'rate_limit'
    }
    
    TIMEOUT_PATTERNS = {
        'timeout', 'timed out', 'read timed out', 'connection timeout',
        'connect timeout', 'deadline', 'econnreset', 'etimedout'
    }
    
    GATEWAY_PATTERNS = {
        'service unavailable', 'service down', 'bad gateway', 'gateway',
        'connection refused', 'connection error', 'econnrefused', 'unreachable',
        'unavailable', 'temporarily unavailable', 'maintenance'
    }
    
    @staticmethod
    def map_error(error: Exception, provider: str = "unknown") -> Exception:
        """Map any provider error to unified type using generic patterns.
        
        Args:
            error: Original exception from aiohttp or provider SDK
            provider: Provider name for error context (optional)
        
        Returns:
            Mapped exception (UnifiedLLMError subclass)
        """
        error_str = str(error).lower()
        status_code = BaseErrorMapper.extract_status_code(str(error))
        
        # 401/403 → AuthError
        if status_code in [401, 403] or any(
            pattern in error_str for pattern in BaseErrorMapper.AUTH_PATTERNS
        ):
            return AuthError(
                str(error),
                provider=provider,
                original_error=error,
            )
        
        # 429 → RateLimitError
        if status_code == 429 or any(
            pattern in error_str for pattern in BaseErrorMapper.RATE_LIMIT_PATTERNS
        ):
            retry_after = BaseErrorMapper.extract_retry_after(str(error))
            return RateLimitError(
                str(error),
                provider=provider,
                retry_after_seconds=retry_after,
                original_error=error,
            )
        
        # Timeout → TimeoutError
        if any(pattern in error_str for pattern in BaseErrorMapper.TIMEOUT_PATTERNS):
            return TimeoutError(
                str(error),
                provider=provider,
                original_error=error,
            )
        
        # 5xx → GatewayError
        if status_code and 500 <= status_code < 600:
            return GatewayError(
                str(error),
                provider=provider,
                original_error=error,
            )
        
        # Gateway patterns → GatewayError
        if any(pattern in error_str for pattern in BaseErrorMapper.GATEWAY_PATTERNS):
            return GatewayError(
                str(error),
                provider=provider,
                original_error=error,
            )
        
        # Default → UnknownError
        return UnknownError(
            str(error),
            provider=provider,
            original_error=error,
        )


class AnthropicErrorMapper(BaseErrorMapper):
    """Map Anthropic SDK errors to unified types using provider-specific patterns."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Anthropic error to unified type."""
        # Use generic mapping (BaseErrorMapper.map_error)
        return BaseErrorMapper.map_error(error, provider="anthropic")


class OpenAIErrorMapper(BaseErrorMapper):
    """Map OpenAI SDK errors to unified types using provider-specific patterns."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map OpenAI error to unified type."""
        return BaseErrorMapper.map_error(error, provider="openai")


class OllamaErrorMapper(BaseErrorMapper):
    """Map Ollama errors (usually aiohttp exceptions) to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Ollama error to unified type."""
        return BaseErrorMapper.map_error(error, provider="ollama")


class GeminiErrorMapper(BaseErrorMapper):
    """Map Google Gemini errors to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Gemini error to unified type."""
        return BaseErrorMapper.map_error(error, provider="gemini")


class GroqErrorMapper(BaseErrorMapper):
    """Map Groq errors to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Groq error to unified type."""
        return BaseErrorMapper.map_error(error, provider="groq")


# Dispatcher: maps provider → mapper function
ERROR_MAPPERS: dict[ProviderType, Callable[[Exception], Exception]] = {
    ProviderType.ANTHROPIC: AnthropicErrorMapper.map_error,
    ProviderType.OPENAI: OpenAIErrorMapper.map_error,
    ProviderType.OLLAMA: OllamaErrorMapper.map_error,
    ProviderType.GEMINI: GeminiErrorMapper.map_error,
    ProviderType.GROQ: GroqErrorMapper.map_error,
    # Add more mappers as needed for other providers
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
    
    Example:
        try:
            response = await sdk.call_llm(model, messages)
        except Exception as e:
            mapped = map_provider_error(ProviderType.ANTHROPIC, e)
            if isinstance(mapped, AuthError):
                log_authentication_failure(...)
            elif isinstance(mapped, RateLimitError):
                wait_and_retry(mapped.retry_after_seconds)
            else:
                raise mapped
    """
    mapper = ERROR_MAPPERS.get(provider_id)
    if mapper:
        return mapper(error)
    
    # Fallback: use BaseErrorMapper for unknown providers (generic REST providers)
    provider_name = provider_id.value if provider_id else "unknown"
    return BaseErrorMapper.map_error(error, provider=provider_name)
