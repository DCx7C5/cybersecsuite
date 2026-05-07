# @agents — Agent Management & Orchestration

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.modules.events` | → consumes | `@instrument("agent.run.{agent_id}")` — Phase 14 entry point |
| `css.modules.permissions` | → consumes | PermissionChecker.can_tool(), require_path() |
| `css.modules.working_dir` | → consumes | WorkingDirManager.create() → SessionContext |
| `css.modules.llm_models` | → consumes | Routing tier selection for agent LLM calls |
| `css.core.session` | → consumes | SessionContext (session_id, agent_id, project_dir, target) |

---

## Current State

✅ **Active** — AgentExecutor implemented with provider-agnostic execution via HttpProviderAdapter.
Claude SDK hardcode removed from streaming/runner.py.

---

## Purpose

- Manage agent instances and lifecycle
- Coordinate multi-agent workflows
- Track agent state and metrics
- Handle agent communication patterns
- Support nested agent hierarchies

---

## Implementation Checklist

- [ ] Agent registry and lifecycle management
- [x] Agent execution engine (AgentExecutor → HttpProviderAdapter)
- [ ] State management
- [ ] Communication layer
- [ ] Monitoring and metrics
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/agents/__init__.py
"""Agent management and orchestration."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import AgentManager

__all__ = ['AgentManager']
```

---

**Status**: 🟢 Priority (Medium) | **Last Updated**: 2026-05-05
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

---

## Phase 14 — @instrument Entry Point

`Agent.run()` is **entry point 4 of 5** for the `@events` instrumentation system.

- Namespace: `@instrument("agent.run.{agent_id}")`
- Events fired: `agent.run.started`, `agent.run.completed`, `agent.run.failed`
- All runs inherit `correlation_id` ContextVar (propagated from HTTP middleware — entry point 1)
- Pre/post interceptors in `permissions/hooks.py` can mutate inputs or raise `HookErrorStrategy`

---

## Phase 15 — SessionContext Lifecycle

1. Agent startup → `WorkingDirManager.create(session_id, agent_id, mode)` → returns `SessionContext`
2. `ctx.project_dir` becomes the agent's working directory
3. Agent starts with **zero tool grants** — orchestrator must explicitly grant tools via `GrantManager`
4. Agent receives `SessionContext` as dependency injection (NOT `ScopeContext` — `@scopes` module is deleted in Phase 15)

### SessionContext Fields

```python
class SessionContext(msgspec.Struct, frozen=True):
    session_id: str
    agent_id: str
    project_dir: Path       # set by WorkingDirManager.create()
    target: str | None      # scan target (IP, domain, etc.)
    parent_session_id: str | None  # for sub-agents
```

### Working Directory Modes

| Mode | Contents | Use Case |
|------|----------|----------|
| `planner` | full layout + plan.md template | planning agents |
| `search` | findings/ + artifacts/ only | recon/search agents |
| `minimal` | root dir only | lightweight agents |

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
