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
| `models.py` | `Account`, `UserProfile`, `Organization`, `OrganizationMembership`, `RoleAssignment` |
| `endpoints.py` | FastAPI router for registration, profile, and organization flows |
| `__init__.py` | Public exports for models and router |

## Ownership Rule

`accounts` belongs in `src/css/core/accounts/` only.
