# @scopes — Scope Resolution & Config Cascade (Informational)

⚠️ **NOTE**: This module is **informational only** — it documents the scope hierarchy and config resolution strategy. No code/enums to implement. Actual scope enforcement happens in other modules (permissions, working_dir, projects, etc.).

---

## Scope Hierarchy: 3 Levels (Non-Nested Cascade)

Scopes are **NOT nested folders**. They are independent paths used for **config resolution cascade**.

### Level 1: GLOBAL Scope

**Location**: `~/.css/`  
**Applies to**: All projects, all sessions  
**Examples**: Global config, user credentials, global cache  
**Access**: User-level, cross-project

### Level 2: PROJECT Scope

**Location**: `$(pwd)/.css/` (dynamic path — wherever the project is)  
**Applies to**: This project, all sessions in this project  
**Examples**: Project-level config, project-level settings  
**Access**: Full project directory read/write (all processes)

### Level 3: SESSION Scope

**Location**: `~/.css/sessions/session-<sid>/`  
**Applies to**: This session only  
**Examples**: Session-level config, session results, task queues  
**Access**: Session-specific read/write

### Note on Teams

Teams organize **within** a session but use `session_id` for scope context. No separate TEAM config level yet (Phase 15 enhancement may add this).

---

## Config Cascade: Resolution Strategy

When resolving config values (e.g., `get_config("log_level")`):

**Check in this order** (highest → lowest priority):
1. **Session scope**: `~/.css/sessions/session-<sid>/config.yaml`
2. **Project scope**: `$(pwd)/.css/config.yaml` (PROJECT path is dynamic)
3. **Global scope**: `~/.css/config.yaml`
4. **Built-in defaults**: hardcoded in config.py

**First match wins.** Lower levels only consulted if higher level doesn't have value.

Example:
```yaml
# ~/.css/config.yaml (GLOBAL)
log_level: info

# $(pwd)/.css/config.yaml (PROJECT)
log_level: debug        # ← overrides GLOBAL

# ~/.css/sessions/session-123/config.yaml (SESSION)
log_level: trace        # ← overrides PROJECT + GLOBAL
```

---

## Implementation Pattern (Like Other Modules)

Each module handles its own scope via **ID references**, not cascading objects:

- **ConversationContext**: carries `session_id`, `user_id` (core/types/context.py)
- **ProjectRecord**: carries `project_id` (projects module)
- **ToolGrant/PathGrant**: carry `session_id` (permissions module, replaces old `scope_id`)
- **Roles**: implicitly scoped per session/team (roles module)

**No central ScopeManager.** Each module manages its own scope concerns using IDs.

---

## Scope Boundary Enforcement

| Scope | Boundary | Enforced By |
|-------|----------|------------|
| GLOBAL | `~/.css/` files only | PathGrant + permissions module |
| PROJECT | `$(pwd)/.css/` + project tree | PathGrant + permissions module |
| SESSION | `~/.css/sessions/session-<sid>/` | WorkingDirManager (Phase 15) |

---

## Stateless Agent/Team Model

**Key Design**: Subprocess teams and agents are **stateless workers**.

- Subprocess receives: input data
- Subprocess processes: executes agent/team work
- Subprocess returns: output directly to parent orchestrator
- Parent orchestrator: maintains all state/context

**No state cascade on session exit.** No merging memory back to parent. Cleaner, simpler, crash-resistant.

---

## Replacements for Old ScopeContext

Old model (deprecated):
| Old (scopes) | New | Location |
|-----|---|--------|
| ScopeContext | ConversationContext | core/types/context.py |
| scope_id | session_id | permissions, agents, etc. |
| ScopeManager | WorkingDirManager | (Phase 15) |
| ScopeLevel enum | (implicit via IDs) | (distributed) |

---

## Phase Timeline

- **Phase 15 addendum**: Implement WorkingDirManager (Phase 15 main task)
- **Phase 15 addendum**: Complete scope_id → session_id renames in permissions
- **Phase 15 final**: Delete any remaining ScopeLevel code

**Status**: Informational | **Phase**: 15 (no action needed until Phase 15) | **Last Updated**: 2026-05-05

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
