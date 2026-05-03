"""Triage exceptions."""

from css.core.exceptions import BaseModuleException


class BaseTriageException(BaseModuleException):
    """Base exception for the triage module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="triage", **kwargs)


class TriageExecutionError(BaseTriageException):
    """Raised when triage execution fails."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message or "Triage execution failed",
            **kwargs
        )


class TriageClassificationError(BaseTriageException):
    """Raised when classification fails."""
    def __init__(self, message: str = None, **kwargs):
        super().__init__(
            message or "Classification failed",
            **kwargs
        )
