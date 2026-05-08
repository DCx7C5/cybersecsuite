# Modules Planning Index

This file is the modules-level navigation document.

## Source of truth

- Global session and phase state: `.plan/session.db`
- Cross-project planning context: `.plan/plan.md`
- Per-module implementation details: `src/css/modules/<module>/<module>.md`

## Working rule

When updating a module, treat that module's local same-name Markdown file as the primary implementation reference and keep it synchronized with `.plan/session.db`.

## Ownership overrides

- `accounts`, `events`, `marketplace`, and `memory` are core-owned domains under `src/css/core/`.
- `accounts` is core-only now; there must not be a `src/css/modules/accounts/` package.
- `events`, `memory`, and `marketplace` are core-only now; there must not be `src/css/modules/events/`, `src/css/modules/memory/`, or `src/css/modules/marketplace/` packages.
- `rag_vector` is the remaining module-side migration surface; active shared retrieval runtime code now lives under `src/css/core/rag_vector/` and `src/css/core/rag_graph/`.
- `working_dir` is retired; use `src/css/core/workspace/` for session/project directory management.

## Connectivity audit

Cache use is intentionally selective, not universal.

- Direct cache consumers: `a2a_internal` (Redis transport, not KV object caching), `llm_proxy` (prompt cache path), `triage` (prompt cache path), `rag_vector` / `rag_graph` (retrieval cache path), plus core-owned `settings`, `permissions`, `marketplace`, and `memory`.
- Indirect cache consumers: `agents`, `chat`, `workflows`, `mitre`, `threat_intel`, and `siem` consume cached prompt/retrieval/context layers through the modules above instead of owning cache policy themselves.
- Canonical-store modules that should stay DB/OpenObserve/graph-first: `alerts`, `compliance`, `evidence`, `incidents`, `local_assist`, `obsidian_memory`, `projects`, `reports`, `scans`, `scheduler`, `strategies`, and `webhooks`.
- Open gap: local docs still need a few richer integration tables, but the architecture stance is now explicit that "not directly cached" is often the correct design, not a missing feature.

## Module Rules

- Every module directory under `src/css/modules/` must contain `<module>.md`.
- Tortoise ORM table entities in `models.py` inherit `css.core.db.models.base.BaseModel`.
- If a module defines `Enum` classes, they belong in `enums.py`.
