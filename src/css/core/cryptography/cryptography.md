# core/cryptography — Cryptographic Primitive Ownership

**Location**: `src/css/core/cryptography/`
**Status**: New canonical package; Phase 44 crypto44-key-boundary is in_progress. Ed25519 key generation, signing, and verification being implemented.
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
| `__init__.py` | Ed25519 primitives: generate_ed25519_keypair(), sign_bytes(), verify_signature(), PEM load helpers. Typed exceptions: CryptographyError, KeyPurposeError. Respects SECUREMD_ENABLED config gate. |
| `cryptography.md` | This executable owner document. |
| `../settings/config.py` | Configuration consumer; now also has SECUREMD_ENABLED and SECUREMD_ENFORCE_HEADER toggles. |

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
| `securemd-config-toggles` | in_progress | Add SECUREMD_ENABLED and SECUREMD_ENFORCE_HEADER config toggles. |
| `crypto44-key-boundary` | in_progress | Implement Ed25519 key generation, sign_bytes(), verify_signature(), PEM load helpers, typed failures. Respects SECUREMD_ENABLED gate. |
| `securemd44-header-integrity` | in_progress | Consume Ed25519 verification for SecureMD BaseFrontmatterHeader. |
| `auth-secrets-settings` | pending | Consume the cryptography boundary for encrypted provider credentials. |
| `securemd-fix-duplicate-secret-key` | pending | Remove duplicate SECRET_KEY at config.py lines 5-9. |

## Dependencies

- `crypto44-key-boundary` is the first Phase 44 implementation gate.
- `securemd44-header-integrity` and `auth-secrets-settings` must not define
  separate key policy outside this package.

## Validation

- Cover configured and missing-key behavior plus primitive round trips.
- Run Ruff and basedpyright on this package and its configuration consumers.
- Never emit secret key material in logs, errors, serialized output, or docs.
