"""Redis-backed exact-match prompt cache (Tier 1).

Provides O(1) cached LLM responses for identical input prompts across all providers.
Uses SHA256(messages + model + system_prompt) as cache key, stores complete response.
"""

import msgspec

from css.core.cache.redis_cache import L2RedisCache
from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse

logger = getLogger(__name__)


class ExactMatchPromptCache:
    """O(1) exact-match cache for LLM responses using Redis."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ttl_seconds: int = 86400,
        namespace: str = "prompt_cache:exact",
    ):
        """Initialize exact-match prompt cache backed by Redis.

        Args:
            redis_url: Redis connection string
            ttl_seconds: Cache TTL in seconds (default 24 hours)
            namespace: Redis namespace prefix for this cache
        """
        self.backend = L2RedisCache(namespace=namespace, redis_url=redis_url)
        self.ttl_seconds = ttl_seconds

    async def get(self, cache_key: str) -> LLMResponse | None:
        """Retrieve cached LLM response by exact-match key.

        Args:
            cache_key: SHA256 hash key from PromptCacheManager.compute_exact_match_key()

        Returns:
            LLMResponse if found, None if miss/error
        """
        raw = await self.backend.get(cache_key)
        if raw is None:
            return None

        raw_bytes: bytes
        if isinstance(raw, bytes):
            raw_bytes = raw
        elif isinstance(raw, str):
            raw_bytes = raw.encode()
        else:
            logger.warning(
                "Exact-match cache get received unsupported payload type %s",
                type(raw).__name__,
            )
            return None

        try:
            decoded = msgspec.json.decode(raw_bytes)
        except msgspec.DecodeError:
            logger.warning("Exact-match cache get failed to decode payload")
            return None

        if not isinstance(decoded, dict):
            logger.warning(
                "Exact-match cache get decoded unsupported payload type %s",
                type(decoded).__name__,
            )
            return None

        try:
            response = LLMResponse(**decoded)
        except TypeError:
            logger.warning("Exact-match cache get decoded invalid LLMResponse payload")
            return None

        logger.debug("Exact-match cache hit for key %s...", cache_key[:16])
        return response

    async def set(
        self,
        cache_key: str,
        response: LLMResponse,
    ) -> bool:
        """Store LLM response in exact-match cache.

        Args:
            cache_key: SHA256 hash key from PromptCacheManager.compute_exact_match_key()
            response: LLMResponse to cache

        Returns:
            True if stored, False on error
        """
        try:
            serialized = msgspec.json.encode(msgspec.to_builtins(response))
        except msgspec.EncodeError:
            logger.warning("Exact-match cache set failed to encode LLMResponse payload")
            return False

        success = await self.backend.set(
            cache_key,
            serialized,
            ttl_seconds=self.ttl_seconds,
        )
        if success:
            logger.debug("Exact-match cache stored for key %s...", cache_key[:16])
        return success

    async def delete(self, cache_key: str) -> bool:
        """Invalidate cached response by key.

        Args:
            cache_key: Key to invalidate

        Returns:
            True if deleted, False if not found or error
        """
        return await self.backend.delete(cache_key)

    async def clear(self) -> bool:
        """Clear all entries in this cache namespace.

        Returns:
            True if cleared, False on error
        """
        return await self.backend.clear()

    @property
    def stats(self):
        """Get cache statistics from underlying backend."""
        return self.backend.stats
