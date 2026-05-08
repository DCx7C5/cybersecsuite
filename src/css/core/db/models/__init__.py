"""Core database models — enums, scopes management, and essential entities.

This module exports the core models and enums needed for the CyberSecSuite
database layer. Copied from legacy/db/models with localized imports.
"""

from .base import BaseModel, BaseItemModel
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
from .scope import ProjectScope, SessionScope

__all__ = [
    "BaseModel",
    "BaseItemModel",
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
]
