# core/accounts — Identity, Organization, and RBAC

**Location**: `src/css/core/accounts/`
**Status**: ✅ Canonical ownership in `core/accounts/`

## Purpose

- Own account, profile, organization, membership, and role-assignment models
- Expose the canonical accounts API router
- Provide the source-of-truth package for identity and tenant management

## Files

| File | Contents |
|------|----------|
| `src/css/core/db/models/accounts.py` | Canonical ORM models: `Account`, `UserProfile`, `Organization`, `OrganizationMembership`, `RoleAssignment` |
| `src/css/core/accounts/endpoints.py` | FastAPI router for registration, profile, and organization flows |
| `src/css/core/accounts/__init__.py` | Public router exports; it does not own a second model schema |

## Ownership Rule

`accounts` belongs in `src/css/core/accounts/` only.

Boundary clarification for Phase 40 lane C:
- `core/db/models/user.py` owns internal/admin user identity.
- `core/db/models/accounts.py` owns account/profile/organization tenancy records.
  Account owns identity and tenant-facing registration/profile flows.
- `core/db/models/provider.py` + `core/db/models/llm_models.py` own provider/model catalogs.
- Boundary phrase: user/admin vs provider-account is preserved by keeping
  provider catalog ownership separate from both `User` and `Account`.

## Executable Owner Contract

### Current Symbols

| Path | Symbols |
|------|---------|
| `src/css/core/db/models/accounts.py` | `Account`, `UserProfile`, `Organization`, `OrganizationMembership`, `RoleAssignment`; response value structs beside the ORM records. |
| `src/css/core/accounts/endpoints.py` | `register_account(req)`, `get_account(account_id)`, `get_user_profile(account_id)`, `update_user_profile(...)`, `create_organization(req)`, `get_organization(org_id)`, `add_organization_member(...)`, `list_organization_members(org_id)`. |
| `src/css/core/auth/manager.py` | Password/token verification boundary consumed by accounts; credentials are not implemented in this package. |

### Live Todo Map

| Todo ID | Status in `session.db` | Required change |
|---------|------------------------|-----------------|
| `accounts-user-orm` | done | Canonical account/tenant ORM surface exists under `core/db/models`. |
| `accounts-module` | pending | Complete current account routes, password hashing integration, and tenant authorization around the canonical ORM records. |
| `auth-project-isolation` | pending | Add authenticated account/tenant isolation to project and session access in the auth-owned work, not by duplicating account models. |

### Numbered Work Order

1. Preserve `src/css/core/db/models/accounts.py` as the only ORM ownership
   surface and import its models from account endpoints.
2. Replace the placeholder password handling in `register_account()` with
   `core/auth` password-manager behavior and never return credential material.
3. Enforce authenticated organization access in membership and organization
   handlers before exposing records.
4. Validate with endpoint tests for registration hashing, profile updates,
   membership operations, and cross-organization denial, plus import checks
   showing no `modules/auth` or `core/accounts/models.py` shadow package.

## Implementation Contract

| Concern | Required behavior |
|---------|-------------------|
| Registration | Replace the placeholder password handling in `endpoints.py` with `core/auth` password hashing; never persist plaintext credentials. |
| Tenant access | Organization and membership reads/writes must verify the authenticated caller's organization access before exposing records. |
| Boundary | Accounts owns identity/profile/organization records; `core/auth` owns token, password, and API-key verification. |

## Validation

- Cover registration hashing, invalid credentials, and cross-organization access denial.
- Confirm account endpoints import authentication services from `css.core.auth`, not a module-level shim.
