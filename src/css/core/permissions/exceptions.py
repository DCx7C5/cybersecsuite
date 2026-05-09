"""Permission-related exceptions for RBAC."""

from css.core.exceptions import BaseCoreException


class PermissionError(BaseCoreException):
    """Base exception for permission-related errors."""
    pass


class PermissionDenied(PermissionError):
    """Raised when an operation is not permitted."""
    pass


class TokenInvalid(PermissionError):
    """Raised when a token is invalid or expired."""
    pass


class ScopeContextError(PermissionError):
    """Raised when scope context is invalid."""
    pass


class RoleNotFound(PermissionError):
    """Raised when a role is not found."""
    pass


__all__ = [
    "PermissionError",
    "PermissionDenied",
    "TokenInvalid",
    "ScopeContextError",
    "RoleNotFound",
]
