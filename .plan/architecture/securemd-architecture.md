# SecureMD Architecture & Concept

## Overview

**SecureMD** is a cryptographically signed Markdown format designed to prevent
unsigned or tampered Markdown from being loaded into trusted LLM-context
ingestion paths.

It uses a strict frontmatter header + body separation with Ed25519 signatures.
Any modification after signing invalidates the signature. A valid signature
does not make malicious content from an authorized signer safe.

## Core Principles

- **Clear separation**: Frontmatter (`--- ... ---`) vs Body
- **Cryptographic integrity**: Ed25519 signatures (raw 64-byte)
- **No base64**: Signature stored as uppercase hex
- **Minimal & fast**: Built with `msgspec.Struct`
- **Integrity gate**: Only `verify_and_get_body(marketplace_pubkey)` gives trusted-document ingestion paths access to a verified body

## Class Architecture

### 1. `BaseFrontmatterHeader` (Data + Crypto)

```python
class BaseFrontmatterHeader(msgspec.Struct):
    name: str
    description: str
    hash: str = ""
    signature: str = ""
    body: str = ""

    # sign(), verify(), verify_and_get_body(), _canonical()
```

**Responsibilities**:
- Holds the model
- Computes canonical bytes for signing
- Performs Ed25519 signing/verification
- Gates access to a body whose bytes and signer origin have been verified

### 2. Serializer Hierarchy

```
BaseSerializer (abstract)
    └── FrontmatterSerializer
```

**Responsibilities**:
- `from_string()` / `from_file()`
- `to_string()` / `to_file()`
- Strict parsing with clear error handling

## Signature Flow

1. **Signing** (Harness / Runtime with private key)
   - Create header + body
   - Compute `_canonical()` (YAML header + `---` + body)
   - Sign with Ed25519 private key
   - Store signature as hex

2. **Verification** (Marketplace / Consumers with public key)
   - Load via `FrontmatterSerializer`
   - Call `header.verify_and_get_body(marketplace_pubkey)`
   - Any modification → signature fails → rejected

## Security Model

- **Marketplace** publishes the **Public Key**
- **Harness** uses **Private Key** (first-setup or runtime-generated) for signing
- Signature covers the entire document (header + body)
- YAML is always sorted for deterministic canonical form
- Verification establishes integrity and signer origin only. Publisher
  authorization, review, and downstream prompt/content policy remain required.
- A trusted signer can sign harmful instructions; SecureMD must never be
  described as eliminating that risk.

## Example Secure .md

```markdown
---
name: "system-prompt-v1"
description: "Core system instructions"
hash: "a1b2c3d4..."
signature: "<128 uppercase hexadecimal characters for an Ed25519 signature>"
---

# Content here

This content is cryptographically protected.
```

## Usage Example

```python
# Signing
header = BaseFrontmatterHeader(name="...", description="...", body=markdown_body)
header.sign(private_key)

FrontmatterSerializer.to_file(header, "secure_prompt.md")

# Trusted-document loading (verifies integrity and signer origin)
loaded = FrontmatterSerializer.from_file("secure_prompt.md")
safe_body = loaded.verify_and_get_body(marketplace_pubkey)
```

## Why This Design?

- **Performance**: msgspec ≈ 5× faster than PyYAML
- **Security**: Strict parsing + integrity/origin signature gate
- **Extensibility**: Serializer inheritance for JSON etc.
- **Simplicity**: No meta dict, no unnecessary fields

## Token Efficiency Note

This format adds minimal overhead to LLM context while providing strong integrity guarantees.

**Reference**
- Signature: Ed25519 raw 64-byte (hex)
- Canonical: deterministic `msgspec.yaml` frontmatter plus body
- Rejection: typed verification/format failure on any tamper attempt

## Implementation Ownership And Gates

- `src/css/core/cryptography/` owns Ed25519 primitives and key-purpose policy.
- `src/css/core/serializers/` owns strict frontmatter/Markdown parsing and
  canonical serialization.
- `src/css/core/securemd/` owns `BaseFrontmatterHeader`, verification failures,
  and verified-body access.
- Phase 44 in `.plan/session.db` orders implementation as:
  `crypto44-key-boundary` -> `securemd44-header-integrity` ->
  `securemd44-frontmatter-serializer` ->
  `securemd44-context-ingestion-gate` ->
  `securemd44-security-validation`.
- `securemd44-frontmatter-serializer` also depends on the Phase 43 canonical
  serializer cutover, because the current serializer source is placeholder
  code and active consumers still import a removed DB serializer module.

## Consumer Boundary

- The currently implemented Markdown reader is
  `src/css/core/marketplace/endpoints.py::get_marketplace_item_preview()`;
  it returns display content for the UI and is not an LLM-context trust gate.
- The first planned execution consumer is Phase 23 prompt rendering:
  `src/css/modules/prompts/registry.py` and `renderer.py` must verify
  marketplace-origin signed Markdown before text can reach
  `src/css/modules/agents/base.py::AgentExecutor.execute()`.
- Current `src/css/modules/skills/` source stores structured skill
  definitions and has no Markdown-to-context loader; SecureMD must not create
  a speculative skill ingestion path.
