"""Role-related exceptions."""

from css.core.exceptions import BaseModuleException


class BaseRoleException(BaseModuleException):
    """Base exception for the roles module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="roles", **kwargs)


class RoleNotFoundError(BaseRoleException):
    """Raised when a role is not found."""
    
    def __init__(self, role_id: str, **kwargs):
        ctx = kwargs.get("context", {})
        ctx["role_id"] = role_id
        super().__init__(
            f"Role not found: {role_id}",
            context=ctx,
            **kwargs
        )


class PermissionDeniedError(BaseRoleException):
    """Raised when a role lacks required permissions."""
    
    def __init__(self, role_id: str, permission: str, **kwargs):
        ctx = kwargs.get("context", {})
        ctx["role_id"] = role_id
        ctx["permission"] = permission
        super().__init__(
            f"Permission denied for role {role_id}: {permission}",
            context=ctx,
            **kwargs
        )


class InvalidRoleError(BaseRoleException):
    """Raised when attempting to create an invalid role."""
    
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message or "Invalid role specification",
            **kwargs
        )
