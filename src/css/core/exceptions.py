"""Custom exceptions for CyberSecSuite with optional full traceback."""

import traceback


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
        context: dict | None = None,
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
# Base Core Exception (css/core/*/)
# ==============================================================================

class BaseCoreException(CSSException):
    """
    Base exception for all core/ errors.

    All module-specific exceptions (marketplace, streaming, etc.)
    should inherit from this class.

    Attributes:
        dir_name: Optional name of the core dir (e.g., 'streaming', 'marketplace')
        context: Optional dict with additional error context
    """

    def __init__(
            self,
            message: str,
            dir_name: str | None = None,
            capture_traceback: bool = False,
            context: dict | None = None,
    ):
        ctx = context or {}
        if dir_name:
            ctx["dir"] = dir_name

        super().__init__(message, capture_traceback=capture_traceback, context=ctx)
        self.dir_name = dir_name

# ==============================================================================
# Base Module Exception (css/modules/*/)
# ==============================================================================

class BaseModuleException(CSSException):
    """
    Base exception for all modules/ module errors.

    All module-specific exceptions (google_a2a, marketplace, streaming, etc.)
    should inherit from this class.

    Attributes:
        module_name: Optional name of the module (e.g., 'google_a2a', 'marketplace')
        context: Optional dict with additional error context
    """

    def __init__(
            self,
            message: str,
            module_name: str | None = None,
            capture_traceback: bool = False,
            context: dict | None = None,
    ):
        ctx = context or {}
        if module_name:
            ctx["module"] = module_name

        super().__init__(message, capture_traceback=capture_traceback, context=ctx)
        self.module_name = module_name


# ==============================================================================
# Base Provider Exceptions (css/api_services/*/)
# ==============================================================================

class BaseProviderException(CSSException):
    """
    Base exception for all api_services/ provider errors.

    All provider-specific exceptions should inherit from this class
    (directly or via LLMApiServiceError for LLM providers).

    Attributes:
        provider_name: Optional name of the provider (e.g., 'anthropic', 'ollama')
        context: Optional dict with additional error context
    """

    def __init__(
            self,
            message: str,
            provider_name: str | None = None,
            capture_traceback: bool = False,
            context: dict | None = None,
    ):
        ctx = context or {}
        if provider_name:
            ctx["provider"] = provider_name

        super().__init__(message, capture_traceback=capture_traceback, context=ctx)
        self.provider_name = provider_name


# ==============================================================================
# Unified Error Hierarchy (for Retry Orchestrator)
# Issue #3: Map all provider errors to 5-type hierarchy
# ==============================================================================


class UnifiedLLMError(BaseCoreException):
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
            error_code: str | None = None,
            provider: str | None = None,
            original_error: Exception | None = None,
            capture_traceback: bool = False,
            context: dict | None = None,
    ):
        """
        Initialize unified error.

        Args:
            message: Human-readable message
            error_code: Provider-specific error code
            provider: Provider name (anthropic, openai, ollama, etc.)
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


class AuthError(BaseCoreException):
    """Authentication or authorization failed (401, 403, invalid credentials)."""
    pass


class RateLimitError(BaseCoreException):
    """Rate limit exceeded (429, quota exhausted)."""

    def __init__(
            self,
            message: str,
            provider: str | None = None,
            retry_after_seconds: float | None = None,
            original_error: Exception | None = None,
            context: dict | None = None,
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



# ==============================================================================
# LLM API Service Exceptions (Layer 1 — api_services/)
# ==============================================================================


class LLMApiServiceError(BaseProviderException):
    """Base exception for LLM API service errors."""
    
    def __init__(
        self,
        message: str,
        provider_name: str | None = None,
        model_id: str | None = None,
        capture_traceback: bool = False,
        context: dict | None = None,
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
        message: str | None = None,
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


class LLMHarnessError(BaseCoreException):
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
    """Raised when A2A (agents-to-agents) streaming fails."""
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


class ConfigurationError(BaseCoreException):
    """Raised when configuration is invalid or incomplete."""
    pass


class ValidationError(BaseCoreException):
    """Raised when validation fails."""
    pass


# ==============================================================================
# Ollama-Specific Exceptions
# ==============================================================================


class OllamaError(BaseCoreException):
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



class TimeoutError(UnifiedLLMError):
    """Request timed out (connection timeout, read timeout, etc.)."""
    pass


class GatewayError(UnifiedLLMError):
    """Provider error (5xx, service unavailable, temporary failure)."""
    pass


class UnknownError(UnifiedLLMError):
    """Unclassified error (fallback for unmapped errors)."""
    pass
