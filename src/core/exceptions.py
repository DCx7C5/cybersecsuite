
"""Custom exceptions for CyberSecSuite with optional full traceback."""

import traceback
from typing import Optional


class CSSException(Exception):
    """
    Base exception for all CyberSecSuite exceptions.
    
    Supports optional full traceback capture for debugging.
    Subclass this for domain-specific exceptions.
    """
    
    def __init__(
        self,
        message: str,
        capture_traceback: bool = False,
        context: Optional[dict] = None,
    ):
        """
        Initialize CSSException.
        
        Args:
            message: Human-readable error message
            capture_traceback: If True, capture full traceback for debugging
            context: Optional dict with additional context (provider, model, etc.)
        """
        self.message = message
        self.context = context or {}
        self.full_traceback = traceback.format_exc() if capture_traceback else None
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """Return message. Use get_full_error() for traceback."""
        return self.message
    
    def get_full_error(self) -> str:
        """Get formatted error with optional full traceback."""
        if self.full_traceback:
            return f"{self.message}\n\nTraceback:\n{self.full_traceback}"
        return self.message


# ==============================================================================
# LLM API Service Exceptions (Layer 1 — api_services/)
# ==============================================================================


class LLMApiServiceError(CSSException):
    """Base exception for LLM API service errors."""
    
    def __init__(
        self,
        message: str,
        provider_name: Optional[str] = None,
        model_id: Optional[str] = None,
        capture_traceback: bool = False,
        context: Optional[dict] = None,
    ):
        """
        Initialize LLM API service error.
        
        Args:
            message: Error message
            provider_name: Name of LLM provider (e.g., 'openai', 'anthropic')
            model_id: Model ID that was being used
            capture_traceback: If True, capture full traceback
            context: Additional context dict
        """
        ctx = context or {}
        if provider_name:
            ctx["provider"] = provider_name
        if model_id:
            ctx["model_id"] = model_id
        
        super().__init__(message, capture_traceback=capture_traceback, context=ctx)
        self.provider_name = provider_name
        self.model_id = model_id


class ApiKeyMissingError(LLMApiServiceError):
    """Raised when API key is missing for a provider."""
    
    def __init__(
        self,
        provider_name: str,
        message: Optional[str] = None,
        capture_traceback: bool = False,
    ):
        """
        Initialize ApiKeyMissingError.
        
        Args:
            provider_name: Name of provider missing API key
            message: Optional custom message
            capture_traceback: If True, capture full traceback
        """
        if not message:
            message = f"API key missing for provider '{provider_name}'"
        
        super().__init__(
            message,
            provider_name=provider_name,
            capture_traceback=capture_traceback,
        )


class ApiKeyInvalidError(LLMApiServiceError):
    """Raised when API key is invalid or expired."""
    pass


class ProviderConnectionError(LLMApiServiceError):
    """Raised when connection to LLM provider fails."""
    pass


class RateLimitError(LLMApiServiceError):
    """Raised when rate limit is exceeded."""
    
    def __init__(
        self,
        provider_name: str,
        retry_after_seconds: Optional[int] = None,
        capture_traceback: bool = False,
        context: Optional[dict] = None,
    ):
        """Initialize RateLimitError with retry info."""
        ctx = context or {}
        if retry_after_seconds:
            ctx["retry_after_seconds"] = retry_after_seconds
        
        message = f"Rate limit exceeded for '{provider_name}'"
        if retry_after_seconds:
            message += f" (retry after {retry_after_seconds}s)"
        
        super().__init__(
            message,
            provider_name=provider_name,
            capture_traceback=capture_traceback,
            context=ctx,
        )
        self.retry_after_seconds = retry_after_seconds


class ModelNotFoundError(LLMApiServiceError):
    """Raised when requested model is not found."""
    pass


class FeatureNotSupportedError(LLMApiServiceError):
    """Raised when a feature is not supported by the model or provider."""
    pass


class InvalidParameterError(LLMApiServiceError):
    """Raised when invalid parameters are passed to LLM call."""
    pass


class StreamingError(LLMApiServiceError):
    """Raised when streaming fails."""
    pass


class ProviderTimeoutError(LLMApiServiceError):
    """Raised when provider request times out."""
    pass


# ==============================================================================
# Core LLM Harness Exceptions (Layer 2 — core/llm_harness/)
# ==============================================================================


class LLMHarnessError(CSSException):
    """Base exception for LLM harness core logic errors."""
    pass


class ContextError(LLMHarnessError):
    """Raised when context processing fails."""
    pass


class CapabilityDiscoveryError(LLMHarnessError):
    """Raised when capability discovery fails."""
    pass


class ProviderRegistryError(LLMHarnessError):
    """Raised when provider registry operations fail."""
    pass


class A2AStreamingError(LLMHarnessError):
    """Raised when A2A (agent-to-agent) streaming fails."""
    pass


class ResponseInjectionError(LLMHarnessError):
    """Raised when response injection fails."""
    pass


class ModelExecutionError(LLMHarnessError):
    """Raised when model execution fails."""
    pass


# ==============================================================================
# Configuration & Validation Exceptions
# ==============================================================================


class ConfigurationError(CSSException):
    """Raised when configuration is invalid or incomplete."""
    pass


class ValidationError(CSSException):
    """Raised when validation fails."""
    pass


# ==============================================================================
# Ollama-Specific Exceptions
# ==============================================================================


class OllamaError(CSSException):
    """Base exception for Ollama-specific errors."""
    pass


class OllamaConnectionError(OllamaError):
    """Raised when cannot connect to local Ollama server."""
    pass


class OllamaModelNotFoundError(OllamaError):
    """Raised when Ollama model is not found locally."""
    pass


class OllamaModelLoadError(OllamaError):
    """Raised when Ollama model fails to load."""
    pass


# ==============================================================================
# Unified Error Hierarchy (for Retry Orchestrator)
# Issue #3: Map all provider errors to 5-type hierarchy
# ==============================================================================


class UnifiedLLMError(CSSException):
    """
    Base for unified error classification across all providers.
    
    Maps provider-specific errors to 5 standard types:
    - AuthError: Authentication/authorization failed
    - RateLimitError: Rate limit exceeded
    - TimeoutError: Request timed out
    - GatewayError: Provider returned 5xx/unavailable
    - UnknownError: Everything else
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        provider: Optional[str] = None,
        original_error: Optional[Exception] = None,
        capture_traceback: bool = False,
        context: Optional[dict] = None,
    ):
        """
        Initialize unified error.
        
        Args:
            message: Human-readable message
            error_code: Provider-specific error code
            provider: Provider name (anthropic, openai, ollama, etc)
            original_error: Original exception from SDK
            capture_traceback: If True, capture full traceback
            context: Additional context dict
        """
        ctx = context or {}
        if provider:
            ctx["provider"] = provider
        if error_code:
            ctx["error_code"] = error_code
        
        super().__init__(message, capture_traceback=capture_traceback, context=ctx)
        self.error_code = error_code
        self.provider = provider
        self.original_error = original_error


class AuthError(UnifiedLLMError):
    """Authentication or authorization failed (401, 403, invalid credentials)."""
    pass


class RateLimitError(UnifiedLLMError):
    """Rate limit exceeded (429, quota exhausted)."""
    
    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        retry_after_seconds: Optional[float] = None,
        original_error: Optional[Exception] = None,
        context: Optional[dict] = None,
    ):
        """Initialize rate limit error with retry info."""
        ctx = context or {}
        if retry_after_seconds:
            ctx["retry_after_seconds"] = retry_after_seconds
        
        super().__init__(
            message,
            provider=provider,
            original_error=original_error,
            context=ctx,
        )
        self.retry_after_seconds = retry_after_seconds


class TimeoutError(UnifiedLLMError):
    """Request timed out (connection timeout, read timeout, etc)."""
    pass


class GatewayError(UnifiedLLMError):
    """Provider error (5xx, service unavailable, temporary failure)."""
    pass


class UnknownError(UnifiedLLMError):
    """Unclassified error (fallback for unmapped errors)."""
    pass
