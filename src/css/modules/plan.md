# Modules Planning Index

This file is the modules-level navigation document.

## Source of truth

- Global session and phase state: `.plan/session.db`
- Cross-project planning context: `.plan/plan.md`
- Per-module implementation details: `src/css/modules/<module>/plan.md`

## Working rule

When updating a module, treat that module's local `plan.md` as the primary implementation reference and keep it synchronized with `.plan/session.db`.
