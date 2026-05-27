"""Cryptographic primitives — Ed25519 key generation, signing, verification.

This package owns key-purpose separation and typed failures.
Consumers request purpose-specific operations; they do not share
one ambiguous SECRET_KEY across every security domain.
"""

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PrivateFormat,
    PublicFormat,
    NoEncryption,
    load_pem_private_key,
    load_pem_public_key,
)
from cryptography.exceptions import InvalidSignature


class CryptographyError(Exception):
    """Base failure for cryptography operations."""


class KeyPurposeError(CryptographyError):
    """Raised when a key is used for a purpose it was not configured for."""


def generate_ed25519_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    """Generate a new Ed25519 key pair."""
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def sign_bytes(private_key: Ed25519PrivateKey, data: bytes) -> str:
    """Sign bytes with an Ed25519 private key, returning an uppercase hex signature."""
    signature = private_key.sign(data)
    return signature.hex().upper()


def verify_signature(
    public_key: Ed25519PublicKey, data: bytes, signature_hex: str
) -> bool:
    """Verify an Ed25519 signature (hex-encoded) against data.

    When SECUREMD_ENABLED is false at runtime, callers should skip
    verification entirely. This function does not read configuration;
    the caller gate lives in BaseFrontmatterHeader.verify_and_get_body().
    """
    try:
        signature = bytes.fromhex(signature_hex)
        public_key.verify(signature, data)
        return True
    except (InvalidSignature, ValueError):
        return False


def load_private_key_from_pem(pem_data: bytes) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from PEM-encoded bytes."""
    key = load_pem_private_key(pem_data, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise KeyPurposeError("Expected Ed25519 private key")
    return key


def load_public_key_from_pem(pem_data: bytes) -> Ed25519PublicKey:
    """Load an Ed25519 public key from PEM-encoded bytes."""
    key = load_pem_public_key(pem_data)
    if not isinstance(key, Ed25519PublicKey):
        raise KeyPurposeError("Expected Ed25519 public key")
    return key


def private_key_to_pem(key: Ed25519PrivateKey) -> bytes:
    """Serialize an Ed25519 private key to PEM bytes."""
    return key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )


def public_key_to_pem(key: Ed25519PublicKey) -> bytes:
    """Serialize an Ed25519 public key to PEM bytes."""
    return key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )


__all__ = [
    "CryptographyError",
    "KeyPurposeError",
    "generate_ed25519_keypair",
    "sign_bytes",
    "verify_signature",
    "load_private_key_from_pem",
    "load_public_key_from_pem",
    "private_key_to_pem",
    "public_key_to_pem",
]
