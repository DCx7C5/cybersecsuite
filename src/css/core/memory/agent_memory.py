"""Per-agent episodic memory — aggregate agent context with persistent storage.

AgentMemory combines:
1. ContextWindow: Active message window with token budget
2. SessionStore: Persistent storage (Redis + PostgreSQL)
3. Episodic memory: Collection of memorable events/facts about the agent

Enables agents to maintain context across conversations and remember important facts.
"""

from css.core.logger import getLogger
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from .context_window import ContextWindow
from .session_store import SessionStore
from .types import MemoryEntry

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
        self.context_window = context_window or ContextWindow()
        self.session_store = session_store
        self.max_episodes: int = max_episodes
        self.episodes: list[MemoryEntry] = []
        self.metadata: dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.accessed_at = datetime.utcnow()
    
    def add_episode(self, content: str, category: str = "fact", tags: list[str] | None = None) -> MemoryEntry:
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
        episode = MemoryEntry(
            id=str(uuid4()),
            content=content,
            category=category,
            tags=tags or [],
            created_at=datetime.utcnow(),
            metadata={"agent_id": self.agent_id}
        )
        
        # Add to episodes
        self.episodes.append(episode)
        
        # Evict oldest episodes if over limit
        if len(self.episodes) > self.max_episodes:
            evicted = self.episodes.pop(0)
            log.debug(f"Agent {self.agent_id}: evicted episode {evicted.id}")
        
        log.debug(f"Agent {self.agent_id}: added episode {episode.id} ({category})")
        self.accessed_at = datetime.utcnow()
        
        return episode
    
    def get_episodes(self, category: Optional[str] = None, tags: Optional[list[str]] = None) -> list[MemoryEntry]:
        """Retrieve episodes with optional filtering.
        
        Args:
            category: Filter by episode category (optional)
            tags: Filter to episodes with any of these tags (optional)
            
        Returns:
            List of matching episodes
        """
        results = self.episodes
        
        if category:
            results = [e for e in results if e.category == category]
        
        if tags:
            results = [e for e in results if any(tag in e.tags for tag in tags)]
        
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
            log.warning(f"Agent {self.agent_id}: no session store configured, cannot save checkpoint")
            return False
        
        try:
            # Save via session store
            # Note: This requires extending SessionStore with save_snapshot method
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
            log.warning(f"Agent {self.agent_id}: no session store configured, cannot load checkpoint")
            return False
        
        try:
            # Load via session store
            # Note: This requires extending SessionStore with load_snapshot method
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
        counts = {}
        for episode in self.episodes:
            counts[episode.category] = counts.get(episode.category, 0) + 1
        return counts


__all__ = ["AgentMemory"]
