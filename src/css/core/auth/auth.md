# core/auth - Authentication Runtime Surface

**Location**: `src/css/core/auth/`
**Status**: Partial implementation; live source establishes `core/auth` as the Phase 28 implementation owner.

## Purpose

`core/auth` owns authentication primitives used by API surfaces:

- JWT access and refresh token issuance/validation
- API key generation and hashing
- password hashing helpers
- HTTP authentication endpoints under `/api/auth/*`

Authorization policy and filesystem/tool grants are not owned here; those belong to `core/permissions`.

## Current Code Reality

| File | Current responsibility | Known gap |
|------|------------------------|-----------|
| `manager.py` | `JWTManager`, `APIKeyManager`, password/revocation primitives | uses synchronous helpers and still contains legacy typing/error-handling debt |
| `endpoints.py` | login, refresh, logout and API-key HTTP routes | credential/user-store validation and persistence are incomplete |
| `__init__.py` | package exports | verify public surface after auth reconciliation |

The tracker title historically described auth work as `modules/auth/`, while
the prepared todo description and live implementation use `core/auth/`. Do
not create a second auth package.

## Implementation Contract

Phase 28 requires:

1. Canonical auth package ownership to be decided from current code.
2. Signed token lifecycle with refresh-token rotation and revocation.
3. Persisted API keys with one-time raw-secret display and hashed-at-rest storage.
4. `get_current_user()` integration on protected routers.
5. Project/session ownership enforcement tied to the authenticated user.
6. Encrypted provider-secret storage through settings, never raw API keys in responses or logs.

## Integration Points

| Component | Relationship |
|-----------|--------------|
| `core/accounts` | user identity and account persistence |
| `core/settings` | sensitive provider/API-key configuration |
| `core/permissions` | authorization after authentication |
| `core/asgi` | HTTP route mounting and auth middleware/dependencies |
| `modules/projects` | user-owned project/session filtering |

## Validation Boundary

### Live Todo Map

| Todo ID | Status | Required execution |
|---------|--------|--------------------|
| `auth-jwt-module` | pending | Extend existing `src/css/core/auth/manager.py`, `src/css/core/auth/endpoints.py`, and `src/css/core/auth/__init__.py` for credential validation, token rotation/revocation, and hashed persisted API keys. |
| `auth-middleware` | pending | Mount authenticated dependencies/middleware over the retained core auth manager. |
| `auth-project-isolation` | pending | Apply caller identity to project/session isolation. |
| `auth-secrets-settings` | pending | Store provider secrets encrypted through settings and never expose raw values. |

1. Keep `JWTManager`, `APIKeyManager`, `PasswordManager`, and
   `TokenRevocationStore` in `src/css/core/auth/manager.py`.
2. Complete `/api/auth/*` handlers in `src/css/core/auth/endpoints.py` using
   real account credential persistence and one-time-only secret display.
3. Wire authentication into authorization/settings/project consumers only
   after login/token/key behavior is tested.
4. Validate login/refresh/logout, API-key hash/revocation, middleware denial,
   project isolation, and secret non-disclosure; verify no `modules/auth`
   package or import is introduced.
