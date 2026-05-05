"""Scope management and hierarchy."""

from css.core.logger import getLogger

logger = getLogger(__name__)

from .context import ScopeContext
from .manager import ScopeManager
from .enums import ScopeLevel
from .exceptions import (
    BaseScopeException,
    ScopeValidationError,
    ScopeResolutionError,
)

__all__ = [
    "ScopeContext",
    "ScopeManager",
    "ScopeLevel",
    "BaseScopeException",
    "ScopeValidationError",
    "ScopeResolutionError",
]

logger.info("Scopes module loaded")
