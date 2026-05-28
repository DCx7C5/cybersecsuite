"""
Base error mapper: Convert provider-specific errors to unified 5-type hierarchy.

Issue #3: Error Code Mapping — Map all SDK errors to standard types:
  - AuthError: 401, 403, invalid credentials
  - RateLimitError: 429, quota exceeded
  - TimeoutError: Connection timeout, read timeout
  - GatewayError: 5xx, service unavailable
  - UnknownError: Everything else (fallback)
"""

import re

from css.core.exceptions import (
    AuthError,
    GatewayError,
    RateLimitError,
    TimeoutError,
    UnknownError,
)


class BaseErrorMapper:
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

    AUTH_PATTERNS = {
        'authentication', 'unauthorized', 'forbidden', 'invalid_api_key',
        'invalid api key', 'authentication', 'api key', 'token invalid', 'credentials',
    }

    RATE_LIMIT_PATTERNS = {
        'rate limit', 'rate-limited', 'rate_limited', 'quota', 'quota_exceeded',
        'quota exceeded', 'throttle', 'too many requests', 'rate_limit',
    }

    TIMEOUT_PATTERNS = {
        'timeout', 'timed out', 'read timed out', 'connection timeout',
        'connect timeout', 'deadline', 'econnreset', 'etimedout',
    }

    GATEWAY_PATTERNS = {
        'service unavailable', 'service down', 'bad gateway', 'gateway',
        'connection refused', 'connection error', 'econnrefused', 'unreachable',
        'unavailable', 'temporarily unavailable', 'maintenance',
    }

    @staticmethod
    def extract_status_code(error_message: str) -> int | None:
        """Extract HTTP status code from error message."""
        match = re.search(r'\b([4-5]\d{2})\b', error_message)
        return int(match.group(1)) if match else None

    @staticmethod
    def extract_retry_after(error_message: str) -> float | None:
        """Extract retry-after seconds from error message."""
        match = re.search(r'retry[_-]after[:\s]+(\d+)', error_message, re.IGNORECASE)
        return float(match.group(1)) if match else None

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

        if status_code in (401, 403) or any(
            pattern in error_str for pattern in BaseErrorMapper.AUTH_PATTERNS
        ):
            return AuthError(str(error), provider=provider, original_error=error)

        if status_code == 429 or any(
            pattern in error_str for pattern in BaseErrorMapper.RATE_LIMIT_PATTERNS
        ):
            retry_after = BaseErrorMapper.extract_retry_after(str(error))
            return RateLimitError(
                str(error), provider=provider, retry_after_seconds=retry_after, original_error=error,
            )

        if any(pattern in error_str for pattern in BaseErrorMapper.TIMEOUT_PATTERNS):
            return TimeoutError(str(error), provider=provider, original_error=error)

        if status_code and 500 <= status_code < 600:
            return GatewayError(str(error), provider=provider, original_error=error)

        if any(pattern in error_str for pattern in BaseErrorMapper.GATEWAY_PATTERNS):
            return GatewayError(str(error), provider=provider, original_error=error)

        return UnknownError(str(error), provider=provider, original_error=error)
