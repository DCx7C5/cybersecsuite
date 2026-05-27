# core/authentication — Authentication Boundary

**Location**: `src/css/core/authentication/`
**Status**: Canonical package introduced by the `core/auth` rename; cutover is pending.
**Tracker authority**: `.plan/session.db`; this document owns the executable authentication specification.

## Purpose

- Own password verification, token/API-key authentication, and request
  authentication dependencies.
- Expose the canonical authentication endpoints.
- Consume account and tenancy records without redefining them.

## Files

| File | Contents / current status |
|------|---------------------------|
| `manager.py` | Password/token manager moved from `core/auth`; implementation validation remains pending. |
| `endpoints.py` | Authentication endpoints now using the `/api/authentication/*` route prefix in source. |
| `__init__.py` | Public package exports moved from `core/auth`. |
| `authentication.md` | This executable owner document. |

## Ownership Rule

`core/authentication` owns password verification, token/API-key authentication,
authentication endpoints, and request authentication dependencies. It consumes
identity and tenancy records from `core/accounts`; it does not define duplicate
account/profile ORM models.

`core/cryptography` owns cryptographic primitives and key-purpose policy used
by authentication. Authentication must not implement independent encryption or
signature helpers.

## Current Source Reality

- `manager.py` and `endpoints.py` have moved from `core/auth`.
- `accounts/endpoints.py` already imports `css.core.authentication`.
- The public route prefix has changed in source to `/api/authentication/*`;
  tests, router/OpenAPI expectations, and docs still require reconciliation.
- Focused type checking currently reports frozen-structure inheritance errors
  in authentication request/response endpoint types.

## Live Todo Map

| Todo ID | Status in `session.db` | Required change |
|---------|------------------------|-----------------|
| `authentication-package-cutover` | pending | Retire active `core/auth` paths and validate imports/routes/docs. |
| `auth-jwt-module` | pending | Implement JWT and API-key behavior in the canonical package. |
| `auth-middleware` | pending | Wire FastAPI request authentication dependencies. |
| `auth-endpoint-validation` | pending | Complete typed endpoint validation after package and auth primitives exist. |
| `auth-secrets-settings` | pending | Encrypt provider secrets through the cryptography boundary. |

## Dependencies

- `accounts-module`, `auth-jwt-module`, `auth-middleware`, and
  `auth-endpoint-validation` depend on `authentication-package-cutover`.
- `auth-secrets-settings` depends on `crypto44-key-boundary` as well as the
  JWT/key-management work.

## Validation

- Run the dependency analyzer on `src/css/core/authentication/`.
- Reject active references to `css.core.auth` or `src/css/core/auth/`.
- Run focused Ruff and basedpyright on authentication, accounts, and router
  consumers; test the final route prefix and authentication failure behavior.
