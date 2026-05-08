# src/css — CyberSecSuite Package Root

**Location**: `src/css/`  
**Status**: 🟡 Active Development | See `.plan/memory.md` and `.plan/session.db` for exact phase status

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

- `core/` = infrastructure plus core-owned cross-cutting packages (`accounts`, `events`, `marketplace`, `memory`, `workspace`, `rag_vector`, and `rag_graph`)
- `modules/` = business logic only; `accounts`, `events`, `marketplace`, and `memory` are core-only and must not exist as module packages
- `working_dir` is deprecated terminology; use the general directory structure owned by `core/workspace/`
- `api_services/` = provider adapters (YAML-driven, Phase 6 P2)
- See `.plan/rules.md` for full absolute rules

---

## Phase Progress

See `.plan/memory.md` for full phase table and `.plan/session.db` for all todos. Avoid copying exact counts into this file unless you are explicitly refreshing them from the tracker.

| Phase | Status |
|-------|--------|
| Phase 0 — TeamScope Foundation | ✅ Done |
| Phase 1 — Multi-Orchestrator Core | ✅ Done |
| Phase 2 — SDK Architecture | ✅ Done |
| Phase 3 — Module Consistency | 🟡 In progress |
| Phase 4 — Core Consistency + Types | 🟡 In progress |
| Phase 5 — Integration & Testing | 🟡 In progress |
| Phase 6 — Architecture Overhaul | ✅ Done |
| Phase 7–37 | 🔴 Pending / mixed planning state |

---

## Local Planning Docs

Core areas use the nearest planning markdown (`core.md`, `plan.md`, or area-specific markdown). Module directories under `src/css/modules/` use same-name docs like `agents/agents.md`. Read the nearest local planning markdown before working in that area.
