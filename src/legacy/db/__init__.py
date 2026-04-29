"""Database layer — ORM models, managers, utilities, audit logging, and scope management."""

# Core exception types
from core.db.exceptions import (
    ScopeError,
    ScopePermissionError,
    ScopeValidationError,
)

# Scope utilities
from core.db.scope_utils import (
    ScopeLevel,
    check_scope_permission,
    validate_scope_fields,
)

# Audit logging
from core.db.audit_logger import get_audit_logger

__all__ = [
    "ScopeError",
    "ScopePermissionError",
    "ScopeValidationError",
    "ScopeLevel",
    "check_scope_permission",
    "validate_scope_fields",
    "get_audit_logger",
]

# Note: ORM models are available via:
#   from core.db.models import X  (specific models)
#   from core.db.managers import XManager (model managers)
#   from core.db.settings import TORTOISE_ORM (ORM config)
