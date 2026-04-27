"""Dystopian-crypto in-process MCP server.

Wraps src/crypto/ (Ed25519, Argon2id, AES-256-GCM, BLAKE2b) with 5 SDK tools.
"""
from __future__ import annotations

from typing import Any

from cssmcp._sdk_compat import tool, create_sdk_mcp_server
from cssmcp.cybersec.helpers import JsonDict, sdk_result, sdk_error


@tool(
    "crypto_generate_keypair",
    "Generate an Ed25519 CA or signing keypair and encrypt the private key with Argon2id+AES-256-GCM.",
    {
        "name": "string",
        "key_type": {"type": "string", "enum": ["ca", "signing"], "default": "signing"},
        "keys_dir": {"type": "string", "default": "/etc/dystopian/crypto/cert/private"},
        "password_file": {"type": "string", "nullable": True},
    },
)
def crypto_generate_keypair(args: dict[str, Any]) -> JsonDict:
    try:
        from crypto.key_manager import KeyManager
    except ImportError:
        return sdk_error("crypto.key_manager not available — ensure src/ is in PYTHONPATH")

    km = KeyManager(keys_dir=args.get("keys_dir", "/etc/dystopian/crypto/cert/private"))
    name = args["name"]
    key_type = args.get("key_type", "signing")
    password_file = args.get("password_file") or f"/tmp/{name}.pwd"

    try:
        if key_type == "ca":
            metadata = km.create_ca_keypair(name=name, password_file=password_file)
        else:
            metadata = km.create_signing_keypair(name=name, password_file=password_file)

        return sdk_result({
            "status": "success",
            "name": name,
            "key_type": key_type,
            "public_key_path": metadata["public_key_path"],
            "private_key_path": metadata["private_key_path"],
            "algorithm": "Ed25519",
            "kdf": "Argon2id",
            "cipher": "AES-256-GCM",
        })
    except Exception as exc:
        return sdk_error(str(exc))


@tool(
    "crypto_sign_artifact",
    "Sign an artifact (file or bytes) with an Ed25519 private key.",
    {
        "artifact_path": "string",
        "key_name": "string",
        "keys_dir": {"type": "string", "default": "/etc/dystopian/crypto/cert/private"},
        "password_file": {"type": "string", "nullable": True},
    },
)
def crypto_sign_artifact(args: dict[str, Any]) -> JsonDict:
    try:
        from crypto.ssl_signer import SSLArtifactSigner
    except ImportError:
        return sdk_error("crypto.ssl_signer not available")

    key_name = args["key_name"]
    keys_dir = args.get("keys_dir", "/etc/dystopian/crypto/cert/private")
    password_file = args.get("password_file") or f"/tmp/{key_name}.pwd"

    try:
        signer = SSLArtifactSigner(
            private_key_path=f"{keys_dir}/{key_name}.private.pem",
            public_key_path=f"{keys_dir}/{key_name}.public.pem",
            password_file=password_file,
        )
        import pathlib
        artifact_bytes = pathlib.Path(args["artifact_path"]).read_bytes()
        token = signer.sign_artifact(artifact_bytes)
        meta = signer.get_signature_metadata(token)
        return sdk_result({"status": "success", "token": token, "metadata": meta})
    except Exception as exc:
        return sdk_error(str(exc))


@tool(
    "crypto_verify_artifact",
    "Verify an Ed25519-signed artifact token.",
    {
        "token": "string",
        "key_name": "string",
        "keys_dir": {"type": "string", "default": "/etc/dystopian/crypto/cert/private"},
    },
)
def crypto_verify_artifact(args: dict[str, Any]) -> JsonDict:
    try:
        from crypto.ssl_signer import SSLArtifactSigner
    except ImportError:
        return sdk_error("crypto.ssl_signer not available")

    key_name = args["key_name"]
    keys_dir = args.get("keys_dir", "/etc/dystopian/crypto/cert/private")

    try:
        signer = SSLArtifactSigner(
            private_key_path=f"{keys_dir}/{key_name}.private.pem",
            public_key_path=f"{keys_dir}/{key_name}.public.pem",
        )
        valid, payload = signer.verify_artifact(args["token"])
        return sdk_result({"status": "success", "valid": valid, "payload": payload})
    except Exception as exc:
        return sdk_error(str(exc))


@tool(
    "crypto_list_keys",
    "List all managed Ed25519 key pairs with metadata.",
    {"keys_dir": {"type": "string", "default": "/etc/dystopian/crypto/cert/private"}},
)
def crypto_list_keys(args: dict[str, Any]) -> JsonDict:
    try:
        from crypto.key_manager import KeyManager
    except ImportError:
        return sdk_error("crypto.key_manager not available")

    try:
        km = KeyManager(keys_dir=args.get("keys_dir", "/etc/dystopian/crypto/cert/private"))
        keys = km.list_keys()
        return sdk_result({"status": "success", "keys": keys, "count": len(keys)})
    except Exception as exc:
        return sdk_error(str(exc))


@tool(
    "crypto_rotate_key",
    "Rotate an existing Ed25519 key pair, re-encrypting with a new Argon2id-derived key.",
    {
        "name": "string",
        "old_password_file": "string",
        "new_password_file": "string",
        "keys_dir": {"type": "string", "default": "/etc/dystopian/crypto/cert/private"},
    },
)
def crypto_rotate_key(args: dict[str, Any]) -> JsonDict:
    try:
        from crypto.key_manager import KeyManager
    except ImportError:
        return sdk_error("crypto.key_manager not available")

    try:
        km = KeyManager(keys_dir=args.get("keys_dir", "/etc/dystopian/crypto/cert/private"))
        result = km.rotate_key(
            name=args["name"],
            old_password_file=args["old_password_file"],
            new_password_file=args["new_password_file"],
        )
        return sdk_result({"status": "success", "rotated": args["name"], "result": result})
    except Exception as exc:
        return sdk_error(str(exc))


_ALL_DYSTOPIAN_TOOLS = [
    crypto_generate_keypair,
    crypto_sign_artifact,
    crypto_verify_artifact,
    crypto_list_keys,
    crypto_rotate_key,
]

dystopian_server = create_sdk_mcp_server(
    name="dystopian",
    version="0.1.0",
    tools=_ALL_DYSTOPIAN_TOOLS,
)

__all__ = ["dystopian_server", "_ALL_DYSTOPIAN_TOOLS"]
