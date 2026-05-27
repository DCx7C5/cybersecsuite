# core/accounts — Identity, Organization, and RBAC

**Location**: `src/css/core/accounts/`
**Status**: Canonical API owner; Phase 45 identity/provider relation decisions are resolved and pending implementation.

## Purpose

- Own account, profile, organization, membership, and role-assignment behavior
- Expose the canonical accounts API router
- Provide the source-of-truth package for identity and tenant management

## Files

| File | Contents |
|------|----------|
| `src/css/core/db/models/accounts.py` | Current ORM models: `Account`, `UserProfile`, `Organization`, `OrganizationMembership`, `RoleAssignment`; Phase 45 adds confirmed `UserAccountMembership` and one-profile-per-account enforcement. |
| `src/css/core/db/models/provider.py` | Current provider catalog; Phase 45 adds named repeatable `AccountProviderConnection` relation ownership. |
| `src/css/core/serializers/accounts.py`, `src/css/core/serializers/provider.py` | Planned final serializer owners; serializers must not remain in ORM modules. |
| `src/css/core/accounts/endpoints.py` | FastAPI router for registration, profile, and organization flows |
| `src/css/core/accounts/__init__.py` | Public router exports; it does not own a second model schema |

## Ownership Rule

`accounts` belongs in `src/css/core/accounts/` only.

Boundary clarification for Phase 40 lane C:
- `core/db/models/user.py` owns internal/admin user identity.
- `core/db/models/accounts.py` owns account/profile/organization tenancy
  records. Phase 45 implements confirmed `User <-> Account` membership while
  retaining one `UserProfile` per `Account`.
- `core/db/models/provider.py` + `core/db/models/llm_models.py` own provider/model catalogs.
- `AccountProviderConnection` is the confirmed explicit M:N link between
  accounts and provider catalog entries. An account may have multiple named
  connections to one provider; credential bytes stay in encrypted settings
  ownership.

## Executable Owner Contract

### Current Symbols

| Path | Symbols |
|------|---------|
| `src/css/core/db/models/accounts.py` | `Account`, `UserProfile`, `Organization`, `OrganizationMembership`, `RoleAssignment`; response value structs beside the ORM records. |
| `src/css/core/accounts/endpoints.py` | `register_account(req)`, `get_account(account_id)`, `get_user_profile(account_id)`, `update_user_profile(...)`, `create_organization(req)`, `get_organization(org_id)`, `add_organization_member(...)`, `list_organization_members(org_id)`. |
| `src/css/core/authentication/manager.py` | Password/token verification boundary consumed by accounts; credentials are not implemented in this package. |

### Live Todo Map

| Todo ID | Status in `session.db` | Required change |
|---------|------------------------|-----------------|
| `accounts-user-orm` | done | Canonical account/tenant ORM surface exists under `core/db/models`. |
| `authentication-package-cutover` | pending | Finish the `core/auth` to `core/authentication` path, route, and owner-document cutover. |
| `accounts-module` | pending | Complete current account routes, password hashing integration, and tenant authorization around the canonical ORM records. |
| `auth-project-isolation` | pending | Add authenticated account/tenant isolation to project and session access in the auth-owned work, not by duplicating account models. |
| `db45-schema-decision-gates` | done | Confirmed `UserAccountMembership`, one profile per account, and named multiple same-provider connections. |
| `db45-identity-account-profile-schema` | pending | Implement `UserAccountMembership` and unique/one-to-one `Account -> UserProfile`. |
| `db45-account-provider-junction` | pending | Add repeatable named provider connection metadata without plaintext credentials. |
| `serializer-model-user-accounts`, `serializer-apply-accounts` | pending | Move account serializers into `core/serializers/accounts.py` only after model shape is approved. |

### Numbered Work Order

1. Implement the resolved identity shape: one-to-one `Account -> UserProfile`
   plus explicit `UserAccountMembership` with unique `(user_id, account_id)`.
2. Preserve `src/css/core/db/models/accounts.py` as the ORM ownership surface
   for retained account/organization relations and import models from account endpoints.
3. Implement `AccountProviderConnection` in provider/model ownership with a
   required normalized `connection_name` and unique
   `(account_id, provider_id, connection_name)`; store no token or API-key value.
4. Replace the placeholder password handling in `register_account()` with
   `core/authentication` password-manager behavior and never return credential material.
5. Enforce authenticated organization access in membership and organization
   handlers before exposing records.
6. Move serializer implementations to `core/serializers` and validate with
   endpoint tests for registration hashing, profile updates,
   membership operations, and cross-organization denial, plus import checks
   showing no retired `core/auth`, `modules/auth`, or `core/accounts/models.py` shadow package.

## Implementation Contract

| Concern | Required behavior |
|---------|-------------------|
| Registration | Replace the placeholder password handling in `endpoints.py` with `core/authentication` password hashing; never persist plaintext credentials. |
| Tenant access | Organization and membership reads/writes must verify the authenticated caller's organization access before exposing records. |
| Boundary | Accounts owns identity/profile/organization records; `core/authentication` owns token, password, and API-key verification. |
| Rich model behavior | `Account` and `User` model methods may enforce membership/profile/provider-link invariants; manager modules own collection queries and bulk operations; serializers remain in `core/serializers`. |
| Provider connections | `AccountProviderConnection` supports multiple normalized names per account/provider and references encrypted credential ownership; it never stores plaintext API/OAuth secrets. |
| Profile cardinality | `UserProfile` is one-to-one with `Account`; sharing identities is represented through `UserAccountMembership`, not shared profile rows. |

## Validation

- Cover registration hashing, invalid credentials, and cross-organization access denial.
- Confirm account endpoints import authentication services from `css.core.authentication`, not a retired or module-level shim.
