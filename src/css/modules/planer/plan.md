⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

# @planer — Structured Multi-Step Planning

## 🔗 Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.core.types` | → consumes | Base types, Protocol contracts |
| `css.core.db` | → consumes | ORM models for plan persistence |
| `css.modules.working_dir` | → consumes | `planner` mode creates session dir + plan.md template |
| `css.modules.tasks` | ← provides to | Plan steps become @tasks tasks |
| `css.modules.agents` | ← provides to | Agents execute plan steps |
| `css.core.session` | → consumes | SessionContext (session_id, project_dir) |

---

## Purpose

The `@planer` module manages **structured multi-step planning** for agent sessions. It bridges the gap between a high-level objective and discrete executable steps, and tracks plan progress from creation through completion.

Key responsibilities:
- Create and manage plans (objective, steps, progress)
- Generate the `plan.md` template written into a session's working directory
- Track step execution state (pending → running → completed/failed)
- Report plan progress back to the orchestrator
- Integrate with `@tasks` so each plan step becomes a dispatchable task

---

## Working Directory Integration

When an agent session starts in **`planner` mode**, `WorkingDirManager.create(session_id, agent_id, mode="planner")` creates the full directory layout:

```
{session_dir}/
├── plan.md          ← planer module populates this
├── findings/
├── artifacts/
├── notes/
└── scratch/
```

The `plan.md` template written here has:
- Objective header
- Numbered steps (status: [ ] pending, [~] running, [x] done, [!] failed)
- Notes section

The planer module is responsible for reading/updating this file as steps execute.

---

## Plan Lifecycle

```
1. PlanCreator.create(objective, steps) → Plan
2. WorkingDirManager.create(mode="planner") → writes plan.md template
3. PlanExecutor.run_next_step() → dispatches step as @task
4. Step completes → PlanTracker.mark_complete(step_id)
5. plan.md updated in-place with progress markers
6. PlanReporter.summarize() → produces final report
```

---

## Implementation Checklist

- [ ] `Plan` model — objective, steps, status, created_at
- [ ] `PlanStep` model — id, description, status, result, depends_on
- [ ] `PlanCreator` — create plan from objective + step list
- [ ] `PlanExecutor` — dispatch next ready step as @task
- [ ] `PlanTracker` — update step status in DB + plan.md
- [ ] `PlanReporter` — summarize completed plan
- [ ] `plan_template.py` — generate initial plan.md content
- [ ] Add logger initialization in `__init__.py`

---

## Module Pattern

```python
# src/css/modules/planer/__init__.py
"""Structured multi-step planning for agent sessions."""

from css.core.logger import getLogger

logger = getLogger(__name__)

from .creator import PlanCreator
from .executor import PlanExecutor
from .tracker import PlanTracker

__all__ = ['PlanCreator', 'PlanExecutor', 'PlanTracker']
```

---

**Status**: 🔴 Priority (Medium) | **Last Updated**: 2026-05-03

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
