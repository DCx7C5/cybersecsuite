# Modules Planning Index

This file is the modules-level navigation document.

## Source of truth

- Global session and phase state: `.plan/session.db`
- Global navigation and current planning snapshot: `.plan/plan.md`
- Per-module implementation details: `src/css/modules/<module>/<module>.md`

## Working rule

When updating a module, treat that module's local same-name Markdown file as the primary implementation reference and keep it synchronized with `.plan/session.db`.

## Ownership overrides

- `accounts`, `events`, `marketplace`, and `memory` are core-owned domains under `src/css/core/`.
- `accounts` is core-only now; there must not be a `src/css/modules/accounts/` package.
- `events`, `memory`, and `marketplace` are core-only now; there must not be `src/css/modules/events/`, `src/css/modules/memory/`, or `src/css/modules/marketplace/` packages.
- `hooks` is module-owned runtime glue for event consumers; it consumes `core/events` but does not replace `core/events` ownership.
- The former module-side `rag_vector` planning surface has been retired;
  shared retrieval ownership is `src/css/core/rag_vector/` and
  `src/css/core/rag_graph/`.
- `working_dir`/`core/workspace` ownership requires source-code reconciliation;
  no implemented `src/css/core/workspace/` package was found in this cleanup.

## Connectivity audit

Cache use is intentionally selective, not universal.

- Direct cache consumers: `a2a_internal` (Redis transport, not KV object caching), `llm_proxy` (prompt cache path), `triage` (prompt cache path), `rag_vector` / `rag_graph` (retrieval cache path), plus core-owned `settings`, `permissions`, `marketplace`, and `memory`.
- Indirect cache consumers: `agents`, `chat`, `workflows`, `mitre`, `threat_intel`, and `siem` consume cached prompt/retrieval/context layers through the modules above instead of owning cache policy themselves.
- Canonical-store modules that should stay DB/OpenObserve/graph-first: `alerts`, `compliance`, `evidence`, `incidents`, `local_assist`, `projects`, `reports`, `scans`, `scheduler`, `strategies`, and `webhooks`.
- Open gap: local docs still need a few richer integration tables, but the architecture stance is now explicit that "not directly cached" is often the correct design, not a missing feature.

## Planned Runtime Owners Added During Sanitization

| Module | Local document | Contract held locally |
|--------|----------------|-----------------------|
| `acp` | `src/css/modules/acp/acp.md` | ACP transport/session runtime ownership + LSP bridge ownership with JetBrains retained as legacy compatibility surface. |
| `sessions` | `src/css/modules/sessions/sessions.md` | Session lifecycle, isolation requirement, and git/worktree validation boundary. |
| `approvals` | `src/css/modules/approvals/approvals.md` | Human approval gate, endpoints, event and audit integration. |
| `graphs` | `src/css/modules/graphs/graphs.md` | Operational graph/query/rendering contract. |
| `reports` | `src/css/modules/reports/reports.md` | Report lifecycle, artifacts, templates, and frontend/API requirements. |

## Architecture Audit (2026-05-09)

- `scripts/codebase_dependency_analyzer.py` was rerun against `src/css/modules/`.
- The earlier `core` indirection for A2A contracts was removed; A2A ownership stays in `@a2a_google` and `@a2a_internal`.
- Cross-module imports should now be interpreted against ownership boundaries, not driven toward `core` when the domain is still module-owned.

## Module Rules

- Every module directory under `src/css/modules/` must contain `<module>.md`.
- Tortoise ORM table entities in `models.py` inherit `css.core.db.models.base.BaseModel`.
- If a module defines `Enum` classes, they belong in `enums.py`.
- `hooks` module plan lives at `src/css/modules/hooks/hooks.md`.
- Keep hook responsibilities split: `@on_event` in `hooks/registry.py`; mutating/blocking `@pre_hook` and `@post_hook` in `hooks/interceptors.py`.
- When a module class emits runtime events, use `css.core.base.emitter.BaseEmitterClass` where practical.
