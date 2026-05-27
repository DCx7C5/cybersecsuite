# core/securemd — Signed Markdown Integrity Gate

**Location**: `src/css/core/securemd/`
**Status**: New package scaffold; Phase 44 implementation is pending.
**Tracker authority**: `.plan/session.db`; this document owns the executable SecureMD specification.
**Architecture**: `.plan/architecture/securemd-architecture.md`

## Purpose

- Own the signed Markdown header contract and verified-body release API.
- Reject malformed, unsigned, incorrectly keyed, or tampered trusted
  documents before body content enters approved ingestion paths.
- Keep signature integrity separate from publisher/content authorization.

## Files

| File | Contents / current status |
|------|---------------------------|
| `header.py` | Incomplete header scaffold; currently references an undefined base class. |
| `__init__.py` | Empty public package scaffold; exports are pending. |
| `securemd.md` | This executable owner document. |

## Ownership Rule

SecureMD owns the signed-document header contract, verification failures, and
the API that releases a verified Markdown body to trusted-document ingestion
paths. `core/cryptography` owns Ed25519 operations and key policy;
`core/serializers` owns strict frontmatter and Markdown serialization.

## Trust Boundary

A valid SecureMD signature proves that document bytes have not changed after
signing and identifies an accepted signer key. It does not prove that content
signed by an accepted publisher is benign. Publisher authorization, review,
and downstream content/prompt policy remain required.

## Current Source Reality

- `header.py` currently declares `FrontMatterHeader(BaseFrontMatterHeader)`
  while the base is undefined and the architecture names the canonical symbol
  `BaseFrontmatterHeader`.
- There is no verified-body implementation or public export yet.
- Serializer implementation is blocked on the Phase 43 canonical
  `core/serializers` contract.

## Live Todo Map

| Todo ID | Status in `session.db` | Required change |
|---------|------------------------|-----------------|
| `securemd44-header-integrity` | pending | Implement canonical header and signature verification. |
| `securemd44-frontmatter-serializer` | pending | Strictly parse/serialize signed Markdown and reject invalid documents. |
| `securemd44-context-ingestion-gate` | pending | Gate marketplace-origin prompt Markdown before `PromptRenderer`/`AgentExecutor` execution. |
| `securemd44-security-validation` | pending | Test tamper, wrong-key, malformed and untrusted-publisher rejection. |

## Dependencies

- `securemd44-header-integrity` depends on `crypto44-key-boundary`.
- `securemd44-frontmatter-serializer` depends on the canonical serializer
  cutover owned by Phase 43.
- `securemd44-context-ingestion-gate` depends on `prompt-marketplace-wire`
  and `agent-execution-logic`; current marketplace Markdown preview is a UI
  surface, not an execution-context loader.

## Consumer Boundary

- Marketplace preview in `core/marketplace/endpoints.py` may display Markdown
  but must not be treated as verified prompt content.
- Phase 23 prompt rendering is the first planned marketplace-origin Markdown
  execution consumer; it must release text only after SecureMD verification.
- The current `modules/skills` implementation stores structured definitions
  and does not load Markdown into context; do not add skill wiring without a
  separately tracked runtime surface.

## Validation

- Test sign/verify, modified frontmatter/body, wrong key, malformed signature,
  and publisher/key-policy rejection.
- Run the dependency analyzer, Ruff, and basedpyright for SecureMD and
  serializer consumers once prerequisite implementation tasks are complete.
