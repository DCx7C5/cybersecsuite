"""Value types for memory state and snapshots."""

from typing import Any

try:
    import msgspec
except ImportError:  # pragma: no cover - fallback for minimal dev envs
    msgspec = None

from .enums import MemoryEntryKind, MemoryScope, MemoryTier

if msgspec is not None:

    class MemoryEntry(msgspec.Struct, frozen=True):
        """Provider-agnostic memory entry value object."""

        entry_id: str
        session_id: str
        agent_id: str | None
        scope: MemoryScope
        tier: MemoryTier
        kind: MemoryEntryKind
        content: str
        metadata: dict[str, Any] = msgspec.field(default_factory=dict)
        created_at: str = ""

    class MemorySnapshot(msgspec.Struct, frozen=True):
        """Point-in-time session memory snapshot."""

        snapshot_id: str
        session_id: str
        summary: str
        entries: list[str] = msgspec.field(default_factory=list)
        metadata: dict[str, Any] = msgspec.field(default_factory=dict)
        created_at: str = ""
else:

    class MemoryEntry(msgspec.Struct, frozen=True):
        """Fallback memory entry value object when msgspec is unavailable."""

        entry_id: str
        session_id: str
        agent_id: str | None
        scope: MemoryScope
        tier: MemoryTier
        kind: MemoryEntryKind
        content: str
        metadata: dict[str, Any] = msgspec.field(default_factory=dict)
        created_at: str = ""

    class MemorySnapshot(msgspec.Struct, frozen=True):
        """Fallback memory snapshot value object when msgspec is unavailable."""

        snapshot_id: str
        session_id: str
        summary: str
        entries: list[str] = msgspec.field(default_factory=list)
        metadata: dict[str, Any] = msgspec.field(default_factory=dict)
        created_at: str = ""
