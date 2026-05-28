"""Permission management and access control (RBAC)."""

from css.core.logger import getLogger

from css.core.enums import ScopeLevel, Permission, Role as RoleEnum
from .enums import PathOp
from .types import Role, PermissionPolicy, ScopeContext, TokenPayload, ToolGrant
from .checker import PermissionChecker, permission_checker
from .exceptions import (
    BasePermissionError,
    PermissionDenied,
    TokenInvalid,
    ScopeContextError,
    RoleNotFound,
)

logger = getLogger(__name__)
