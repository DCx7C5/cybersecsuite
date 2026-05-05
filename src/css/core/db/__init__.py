"""Core database layer — models, enums, and scopes utilities."""

# Scope and core exceptions
from .exceptions import (
    ScopeError,
    ScopePermissionError,
    ScopeValidationError,
)

# Enums (import before scope_utils to avoid circular import)
from .enums import ScopeLevel

# Scope utilities
from .scope_utils import (
    check_scope_permission,
    validate_scope_fields,
)

# Models and enums
from .models import (
    RedBlueMode,
    AuditAction,
    Severity,
    Confidence,
    FindingStatus,
    IOCStatus,
    ProjectScope,
    SessionScope,
)

__all__ = [
    # Exceptions
    "ScopeError",
    "ScopePermissionError",
    "ScopeValidationError",
    # Utilities
    "ScopeLevel",
    "check_scope_permission",
    "validate_scope_fields",
    # Models
    "ProjectScope",
    "SessionScope",
    # Enums
    "RedBlueMode",
    "AuditAction",
    "Severity",
    "Confidence",
    "FindingStatus",
    "IOCStatus",
]
