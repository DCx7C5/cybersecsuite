"""Scope-related exceptions."""

from css.core.exceptions import BaseModuleException


class BaseScopeException(BaseModuleException):
    """Base exception for the scopes module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="scopes", **kwargs)


class ScopeValidationError(BaseScopeException):
    """Raised when scope context validation fails."""
    
    def __init__(self, message: str, scope_level: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if scope_level:
            ctx["scope_level"] = scope_level
        super().__init__(
            message or "Scope validation failed",
            context=ctx,
            **kwargs
        )


class ScopeResolutionError(BaseScopeException):
    """Raised when scope path resolution fails."""
    
    def __init__(self, scope_path: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if scope_path:
            ctx["scope_path"] = scope_path
        super().__init__(
            f"Scope resolution failed: {scope_path}" if scope_path else "Scope resolution failed",
            context=ctx,
            **kwargs
        )
