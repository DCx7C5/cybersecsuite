# core/cryptography — Cryptographic Primitive Ownership

**Location**: `src/css/core/cryptography/`
**Status**: New canonical package; implementation is pending in Phase 44.
**Tracker authority**: `.plan/session.db`; this document owns the executable cryptography specification.

## Purpose

- Own cryptographic primitives, key validation, key-purpose separation, and
  typed security failures.
- Supply narrowly scoped operations to authentication, SecureMD, and future
  encrypted database-field consumers.
- Define fail-closed configuration behavior before security-sensitive use.

## Files

| File | Contents / current status |
|------|---------------------------|
| `__init__.py` | Empty public package scaffold; exports are pending. |
| `cryptography.md` | This executable owner document. |
| `../settings/config.py` | Configuration consumer currently exposing incomplete `SECRET_KEY` validation. |

## Ownership Rule

This package owns cryptographic primitives, key loading/validation, key-purpose
separation, rotation identifiers, and typed failures. Consumers request
purpose-specific operations; they do not share one ambiguous secret as the
password, token, document-signing, and field-encryption key.

| Purpose | Required primitive boundary |
|---------|-----------------------------|
| Account password verification | Password-specific Argon2id hash/verify policy; no reversible storage. |
| Authentication/provider secrets | Separate token or at-rest encryption key policy owned with authentication/settings consumers. |
| SecureMD document trust | Ed25519 signing and verification with explicit publisher public-key policy. |
| Sensitive database fields | Dedicated at-rest encryption contract and rotation policy before use. |

## Current Source Reality

- `__init__.py` is empty; no public primitive contract exists.
- `core/settings/config.py` currently allows a missing `SECRET_KEY` with a
  placeholder `pass`; security-sensitive startup must instead fail closed once
  the required key policy is implemented.

## Live Todo Map

| Todo ID | Status in `session.db` | Required change |
|---------|------------------------|-----------------|
| `crypto44-key-boundary` | pending | Define primitive/key-purpose ownership and fail-closed configuration. |
| `securemd44-header-integrity` | pending | Consume Ed25519 verification for SecureMD. |
| `auth-secrets-settings` | pending | Consume the cryptography boundary for encrypted provider credentials. |

## Dependencies

- `crypto44-key-boundary` is the first Phase 44 implementation gate.
- `securemd44-header-integrity` and `auth-secrets-settings` must not define
  separate key policy outside this package.

## Validation

- Cover configured and missing-key behavior plus primitive round trips.
- Run Ruff and basedpyright on this package and its configuration consumers.
- Never emit secret key material in logs, errors, serialized output, or docs.
