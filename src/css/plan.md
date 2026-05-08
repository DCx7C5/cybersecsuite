# src/css — CyberSecSuite Package Root

**Location**: `src/css/`  
**Status**: 🟡 Active Development | Phases 0–4 partially complete, Phases 5–35 in progress

---

## Structure

```
src/css/
├── core/           # Shared infrastructure (db, cache, types, events, otel, accounts, permissions, …)
├── modules/        # Business logic modules (agents, skills, tools, chat, workflows, …)
├── api_services/   # External LLM provider adapters (24 providers)
├── app.py          # FastAPI application + lifespan
├── config.py       # Configuration source of truth (CONFIG_SPEC)
├── loader.py       # Module auto-discovery (endpoints.py + models.py)
├── manager.py      # CLI entry point (serve, init-db, shell)
└── plan.md         # This file
```

---

## Key Rules

- `core/` = infrastructure plus core-owned cross-cutting packages (`accounts`, `events`, `marketplace`, `memory`, `workspace`)
- `modules/` = business logic only; `accounts`, `events`, `marketplace`, and `memory` are core-only and must not exist as module packages
- `working_dir` is deprecated terminology; use the general directory structure owned by `core/workspace/`
- `api_services/` = provider adapters (YAML-driven, Phase 6 P2)
- See `.plan/rules.md` for full absolute rules

---

## Phase Progress

See `.plan/memory.md` for full phase table and `.plan/session.db` for all todos.

| Phase | Status |
|-------|--------|
| Phase 0 — TeamScope Foundation | ✅ Done |
| Phase 1 — Multi-Orchestrator Core | ✅ Done |
| Phase 2 — SDK Architecture | ✅ Done |
| Phase 3 — Module Consistency | 🟡 140/149 done |
| Phase 4 — Core Consistency + Types | 🟡 21/24 done |
| Phase 5 — Integration & Testing | 🟡 In progress |
| Phase 6 — Architecture Overhaul | 🟡 5/37 done |
| Phases 7–35 | 🔴 Pending |

---

## Local Planning Docs

Core areas use `plan.md`. Module directories under `src/css/modules/` use same-name docs like `agents/agents.md`. Read the nearest local planning markdown before working in that area.
