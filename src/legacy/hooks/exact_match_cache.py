#!/usr/bin/env python3
"""
Exact-Match Context Caching — Skill Integration
================================================
Deterministic SHA-256 hash-keyed caching via Redis (shared with
context-cache-server) with TTL enforcement and token-budget eviction.

Pattern (from exact-match-context-caching skill):
    hash(input) → lookup → hit: return cached / miss: execute + store

Usage from hooks (standalone):
    from exact_match_cache import cache_get, cache_put, compute_cache_key

Usage from project code:
    from hooks.exact_match_cache import cache_get, cache_put, compute_cache_key
"""


import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from typing import Any

try:
    import redis.asyncio as aioredis

    _REDIS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _REDIS_AVAILABLE = False  # type: ignore[assignment]
    aioredis = None  # type: ignore[assignment]

# Hooks may be run standalone — import without package prefix in that case.
try:
    from hooks.uvloop_integration import run_with_uvloop
except ModuleNotFoundError:  # pragma: no cover
    from uvloop_integration import run_with_uvloop  # type: ignore[no-redef]

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration (mirrors context-cache-server config.py)
# ---------------------------------------------------------------------------
_REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
_USE_REDIS: bool = os.getenv("USE_REDIS", "true").lower() == "true"
_DEFAULT_TTL: int = int(os.getenv("CACHE_TTL_SECONDS", 86400))   # 24 h
_KEY_PREFIX: str = "cybersec:"

# In-memory fallback (process-local, no persistence)
_local_cache: dict[str, dict[str, Any]] = {}


def _get_redis() -> "aioredis.Redis | None":  # type: ignore[name-defined]
    """Return an async Redis client, or None when Redis is unavailable."""
    if not _USE_REDIS or not _REDIS_AVAILABLE:
        return None
    try:
        return aioredis.from_url(_REDIS_URL, decode_responses=True)
    except Exception as exc:  # pragma: no cover
        logger.warning("exact_match_cache: Redis unavailable — %s", exc)
        return None


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def compute_cache_key(params: dict[str, Any]) -> str:
    """Return a deterministic ``cybersec:<sha256>`` key for *params*.

    The dict is serialised as canonical JSON (sorted keys, no whitespace)
    before hashing so that insertion order does not affect the key.
    """
    canonical = json.dumps(params, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(canonical.encode()).hexdigest()
    return f"{_KEY_PREFIX}{digest}"


# ---------------------------------------------------------------------------
# Async core
# ---------------------------------------------------------------------------

async def cache_get_async(key: str) -> dict[str, Any] | None:
    """Look up *key* in Redis (or in-memory fallback).

    Returns the cached dict ``{result, tokens_saved, timestamp}``
    or ``None`` on a miss.
    """
    client = _get_redis()
    if client:
        async with client as conn:
            raw = await conn.get(key)
        if raw:
            return json.loads(str(raw))
        return None
    return _local_cache.get(key)


async def cache_put_async(
    key: str,
    result: str,
    tokens_saved: int,
    ttl_seconds: int | None = None,
) -> str:
    """Store *result* under *key* with optional TTL.

    Falls back to the in-memory store when Redis is unavailable.
    Returns a short confirmation string.
    """
    ttl = ttl_seconds if ttl_seconds is not None else _DEFAULT_TTL
    entry: dict[str, Any] = {
        "result": result,
        "tokens_saved": tokens_saved,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    client = _get_redis()
    if client:
        async with client as conn:
            await conn.setex(key, ttl, json.dumps(entry))
    else:
        _local_cache[key] = entry
    backend = "redis" if (client is not None) else "in-memory"
    return f"Cached via {backend}. TTL: {ttl}s. Tokens saved: {tokens_saved}."


async def cache_invalidate_async(key: str) -> str:
    """Remove a single entry from the cache."""
    client = _get_redis()
    if client:
        async with client as conn:
            await conn.delete(key)
    else:
        _local_cache.pop(key, None)
    return f"Invalidated: {key}"


async def cache_analytics_async() -> dict[str, Any]:
    """Return live stats: entry count, total tokens saved, backend."""
    client = _get_redis()
    if client:
        async with client as conn:
            keys = await conn.keys(f"{_KEY_PREFIX}*")
            total_entries = len(keys)
            total_savings = 0
            for k in keys:
                raw = await conn.get(k)
                if raw:
                    try:
                        total_savings += int(json.loads(str(raw)).get("tokens_saved", 0))
                    except (ValueError, TypeError):
                        pass
        backend = "redis"
    else:
        total_entries = len(_local_cache)
        total_savings = sum(
            int(v.get("tokens_saved", 0)) for v in _local_cache.values()
        )
        backend = "in-memory"

    return {
        "total_entries": total_entries,
        "estimated_total_savings": total_savings,
        "backend": backend,
        "key_prefix": _KEY_PREFIX,
        "default_ttl_seconds": _DEFAULT_TTL,
    }


# ---------------------------------------------------------------------------
# Sync wrappers (mandatory project pattern — never asyncio.run())
# ---------------------------------------------------------------------------

def cache_get(key: str) -> dict[str, Any] | None:
    return run_with_uvloop(cache_get_async(key))


def cache_put(
    key: str,
    result: str,
    tokens_saved: int,
    ttl_seconds: int | None = None,
) -> str:
    return run_with_uvloop(cache_put_async(key, result, tokens_saved, ttl_seconds))


def cache_invalidate(key: str) -> str:
    return run_with_uvloop(cache_invalidate_async(key))


def cache_analytics() -> dict[str, Any]:
    return run_with_uvloop(cache_analytics_async())

