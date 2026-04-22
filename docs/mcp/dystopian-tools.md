# Dystopian Crypto Tools (5)

Tools exposed by the `dystopian` MCP server (`mcp__dystopian__*`). Backed by `src/csmcp/dystopian.py` and `src/crypto/`.

Start: `uv run python -m csmcp.cybersec.server`

---

## `crypto_generate_keypair`

Generate a new Ed25519 CA or signing keypair. The private key is encrypted with Argon2id + AES-256-GCM.

| Parameter       | Type   | Required | Description                                                             |
|-----------------|--------|----------|-------------------------------------------------------------------------|
| `name`          | string | yes      | Identifier for the new keypair                                          |
| `key_type`      | string | no       | `"ca"` or `"signing"` (default: `"signing"`)                            |
| `keys_dir`      | string | no       | Directory to store keys (default: `/etc/dystopian/crypto/cert/private`) |
| `password_file` | string | no       | Path to password file (default: `/tmp/{name}.pwd`)                      |

---

## `crypto_sign_artifact`

Sign a forensic artifact file with an Ed25519 private key. Returns a signed token.

| Parameter       | Type   | Required | Description                                                               |
|-----------------|--------|----------|---------------------------------------------------------------------------|
| `artifact_path` | string | yes      | Path to the artifact file to sign                                         |
| `key_name`      | string | yes      | Name of the keypair to sign with                                          |
| `keys_dir`      | string | no       | Directory containing keys (default: `/etc/dystopian/crypto/cert/private`) |
| `password_file` | string | no       | Path to password file (default: `/tmp/{key_name}.pwd`)                    |

Returns: `{"token": "...", "metadata": {...}}`

---

## `crypto_verify_artifact`

Verify a signed artifact token produced by `crypto_sign_artifact`.

| Parameter  | Type   | Required | Description                                                               |
|------------|--------|----------|---------------------------------------------------------------------------|
| `token`    | string | yes      | The signed token returned by `crypto_sign_artifact`                       |
| `key_name` | string | yes      | Name of the keypair to verify against                                     |
| `keys_dir` | string | no       | Directory containing keys (default: `/etc/dystopian/crypto/cert/private`) |

Returns: `{"valid": true/false, "payload": {...}}`

---

## `crypto_list_keys`

List all managed Ed25519 keypairs with metadata.

| Parameter  | Type   | Required | Description                                                                 |
|------------|--------|----------|-----------------------------------------------------------------------------|
| `keys_dir` | string | no       | Directory to list keys from (default: `/etc/dystopian/crypto/cert/private`) |

---

## `crypto_rotate_key`

Rotate an Ed25519 keypair: re-encrypts the private key with a new Argon2id-derived key.

| Parameter           | Type   | Required | Description                                                               |
|---------------------|--------|----------|---------------------------------------------------------------------------|
| `name`              | string | yes      | Name of the keypair to rotate                                             |
| `old_password_file` | string | yes      | Path to the current password file                                         |
| `new_password_file` | string | yes      | Path to the new password file                                             |
| `keys_dir`          | string | no       | Directory containing keys (default: `/etc/dystopian/crypto/cert/private`) |

---

## Key Storage

Keys are stored in `keys_dir` (default `/etc/dystopian/crypto/cert/private`). Override per call via the `keys_dir` parameter. The `DYSTOPIAN_KEYS_DIR` env var in `mcp.json` sets the server's working default.

Private key files: `{keys_dir}/{name}.private.pem`  
Public key files: `{keys_dir}/{name}.public.pem`

## Algorithms

| Algorithm   | Use                          | Parameters              |
|-------------|------------------------------|-------------------------|
| Ed25519     | Key generation + signing     | 256-bit keys            |
| BLAKE2b-256 | Content hashing              | 256-bit digests         |
| Argon2id    | Key encryption               | mem=262144, iters=4     |
| AES-256-GCM | Private key encryption       | Random 12-byte nonce    |
