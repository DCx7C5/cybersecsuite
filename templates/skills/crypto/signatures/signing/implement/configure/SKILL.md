---
name: signatures-signing-implement-configure
description: Ed25519 artifact signing, BLAKE2b-256 integrity verification, chain of custody, Argon2id key protection, AES-256-GCM encryption. Available to ALL agents as a core skill — not a standalone agent.
model: sonnet
maxTurns: 10
tools:
  - Read
  - Bash
  - Glob
  - Grep
skills:
  - shared-memory
tags:
- crypto-pki
- signing
- artifact-signing
nist_csf: []
capec: []
---

# Artifact Signing — Ed25519 + BLAKE2b Integrity Skill

**Purpose:** Every agent in the cybersecsuite framework can sign, verify, and hash artifacts. This skill provides the crypto primitives and patterns used across all agents.

---

## Crypto Stack

| Operation | Algorithm | Implementation |
|---|---|---|
| Signing | Ed25519 | `cryptography.hazmat.primitives.asymmetric.ed25519` |
| Hashing | BLAKE2b-256 | `hashlib.blake2b(digest_size=32)` |
| KDF | Argon2id | `memory_cost=262144, iterations=4, lanes=4, salt_length=32` |
| Encryption | AES-256-GCM | `cryptography.hazmat.primitives.ciphers.aead.AESGCM` |
| Key Storage | PEM + Argon2id-encrypted | `PasswordManager.encrypt_key()` |

---

## Usage Patterns

### Compute BLAKE2b-256 Hash

```python
import hashlib
import json

data = {"key": "value"}
content_hash = hashlib.blake2b(
    json.dumps(data, sort_keys=True).encode(),
    digest_size=32
).hexdigest()
```

### Sign an Artifact with Ed25519

```python
from crypto.ssl_signer import SSLArtifactSigner

signer = SSLArtifactSigner(
    private_key_path="/etc/dystopian/crypto/cert/private/default-private.key",
    public_key_path="/etc/dystopian/crypto/cert/private/default-public.pem",
    key_id="default",
)

# Sign — returns frontmatter.payload token
token = signer.sign_artifact(
    artifact_data={"name": "evidence.json", "content": data},
    expires_in_hours=8760,  # 1 year
    custom_claims={"version": 1},
)

# Verify
is_valid, payload = signer.verify_artifact(token)

# Extract frontmatter (includes embedded signature)
metadata = signer.get_signature_metadata(token)
# → {"alg": "Ed25519", "kid": "default", "sig": "<base64>", "created_at": "..."}
```

### Managed Artifact Lifecycle (with DB)

```python
from crypto.artifact_manager import ArtifactManager
from crypto.ssl_signer import SSLArtifactSigner

signer = SSLArtifactSigner(private_key_path="...", key_id="default")
manager = ArtifactManager(signer)

# Create + auto-sign
artifact = await manager.create_artifact(
    name="evidence-001",
    content={"finding": "suspicious binary"},
    workspace_id=1,
    created_by="hunter",
    reason="Phase 5 memory forensics",
)

# Update + auto-re-sign
artifact = await manager.update_artifact(
    artifact_id=artifact.id,
    content={"finding": "confirmed rootkit", "ioc": "..."},
    modified_by="memory-analyst",
    reason="Cross-validated with kernel-analyst",
)

# Verify
result = await manager.verify_artifact(artifact.id, operator="hunter")
# → {"artifact_id": 1, "valid": True, "status": "valid", "payload": {...}}
```

### Pydantic Model with Signature

```python
from crypto.pydantic_models import ArtifactWithIntegrity, Ed25519Signer
from cryptography.hazmat.primitives.asymmetric import ed25519

# Create with HMAC checksum + optional Ed25519 signature
private_key = ed25519.Ed25519PrivateKey.generate()
artifact = ArtifactWithIntegrity.create(
    data={"config": {"env": "production"}},
    name="config.yaml",
    created_by="python-developer",
    private_key=private_key,
    key_id="deploy-key",
)

# Verify HMAC
assert artifact.verify_integrity()

# Verify Ed25519
public_key = private_key.public_key()
assert artifact.verify_signature(public_key)

# Frontmatter contains embedded signature
print(artifact.frontmatter)
# → {"alg": "Ed25519", "kid": "deploy-key", "sig": "...", "signed_at": "..."}
```

### Key Management (Argon2id + AES-256-GCM)

```python
from crypto.key_manager import KeyManager

km = KeyManager(keys_dir="/etc/dystopian/crypto/cert/private")

# Create CA keypair (Ed25519, password-protected)
metadata = km.create_ca_keypair(
    name="RootCA",
    password_file="/etc/dystopian-crypto/password",
)

# Load private key (decrypts with Argon2id + AES-256-GCM)
private_key = km.load_private_key("RootCA", password_file="/etc/dystopian-crypto/password")

# Rotate key
new_metadata = km.rotate_key("RootCA", password_file="/etc/dystopian-crypto/password")

# Verify integrity (file exists + permissions = 0o600)
is_valid, msg = km.verify_key_integrity("RootCA")
```

---

## Token Format

Signed tokens use **frontmatter.payload** format (2 parts, dot-separated):

```
<base64(frontmatter_json)>.<base64(payload_json)>
```

### Frontmatter (header with embedded signature)
```json
{
  "alg": "Ed25519",
  "typ": "ARTIFACT",
  "kid": "default",
  "created_at": "2026-04-17T00:00:00+00:00",
  "sig": "<base64 Ed25519 signature of payload>"
}
```

### Payload
```json
{
  "data": {"...artifact content..."},
  "body_hash": "<BLAKE2b-256 hex>",
  "exp": "2027-04-17T00:00:00+00:00",
  "iat": "2026-04-17T00:00:00+00:00"
}
```

---

## Rules for All Agents

1. **Every collected evidence artifact** MUST have a BLAKE2b-256 hash computed before storage
2. **Every artifact submitted to the DB** MUST be signed with Ed25519 via `ArtifactManager`
3. **Every signing operation** is logged to `ArtifactSignatureLog` (audit trail)
4. **Never hardcode passwords** — always use password files + `PasswordManager`
5. **Key file permissions** must be `0o600` for private keys, `0o644` for public keys
6. **Chain of custody**: every artifact records `created_by`, `modified_by`, `change_reason`
7. **Verification**: call `verify_artifact()` before acting on any artifact from external sources

---

## MITRE ATT&CK Mapping

| Finding | Technique |
|---|---|
| Unsigned artifact in evidence chain | T1565 – Data Manipulation |
| Key file with wrong permissions | T1552.004 – Private Keys |
| Missing audit log entry | T1070 – Indicator Removal |
| Tampered artifact (hash mismatch) | T1565.001 – Stored Data Manipulation |

