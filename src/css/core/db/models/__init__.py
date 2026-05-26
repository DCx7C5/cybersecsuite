"""Core database models — enums, scopes management, and essential entities.

This module exports the core models and enums needed for the CyberSecSuite
database layer. Copied from legacy/db/models with localized imports.
"""

from .base import (
    BaseModel,
    BaseUserModel,
    BaseTreeModel,
)

from .accounts import (
    Account,
    Organization,
    OrganizationMembership,
    RoleAssignment,
    UserProfile,
)

from .enums import (
    AuditAction,
    Confidence,
    FindingStatus,
    IOCStatus,
    RedBlueMode,
    Severity,
)
from .mixins import (
    TimestampMixin,
    VersionMixin,
    SoftDeleteMixin,
    BaseFrontmatterMixin,
)

from .scope import ProjectScope, SessionScope
from .menu import MenuItem, MenuItemInfo
from .provider import ApiServiceProvider
from .machine import Machine, MachineInfo, MachineManager

__all__ = [
    "BaseModel",
    "BaseUserModel",
    "BaseTreeModel",
    "TimestampMixin",
    "VersionMixin",
    "SoftDeleteMixin",
    "BaseFrontmatterMixin",
    "Account",
    "UserProfile",
    "Organization",
    "OrganizationMembership",
    "RoleAssignment",
    "RedBlueMode",
    "AuditAction",
    "Severity",
    "Confidence",
    "FindingStatus",
    "IOCStatus",
    "ProjectScope",
    "SessionScope",
    "MenuItem",
    "MenuItemInfo",
    "ApiServiceProvider",
    "Machine",
    "MachineInfo",
    "MachineManager",
]
