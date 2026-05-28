"""Permission-related exceptions for RBAC."""

from css.core.exceptions import BaseCoreException


class BasePermissionError(BaseCoreException):
    """Base exception for permission-related errors."""
    pass


class PermissionDenied(BasePermissionError):
    """Raised when an operation is not permitted."""
    pass


class TokenInvalid(BasePermissionError):
    """Raised when a token is invalid or expired."""
    pass


class ScopeContextError(BasePermissionError):
    """Raised when scope context is invalid."""
    pass


class RoleNotFound(BasePermissionError):
    """Raised when a role is not found."""
    pass

