"""Memory module exception hierarchy."""

from css.core.exceptions import BaseModuleException


class BaseMemoryException(BaseModuleException):
    """Base exception for the memory module."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="memory", **kwargs)


class MemoryNotFoundError(BaseMemoryException):
    """Raised when a memory record cannot be found."""

    def __init__(self, entry_id: str | None = None, **kwargs):
        context = kwargs.get("context", {})
        if entry_id:
            context["entry_id"] = entry_id
        super().__init__(
            f"Memory entry not found: {entry_id}" if entry_id else "Memory entry not found",
            context=context,
            **kwargs,
        )


class MemoryPersistenceError(BaseMemoryException):
    """Raised when memory persistence operations fail."""

    def __init__(self, message: str | None = None, operation: str | None = None, **kwargs):
        context = kwargs.get("context", {})
        if operation:
            context["operation"] = operation
        super().__init__(
            message or f"Memory persistence failed: {operation}" if operation else "Memory persistence failed",
            context=context,
            **kwargs,
        )
