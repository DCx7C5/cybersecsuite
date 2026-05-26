# core/permissions — Plan

**Status**: Phase 15 redesign — NOT YET IMPLEMENTED
**Phase**: 15 (depends on Phase 14 interceptors for enforcement)
**Status authority**: `.plan/session.db`; this document owns the executable local specification

---

## What This Module Does

Fine-grained access control for agents. Two orthogonal axes:
1. **Path access**: can agent X read/write/execute filesystem path Y? Can they do it as root?
2. **Tool access**: can agent X use tool Y?

Nothing else. Session/project scoping must use the surviving canonical DB and
session contracts rather than recreating the removed `modules/scopes`
surface. Session/project output-directory ownership is unresolved:
documentation cleanup found no implemented
`core/workspace/` package. Preserve legacy `working-dir-*` todo identifiers
until the later source/architecture reconciliation determines the real owner.

---

## Architecture

### Three Core Types

```python
class PathOp(Flag):
    READ    = auto()
    WRITE   = auto()
    EXECUTE = auto()
    ALL     = READ | WRITE | EXECUTE

class PathGrant(msgspec.Struct, frozen=True):
    agent_id: str
    path_pattern: str      # glob: "/etc/**", "/home/**", "/usr/bin/nmap"
    ops: frozenset[str]    # {"READ"}, {"WRITE","READ"}, {"EXECUTE"}
    elevated: bool = False # True = agent MAY use sudo/root for this path
    scope_id: str | None = None
    expires_at: float | None = None

class ToolGrant(msgspec.Struct, frozen=True):
    agent_id: str
    tool_pattern: str  # glob: "bash.*", "file.read", "*"
    allowed: bool = True  # False = explicit deny (deny-wins)
    scope_id: str | None = None
    expires_at: float | None = None
```

### The PermissionChecker (only import other modules need)

```python
from css.core.permissions import PermissionChecker

checker = PermissionChecker(cache)

# Path check
ok = await checker.can_path(agent_id, "/etc/passwd", PathOp.READ)

# Tool check — deny-wins
ok = await checker.can_tool(agent_id, "bash.execute")

# Elevation check — SEPARATE from can_path
ok = await checker.can_elevated(agent_id, "/usr/bin/nmap")

# Raise versions
await checker.require_path(agent_id, path, PathOp.WRITE)   # raises PermissionDenied
await checker.require_tool(agent_id, "browser.navigate")   # raises PermissionDenied
await checker.require_elevated(agent_id, "/root/")         # raises ElevationDenied
```

### Deny-Wins Rule for Tools

If ANY `ToolGrant` with `allowed=False` matches `tool_name` → access **DENIED**, even if other grants allow it.

Example: grant `"*"` to orchestrator, then deny `"bash.rm_rf"` → bash.rm_rf is blocked, all others work.

### Elevation is a Separate Gate

`can_path(agent_id, "/usr/bin/nmap", PathOp.EXECUTE)` → checks execute permission  
`can_elevated(agent_id, "/usr/bin/nmap")` → checks sudo/root flag separately  
**Both must be True** to run something as root. They are independent checks.

---

## File Layout (Phase 15 target)

```
core/permissions/
├── __init__.py          # exports: PermissionChecker, GrantManager, PathGrant, ToolGrant, PathOp
├── enums.py             # PathOp(Flag), GrantProfile enum
├── types.py             # PathGrant, ToolGrant (msgspec.Struct)
├── exceptions.py        # AccessDenied, PermissionDenied, ElevationDenied
├── models.py            # PathGrantRecord, ToolGrantRecord (Tortoise)
├── cache.py             # GrantCache (Redis, TTL 60s, per-agent key)
├── checker.py           # PermissionChecker — can_path / can_tool / can_elevated
├── decorators.py        # @require_path, @require_tool
├── manager.py           # GrantManager — CRUD + apply_profile
├── profiles.py          # PROFILE_DEFINITIONS dict
├── hooks.py             # @pre_hook("tool.call.*") + @pre_hook("agent.run.*")
├── endpoints.py         # 8 REST routes
└── permissions.md       # THIS FILE
```

---

## Module Boundary Rules

| ❌ Do NOT put in @permissions | ✅ Put here instead |
|-------------------------------|-------------------|
| Scope hierarchy (GLOBAL→SESSION) | Canonical DB/session types after `ScopeLevel` reconciliation |
| Session/output-directory building | Owner to be confirmed from source; do not create or assume `core/workspace/` from this plan alone. |
| JWT / auth token validation | `@asgi` middleware |
| Role definitions (ADMIN, etc.) | `@roles` |

---

## Todos (session.db — Phase 15)

| ID | Task | Status |
|----|------|--------|
| `perm-path-op-flag` | PathOp(Flag) enum | pending |
| `perm-path-grant-struct` | PathGrant msgspec.Struct | pending |
| `perm-tool-grant-struct` | ToolGrant msgspec.Struct | pending |
| `perm-grant-models` | PathGrantRecord + ToolGrantRecord ORM | pending |
| `perm-grant-redis-cache` | GrantCache Redis layer | pending |
| `perm-checker-exceptions` | PermissionDenied + ElevationDenied | pending |
| `perm-checker-can-path` | can_path + require_path | pending |
| `perm-checker-can-tool` | can_tool + require_tool (deny-wins) | pending |
| `perm-checker-can-elevated` | can_elevated + require_elevated | pending |
| `perm-decorator-require-path` | @require_path decorator | pending |
| `perm-decorator-require-tool` | @require_tool decorator | pending |
| `perm-grant-manager` | GrantManager CRUD | pending |
| `perm-grant-profiles` | GrantProfile + PROFILE_DEFINITIONS | pending |
| `perm-hook-tool-enforcement` | @pre_hook("tool.call.*") | pending |
| `perm-hook-path-enforcement` | @pre_hook("agent.run.*") | pending |
| `perm-scopes-cleanup` | Remove permission logic from @scopes | pending |
| `perm-rest-endpoints` | 8 REST endpoints | pending |

All todos have deps in session.db. Start with `perm-path-op-flag`, then `perm-checker-exceptions` (no deps).

## Audit (2026-05-04)

**Status**: TODO `db-fix-pk-permissions` completed
**Changes**:
- `PermissionGrant.id` and `RolePermissionCache.id` migrated to `BigIntField(primary_key=True)`
- `ScopeSession.id` migrated to `BigIntField(primary_key=True)` and `session_id` added as unique external identifier

---

## What Needs Replacing (Current State)

Current `types.py` has `PermissionPolicy` (path_permissions set + tool_permissions set) — **replace with PathGrant + ToolGrant**.

Current `models.py` has `PermissionGrant` Tortoise model — **replace with PathGrantRecord + ToolGrantRecord**.

Current `ScopeContext.has_permission()` in `@scopes` always returns `True` — **delete after `perm-checker-can-path` is done**.

`__init__.py` is empty — **fill after T15.3 complete**.
