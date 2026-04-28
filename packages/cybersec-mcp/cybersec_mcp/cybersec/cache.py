"""Exact-match context caching tools — SDK in-process MCP server module."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from typing import Any

from cybersec_mcp.sdk_compat import tool
from ..helpers import JsonDict, sdk_result

_CACHE: dict[str, dict[str, Any]] = {}


def _cache_key(tool_name: str, params: dict[str, Any]) -> str:
    payload = json.dumps({"tool": tool_name, "params": params}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode()).hexdigest()


@tool(
    "cache_lookup",
    "Deterministic exact-match cache lookup. Returns cached result if TTL is valid.",
    {
        "tool_name": "string",
        "params": "object",
        "ttl_seconds": {"type": "integer", "default": 3600},
    },
)
async def cache_lookup(args: dict[str, Any]) -> JsonDict:
    key = _cache_key(args["tool_name"], args.get("params", {}))
    entry = _CACHE.get(key)
    if entry is None:
        return sdk_result({"status": "miss", "key": key})

    import time
    ttl = args.get("ttl_seconds", 3600)
    age = time.time() - entry["stored_at"]
    if age > ttl:
        del _CACHE[key]
        return sdk_result({"status": "expired", "key": key, "age_seconds": int(age)})

    return sdk_result({"status": "hit", "key": key, "result": entry["result"], "age_seconds": int(age)})


@tool(
    "cache_store",
    "Store a tool call result in the exact-match cache.",
    {
        "tool_name": "string",
        "params": "object",
        "result": "object",
        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
    },
)
async def cache_store(args: dict[str, Any]) -> JsonDict:
    import time
    key = _cache_key(args["tool_name"], args.get("params", {}))
    _CACHE[key] = {
        "tool_name": args["tool_name"],
        "params": args.get("params", {}),
        "result": args["result"],
        "tags": args.get("tags", []),
        "stored_at": time.time(),
        "stored_iso": datetime.now().isoformat(),
    }
    return sdk_result({"status": "stored", "key": key, "cache_size": len(_CACHE)})


@tool(
    "cache_analytics",
    "Return cache hit/miss statistics and entry listing.",
    {"limit": {"type": "integer", "default": 20}},
)
async def cache_analytics(args: dict[str, Any]) -> JsonDict:
    import time
    limit = min(int(args.get("limit", 20)), 200)
    now = time.time()
    entries = [
        {
            "key": k[:16] + "...",
            "tool_name": v["tool_name"],
            "stored_iso": v.get("stored_iso"),
            "age_seconds": int(now - v["stored_at"]),
            "tags": v.get("tags", []),
        }
        for k, v in list(_CACHE.items())[:limit]
    ]
    return sdk_result({"status": "success", "total_entries": len(_CACHE), "entries": entries})


@tool(
    "cache_invalidate",
    "Invalidate cache entries by key prefix, tag, or tool name.",
    {
        "tool_name": {"type": "string", "nullable": True},
        "tag": {"type": "string", "nullable": True},
        "key_prefix": {"type": "string", "nullable": True},
    },
)
async def cache_invalidate(args: dict[str, Any]) -> JsonDict:
    tool_name = args.get("tool_name")
    tag = args.get("tag")
    key_prefix = args.get("key_prefix")
    removed = 0

    keys_to_remove = []
    for k, v in _CACHE.items():
        if tool_name and v["tool_name"] == tool_name:
            keys_to_remove.append(k)
        elif tag and tag in v.get("tags", []):
            keys_to_remove.append(k)
        elif key_prefix and k.startswith(key_prefix):
            keys_to_remove.append(k)

    for k in keys_to_remove:
        del _CACHE[k]
        removed += 1

    return sdk_result({"status": "success", "removed": removed, "remaining": len(_CACHE)})


ALL_TOOLS = [cache_lookup, cache_store, cache_analytics, cache_invalidate]
