"""Per-agent episodic memory — aggregate agent context with persistent storage.

AgentMemory combines:
1. ContextWindow: Active message window with token budget
2. SessionStore: Persistent storage (Redis + PostgreSQL)
3. Episodic memory: Collection of memorable events/facts about the agent

Enables agents to maintain context across conversations and remember important facts.
"""

from css.core.logger import getLogger
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from .context_window import ContextWindow
from .enums import MemoryEntryKind, MemoryScope, MemoryTier
from .session_store import SessionStore
from .types import MemoryEntry
from css.core.types.context import ConversationContext

log = getLogger(__name__)


class AgentMemory:
    """Per-agent episodic memory combining context window + persistent storage.

    Manages an agent's memory across multiple dimensions:
    - Active context: ContextWindow for current message window
    - Session state: SessionStore for persistent context
    - Episodic facts: Important facts/events the agent should remember

    Attributes:
        agent_id: Unique agent identifier
        context_window: Active message window with token budget
        session_store: Persistent storage for contexts
        episodes: List of memorable events/facts
        metadata: Custom agent metadata
    """

    def __init__(
        self,
        agent_id: str,
        session_id: str | None = None,
        context_window: Optional[ContextWindow] = None,
        session_store: Optional[SessionStore] = None,
        max_episodes: int = 100,
    ):
        """Initialize agent memory.

        Args:
            agent_id: Unique agent identifier
            context_window: Active context window (default: new 8192-token window)
            session_store: Persistent session store (optional)
            max_episodes: Maximum episodic memories to retain
        """
        self.agent_id = agent_id
        self.session_id = session_id or f"agent:{agent_id}"
        self.context_window = context_window or ContextWindow()
        self.session_store = session_store
        self.max_episodes: int = max_episodes
        self.episodes: list[MemoryEntry] = []
        self.metadata: dict[str, Any] = {}
        self.created_at = datetime.now(timezone.utc)
        self.accessed_at = datetime.now(timezone.utc)

    def add_episode(
        self, content: str, category: str = "fact", tags: list[str] | None = None
    ) -> MemoryEntry:
        """Record a memorable episode or fact.

        Episodes are important facts/events the agent should remember across sessions.
        When max_episodes is reached, oldest episodes are evicted.

        Args:
            content: Episode content or fact
            category: Episode type (fact, event, insight, decision, etc.)
            tags: Optional tags for filtering (e.g., ["important", "user-feedback"])

        Returns:
            MemoryEntry with episode details
        """
        kind = self._resolve_kind(category)
        now = datetime.now(timezone.utc)
        episode = MemoryEntry(
            entry_id=str(uuid4()),
            session_id=self.session_id,
            agent_id=self.agent_id,
            scope=MemoryScope.AGENT,
            tier=MemoryTier.WARM,
            kind=kind,
            content=content,
            metadata={
                "agent_id": self.agent_id,
                "session_id": self.session_id,
                "category": category,
                "tags": tags or [],
            },
            created_at=now.isoformat(),
        )

        # Add to episodes
        self.episodes.append(episode)

        # Evict oldest episodes if over limit
        if len(self.episodes) > self.max_episodes:
            evicted = self.episodes.pop(0)
            log.debug(f"Agent {self.agent_id}: evicted episode {evicted.entry_id}")

        log.debug(f"Agent {self.agent_id}: added episode {episode.entry_id} ({category})")
        self.accessed_at = datetime.now(timezone.utc)

        return episode

    def get_episodes(
        self, category: Optional[str] = None, tags: Optional[list[str]] = None
    ) -> list[MemoryEntry]:
        """Retrieve episodes with optional filtering.

        Args:
            category: Filter by episode category (optional)
            tags: Filter to episodes with any of these tags (optional)

        Returns:
            List of matching episodes
        """
        results = self.episodes

        if category:
            results = [e for e in results if self._episode_category(e) == category]

        if tags:
            results = [e for e in results if any(tag in self._episode_tags(e) for tag in tags)]

        return results

    async def save_checkpoint(self, session_id: str) -> bool:
        """Save current context + episodes to persistent storage.

        This creates a snapshot of the current memory state for later recall.
        Requires session_store to be configured.

        Args:
            session_id: Session identifier for checkpoint

        Returns:
            True if save succeeded, False otherwise
        """
        if not self.session_store:
            log.warning(
                f"Agent {self.agent_id}: no session store configured, cannot save checkpoint"
            )
            return False

        try:
            context = ConversationContext(
                session_id=session_id,
                user_id=self.agent_id,
                messages=self.context_window.get_messages(),
                turn_number=len(self.context_window.messages),
                metadata={
                    **self.metadata,
                    "agent_id": self.agent_id,
                    "episodes": [self._serialize_episode(episode) for episode in self.episodes],
                },
            )
            await self.session_store.save_context(session_id=session_id, context=context)
            log.info(f"Agent {self.agent_id}: checkpoint saved for session {session_id}")
            return True

        except Exception as e:
            log.exception(f"Agent {self.agent_id}: checkpoint save failed: {e}")
            return False

    async def load_checkpoint(self, session_id: str) -> bool:
        """Load context + episodes from persistent storage.

        Restores previous memory state if available.

        Args:
            session_id: Session identifier for checkpoint

        Returns:
            True if load succeeded, False if checkpoint not found
        """
        if not self.session_store:
            log.warning(
                f"Agent {self.agent_id}: no session store configured, cannot load checkpoint"
            )
            return False

        try:
            context = await self.session_store.load_context(session_id=session_id)
            if context is None:
                return False

            self.session_id = session_id
            self.context_window.clear()
            for message in context.messages:
                self.context_window.add_message(message, force=True)

            raw_episodes = context.metadata.get("episodes", [])
            self.episodes = [
                self._deserialize_episode(raw) for raw in raw_episodes if isinstance(raw, dict)
            ]
            self.metadata = {
                key: value for key, value in context.metadata.items() if key != "episodes"
            }
            log.info(f"Agent {self.agent_id}: checkpoint loaded for session {session_id}")
            return True

        except Exception as e:
            log.debug(f"Agent {self.agent_id}: checkpoint load failed (may not exist): {e}")
            return False

    def get_summary(self) -> dict[str, Any]:
        """Get memory summary for diagnostics.

        Returns:
            Dictionary with memory statistics
        """
        return {
            "agent_id": self.agent_id,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "context_window": {
                "max_tokens": self.context_window.max_tokens,
                "current_tokens": self.context_window.total_tokens,
                "message_count": len(self.context_window.messages),
                "evicted_count": self.context_window.evicted_count,
            },
            "episodes": {
                "total": len(self.episodes),
                "max_retained": self.max_episodes,
                "by_category": self._count_by_category(),
            },
            "storage": {
                "session_store": "configured" if self.session_store else "none",
            },
        }

    def _count_by_category(self) -> dict[str, int]:
        """Count episodes by category."""
        counts: dict[str, int] = {}
        for episode in self.episodes:
            category = self._episode_category(episode)
            counts[category] = counts.get(category, 0) + 1
        return counts

    @staticmethod
    def _resolve_kind(category: str) -> MemoryEntryKind:
        """Map free-form category input to a known MemoryEntryKind."""
        normalized = category.strip().lower()
        mapping = {
            "note": MemoryEntryKind.NOTE,
            "fact": MemoryEntryKind.FACT,
            "finding": MemoryEntryKind.FINDING,
            "plan": MemoryEntryKind.PLAN,
            "artifact": MemoryEntryKind.ARTIFACT,
            "snapshot": MemoryEntryKind.SNAPSHOT,
        }
        return mapping.get(normalized, MemoryEntryKind.NOTE)

    @staticmethod
    def _episode_category(episode: MemoryEntry) -> str:
        """Return normalized category for an episode."""
        category = episode.metadata.get("category")
        if isinstance(category, str) and category:
            return category
        return episode.kind.value

    @staticmethod
    def _episode_tags(episode: MemoryEntry) -> list[str]:
        """Return tags from episode metadata."""
        tags = episode.metadata.get("tags", [])
        if isinstance(tags, list):
            return [tag for tag in tags if isinstance(tag, str)]
        return []

    @staticmethod
    def _serialize_episode(episode: MemoryEntry) -> dict[str, Any]:
        """Serialize immutable episode struct for checkpoint storage."""
        return {
            "entry_id": episode.entry_id,
            "session_id": episode.session_id,
            "agent_id": episode.agent_id,
            "scope": episode.scope.value,
            "tier": episode.tier.value,
            "kind": episode.kind.value,
            "content": episode.content,
            "metadata": episode.metadata,
            "importance": episode.importance,
            "persistent": episode.persistent,
            "ttl_seconds": episode.ttl_seconds,
            "expires_at": episode.expires_at,
            "created_at": episode.created_at,
        }

    def _deserialize_episode(self, payload: dict[str, Any]) -> MemoryEntry:
        """Deserialize checkpoint payload into MemoryEntry."""
        return MemoryEntry(
            entry_id=str(payload.get("entry_id", str(uuid4()))),
            session_id=str(payload.get("session_id", self.session_id)),
            agent_id=str(payload.get("agent_id", self.agent_id))
            if payload.get("agent_id") is not None
            else None,
            scope=MemoryScope(str(payload.get("scope", MemoryScope.AGENT.value))),
            tier=MemoryTier(str(payload.get("tier", MemoryTier.WARM.value))),
            kind=MemoryEntryKind(str(payload.get("kind", MemoryEntryKind.NOTE.value))),
            content=str(payload.get("content", "")),
            metadata=payload.get("metadata", {})
            if isinstance(payload.get("metadata"), dict)
            else {},
            importance=float(payload.get("importance", 0.5)),
            persistent=bool(payload.get("persistent", True)),
            ttl_seconds=payload.get("ttl_seconds")
            if isinstance(payload.get("ttl_seconds"), int)
            else None,
            expires_at=str(payload.get("expires_at"))
            if payload.get("expires_at") is not None
            else None,
            created_at=str(payload.get("created_at", "")),
        )


__all__ = ["AgentMemory"]
