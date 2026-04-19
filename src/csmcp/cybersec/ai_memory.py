"""AI memory management tools — SDK in-process MCP server module."""
from __future__ import annotations

from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, _get_current_scope, sdk_result, sdk_error

# Module-level memory store: scope_key -> list of memory entries
_MEMORY_STORE: dict[str, list[dict[str, Any]]] = {}


def _get_scope_key(scope: dict[str, Any]) -> str:
    """Generate a unique key for the current scope."""
    return f"{scope['project']}:{scope['session'] or 'global'}"


@tool(
    "memory_search",
    "Search memories by query, type, or API key with token budget enforcement.",
    {
        "query": {"type": "string", "default": ""},
        "type": {"type": "string", "enum": ["factual", "episodic", "procedural", "semantic"], "nullable": True},
        "limit": {"type": "integer", "default": 10},
    },
)
async def memory_search(args: dict[str, Any]) -> JsonDict:
    scope = _get_current_scope()
    scope_key = _get_scope_key(scope)
    query = args.get("query", "").lower()
    mem_type = args.get("type")
    limit = min(args.get("limit", 10), 50)  # Cap at 50

    memories = _MEMORY_STORE.get(scope_key, [])
    if mem_type:
        memories = [m for m in memories if m.get("type") == mem_type]

    if query:
        memories = [m for m in memories if query in m.get("content", "").lower() or query in m.get("tags", [])]

    # Sort by timestamp descending
    memories.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
    results = memories[:limit]

    return sdk_result({
        "status": "success",
        "memories": results,
        "count": len(results),
        "total_available": len(memories),
        "scope": scope,
    })


@tool(
    "memory_add",
    "Add memory entry (factual/episodic/procedural/semantic).",
    {
        "content": "string",
        "type": {"type": "string", "enum": ["factual", "episodic", "procedural", "semantic"], "default": "factual"},
        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
        "metadata": {"type": "object", "default": {}},
    },
)
async def memory_add(args: dict[str, Any]) -> JsonDict:
    scope = _get_current_scope()
    scope_key = _get_scope_key(scope)
    content = args.get("content", "").strip()
    if not content:
        return sdk_error("content is required")

    import datetime
    entry = {
        "id": f"mem_{int(datetime.datetime.now().timestamp() * 1000)}",
        "content": content,
        "type": args.get("type", "factual"),
        "tags": args.get("tags", []),
        "metadata": args.get("metadata", {}),
        "timestamp": datetime.datetime.now().isoformat(),
        "scope": scope,
    }

    if scope_key not in _MEMORY_STORE:
        _MEMORY_STORE[scope_key] = []
    _MEMORY_STORE[scope_key].append(entry)

    return sdk_result({
        "status": "success",
        "memory_id": entry["id"],
        "message": f"Added {entry['type']} memory entry",
        "scope": scope,
    })


@tool(
    "memory_clear",
    "Clear memories for API key, optionally filtered by type or age.",
    {
        "type": {"type": "string", "enum": ["factual", "episodic", "procedural", "semantic"], "nullable": True},
        "older_than_days": {"type": "integer", "nullable": True},
    },
)
async def memory_clear(args: dict[str, Any]) -> JsonDict:
    scope = _get_current_scope()
    scope_key = _get_scope_key(scope)
    mem_type = args.get("type")
    older_than_days = args.get("older_than_days")

    if scope_key not in _MEMORY_STORE:
        return sdk_result({"status": "success", "cleared_count": 0, "message": "No memories to clear"})

    memories = _MEMORY_STORE[scope_key]
    original_count = len(memories)

    if mem_type:
        memories[:] = [m for m in memories if m.get("type") != mem_type]

    if older_than_days:
        import datetime
        cutoff = datetime.datetime.now() - datetime.timedelta(days=older_than_days)
        memories[:] = [m for m in memories if datetime.datetime.fromisoformat(m.get("timestamp", "")) > cutoff]

    cleared_count = original_count - len(memories)
    return sdk_result({
        "status": "success",
        "cleared_count": cleared_count,
        "remaining_count": len(memories),
        "message": f"Cleared {cleared_count} memories",
        "scope": scope,
    })


ALL_TOOLS = [memory_search, memory_add, memory_clear]
