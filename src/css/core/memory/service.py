"""Core memory service API for CRUD/search/optimise operations."""

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import uuid4

from .contracts import MemoryPolicy
from .session_store import SessionStore
from .types import (
    MemoryDeleteRequest,
    MemoryDeleteResult,
    MemoryEntry,
    MemoryListResult,
    MemoryPolicyConfig,
    MemoryPolicyDecision,
    MemoryQuery,
    MemorySnapshot,
    MemoryWriteRequest,
    MemoryWriteResult,
)

if TYPE_CHECKING:
    from css.core.db.models.memory import MemoryEntryRecord as _MER
    from css.core.db.models.memory import MemorySnapshotRecord as _MSR


def _record_cls() -> "type[_MER]":
    from css.core.db.models.memory import MemoryEntryRecord
    return MemoryEntryRecord


def _snapshot_cls() -> "type[_MSR]":
    from css.core.db.models.memory import MemorySnapshotRecord
    return MemorySnapshotRecord


class DefaultMemoryPolicy:
    """Default policy deciding whether a write should be persisted."""

    def evaluate(
        self, request: MemoryWriteRequest, *, config: MemoryPolicyConfig
    ) -> MemoryPolicyDecision:
        if not request.persistent:
            return MemoryPolicyDecision(
                should_persist=False,
                resolved_ttl_seconds=request.ttl_seconds,
                reason="request-marked-ephemeral",
            )

        if request.scope not in config.persistent_scopes:
            return MemoryPolicyDecision(
                should_persist=False,
                resolved_ttl_seconds=request.ttl_seconds,
                reason="scope-not-persistent",
            )

        if request.kind in config.ephemeral_kinds:
            return MemoryPolicyDecision(
                should_persist=False,
                resolved_ttl_seconds=request.ttl_seconds,
                reason="kind-marked-ephemeral",
            )

        if request.importance < config.min_importance_to_persist:
            return MemoryPolicyDecision(
                should_persist=False,
                resolved_ttl_seconds=request.ttl_seconds,
                reason="importance-below-threshold",
            )

        ttl_seconds = request.ttl_seconds
        if ttl_seconds is None:
            ttl_seconds = config.default_ttl_seconds
        return MemoryPolicyDecision(
            should_persist=True,
            resolved_ttl_seconds=ttl_seconds,
            reason="policy-accepted",
        )


class MemoryService:
    """Core memory API for storage operations and retrieval."""

    def __init__(
        self,
        session_store: SessionStore,
        policy: MemoryPolicy | None = None,
        policy_config: MemoryPolicyConfig | None = None,
    ) -> None:
        self.session_store = session_store
        self.policy: MemoryPolicy = policy or DefaultMemoryPolicy()
        self.policy_config = policy_config or MemoryPolicyConfig()

    async def write(self, request: MemoryWriteRequest) -> MemoryWriteResult:
        """Persist/upsert a memory entry according to policy."""
        decision = self.policy.evaluate(request, config=self.policy_config)
        if not decision.should_persist:
            return MemoryWriteResult(
                success=True,
                persisted=False,
                reason=decision.reason,
            )

        now = datetime.now(timezone.utc)
        ttl_seconds = decision.resolved_ttl_seconds
        expires_at = (
            now + timedelta(seconds=ttl_seconds)
            if ttl_seconds is not None and ttl_seconds > 0
            else None
        )

        entry_id = request.entry_id or str(uuid4())
        existing = await _record_cls().get_or_none(entry_id=entry_id)
        if existing is None:
            record = await _record_cls().create(
                entry_id=entry_id,
                session_id=request.session_id,
                agent_id=request.agent_id,
                scope=request.scope,
                tier=request.tier,
                kind=request.kind,
                content=request.content,
                metadata=request.metadata,
                importance=request.importance,
                persistent=True,
                ttl_seconds=ttl_seconds,
                expires_at=expires_at,
            )
        else:
            existing.session_id = request.session_id
            existing.agent_id = request.agent_id
            existing.scope = request.scope
            existing.tier = request.tier
            existing.kind = request.kind
            existing.content = request.content
            existing.metadata = request.metadata
            existing.importance = request.importance
            existing.persistent = True
            existing.ttl_seconds = ttl_seconds
            existing.expires_at = expires_at
            await existing.save()
            record = existing

        return MemoryWriteResult(
            success=True,
            entry=record.to_struct(),
            persisted=True,
            reason=decision.reason,
        )

    async def get(self, entry_id: str) -> MemoryEntry | None:
        """Get one entry by ID."""
        record = await _record_cls().get_or_none(entry_id=entry_id)
        if record is None:
            return None
        return record.to_struct()

    async def list(self, query: MemoryQuery | None = None) -> MemoryListResult:
        """List entries using a typed query."""
        return await self.session_store.list_memory_entries(query=query)

    async def delete(self, request: MemoryDeleteRequest) -> MemoryDeleteResult:
        """Delete entries based on request scope."""
        queryset = (_record_cls()).all()
        if request.entry_id:
            queryset = queryset.filter(entry_id=request.entry_id)
        if request.session_id:
            queryset = queryset.filter(session_id=request.session_id)
        if request.agent_id:
            queryset = queryset.filter(agent_id=request.agent_id)
        if request.scope:
            queryset = queryset.filter(scope=request.scope)

        deleted = await queryset.delete()
        return MemoryDeleteResult(
            success=deleted > 0,
            deleted_count=deleted,
            reason="deleted" if deleted > 0 else "no-matching-entries",
        )

    async def snapshot(
        self,
        session_id: str,
        summary: str,
        metadata: dict[str, str] | None = None,
    ) -> MemorySnapshot:
        """Create a memory snapshot from current session entries."""
        query = MemoryQuery(session_id=session_id, include_ephemeral=True, limit=500)
        entries = await self.list(query)
        snapshot = await _snapshot_cls().create(
            snapshot_id=f"snapshot-{session_id}-{uuid4()}",
            session_id=session_id,
            summary=summary,
            entries=[entry.content for entry in entries.entries],
            metadata=metadata or {},
            entry_count=len(entries.entries),
        )
        return snapshot.to_struct()

    async def summarize_session(self, session_id: str, limit: int = 20) -> str:
        """Generate a lightweight text summary from recent session entries."""
        entries = await self.list(
            MemoryQuery(
                session_id=session_id,
                include_ephemeral=False,
                limit=max(1, limit),
            )
        )
        if not entries.entries:
            return f"No persisted memory entries for session {session_id}."
        snippets = [entry.content.strip() for entry in entries.entries if entry.content.strip()]
        if not snippets:
            return f"No textual memory content for session {session_id}."
        return "\n".join(f"- {snippet}" for snippet in snippets[:limit])
