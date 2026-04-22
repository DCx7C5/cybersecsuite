"""AI memory management tools — vault-backed MCP server module.

Memories persist to disk under CYBERSEC_VAULT_PATH/memories/{type}/*.md.
Falls back to in-process dict if the vault path is not writable.
"""
from __future__ import annotations

import datetime
import os
from pathlib import Path
from typing import Any

from csmcp._sdk_compat import tool
from csmcp.cybersec.helpers import JsonDict, _get_current_scope, sdk_result, sdk_error

_DEFAULT_VAULT_PATH = str(
    Path(os.environ.get("CYBERSECSUITE_HOME", str(Path.home() / ".cybersecsuite"))).expanduser()
    / "vault"
)
_VAULT_PATH = os.getenv("CYBERSEC_VAULT_PATH", _DEFAULT_VAULT_PATH)

# Fallback in-memory store used when disk writes fail
_MEMORY_STORE: dict[str, list[dict[str, Any]]] = {}


def _mem_root() -> Path:
    p = Path(_VAULT_PATH) / "memories"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _type_dir(mem_type: str) -> Path:
    d = _mem_root() / mem_type
    d.mkdir(exist_ok=True)
    return d


def _get_scope_key(scope: dict[str, Any]) -> str:
    return f"{scope['project']}:{scope['session'] or 'global'}"


def _ts() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _write_memory(mem_id: str, mem_type: str, content: str, tags: list[str], scope: dict) -> None:
    """Write memory entry as Markdown to vault; raise on failure."""
    tag_str = ", ".join(f'"{t}"' for t in tags)
    frontmatter = (
        f"---\n"
        f"id: {mem_id}\n"
        f"type: {mem_type}\n"
        f"tags: [{tag_str}]\n"
        f"scope: {scope['project']}\n"
        f"timestamp: {_ts()}\n"
        f"---\n\n"
    )
    path = _type_dir(mem_type) / f"{mem_id}.md"
    path.write_text(frontmatter + content + "\n", encoding="utf-8")


def _read_memories(mem_type: str | None, query: str, limit: int) -> list[dict[str, Any]]:
    """Read memories from vault, filter by type/query, return up to limit entries."""
    root = _mem_root()
    results: list[dict[str, Any]] = []
    q = query.lower()

    dirs = [root / mem_type] if mem_type else [d for d in root.iterdir() if d.is_dir()]
    for d in dirs:
        if not d.exists():
            continue
        for md in sorted(d.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                text = md.read_text(encoding="utf-8")
            except OSError:
                continue
            if q and q not in text.lower():
                continue
            # Parse minimal frontmatter
            entry: dict[str, Any] = {"id": md.stem, "type": d.name}
            if text.startswith("---"):
                fm_end = text.find("---", 3)
                if fm_end != -1:
                    for line in text[3:fm_end].splitlines():
                        if ": " in line:
                            k, v = line.split(": ", 1)
                            entry[k.strip()] = v.strip()
                    entry["content"] = text[fm_end + 3:].strip()
                else:
                    entry["content"] = text
            else:
                entry["content"] = text
            results.append(entry)
            if len(results) >= limit:
                break
        if len(results) >= limit:
            break
    return results


@tool(
    "memory_search",
    "Search vault-persisted memories by query and optional type.",
    {
        "query": {"type": "string", "default": ""},
        "type": {"type": "string", "enum": ["factual", "episodic", "procedural", "semantic"], "nullable": True},
        "limit": {"type": "integer", "default": 10},
    },
)
async def memory_search(args: dict[str, Any]) -> JsonDict:
    scope = _get_current_scope()
    query = args.get("query", "")
    mem_type = args.get("type")
    limit = min(int(args.get("limit", 10)), 50)

    try:
        results = _read_memories(mem_type, query, limit)
        return sdk_result({
            "status": "success",
            "memories": results,
            "count": len(results),
            "vault_path": str(Path(_VAULT_PATH) / "memories"),
            "scope": scope,
        })
    except Exception as exc:
        # Graceful fallback to in-memory store
        scope_key = _get_scope_key(scope)
        memories = _MEMORY_STORE.get(scope_key, [])
        q = query.lower()
        if mem_type:
            memories = [m for m in memories if m.get("type") == mem_type]
        if q:
            memories = [m for m in memories if q in m.get("content", "").lower()]
        memories.sort(key=lambda m: m.get("timestamp", ""), reverse=True)
        return sdk_result({
            "status": "success",
            "memories": memories[:limit],
            "count": len(memories[:limit]),
            "fallback": True,
            "error": str(exc),
            "scope": scope,
        })


@tool(
    "memory_add",
    "Add memory entry (factual/episodic/procedural/semantic). Persisted to vault on disk.",
    {
        "content": "string",
        "type": {"type": "string", "enum": ["factual", "episodic", "procedural", "semantic"], "default": "factual"},
        "tags": {"type": "array", "items": {"type": "string"}, "default": []},
        "metadata": {"type": "object", "default": {}},
    },
)
async def memory_add(args: dict[str, Any]) -> JsonDict:
    scope = _get_current_scope()
    content = args.get("content", "").strip()
    if not content:
        return sdk_error("content is required")

    mem_type = args.get("type", "factual")
    tags = args.get("tags", [])
    mem_id = f"mem_{int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)}"

    try:
        _write_memory(mem_id, mem_type, content, tags, scope)
        return sdk_result({
            "status": "success",
            "memory_id": mem_id,
            "message": f"Added {mem_type} memory entry",
            "vault_path": str(Path(_VAULT_PATH) / "memories" / mem_type / f"{mem_id}.md"),
            "scope": scope,
        })
    except Exception as exc:
        # Fallback to in-memory store
        scope_key = _get_scope_key(scope)
        entry = {
            "id": mem_id,
            "content": content,
            "type": mem_type,
            "tags": tags,
            "timestamp": _ts(),
            "scope": scope,
        }
        if scope_key not in _MEMORY_STORE:
            _MEMORY_STORE[scope_key] = []
        _MEMORY_STORE[scope_key].append(entry)
        return sdk_result({
            "status": "success",
            "memory_id": mem_id,
            "message": f"Added {mem_type} memory entry (in-memory fallback)",
            "fallback": True,
            "error": str(exc),
            "scope": scope,
        })


@tool(
    "memory_clear",
    "Clear vault memories, optionally filtered by type or age.",
    {
        "type": {"type": "string", "enum": ["factual", "episodic", "procedural", "semantic"], "nullable": True},
        "older_than_days": {"type": "integer", "nullable": True},
    },
)
async def memory_clear(args: dict[str, Any]) -> JsonDict:
    scope = _get_current_scope()
    mem_type = args.get("type")
    older_than_days = args.get("older_than_days")

    cleared = 0
    try:
        root = _mem_root()
        dirs = [root / mem_type] if mem_type else [d for d in root.iterdir() if d.is_dir()]
        cutoff: datetime.datetime | None = None
        if older_than_days:
            cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=int(older_than_days))
        for d in dirs:
            if not d.exists():
                continue
            for md in list(d.glob("*.md")):
                if cutoff is not None:
                    mtime = datetime.datetime.fromtimestamp(md.stat().st_mtime, tz=datetime.timezone.utc)
                    if mtime > cutoff:
                        continue
                md.unlink(missing_ok=True)
                cleared += 1
    except Exception as exc:
        # Also clear in-memory fallback
        scope_key = _get_scope_key(scope)
        old = len(_MEMORY_STORE.get(scope_key, []))
        _MEMORY_STORE.pop(scope_key, None)
        return sdk_result({
            "status": "success",
            "cleared_count": old,
            "message": f"Cleared {old} in-memory entries (vault error: {exc})",
            "scope": scope,
        })

    return sdk_result({
        "status": "success",
        "cleared_count": cleared,
        "message": f"Cleared {cleared} memory file(s) from vault",
        "vault_path": str(Path(_VAULT_PATH) / "memories"),
        "scope": scope,
    })


ALL_TOOLS = [memory_search, memory_add, memory_clear]
