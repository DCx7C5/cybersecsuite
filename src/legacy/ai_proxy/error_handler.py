"""
Error Handling & Retry Logic for FastAPI/ASGI.

Provides:
- Custom exception types for different error scenarios
- Automatic retry logic with exponential backoff
- Structured error logging and propagation
- Context-aware error messages for frontend
"""


import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, ParamSpec

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.requests import Request

logger = logging.getLogger("error_handler")

T = TypeVar("T")
P = ParamSpec("P")


class ErrorSeverity(str, Enum):
    """Error severity levels for frontend display."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCode(str, Enum):
    """Standardized error codes for frontend error handling."""
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND_ERROR = "NOT_FOUND_ERROR"
    CONFLICT_ERROR = "CONFLICT_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    SERVICE_UNAVAILABLE_ERROR = "SERVICE_UNAVAILABLE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    OLLAMA_CONNECTION_ERROR = "OLLAMA_CONNECTION_ERROR"
    PROVIDER_ERROR = "PROVIDER_ERROR"


class CyberSecError(Exception):
    """Base error class for CyberSecSuite."""

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
        context: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize CyberSecError.

        Args:
            message: Human-readable error message
            code: Standardized error code
            severity: Error severity for frontend
            status_code: HTTP status code
            details: Additional error details
            context: Contextual information for debugging
        """
        self.message = message
        self.code = code
        self.severity = severity
        self.status_code = status_code
        self.details = details or {}
        self.context = context or {}
        self.timestamp = time.time()
        super().__init__(message)

    def to_response(self) -> JSONResponse:
        """Convert to FastAPI JSONResponse."""
        return JSONResponse(
            status_code=self.status_code,
            content={
                "error": {
                    "message": self.message,
                    "code": self.code.value,
                    "severity": self.severity.value,
                    "details": self.details,
                    "timestamp": self.timestamp,
                }
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dict for logging/serialization."""
        return {
            "message": self.message,
            "code": self.code.value,
            "severity": self.severity.value,
            "status_code": self.status_code,
            "details": self.details,
            "context": self.context,
            "timestamp": self.timestamp,
        }


class ValidationError(CyberSecError):
    """Validation error (HTTP 422)."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.VALIDATION_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=422,
            details=details,
        )


class AuthenticationError(CyberSecError):
    """Authentication error (HTTP 401)."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHENTICATION_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=401,
            details=details,
        )


class AuthorizationError(CyberSecError):
    """Authorization error (HTTP 403)."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.AUTHORIZATION_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=403,
            details=details,
        )


class NotFoundError(CyberSecError):
    """Resource not found (HTTP 404)."""

    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(
            message=message,
            code=ErrorCode.NOT_FOUND_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=404,
            details={"resource": resource, "id": resource_id},
        )


class ConflictError(CyberSecError):
    """Conflict error (HTTP 409)."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=message,
            code=ErrorCode.CONFLICT_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=409,
            details=details,
        )


class RateLimitError(CyberSecError):
    """Rate limit exceeded (HTTP 429)."""

    def __init__(self, provider: str, retry_after_seconds: int = 60):
        super().__init__(
            message=f"Rate limit exceeded for provider: {provider}",
            code=ErrorCode.RATE_LIMIT_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=429,
            details={"provider": provider, "retry_after_seconds": retry_after_seconds},
        )


class TimeoutError(CyberSecError):
    """Timeout error (HTTP 504)."""

    def __init__(self, operation: str, timeout_seconds: float = 0):
        super().__init__(
            message=f"Operation timed out: {operation}",
            code=ErrorCode.TIMEOUT_ERROR,
            severity=ErrorSeverity.WARNING,
            status_code=504,
            details={"operation": operation, "timeout_seconds": timeout_seconds},
        )


class ServiceUnavailableError(CyberSecError):
    """Service unavailable (HTTP 503)."""

    def __init__(self, service: str, reason: str = ""):
        super().__init__(
            message=f"Service unavailable: {service}",
            code=ErrorCode.SERVICE_UNAVAILABLE_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=503,
            details={"service": service, "reason": reason},
        )


class OllamaConnectionError(CyberSecError):
    """Ollama connection error."""

    def __init__(self, base_url: str, reason: str = ""):
        super().__init__(
            message=f"Cannot connect to Ollama at {base_url}",
            code=ErrorCode.OLLAMA_CONNECTION_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=503,
            details={"base_url": base_url, "reason": reason},
        )


class ProviderError(CyberSecError):
    """Provider-specific error."""

    def __init__(self, provider: str, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(
            message=f"Provider error ({provider}): {message}",
            code=ErrorCode.PROVIDER_ERROR,
            severity=ErrorSeverity.ERROR,
            status_code=502,
            details={"provider": provider, **(details or {})},
        )


class DatabaseError(CyberSecError):
    """Database operation error."""

    def __init__(self, operation: str, reason: str = ""):
        super().__init__(
            message=f"Database error during {operation}",
            code=ErrorCode.DATABASE_ERROR,
            severity=ErrorSeverity.CRITICAL,
            status_code=500,
            details={"operation": operation, "reason": reason},
        )


class RetryConfig(BaseModel):
    """Configuration for retry logic."""

    max_retries: int = Field(default=3, ge=1, le=10)
    initial_delay_seconds: float = Field(default=0.1, gt=0)
    max_delay_seconds: float = Field(default=30.0, gt=0)
    exponential_base: float = Field(default=2.0, gt=1)
    jitter: bool = Field(default=True)


async def retry_with_backoff(
    func: Callable[P, asyncio.coroutine],
    *args: P.args,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    **kwargs: P.kwargs,
) -> Any:
    """
    Execute async function with exponential backoff retry.

    Args:
        func: Async function to execute
        args: Positional arguments for func
        config: Retry configuration
        on_retry: Callback function called on retry (retry_count, exception)
        kwargs: Keyword arguments for func

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    if config is None:
        config = RetryConfig()

    last_exception: Optional[Exception] = None

    for attempt in range(config.max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            is_last_attempt = attempt == config.max_retries - 1

            if is_last_attempt:
                logger.error(f"Retry exhausted for {func.__name__}: {e}")
                raise

            # Calculate delay with exponential backoff
            delay = min(
                config.initial_delay_seconds * (config.exponential_base ** attempt),
                config.max_delay_seconds,
            )

            # Add jitter to prevent thundering herd
            if config.jitter:
                import random
                delay *= random.uniform(0.5, 1.5)

            if on_retry:
                on_retry(attempt + 1, e)

            logger.warning(
                f"Retry {attempt + 1}/{config.max_retries} for {func.__name__} "
                f"after {delay:.2f}s: {e}"
            )
            await asyncio.sleep(delay)

    # Should not reach here, but raise the last exception just in case
    raise last_exception or CyberSecError("Unknown error during retry")


async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for FastAPI/Starlette.

    Args:
        request: Starlette request object
        exc: Exception to handle

    Returns:
        JSONResponse with error details
    """
    # Log the exception
    logger.error(
        f"Unhandled exception for {request.method} {request.url.path}",
        exc_info=exc,
    )

    # If it's already a CyberSecError, use its response
    if isinstance(exc, CyberSecError):
        return exc.to_response()

    # Convert standard exceptions to CyberSecErrors
    if isinstance(exc, TimeoutError):
        error = TimeoutError("Operation")
    elif isinstance(exc, ValueError):
        error = ValidationError(str(exc))
    else:
        error = CyberSecError(
            message="An unexpected error occurred",
            code=ErrorCode.INTERNAL_ERROR,
            severity=ErrorSeverity.CRITICAL,
            status_code=500,
            context={"exception_type": type(exc).__name__},
        )

    return error.to_response()
