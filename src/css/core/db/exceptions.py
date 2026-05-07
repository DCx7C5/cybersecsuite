"""
Scope and permission exception classes for CyberSecSuite.

Provides structured exception types for scopes validation failures,
permission denials, and resource access errors.
"""


from typing import Any


class ScopeError(Exception):
    """Base exception for scopes-related errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "SCOPE_ERROR",
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize scopes error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code (e.g., SCOPE_VALIDATION_FAILED)
            context: Additional context information (user_id, resource, etc.)
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}


class ScopeValidationError(ScopeError):
    """Raised when scopes context fails validation."""

    def __init__(
        self,
        message: str,
        scope_level: str | None = None,
        invalid_fields: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize scopes validation error.

        Args:
            message: Description of what failed validation
            scope_level: Scope level that failed validation
            invalid_fields: List of invalid field names
            context: Context info (required_fields, provided_fields, etc.)
        """
        merged_context = {
            'scope_level': scope_level,
            'invalid_fields': invalid_fields or []
        }
        if context:
            merged_context.update(context)
        super().__init__(message, error_code="SCOPE_VALIDATION_FAILED", context=merged_context)


class ScopePermissionError(ScopeError):
    """Raised when user lacks permission for requested action.

    Maps to HTTP 403 Forbidden in FastAPI exception handlers.
    """

    def __init__(
        self,
        message: str,
        user_id: str | None = None,
        resource: str | None = None,
        action: str | None = None,
        scope_level: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize permission error.

        Args:
            message: Description of permission denial
            user_id: User who lacked permission
            resource: Resource being accessed
            action: Action attempted (read, write, delete, etc.)
            scope_level: Scope at which permission was denied
            context: Additional context information to merge
        """
        built_context = {}
        if user_id:
            built_context["user_id"] = user_id
        if resource:
            built_context["resource"] = resource
        if action:
            built_context["action"] = action
        if scope_level:
            built_context["scope_level"] = scope_level
        if context:
            built_context.update(context)
        super().__init__(
            message, error_code="PERMISSION_DENIED", context=built_context
        )


class ScopeResourceNotFoundError(ScopeError):
    """Raised when resource not found within requested scopes.

    Maps to HTTP 404 Not Found in FastAPI exception handlers.
    """

    def __init__(
        self,
        message: str,
        resource_id: str | int | None = None,
        resource_type: str | None = None,
        scope_level: str | None = None,
    ) -> None:
        """Initialize resource not found error.

        Args:
            message: Description of missing resource
            resource_id: ID of the missing resource
            resource_type: Type of resource (Finding, IOC, etc.)
            scope_level: Scope context where search occurred
        """
        context = {}
        if resource_id is not None:
            context["resource_id"] = resource_id
        if resource_type:
            context["resource_type"] = resource_type
        if scope_level:
            context["scope_level"] = scope_level
        super().__init__(
            message, error_code="RESOURCE_NOT_FOUND", context=context
        )


class ScopeHierarchyError(ScopeError):
    """Raised when scopes hierarchy check fails."""

    def __init__(
        self,
        message: str,
        source_scope: str | None = None,
        target_scope: str | None = None,
    ) -> None:
        """Initialize hierarchy error.

        Args:
            message: Description of hierarchy violation
            source_scope: Higher scopes level
            target_scope: Lower scopes level
        """
        context = {}
        if source_scope:
            context["source_scope"] = source_scope
        if target_scope:
            context["target_scope"] = target_scope
        super().__init__(
            message, error_code="SCOPE_HIERARCHY_ERROR", context=context
        )


class CacheInvalidationError(ScopeError):
    """Raised when cache invalidation fails."""

    def __init__(
        self,
        message: str,
        cache_key: str | None = None,
        scope_level: str | None = None,
    ) -> None:
        """Initialize cache invalidation error.

        Args:
            message: Description of invalidation failure
            cache_key: Cache key that failed to invalidate
            scope_level: Associated scopes level
        """
        context = {}
        if cache_key:
            context["cache_key"] = cache_key
        if scope_level:
            context["scope_level"] = scope_level
        super().__init__(
            message, error_code="CACHE_INVALIDATION_FAILED", context=context
        )
