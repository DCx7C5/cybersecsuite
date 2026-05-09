"""Permission management and access control (RBAC)."""

from css.core.logger import getLogger

from css.core.enums import ScopeLevel, Permission, Role as RoleEnum
from .types import Role, PermissionPolicy, ScopeContext, TokenPayload
from .checker import PermissionChecker, permission_checker
from .exceptions import (
    PermissionError,
    PermissionDenied,
    TokenInvalid,
    ScopeContextError,
    RoleNotFound,
)

logger = getLogger(__name__)

__all__ = [
    "Role",
    "RoleEnum",
    "ScopeLevel",
    "Permission",
    "PermissionPolicy",
    "ScopeContext",
    "TokenPayload",
    "PermissionChecker",
    "permission_checker",
    "PermissionError",
    "PermissionDenied",
    "TokenInvalid",
    "ScopeContextError",
    "RoleNotFound",
]
