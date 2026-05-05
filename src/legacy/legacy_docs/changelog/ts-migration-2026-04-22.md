# Changelog: TypeScript Migration Completion (2026-04-22)

## Summary

Completed the TypeScript-as-source-of-truth migration for the dashboard frontend.
All JavaScript served by the dashboard is now compiled from TypeScript via `tsc`.

## Changes

### TypeScript / Build

- **Fixed type error** in `qol.ts`: `settings.toggles` → `settings.active_toggles`
  (field name matches the actual REST API response from `QoLManager.status()`)
- **Compiled** `src/dashboard/static/ts/*.ts` → `src/dashboard/static/js/` using
  `tsc -p src/dashboard/tsconfig.json` (TypeScript 6.0.3)
- **Generated 24 JS modules** from 24 TS sources — two previously missing:
  - `routing.js` — compiled from `routing.ts` (loadRouting, routingSetStrategy, etc.)
  - `crud_ops.js` — compiled from `crud_ops.ts` (loadCases, loadTasks, loadPocs, etc.)
- **Removed** the two hand-written/stale `index.js` and `qol.js` that were
  force-committed in the previous session and replaced them with tsc output
- `src/dashboard/static/js/` is gitignored (build artifact); TS files are source of truth

### References

- `src/dashboard/templates/__init__.py` — `<script src="/static/js/index.js">` is
  correct; no change needed
- `Makefile` — `build-ts`, `lint-ts`, `watch-ts` targets already present; no change needed

### Tests

- 27 QoL tests pass (`tests/test_qol.py`)

## Build Command

```bash
make build-ts
# or directly:
cd src/dashboard && npx tsc -p tsconfig.json
```
