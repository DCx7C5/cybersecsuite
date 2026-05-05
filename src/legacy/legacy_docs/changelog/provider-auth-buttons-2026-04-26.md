# Provider Auth Buttons + Health Hook Repair — 2026-04-26

## Summary

Implemented provider sign-in/auth management for the React Provider Hub, including backend auth endpoints, frontend modal/hook integration, and test coverage. Also repaired `useSystemHealth` to use the shared API query pattern and the live `/api/health` endpoint.

## Delivered

### Provider Auth API (Dashboard)
- Added:
  - `POST /api/providers/{provider_id}/auth/initiate`
  - `POST /api/providers/{provider_id}/auth/verify`
  - `POST /api/providers/{provider_id}/auth/revoke`
  - `GET /api/providers/{provider_id}/accounts`
- Implemented OAuth/device-flow orchestration and account persistence through `AccountManager`.
- Added safe in-memory auth-flow tracking with expiry cleanup.

### Data Model + Sync
- Extended `ProviderAuthMethod` with:
  - `auth_flow_id`
  - `device_code`
  - `user_code`
  - `expires_at`
  - `last_polled_at`
  - `revoked_at`
- Added provider+revoked index in DB bootstrap SQL.
- Updated auth-method sync to clear revoked state on resync.
- Updated provider hub auth-method query to ignore revoked rows.

### Frontend Provider Hub
- Added provider auth config map for common providers.
- Added `useProviderAuth` hook for initiate/verify/revoke + polling control.
- Added `ProviderAuthModal` with:
  - Auth method selection
  - OAuth start/verify flow
  - Device flow start/status/polling
  - API key/browser credential save
- Updated `ProvidersPanel`:
  - Actions column (`Sign In` / `Add Account`)
  - Account badges and row-level revoke buttons
  - Modal integration and refresh invalidation

### Hook Repair
- Reworked `useSystemHealth` to:
  - Use `useApiQuery` from shared API hook
  - Query `/api/health` (existing backend endpoint)
  - Map backend health payload into UI metrics with defaults
  - Keep default export for compatibility

## Test & Verification

- Backend:
  - `UV_CACHE_DIR=/tmp/uv-cache uv run pytest -q tests/test_provider_auth_api.py`
  - Result: **5 passed**
- Frontend:
  - `npm run test -- --run tests/ProvidersPanel.test.tsx`
  - Result: **4 passed**
  - `npm run type-check`
  - Result: **pass**

## Files

- Backend/API:
  - `src/dashboard/api/provider_auth.py` (new)
  - `src/dashboard/routes.py`
  - `src/dashboard/api/core.py`
  - `src/accounts/sync.py`
- DB/model:
  - `src/db/models/provider.py`
  - `src/db/init_db.sh`
- Frontend:
  - `src/frontend/src/config/providerAuthMethods.ts` (new)
  - `src/frontend/src/hooks/useProviderAuth.ts` (new)
  - `src/frontend/src/features/platform/ProviderAuthModal.tsx` (new)
  - `src/frontend/src/features/platform/ProvidersPanel.tsx`
  - `src/frontend/src/hooks/useSystemHealth.ts`
- Tests:
  - `tests/test_provider_auth_api.py` (new)
  - `src/frontend/tests/ProvidersPanel.test.tsx` (new)
