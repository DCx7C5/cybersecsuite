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
from typing import Optional, Callable
from core.types.api_services import ProviderType
from core.exceptions import (
    AuthError,
    RateLimitError,
    TimeoutError,
    GatewayError,
    UnknownError,
)


class ErrorMapper:
    """Base error mapper with common patterns."""
    
    @staticmethod
    def extract_status_code(error_message: str) -> Optional[int]:
        """Extract HTTP status code from error message."""
        match = re.search(r'\b([4-5]\d{2})\b', error_message)
        return int(match.group(1)) if match else None
    
    @staticmethod
    def extract_retry_after(error_message: str) -> Optional[float]:
        """Extract retry-after seconds from error message."""
        # Look for patterns like "retry-after: 60" or "retry_after_seconds: 30"
        match = re.search(r'retry[_-]after[:\s]+(\d+)', error_message, re.IGNORECASE)
        return float(match.group(1)) if match else None


class AnthropicErrorMapper(ErrorMapper):
    """Map Anthropic SDK errors to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Anthropic error to unified type."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Extract status code if present
        status_code = AnthropicErrorMapper.extract_status_code(str(error))
        
        # 401/403 → AuthError
        if status_code in [401, 403] or any(word in error_str for word in 
            ['authentication', 'unauthorized', 'invalid_api_key', 'forbidden']):
            return AuthError(
                str(error),
                provider="anthropic",
                original_error=error,
            )
        
        # 429 → RateLimitError
        if status_code == 429 or any(word in error_str for word in ['rate limit', 'rate-limited', 'quota']):
            retry_after = AnthropicErrorMapper.extract_retry_after(str(error))
            return RateLimitError(
                str(error),
                provider="anthropic",
                retry_after_seconds=retry_after,
                original_error=error,
            )
        
        # Timeout → TimeoutError
        if any(word in error_str for word in ['timeout', 'timed out', 'read timed out']):
            return TimeoutError(
                str(error),
                provider="anthropic",
                original_error=error,
            )
        
        # 5xx → GatewayError
        if status_code and 500 <= status_code < 600:
            return GatewayError(
                str(error),
                provider="anthropic",
                original_error=error,
            )
        
        # Service unavailable → GatewayError
        if any(word in error_str for word in ['503', '502', '504', 'unavailable', 'service down', 'gateway']):
            return GatewayError(
                str(error),
                provider="anthropic",
                original_error=error,
            )
        
        # Default → UnknownError
        return UnknownError(
            str(error),
            provider="anthropic",
            original_error=error,
        )


class OpenAIErrorMapper(ErrorMapper):
    """Map OpenAI SDK errors to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map OpenAI error to unified type."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Extract status code if present
        status_code = OpenAIErrorMapper.extract_status_code(str(error))
        
        # 401/403 → AuthError
        if status_code in [401, 403] or any(word in error_str for word in 
            ['authentication', 'unauthorized', 'invalid_api_key', 'forbidden', 'invalid api key']):
            return AuthError(
                str(error),
                provider="openai",
                original_error=error,
            )
        
        # 429 → RateLimitError
        if status_code == 429 or any(word in error_str for word in ['rate limit', 'rate-limited', 'quota']):
            retry_after = OpenAIErrorMapper.extract_retry_after(str(error))
            return RateLimitError(
                str(error),
                provider="openai",
                retry_after_seconds=retry_after,
                original_error=error,
            )
        
        # Timeout → TimeoutError
        if any(word in error_str for word in ['timeout', 'timed out', 'read timed out', 'connection timeout']):
            return TimeoutError(
                str(error),
                provider="openai",
                original_error=error,
            )
        
        # 5xx → GatewayError
        if status_code and 500 <= status_code < 600:
            return GatewayError(
                str(error),
                provider="openai",
                original_error=error,
            )
        
        # Service unavailable → GatewayError
        if any(word in error_str for word in ['503', '502', '504', 'unavailable', 'service unavailable']):
            return GatewayError(
                str(error),
                provider="openai",
                original_error=error,
            )
        
        # Default → UnknownError
        return UnknownError(
            str(error),
            provider="openai",
            original_error=error,
        )


class OllamaErrorMapper(ErrorMapper):
    """Map Ollama errors (usually aiohttp exceptions) to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Ollama error to unified type."""
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Extract status code if present
        status_code = OllamaErrorMapper.extract_status_code(str(error))
        
        # 401/403 → AuthError
        if status_code in [401, 403]:
            return AuthError(
                str(error),
                provider="ollama",
                original_error=error,
            )
        
        # 429 → RateLimitError
        if status_code == 429:
            return RateLimitError(
                str(error),
                provider="ollama",
                original_error=error,
            )
        
        # Connection errors → TimeoutError or GatewayError
        if any(word in error_str for word in ['connection', 'refused', 'unreachable', 'econnrefused', 'no such file']):
            return GatewayError(
                str(error),
                provider="ollama",
                original_error=error,
            )
        
        # Timeout → TimeoutError
        if any(word in error_str for word in ['timeout', 'timed out']):
            return TimeoutError(
                str(error),
                provider="ollama",
                original_error=error,
            )
        
        # 5xx → GatewayError
        if status_code and 500 <= status_code < 600:
            return GatewayError(
                str(error),
                provider="ollama",
                original_error=error,
            )
        
        # Default → UnknownError
        return UnknownError(
            str(error),
            provider="ollama",
            original_error=error,
        )


class GeminiErrorMapper(ErrorMapper):
    """Map Google Gemini errors to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Gemini error to unified type."""
        error_str = str(error).lower()
        status_code = GeminiErrorMapper.extract_status_code(str(error))
        
        if status_code in [401, 403]:
            return AuthError(str(error), provider="gemini", original_error=error)
        if status_code == 429:
            return RateLimitError(str(error), provider="gemini", original_error=error)
        if any(w in error_str for w in ['timeout', 'timed out']):
            return TimeoutError(str(error), provider="gemini", original_error=error)
        if status_code and 500 <= status_code < 600:
            return GatewayError(str(error), provider="gemini", original_error=error)
        
        return UnknownError(str(error), provider="gemini", original_error=error)


class GroqErrorMapper(ErrorMapper):
    """Map Groq errors to unified types."""
    
    @staticmethod
    def map_error(error: Exception) -> Exception:
        """Map Groq error to unified type."""
        error_str = str(error).lower()
        status_code = GroqErrorMapper.extract_status_code(str(error))
        
        if status_code in [401, 403]:
            return AuthError(str(error), provider="groq", original_error=error)
        if status_code == 429:
            return RateLimitError(str(error), provider="groq", original_error=error)
        if any(w in error_str for w in ['timeout', 'timed out']):
            return TimeoutError(str(error), provider="groq", original_error=error)
        if status_code and 500 <= status_code < 600:
            return GatewayError(str(error), provider="groq", original_error=error)
        
        return UnknownError(str(error), provider="groq", original_error=error)


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
    
    # Default: wrap unknown providers in UnknownError
    return UnknownError(
        str(error),
        provider=provider_id.value if provider_id else "unknown",
        original_error=error,
    )
