# Plan: Remove Complete Legacy Non-React Webinterface

**Date:** 2026-04-26  
**Status:** Planned  
**Scope Owner:** Frontend + Dashboard integration

## Objective

Remove the remaining legacy non-React dashboard implementation entirely, while keeping the React SPA (`src/frontend` -> `src/dashboard/static/react`) and all `/api/*` + `/sse/*` backend behavior unchanged.

## In Scope (Must Be Removed or Migrated)

1. `src/dashboard/static/ts/**`
2. `src/dashboard/static/tsx/**`
3. `src/dashboard/static/css/**`
4. `src/dashboard/tsconfig.json`
5. Frontend tests importing from legacy paths under `src/dashboard/static/{ts,tsx}`
6. Runtime/test/docs references that still assume legacy static CSS or legacy UI fallback behavior

## Out of Scope

1. React SPA source under `src/frontend/src/**`
2. React build output under `src/dashboard/static/react/**`
3. Backend API/SSE handlers and data models

## Current Repository Snapshot (2026-04-26)

1. Legacy directories still present: `static/ts`, `static/tsx`, `static/css`
2. Frontend unit tests still import legacy modules:
   - `useMenuInput.test.ts`
   - `useHideElement.test.ts`
   - `sidebarPersist.test.ts`
   - `mentionValidation.test.ts`
   - `commandEngine.test.ts`
   - `router.test.tsx`
   - `authProtectedRoutes.test.tsx`
3. Routing test still probes legacy CSS path:
   - `tests/test_dashboard_routing.py` checks `GET /static/css/dashboard.css`
4. Legacy template fallback code is already removed from runtime `dashboard_page`; this plan focuses on remaining static assets/modules and references.

## Execution Plan

### Phase 1: Dependency Extraction and Migration (No Deletes Yet)

1. Decide target for legacy helper logic currently used by tests:
   - Promote to maintained React code if still product-relevant, or
   - Move to `src/frontend/tests/fixtures/legacy/` if test-only.
2. Copy/move these modules out of `src/dashboard/static`:
   - `tsx/hooks/useMenuInput.ts`
   - `tsx/hooks/useHideElement.ts`
   - `tsx/components/Router.tsx`
   - `tsx/components/AuthProtectedRoutes.tsx`
   - `ts/utils/{commandEngine,mentionValidation,sidebarPersist}.ts`
3. Update all frontend test imports to the new locations.
4. Keep behavior parity by running frontend unit tests before any deletion.

**Gate to exit Phase 1:**  
No test imports remain that reference `src/dashboard/static/ts` or `src/dashboard/static/tsx`.

### Phase 2: Remove Legacy Runtime Artifacts

1. Delete:
   - `src/dashboard/static/ts/`
   - `src/dashboard/static/tsx/`
   - `src/dashboard/static/css/`
   - `src/dashboard/tsconfig.json`
2. Remove stale config/proxy references related to legacy TS pipeline (if present), including any `/ts` dev proxy usage that is no longer required.
3. Ensure static serving remains valid for React assets via `/static/react/**`.

**Gate to exit Phase 2:**  
No files/directories from the legacy non-React static interface remain.

### Phase 3: Test and Contract Updates

1. Update `tests/test_dashboard_routing.py` static asset assertion from legacy CSS path to React artifact path (for example `/static/react/index.html` or `/static/react/favicon.svg`).
2. Validate route precedence and redirects remain unchanged (`/`, `/dashboard`, `/api/*`, `/sse/*`, `/v1/*`, `/a2a*`).
3. Re-run affected Python and frontend test suites.

**Gate to exit Phase 3:**  
All updated tests pass with zero dependency on removed legacy assets.

### Phase 4: Documentation and Changelog Cleanup

1. Add a changelog entry documenting full legacy webinterface removal and migration details.
2. Update active docs to reflect React-only dashboard architecture.
3. Keep historical changelog files intact; add superseding notes instead of rewriting history.

**Gate to exit Phase 4:**  
No active docs instruct users to rely on legacy static TS/TSX/CSS dashboard assets.

## Validation Checklist (Release Gate)

1. `rg -n "src/dashboard/static/(ts|tsx|css)|/static/css/dashboard\\.css" src tests docs` returns no active code/test refs
2. Frontend validation:
   - `cd src/frontend && npm run type-check`
   - `cd src/frontend && npm run test`
   - `cd src/frontend && npm run build`
3. Backend validation:
   - `pytest tests/test_dashboard_routing.py`
   - targeted smoke tests for `/`, `/api/overview`, `/sse/health`, `/v1/models`
4. Manual smoke:
   - Open dashboard root `/`
   - Verify key panels load and API calls succeed

## Risk and Mitigation

1. **Risk:** Legacy utility tests break after relocation.  
   **Mitigation:** Migrate modules first, verify parity, then delete legacy directories.
2. **Risk:** Hidden references in docs/tests cause CI failures.  
   **Mitigation:** Run repo-wide `rg` scans before and after deletion.
3. **Risk:** Static asset assumptions in tests drift.  
   **Mitigation:** Assert on React artifact endpoints instead of legacy CSS.

## Rollback Strategy

1. Keep migration and deletion in separate commits:
   - Commit A: migrate imports/modules
   - Commit B: delete legacy files
   - Commit C: docs/changelog updates
2. If regressions occur, revert Commit B only to restore legacy files while keeping migration work.

## Definition of Done

1. Legacy non-React static interface directories (`ts`, `tsx`, `css`) are fully removed.
2. No tests or runtime code import from `src/dashboard/static/ts*`.
3. Dashboard remains fully functional through React SPA at `/` and `/static/react/**`.
4. Documentation and changelog reflect React-only frontend architecture.

---

# Stream 3: Legacy Integration Cleanup (OpenSearch + Wazu Removal)

**Objective:** Remove outdated OpenSearch (search engine) and Wazu (monitoring integration) references from backend, frontend, and dependencies.

**Current State:**
- 22 OpenSearch references in Python + TypeScript code
- OpenSearch dependency in `pyproject.toml` (line 36)
- Wazu skill templates in `templates/skills/` (not production code)
- Not used by Phase 5E or active APIs

**Scope:**
1. Remove OpenSearch from backend API + routes
2. Remove OpenSearch from frontend TypeScript
3. Remove `opensearch-py[async]>=2.7` dependency
4. Keep Wazu skill templates (informational, not active code)

**Execution (Parallel with Phase 5E):**
- Estimated: 2.5 hours
- Can run independently while Phase 5E TypeScript fixes happen
- No shared files = zero merge conflicts

**Reference:** `/plans/cleanup-opensearch-wazu-2026-04-26.md` for detailed 5-phase execution plan.

**Success Criteria:**
- ✅ No `opensearch` references in `/src`
- ✅ `opensearch-py` removed from pyproject.toml
- ✅ Frontend builds cleanly
- ✅ All tests pass
- ✅ Dashboard functionality unchanged
