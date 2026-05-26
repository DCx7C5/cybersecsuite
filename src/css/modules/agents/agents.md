# @agents — Agent Management & Orchestration

**Tracking rule**: `.plan/session.db` is authoritative for todo status. This
document owns the executable agent-management specification.

---

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models (if applicable) |
| `css.core.events` | → consumes | `@instrument("agent.run.{agent_id}")` — Phase 14 entry point |
| `css.core.permissions` | → consumes | `PermissionChecker.can_tool()` and `require_path()` |
| Session/output-directory owner | → consumes | Resolve the canonical creator for isolated session state before wiring `SessionContext`. |
| `css.core.models` / `css.core.resilience` | → consumes | Model metadata and future provider-routing/resilience policy |
| Session context owner (unresolved) | → consumes | `SessionContext(session_id, agent_id, session_dir, project_id)` after ownership decision |

---

## Current State

🟡 **Partial** — `base.AgentExecutor` is the active provider-backed executor.
Its invocation contract now uses `BaseApiServiceClient.call_llm_buffered()`
against `api_services.ProviderRegistry`; the intended `core.sdks.CSSLLMClient`
gateway is not wired yet. The Claude SDK hardcode is removed from
`streaming/runner.py`.

### Architecture Note (2026-05-09)

- `AgentExecutor` now reaches tool execution through `css.core.tools.*`.
- Module-owned compatibility wrappers remain in place for legacy imports, but cross-module imports from `@agents` into `@tools` runtime code were removed.

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
**Details**: Query `.plan/session.db` for current status; retain agent implementation detail in this local document.

---

## Phase 14 — @instrument Entry Point

`Agent.run()` is **entry point 4 of 5** for the `@events` instrumentation system.

- Namespace: `@instrument("agent.run.{agent_id}")`
- Events fired: `agent.run.started`, `agent.run.completed`, `agent.run.failed`
- All runs inherit `correlation_id` ContextVar (propagated from HTTP middleware — entry point 1)
- Pre/post interceptors in `permissions/hooks.py` can mutate inputs or raise `HookErrorStrategy`

---

## Phase 15 — SessionContext Lifecycle

1. Agent startup obtains a `SessionContext` from the confirmed session-output owner.
2. `ctx.session_dir` identifies the permitted isolated session path; a project association is separate.
3. Agent starts with **zero tool grants** — orchestrator must explicitly grant tools via `GrantManager`
4. Agent receives `SessionContext` as dependency injection (NOT `ScopeContext` — `@scopes` module is deleted in Phase 15)

### SessionContext Fields

```python
class SessionContext(msgspec.Struct, frozen=True):
    session_id: str
    agent_id: str
    session_dir: Path       # isolated output path; owning allocator remains to be resolved
    project_id: str | None  # optional source/project association
    target: str | None      # scan target (IP, domain, etc.)
    parent_session_id: str | None  # for sub-agents
```

### Proposed Working Directory Modes

These modes remain behavioral requirements; their owning package is not
confirmed by the current source tree.

| Mode | Contents | Use Case |
|------|----------|----------|
| `planner` | full layout + plan.md template | planning agents |
| `search` | findings/ + artifacts/ only | recon/search agents |
| `minimal` | root dir only | lightweight agents |

---

## Tracker Reminder

> **STATUS AUTHORITY**: Query `.plan/session.db` for live todo progress.
>
> - This file defines the implementation contract, not completion state.
> - Update tracker state as required by `.plan/rules.md`.
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`

## Executable Owner Contract

### Exact File And Symbol Map

| Path | Live or planned symbols |
|------|-------------------------|
| `src/css/modules/agents/base.py` | Live `BaseAgent` protocol and `AgentExecutor.execute()` execution path; target for run instrumentation. |
| `src/css/modules/agents/models.py` | `AgentConfig`, `AgentResult`, `AgentTurn`, `TokenUsage`, `ConversationContext`. |
| `src/css/modules/agents/manager.py` | `AgentRegistry`; separate provisional `AgentExecutor` must not silently replace the execution owner. |
| `src/css/modules/agents/service.py` | `get_agent_registry()`, `create_agent()`, `get_agent()`, `list_agents()`, `delete_agent()`. |
| `src/css/core/session.py` | Planned canonical `SessionContext(session_id, agent_id, session_dir, project_id, target, parent_session_id)`. |
| `src/css/core/tools/` and `src/css/core/events/` | Tool execution and instrumentation dependencies consumed by agent execution. |

### Live Todo Map And Work Order

| Todo ID | Status | Required execution |
|---------|--------|--------------------|
| `events-instrument-agent` | pending | Instrument `AgentExecutor.execute()` or one forwarding `run()` wrapper, not the data-only agent value type. |
| `session-context-create` | pending | Define the shared `SessionContext` primitive using `session_dir`, without selecting an unconfirmed directory allocator. |
| `gap-agents-plan-stale` | pending | Keep this matrix aligned with actual base/manager/tools/session ownership. |
| `approval-agentexecutor-wire` | pending | Insert approval gating at tool preflight after permission evaluation and before side effects. |
| `git-tracker-hook` | pending | After session artifact ownership exists, commit only successful turn artifacts via the event/hook boundary. |
| `agent-execution-logic` | pending | The active `base.AgentExecutor` provider-call contract is repaired; reconcile the separate provisional executor in `manager.py`, which imports absent `AgentMetrics`, `AgentState`, and `AgentMessage`, and validate all public callers. |
| `provider-sdk-runtime-consolidation` | pending | Move the active agent/provider route onto the selected canonical SDK/registry gateway. |

1. Reconcile which `AgentExecutor` is imported by runtime callers and test
   that path before adding event or approval hooks.
2. Introduce `SessionContext` independently of filesystem allocator decisions
   and inject it through executor/planner/session consumers.
3. Apply instrumentation, permission/approval preflight, and eventually Git
   turn hooks in that order so one run emits one correlated lifecycle.
4. Validate import ownership, success/failure instrumentation, approval
   no-side-effect behavior, session field names, and dependency direction.
