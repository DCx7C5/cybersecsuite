"""Permission management and access control (RBAC)."""

import logging

from .enums import Role, ScopeLevel, Permission
from .types import PermissionPolicy, ScopeContext, TokenPayload
from .exceptions import (
    PermissionError,
    PermissionDenied,
    TokenInvalid,
    ScopeContextError,
    RoleNotFound,
)

logger = logging.getLogger(__name__)

__all__ = [
    "Role",
    "ScopeLevel",
    "Permission",
    "PermissionPolicy",
    "ScopeContext",
    "TokenPayload",
    "PermissionError",
    "PermissionDenied",
    "TokenInvalid",
    "ScopeContextError",
    "RoleNotFound",
]
