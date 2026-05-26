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
from .menu import MenuItem, MenuItemInfo, sync_default_menu_items
from .provider import ApiServiceProvider
from .machine import Machine, MachineInfo, MachineManager, sync_default_machines
from .host import Host, HostInfo, HostManager, sync_default_hosts
from .pathfs import PathFS, PathFSInfo, PathFSManager, sync_default_paths

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
    "sync_default_menu_items",
    "ApiServiceProvider",
    "Machine",
    "MachineInfo",
    "MachineManager",
    "sync_default_machines",
    "Host",
    "HostInfo",
    "HostManager",
    "sync_default_hosts",
    "PathFS",
    "PathFSInfo",
    "PathFSManager",
    "sync_default_paths",
]
