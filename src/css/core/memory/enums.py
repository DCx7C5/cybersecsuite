"""Enum definitions for memory tiers, scopes, and entry kinds."""

from enum import Enum


class MemoryTier(str, Enum):
    """Storage temperature tier for a memory entry."""

    HOT = "hot"
    WARM = "warm"
    COLD = "cold"
    ARCHIVE = "archive"


class MemoryScope(str, Enum):
    """Visibility scope for a memory entry."""

    SESSION = "session"
    AGENT = "agent"
    PROJECT = "project"
    GLOBAL = "global"


class MemoryEntryKind(str, Enum):
    """Semantic type of a memory entry."""

    NOTE = "note"
    FACT = "fact"
    FINDING = "finding"
    PLAN = "plan"
    ARTIFACT = "artifact"
    SNAPSHOT = "snapshot"
