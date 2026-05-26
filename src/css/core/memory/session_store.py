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
from typing import Protocol

from css.core.types.context import ConversationContext
from css.core.types.base_messages import BaseMessage
from css.core.types.enums import MessageRole
from css.core.memory.memory import MemoryEntryRecord, MemorySnapshotRecord
from css.core.memory.types import MemoryListResult, MemoryQuery

log = getLogger(__name__)


class _RedisClientProtocol(Protocol):
    async def setex(self, key: str, ttl_seconds: int, value: bytes) -> object: ...
    async def get(self, key: str) -> bytes | None: ...
    async def delete(self, key: str) -> int: ...
    async def keys(self, pattern: str) -> list[bytes | str]: ...
    async def ttl(self, key: str) -> int: ...
    async def expire(self, key: str, ttl_seconds: int) -> bool | int: ...
    async def ping(self) -> object: ...


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
        redis_client: _RedisClientProtocol,
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

    @staticmethod
    def _serialize_messages(messages: list[BaseMessage]) -> list[dict[str, str]]:
        """Serialize conversation messages for persistence."""
        return [
            {
                "role": message.role.value,
                "content": message.content,
            }
            for message in messages
        ]

    @staticmethod
    def _deserialize_messages(raw_messages: object) -> list[BaseMessage]:
        """Deserialize persisted message payload into typed BaseMessage structs."""
        if not isinstance(raw_messages, list):
            return []

        messages: list[BaseMessage] = []
        for raw in raw_messages:
            if not isinstance(raw, dict):
                continue
            role_raw = raw.get("role")
            content_raw = raw.get("content")
            if not isinstance(role_raw, str) or not isinstance(content_raw, str):
                continue
            try:
                role = MessageRole(role_raw)
            except ValueError:
                role = MessageRole.USER
            messages.append(BaseMessage(role=role, content=content_raw))
        return messages

    def _serialize_context(self, context: ConversationContext) -> dict[str, object]:
        """Serialize context to a durable payload shape."""
        return {
            "session_id": context.session_id,
            "user_id": context.user_id,
            "messages": self._serialize_messages(context.messages),
            "turn_number": context.turn_number,
            "metadata": context.metadata,
            "created_at": context.created_at.isoformat() if context.created_at else None,
            "updated_at": context.updated_at.isoformat() if context.updated_at else None,
        }

    def _deserialize_context(self, payload: object, session_id: str) -> ConversationContext | None:
        """Deserialize Redis/DB payload into ConversationContext."""
        if not isinstance(payload, dict):
            return None

        context_session_id = payload.get("session_id")
        user_id = payload.get("user_id")
        turn_number = payload.get("turn_number")
        metadata = payload.get("metadata")

        if not isinstance(context_session_id, str):
            context_session_id = session_id
        if not isinstance(user_id, str):
            user_id = ""
        if not isinstance(turn_number, int):
            turn_number = 0
        if not isinstance(metadata, dict):
            metadata = {}

        messages = self._deserialize_messages(payload.get("messages", []))
        return ConversationContext(
            session_id=context_session_id,
            user_id=user_id,
            messages=messages,
            turn_number=turn_number,
            metadata=metadata,
        )

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
            payload = self._serialize_context(context)
            context_bytes = msgspec.json.encode(payload)

            # Store in Redis with TTL
            key = f"session:{session_id}"
            await self.redis_client.setex(key, self.ttl_seconds, context_bytes)

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
                context_payload = msgspec.json.decode(context_bytes)
                restored = self._deserialize_context(context_payload, session_id=session_id)
                if restored is not None:
                    return restored
        except Exception as e:
            log.warning(f"Redis lookup failed for {session_id}: {e}")

        # Fallback to PostgreSQL
        try:
            log.debug(f"Falling back to PostgreSQL for session {session_id}")
            snapshot = (
                await MemorySnapshotRecord.filter(session_id=session_id)
                .order_by("-created_at")
                .first()
            )
            if snapshot is None:
                return None

            snapshot_payload: dict[str, object] = {
                "session_id": snapshot.session_id,
                "user_id": snapshot.metadata.get("user_id", "")
                if isinstance(snapshot.metadata, dict)
                else "",
                "messages": snapshot.entries if isinstance(snapshot.entries, list) else [],
                "turn_number": snapshot.metadata.get("turn_number", 0)
                if isinstance(snapshot.metadata, dict)
                else 0,
                "metadata": snapshot.metadata if isinstance(snapshot.metadata, dict) else {},
                "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
                "updated_at": snapshot.updated_at.isoformat() if snapshot.updated_at else None,
            }
            restored = self._deserialize_context(snapshot_payload, session_id=session_id)
            if restored is None:
                return None

            try:
                await self.redis_client.setex(
                    f"session:{session_id}",
                    self.ttl_seconds,
                    msgspec.json.encode(self._serialize_context(restored)),
                )
            except Exception as warm_err:
                log.warning(f"Redis warm-up failed for session {session_id}: {warm_err}")
            return restored
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
            entries_payload = self._serialize_messages(context.messages)
            # Create snapshot record
            await MemorySnapshotRecord.create(
                snapshot_id=f"checkpoint-{session_id}-{datetime.now(timezone.utc).isoformat()}",
                session_id=session_id,
                summary=f"Session {session_id} turn {context.turn_number}",
                entries=entries_payload,
                metadata={
                    "user_id": context.user_id,
                    "turn_number": context.turn_number,
                    "message_count": len(context.messages),
                },
                entry_count=len(entries_payload),
            )

            log.debug(f"Checkpointed session {session_id} to PostgreSQL")
            return True
        except Exception as e:
            log.error(f"Failed to checkpoint session {session_id} to database: {e}")
            return False

    async def list_memory_entries(self, query: MemoryQuery | None = None) -> MemoryListResult:
        """List persisted memory entries with scoped filtering."""
        if query is None:
            query = MemoryQuery()

        queryset = MemoryEntryRecord.all()
        if query.session_id:
            queryset = queryset.filter(session_id=query.session_id)
        if query.agent_id:
            queryset = queryset.filter(agent_id=query.agent_id)
        if query.scopes:
            queryset = queryset.filter(scope__in=query.scopes)
        if query.kinds:
            queryset = queryset.filter(kind__in=query.kinds)
        if query.text:
            queryset = queryset.filter(content__icontains=query.text)
        if query.min_importance is not None:
            queryset = queryset.filter(importance__gte=query.min_importance)
        if not query.include_ephemeral:
            queryset = queryset.filter(persistent=True)

        total = await queryset.count()
        records = await queryset.order_by("-created_at").offset(query.offset).limit(query.limit)
        entries = [record.to_struct() for record in records]

        if query.tags:
            required_tags = set(query.tags)
            entries = [
                entry
                for entry in entries
                if required_tags.intersection(
                    tag for tag in entry.metadata.get("tags", []) if isinstance(tag, str)
                )
            ]

        next_offset = None
        if query.offset + len(records) < total:
            next_offset = query.offset + len(records)

        return MemoryListResult(
            entries=entries,
            total=total,
            next_offset=next_offset,
        )

    async def prune_expired_entries(self, now: datetime | None = None) -> int:
        """Delete memory entries whose expires_at has elapsed."""
        cutoff = now or datetime.now(timezone.utc)
        return await MemoryEntryRecord.filter(
            expires_at__isnull=False,
            expires_at__lte=cutoff,
        ).delete()

    async def prune_session_entries(self, session_id: str, max_entries: int) -> int:
        """Enforce a max entry count per session by removing oldest overflow entries."""
        if max_entries < 1:
            return 0

        overflow = (
            await MemoryEntryRecord.filter(session_id=session_id)
            .order_by("-created_at")
            .offset(max_entries)
        )
        overflow_ids = [record.id for record in overflow]
        if not overflow_ids:
            return 0
        return await MemoryEntryRecord.filter(id__in=overflow_ids).delete()

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
            return bool(deleted > 0)
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
            return bool(result)
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
