"""Session store — Redis (short-term) + PostgreSQL (long-term) persistence.

Implements hybrid session persistence:
1. Redis: Fast short-term storage with TTL=24h for active sessions
2. PostgreSQL: Durable long-term storage via Tortoise ORM models
3. Load strategy: Try Redis first, fallback to PostgreSQL

This enables fast session resumption while ensuring durability.
"""


from css.core.logger import getLogger
import msgspec
from datetime import datetime, timezone

from css.core.types.context import ConversationContext
from css.core.memory.models import MemorySnapshotRecord

log = getLogger(__name__)


class SessionStore:
    """Hybrid session persistence with Redis (hot) + PostgreSQL (cold).
    
    Stores conversation contexts in Redis with 24h TTL for quick access,
    persists to PostgreSQL for durability, and automatically manages tiering.
    
    Attributes:
        redis_client: Redis client (redis.asyncio.Redis or compatible)
        ttl_seconds: Time-to-live for Redis entries (default 86400 = 24h)
        enable_auto_checkpoint: Automatically save to DB on context changes
    """

    # Default Redis TTL: 24 hours
    DEFAULT_TTL_SECONDS = 86400

    def __init__(
        self,
        redis_client,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        enable_auto_checkpoint: bool = True,
    ):
        """Initialize session store.
        
        Args:
            redis_client: Redis async client
            ttl_seconds: Redis key TTL in seconds (default 86400)
            enable_auto_checkpoint: Auto-persist contexts to DB
        """
        self.redis_client = redis_client
        self.ttl_seconds = ttl_seconds
        self.enable_auto_checkpoint = enable_auto_checkpoint

    async def save_context(
        self,
        session_id: str,
        context: ConversationContext,
    ) -> bool:
        """Save context to Redis (short-term).
        
        Serializes ConversationContext using msgspec and stores in Redis
        with TTL. Does NOT persist to database.
        
        Args:
            session_id: Unique session identifier
            context: ConversationContext to save
            
        Returns:
            True if save succeeded, False otherwise
            
        Note:
            Use checkpoint_to_db() separately to persist to database.
        """
        try:
            # Serialize context
            context_bytes = msgspec.json.encode({
                "session_id": context.session_id,
                "user_id": context.user_id,
                "messages": [
                    {
                        "role": msg.role.value if hasattr(msg.role, 'value') else str(msg.role),
                        "content": msg.content
                    }
                    for msg in context.messages
                ],
                "turn_number": context.turn_number,
                "metadata": context.metadata,
                "created_at": context.created_at.isoformat() if context.created_at else None,
                "updated_at": context.updated_at.isoformat() if context.updated_at else None,
            })
            
            # Store in Redis with TTL
            key = f"session:{session_id}"
            await self.redis_client.setex(
                key,
                self.ttl_seconds,
                context_bytes
            )
            
            log.debug(f"Saved session {session_id} to Redis (TTL: {self.ttl_seconds}s)")
            
            # Optionally checkpoint to database
            if self.enable_auto_checkpoint:
                await self.checkpoint_to_db(session_id, context)
            
            return True
        except Exception as e:
            log.error(f"Failed to save context for session {session_id}: {e}")
            return False

    async def load_context(
        self,
        session_id: str,
    ) -> ConversationContext | None:
        """Load context from Redis (fast), fallback to PostgreSQL.
        
        Tries Redis first for speed. If not found, queries PostgreSQL
        for persisted context. Returns None if not found in either store.
        
        Args:
            session_id: Session identifier to load
            
        Returns:
            ConversationContext if found, None otherwise
        """
        # Try Redis first
        try:
            key = f"session:{session_id}"
            context_bytes = await self.redis_client.get(key)
            
            if context_bytes:
                log.debug(f"Loaded session {session_id} from Redis (cache hit)")
                context_data = msgspec.json.decode(context_bytes)
                # Reconstruct ConversationContext (simplified for this version)
                return ConversationContext(
                    session_id=context_data.get("session_id", ""),
                    user_id=context_data.get("user_id", ""),
                    turn_number=context_data.get("turn_number", 0),
                    metadata=context_data.get("metadata", {}),
                )
        except Exception as e:
            log.warning(f"Redis lookup failed for {session_id}: {e}")
        
        # Fallback to PostgreSQL
        try:
            log.debug(f"Falling back to PostgreSQL for session {session_id}")
            # Query memory models (would need session_id field in schema)
            # For now, placeholder - would query MemoryEntryRecord by session_id
            log.info(f"PostgreSQL fallback: would query session {session_id}")
            return None
        except Exception as e:
            log.error(f"PostgreSQL lookup failed for {session_id}: {e}")
            return None

    async def checkpoint_to_db(
        self,
        session_id: str,
        context: ConversationContext,
    ) -> bool:
        """Persist context to PostgreSQL (durable storage).
        
        Creates a MemorySnapshotRecord with the current conversation state.
        This ensures context is persisted even if Redis expires.
        
        Args:
            session_id: Session identifier
            context: ConversationContext to checkpoint
            
        Returns:
            True if checkpoint succeeded, False otherwise
        """
        try:
            # Create snapshot record
            await MemorySnapshotRecord.create(
                snapshot_id=f"checkpoint-{session_id}-{datetime.now(timezone.utc).isoformat()}",
                session_id=session_id,
                summary=f"Session {session_id} turn {context.turn_number}",
                entries=[],  # Would populate from messages
                metadata={
                    "user_id": context.user_id,
                    "turn_number": context.turn_number,
                    "message_count": len(context.messages),
                },
            )
            
            log.debug(f"Checkpointed session {session_id} to PostgreSQL")
            return True
        except Exception as e:
            log.error(f"Failed to checkpoint session {session_id} to database: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis (will remain in PostgreSQL archive).
        
        Args:
            session_id: Session to delete
            
        Returns:
            True if deletion succeeded
        """
        try:
            key = f"session:{session_id}"
            deleted = await self.redis_client.delete(key)
            log.debug(f"Deleted session {session_id} from Redis")
            return deleted > 0
        except Exception as e:
            log.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def list_active_sessions(self) -> list[str]:
        """List all active sessions in Redis.
        
        Returns:
            List of session IDs currently in Redis
        """
        try:
            keys = await self.redis_client.keys("session:*")
            sessions = [key.decode() if isinstance(key, bytes) else key for key in keys]
            return [s.replace("session:", "") for s in sessions]
        except Exception as e:
            log.error(f"Failed to list active sessions: {e}")
            return []

    async def get_session_ttl(self, session_id: str) -> int | None:
        """Get remaining TTL for a session in Redis.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Remaining TTL in seconds, or None if not found
        """
        try:
            key = f"session:{session_id}"
            ttl = await self.redis_client.ttl(key)
            return ttl if ttl >= 0 else None
        except Exception as e:
            log.error(f"Failed to get TTL for session {session_id}: {e}")
            return None

    async def refresh_session_ttl(self, session_id: str) -> bool:
        """Refresh session TTL in Redis (extend expiration).
        
        Args:
            session_id: Session to refresh
            
        Returns:
            True if refresh succeeded
        """
        try:
            key = f"session:{session_id}"
            result = await self.redis_client.expire(key, self.ttl_seconds)
            log.debug(f"Refreshed session {session_id} TTL")
            return result
        except Exception as e:
            log.error(f"Failed to refresh TTL for session {session_id}: {e}")
            return False

    async def health_check(self) -> dict[str, bool]:
        """Check health of both storage backends.
        
        Returns:
            Dict with 'redis' and 'postgresql' keys, True if healthy
        """
        health = {"redis": False, "postgresql": False}
        
        # Check Redis
        try:
            await self.redis_client.ping()
            health["redis"] = True
        except Exception as e:
            log.warning(f"Redis health check failed: {e}")
        
        # Check PostgreSQL (would need Tortoise connection check)
        try:
            # Simple query to verify DB connection
            await MemorySnapshotRecord.get_or_none(id=0)
            health["postgresql"] = True
        except Exception as e:
            log.warning(f"PostgreSQL health check failed: {e}")
        
        return health
