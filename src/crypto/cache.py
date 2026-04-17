"""
Simple JSON message cache with HMAC integrity.
No encryption - just integrity checking.
"""
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from collections import OrderedDict
from crypto.pydantic_models import CachedMessage, ArtifactChecksum


class MessageCache:
    """In-memory cache for JSON messages with integrity verification."""

    def __init__(self, max_size: int = 1000, default_ttl_hours: int = 24):
        """
        Initialize message cache.

        Args:
            max_size: Maximum number of cached messages
            default_ttl_hours: Default TTL for cached messages
        """
        self.cache: OrderedDict[str, CachedMessage] = OrderedDict()
        self.max_size = max_size
        self.default_ttl_hours = default_ttl_hours
        self.hits = 0
        self.misses = 0

    def _generate_cache_key(self, request: Dict[str, Any]) -> str:
        """
        Generate cache key from request.

        For exact-match caching, we hash the request.
        For semantic caching, you'd use embeddings instead.

        Args:
            request: Request dictionary

        Returns:
            Hex-encoded SHA256 hash of request
        """
        import json
        request_str = json.dumps(request, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(request_str.encode()).hexdigest()

    def put(
        self,
        request: Dict[str, Any],
        response: Dict[str, Any],
        ttl_hours: Optional[int] = None,
    ) -> str:
        """
        Cache a response.

        Args:
            request: Original request
            response: Response to cache
            ttl_hours: TTL override (None = use default)

        Returns:
            Cache key
        """
        cache_key = self._generate_cache_key(request)
        ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours

        # Create cached message
        cached_msg = CachedMessage.create(
            message_id=cache_key,
            request=request,
            response=response,
            expires_in_hours=ttl,
        )

        # Enforce max size with LRU eviction
        if len(self.cache) >= self.max_size:
            # Remove oldest item
            self.cache.popitem(last=False)

        self.cache[cache_key] = cached_msg
        return cache_key

    def get(
        self,
        request: Dict[str, Any],
        verify_integrity: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response.

        Args:
            request: Request to look up
            verify_integrity: Whether to verify HMAC before returning

        Returns:
            Cached response dict, or None if miss/expired/invalid
        """
        cache_key = self._generate_cache_key(request)

        if cache_key not in self.cache:
            self.misses += 1
            return None

        cached = self.cache[cache_key]

        # Check expiration
        if cached.is_expired():
            del self.cache[cache_key]
            self.misses += 1
            return None

        # Verify integrity if requested
        if verify_integrity:
            if not cached.verify_integrity():
                # Integrity check failed - don't return
                self.misses += 1
                return None

        # Move to end (LRU)
        self.cache.move_to_end(cache_key)

        # Increment hit count
        cached.hit_count += 1
        self.hits += 1

        return cached.response

    def invalidate(self, request: Dict[str, Any]) -> bool:
        """
        Manually invalidate a cached entry.

        Args:
            request: Request to invalidate

        Returns:
            True if entry existed and was removed
        """
        cache_key = self._generate_cache_key(request)
        if cache_key in self.cache:
            del self.cache[cache_key]
            return True
        return False

    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Stats dict with size, hit rate, etc.
        """
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate_percent": round(hit_rate, 2),
        }

    def get_cache_entries(self) -> list[Dict[str, Any]]:
        """
        Get all cached entries (for inspection).

        Returns:
            List of cache entries with metadata
        """
        entries = []
        for key, msg in self.cache.items():
            entries.append({
                "cache_key": key,
                "message_id": msg.message_id,
                "cached_at": msg.cached_at.isoformat(),
                "expires_at": msg.expires_at.isoformat() if msg.expires_at else None,
                "hit_count": msg.hit_count,
                "valid": msg.verify_integrity(),
            })
        return entries


class DistributedCache:
    """Simple file-based cache for persistence (Redis-compatible interface)."""

    def __init__(self, cache_dir: str = "/tmp/artifact_cache"):
        """
        Initialize distributed cache backed by JSON files.

        Args:
            cache_dir: Directory to store cache files
        """
        from pathlib import Path
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def put(self, key: str, value: Dict[str, Any], ttl_seconds: int = 86400) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value dict
            ttl_seconds: TTL in seconds
        """
        import json
        cache_file = self.cache_dir / f"{key}.json"

        data = {
            "value": value,
            "expires_at": (
                datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
            ).isoformat(),
        }

        cache_file.write_text(json.dumps(data))

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve value from cache.

        Args:
            key: Cache key

        Returns:
            Value dict or None if missing/expired
        """
        import json
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        data = json.loads(cache_file.read_text())

        # Check expiration
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            cache_file.unlink()
            return None

        return data["value"]

    def delete(self, key: str) -> bool:
        """
        Delete cache entry.

        Args:
            key: Cache key

        Returns:
            True if entry existed
        """
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            cache_file.unlink()
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries."""
        import shutil
        shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir()

