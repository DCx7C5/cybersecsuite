"""Protocol contracts for provider-agnostic memory persistence and retrieval."""

from collections.abc import Callable
from typing import Protocol

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


class MemoryPolicy(Protocol):
    """Policy contract deciding persistence behavior for candidate entries."""

    def evaluate(
        self, request: MemoryWriteRequest, *, config: MemoryPolicyConfig
    ) -> MemoryPolicyDecision:
        """Evaluate whether the candidate should be persisted and how."""
        ...


class MemoryStore(Protocol):
    """Canonical storage contract for writing and retrieving memory entries."""

    async def write(self, request: MemoryWriteRequest) -> MemoryWriteResult:
        """Persist or upsert a memory entry."""
        ...

    async def get(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve one memory entry by identifier."""
        ...

    async def delete(self, request: MemoryDeleteRequest) -> MemoryDeleteResult:
        """Delete memory entries according to request scope."""
        ...

    async def list(self, query: MemoryQuery | None = None) -> MemoryListResult:
        """List memory entries using an optional typed query."""
        ...

    async def snapshot(
        self, session_id: str, summary: str, metadata: dict[str, str] | None = None
    ) -> MemorySnapshot:
        """Create and persist a point-in-time snapshot for a session."""
        ...


class MemoryRetriever(Protocol):
    """Read-focused retrieval contract for context assembly integrations."""

    async def retrieve(self, query: MemoryQuery) -> MemoryListResult:
        """Return ranked memory entries for context injection."""
        ...

    async def retrieve_for_context(
        self,
        session_id: str,
        *,
        agent_id: str | None = None,
        token_budget: int | None = None,
        predicate: Callable[[MemoryEntry], bool] | None = None,
    ) -> list[MemoryEntry]:
        """Return context-ready entries under optional token budget and filtering."""
        ...
