# Crypto Suite

Cryptographic utilities for artifact signing, key management, and encrypted storage.

## Overview

The crypto module provides:
- **Ed25519** key generation and artifact signing
- **BLAKE2b-256** checksums for data integrity
- **Argon2id** key derivation
- **AES-256-GCM** encryption for secure storage
- **Artifact signing** pipeline for investigation evidence
- **TLS certificate** generation for the ASGI proxy

## Quick Start

```python
from crypto.key_manager import KeyManager
from crypto.artifact_manager import ArtifactManager

# Generate or load Ed25519 key pair
km = KeyManager()
km.ensure_keys()  # creates ~/.cybersecsuite/keys/ if not present

# Sign an artifact
am = ArtifactManager(key_manager=km)
signature = am.sign_artifact(b"evidence data", metadata={"source": "pcap"})

# Verify
valid = am.verify_artifact(b"evidence data", signature)
```

Via `manage.py`:

```bash
python src/manage.py ssl-genkey   # Generate TLS cert + key
python src/manage.py ssl-info     # Display cert info
python src/manage.py ssl-verify   # Verify cert validity
```

## Algorithms

| Algorithm | Use case | Notes |
|-----------|---------|-------|
| Ed25519 | Artifact signing | 32-byte private key, 64-byte signature |
| BLAKE2b-256 | Content checksums | Fast, collision-resistant |
| Argon2id | Key derivation | Memory-hard, configurable cost params |
| AES-256-GCM | Encrypted cache | 32-byte key, 96-bit nonce, 128-bit auth tag |

## Key Lifecycle

```
KeyManager.ensure_keys()
    │
    ├── ~/.cybersecsuite/keys/ed25519_private.key  (mode 0600)
    └── ~/.cybersecsuite/keys/ed25519_public.key   (mode 0644)

ArtifactManager.sign_artifact(data)
    │
    ├── BLAKE2b-256 hash of data
    ├── Ed25519 sign(hash)
    └── returns ArtifactSignature(hash, signature, timestamp, key_id)

ArtifactManager.verify_artifact(data, signature)
    │
    ├── BLAKE2b-256 hash of data
    ├── Ed25519 verify(hash, signature.signature, public_key)
    └── returns bool
```

## Storage Paths

| Path | Contents | Permissions |
|------|---------|-------------|
| `~/.cybersecsuite/keys/` | Ed25519 private + public keys | `600` (private), `644` (public) |
| `~/.cybersecsuite/certs/` | TLS cert + key for ASGI proxy | `600` (key), `644` (cert) |

## Encrypted Cache

The `cache.py` module provides an AES-256-GCM encrypted key-value store:

```python
from crypto.cache import EncryptedCache

cache = EncryptedCache(key_manager=km)
cache.set("scan_result", {"iocs": [...]})
result = cache.get("scan_result")
```

## Configuration

Crypto settings are loaded from the project's `settings.json` (root of CWD or path in `CYBERSEC_SETTINGS_FILE`):

```json
{
  "crypto": {
    "signing_algorithm": "ed25519",
    "checksum_algorithm": "blake2b",
    "kdf": "argon2id",
    "encryption": "aes-256-gcm"
  },
  "artifacts": {
    "auto_sign": true,
    "verify_on_load": true
  },
  "keys": {
    "storage_dir": "~/.cybersecsuite/keys"
  }
}
```

## Files

| File | Purpose |
|------|---------|
| `key_manager.py` | Ed25519 key generation, loading, storage |
| `artifact_manager.py` | Sign + verify investigation artifacts |
| `ssl_signer.py` | TLS certificate generation (self-signed) |
| `cache.py` | AES-256-GCM encrypted cache |
| `config.py` | `settings.json` loader |
| `pydantic_models.py` | `ArtifactSignature`, `KeyPair`, `CryptoConfig` |
| `template_renderer.py` | Jinja2 report templating |
| `cli_integration.py` | CLI helper functions |

## A2A Authentication

A2A agents use Ed25519 for inter-agent authentication. The `AgentCard` specifies `AuthScheme.ED25519`. When calling a remote agent, the client signs the request with the local Ed25519 private key. The server verifies using the caller's public key (resolved from the agent card URL).
