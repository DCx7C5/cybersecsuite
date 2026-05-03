"""Exceptions for the tags module."""

from css.core.exceptions import BaseModuleException


class BaseTagException(BaseModuleException):
    """Base exception for the tags module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="tags", **kwargs)


class TagNotFoundError(BaseTagException):
    """Raised when a tag is not found."""
    
    def __init__(self, tag_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if tag_id:
            ctx["tag_id"] = tag_id
        super().__init__(
            f"Tag not found: {tag_id}" if tag_id else "Tag not found",
            context=ctx,
            **kwargs
        )


class TagCreationError(BaseTagException):
    """Raised when tag creation fails."""
    
    def __init__(self, message: str = None, tag_name: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if tag_name:
            ctx["tag_name"] = tag_name
        super().__init__(
            message or f"Tag creation failed: {tag_name}" if tag_name else "Tag creation failed",
            context=ctx,
            **kwargs
        )


class TagValidationError(BaseTagException):
    """Raised when tag validation fails."""
    
    def __init__(self, message: str = None, field: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if field:
            ctx["field"] = field
        super().__init__(
            message or f"Tag validation failed: {field}" if field else "Tag validation failed",
            context=ctx,
            **kwargs
        )
