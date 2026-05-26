"""Value types for memory entities, operations, and policy configuration."""

from typing import Any

import msgspec

from .enums import MemoryEntryKind, MemoryScope, MemoryTier


class MemoryEntry(msgspec.Struct, frozen=True, kw_only=True):
    """Provider-agnostic memory entry value object."""

    entry_id: str
    session_id: str
    agent_id: str | None
    scope: MemoryScope
    tier: MemoryTier
    kind: MemoryEntryKind
    content: str
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    importance: float = 0.5
    persistent: bool = True
    ttl_seconds: int | None = None
    expires_at: str | None = None
    created_at: str = ""


class MemorySnapshot(msgspec.Struct, frozen=True, kw_only=True):
    """Point-in-time session memory snapshot."""

    snapshot_id: str
    session_id: str
    summary: str
    entries: list[dict[str, object]] = msgspec.field(default_factory=list)
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    created_at: str = ""


class MemoryWriteRequest(msgspec.Struct, frozen=True, kw_only=True):
    """Typed request for persisting one memory entry."""

    session_id: str
    content: str
    scope: MemoryScope = MemoryScope.SESSION
    tier: MemoryTier = MemoryTier.HOT
    kind: MemoryEntryKind = MemoryEntryKind.NOTE
    agent_id: str | None = None
    entry_id: str | None = None
    metadata: dict[str, Any] = msgspec.field(default_factory=dict)
    ttl_seconds: int | None = None
    importance: float = 0.5
    persistent: bool = True


class MemoryWriteResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result of a memory write/upsert operation."""

    success: bool
    entry: MemoryEntry | None = None
    persisted: bool = False
    reason: str | None = None


class MemoryDeleteRequest(msgspec.Struct, frozen=True, kw_only=True):
    """Typed request for deleting one or more memory entries."""

    entry_id: str | None = None
    session_id: str | None = None
    agent_id: str | None = None
    scope: MemoryScope | None = None
    hard_delete: bool = False


class MemoryDeleteResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result of a memory delete operation."""

    success: bool
    deleted_count: int = 0
    reason: str | None = None


class MemoryQuery(msgspec.Struct, frozen=True, kw_only=True):
    """Typed query for memory retrieval/list operations."""

    session_id: str | None = None
    agent_id: str | None = None
    scopes: list[MemoryScope] = msgspec.field(default_factory=list)
    kinds: list[MemoryEntryKind] = msgspec.field(default_factory=list)
    tags: list[str] = msgspec.field(default_factory=list)
    text: str | None = None
    min_importance: float | None = None
    include_ephemeral: bool = False
    limit: int = 50
    offset: int = 0


class MemoryListResult(msgspec.Struct, frozen=True, kw_only=True):
    """Result set for memory list/retrieval queries."""

    entries: list[MemoryEntry] = msgspec.field(default_factory=list)
    total: int = 0
    next_offset: int | None = None


class MemoryPolicyConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Policy configuration controlling persistent vs ephemeral memory."""

    persistent_scopes: set[MemoryScope] = msgspec.field(
        default_factory=lambda: {MemoryScope.SESSION, MemoryScope.AGENT}
    )
    ephemeral_kinds: set[MemoryEntryKind] = msgspec.field(default_factory=set)
    min_importance_to_persist: float = 0.5
    default_ttl_seconds: int | None = None
    max_entries_per_session: int = 1000
    allow_pii_persistence: bool = False


class MemoryPolicyDecision(msgspec.Struct, frozen=True, kw_only=True):
    """Decision output from policy evaluation for a memory write."""

    should_persist: bool
    resolved_ttl_seconds: int | None = None
    reason: str | None = None
