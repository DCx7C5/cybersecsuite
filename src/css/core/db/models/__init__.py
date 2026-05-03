"""Core database models — enums, scopes management, and essential entities.

This module exports the core models and enums needed for the CyberSecSuite
database layer. Copied from legacy/db/models with localized imports.
"""

from .enums import (
    RedBlueMode,
    AuditAction,
    Severity,
    SeverityLevel,
    Confidence,
    ConfidenceLevel,
    FindingStatus,
    IOCStatus,
    ForensicIOCStatus,
)
from .scope import ProjectScope, SessionScope

__all__ = [
    "RedBlueMode",
    "AuditAction",
    "Severity",
    "SeverityLevel",
    "Confidence",
    "ConfidenceLevel",
    "FindingStatus",
    "IOCStatus",
    "ForensicIOCStatus",
    "ProjectScope",
    "SessionScope",
]
