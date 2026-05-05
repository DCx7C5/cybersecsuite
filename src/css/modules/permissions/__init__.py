"""Permission management and access control (RBAC)."""

import logging

from .enums import ScopeLevel, Permission, Role as RoleEnum
from .types import Role, PermissionPolicy, ScopeContext, TokenPayload
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
    "RoleEnum",
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
