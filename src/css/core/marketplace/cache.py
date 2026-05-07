"""In-memory TTL cache for marketplace metadata.

Caches expensive marketplace queries (item listings, tag lookups) so that
repeated API calls don't hit the database on every request.

Cache is invalidated automatically on TTL expiry and can be invalidated
explicitly when marketplace state changes (install/uninstall/update).

The cache emits a ``marketplace.cache.invalidated`` event via the event bus
on each manual invalidation so observers (e.g. frontend WebSocket) can react.

Usage::

    from css.core.marketplace.cache import marketplace_cache

    # Populate
    marketplace_cache.set("items:all", items_list)

    # Lookup
    result = marketplace_cache.get("items:all")   # None on miss/expired

    # Invalidate on change
    marketplace_cache.invalidate("items:all")
    marketplace_cache.invalidate_all()            # nuke everything
"""

from __future__ import annotations

import time
import asyncio
import logging
from typing import Any, Optional

from css.core.config import MarketplaceConfig

logger = logging.getLogger(__name__)


class MarketplaceCache:
    """Simple in-memory TTL cache for marketplace query results.

    Keys are arbitrary strings (e.g. ``"items:all"``, ``"items:agent"``).
    Values are any picklable object.

    Attributes:
        _ttl: Time-to-live in seconds (from MarketplaceConfig).
        _store: Dict mapping key → (value, expiry_timestamp).
    """

    def __init__(self, ttl: Optional[int] = None) -> None:
        self._ttl = ttl if ttl is not None else MarketplaceConfig.CACHE_TTL_SECONDS
        self._store: dict[str, tuple[Any, float]] = {}

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def get(self, key: str) -> Optional[Any]:
        """Return the cached value for *key*, or ``None`` if missing/expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if time.monotonic() > expiry:
            del self._store[key]
            logger.debug("cache miss (expired): %s", key)
            return None
        logger.debug("cache hit: %s", key)
        return value

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key* with the default TTL."""
        expiry = time.monotonic() + self._ttl
        self._store[key] = (value, expiry)
        logger.debug("cache set: %s (ttl=%ss)", key, self._ttl)

    def invalidate(self, key: str) -> None:
        """Remove *key* from the cache and emit an invalidation event."""
        removed = self._store.pop(key, None)
        if removed is not None:
            logger.debug("cache invalidated: %s", key)
            self._emit_invalidated(key)

    def invalidate_prefix(self, prefix: str) -> int:
        """Remove all keys that start with *prefix*.  Returns count removed."""
        targets = [k for k in self._store if k.startswith(prefix)]
        for k in targets:
            del self._store[k]
        if targets:
            logger.debug("cache invalidated prefix '%s': %d keys", prefix, len(targets))
            self._emit_invalidated(prefix + "*")
        return len(targets)

    def invalidate_all(self) -> int:
        """Clear the entire cache.  Returns count removed."""
        count = len(self._store)
        self._store.clear()
        logger.debug("cache fully invalidated (%d keys)", count)
        if count:
            self._emit_invalidated("*")
        return count

    def _emit_invalidated(self, key: str) -> None:
        """Fire-and-forget event on the global event bus (non-blocking)."""
        try:
            from css.core.events.event_bus import event_bus

            async def _fire() -> None:
                await event_bus.emit(
                    "marketplace.cache.invalidated",
                    {"key": key},
                )

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(_fire())
            except RuntimeError:
                pass  # No running loop — skip event (e.g. in sync tests)
        except ImportError:
            pass  # events module not available

    # ------------------------------------------------------------------
    # Stats / introspection
    # ------------------------------------------------------------------

    def size(self) -> int:
        """Return number of non-expired entries currently in the cache."""
        now = time.monotonic()
        return sum(1 for _, (_, exp) in self._store.items() if exp > now)

    def __len__(self) -> int:
        return self.size()


# Module-level singleton
marketplace_cache = MarketplaceCache()

__all__ = ["MarketplaceCache", "marketplace_cache"]
