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
- `vector_rag` is planned to become a core-owned retrieval subsystem under `src/css/core/vector_rag/`; the current `src/css/modules/vector_rag/` package is legacy migration surface until Phase 20 hybrid-retrieval work lands.
- `working_dir` is retired; use `src/css/core/workspace/` for session/project directory management.

## Module Rules

- Every module directory under `src/css/modules/` must contain `<module>.md`.
- Tortoise ORM table entities in `models.py` inherit `css.core.db.models.base.BaseModel`.
- If a module defines `Enum` classes, they belong in `enums.py`.
