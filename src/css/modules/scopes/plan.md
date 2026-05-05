# @scopes — ⛔ DEPRECATED: SCHEDULED FOR DELETION (Phase 15)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## ⛔ STATUS: DEPRECATED — DO NOT USE, DO NOT EXTEND

**Reason**: The `ScopeLevel` (GLOBAL→APP→PROJECT→RUNTIME→SESSION) multi-tenant SaaS hierarchy does not fit a cybersecurity tool. This entire module is being removed in Phase 15.

**Todo ID**: `scopes-module-remove` (tracked in session.db)

> ⚠️ **WARNING**: Do NOT import from this module in any new code. All existing imports must be migrated to replacements before `scopes-module-remove` todo is closed.

---

## What Was Here

| Component | Description |
|-----------|-------------|
| `ScopeLevel` enum | GLOBAL → APP → PROJECT → RUNTIME → SESSION (5-level SaaS hierarchy) |
| `ScopeContext` | Context object carrying scope resolution state |
| `ScopeManager` | CRUD + access control for the scope hierarchy |
| `ScopeRestriction` | NONE, READ_ONLY, DENY, REQUIRE_AUTH, REQUIRE_ROLE |

---

## Replacements

| Old | Replacement | Location |
|-----|-------------|----------|
| `ScopeContext` | `SessionContext(msgspec.Struct, frozen=True)` | `css/core/session.py` |
| `ScopeManager.create()` | `WorkingDirManager.create()` | `css/modules/working_dir/` |
| `scope_id` on PathGrant/ToolGrant | `session_id` field | `css/modules/permissions/` |
| `ScopeLevel` in `options_manager.py` | Local `ConfigLayer(str, Enum)` | `css/modules/streaming/options_manager.py` |

### SessionContext (replacement for ScopeContext)

```python
# css/core/session.py
class SessionContext(msgspec.Struct, frozen=True):
    session_id: str
    agent_id: str
    project_dir: Path
    target: str | None
    parent_session_id: str | None
```

### WorkingDirManager (replacement for scope creation)

`WorkingDirManager.create(session_id, agent_id, mode)` creates the session directory AND auto-registers the least-privilege PathGrant (agent → session_dir/** → READ+WRITE). Returns `SessionContext`.

---

## Migration Todos (in dependency order)

| Todo ID | Description | Status |
|---------|-------------|--------|
| `session-context-create` | Create `SessionContext` in `css/core/session.py` | pending |
| `working-dir-manager` | Implement `WorkingDirManager.create()` | pending |
| `perm-rename-scope-to-session` | Rename `scope_id` → `session_id` on all grants | pending |
| `streaming-decouple-from-scopes` | Replace `ScopeLevel` import with local `ConfigLayer` | pending |
| `scopes-module-remove` | Delete this entire module (LAST step) | pending |

---

**Status**: ⛔ DEPRECATED | **Phase**: Phase 15 addendum | **Last Updated**: 2026-05-03

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
