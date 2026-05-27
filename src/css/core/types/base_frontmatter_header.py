"""Base frontmatter header — cryptographically signed document contract.

``BaseFrontmatterHeader`` is the core data + crypto type for the SecureMD
protocol. It holds frontmatter metadata (name, description, hash), an
Ed25519 signature, and the document body.

Frozen so that entity-specific headers (``BaseAgentHeader``, …) can
inherit from it — mutation in ``sign()`` uses ``object.__setattr__``.

Config-aware behavior:
- ``SECUREMD_ENABLED=false``: ``verify_and_get_body()`` returns the body
  directly with a log warning and no signature check.
- ``SECUREMD_ENFORCE_HEADER=true``: ``__post_init__`` rejects documents
  missing any required field (name, description, signature, hash).
"""

import logging
import os

import msgspec
import msgspec.yaml

from css.core.cryptography import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
    sign_bytes,
    verify_signature,
)

log = logging.getLogger(__name__)


def _securemd_enabled() -> bool:
    return os.getenv("SECUREMD_ENABLED", "true").lower() == "true"


def _securemd_enforce_header() -> bool:
    return os.getenv("SECUREMD_ENFORCE_HEADER", "true").lower() == "true"


_REQUIRED_FIELDS = frozenset({"name", "description", "signature", "hash"})


class BaseFrontmatterHeader(msgspec.Struct, frozen=True, kw_only=True):
    """Frontmatter header with cryptographic integrity verification.

    Fields:
        name: Document name / identifier (required when enforcement is on).
        description: Document description / purpose (required when enforcement is on).
        hash: Content hash (required when enforcement is on). Not yet validated;
            carried for future SHA-512 body verification.
        signature: Ed25519 hex signature covering canonical frontmatter + body
            (required when enforcement is on).
        body: The Markdown body text following the frontmatter delimiter.
    """

    name: str
    description: str
    hash: str = ""
    signature: str = ""
    body: str = ""

    def __post_init__(self) -> None:
        """Validate minimum header requirements when enforcement is enabled."""
        if _securemd_enforce_header():
            missing = _REQUIRED_FIELDS - {
                k for k in _REQUIRED_FIELDS if getattr(self, k)
            }
            if missing:
                raise ValueError(
                    f"SecureMD header missing required fields: {', '.join(sorted(missing))}"
                )

    def _canonical(self) -> bytes:
        """Deterministic canonical bytes: sorted-key YAML frontmatter + body."""
        frontmatter: dict[str, str] = {"name": self.name, "description": self.description}
        if self.hash:
            frontmatter["hash"] = self.hash

        yaml_bytes = msgspec.yaml.encode(frontmatter)

        separator = b"---\n"
        body_bytes = self.body.encode("utf-8") if self.body else b""
        return yaml_bytes + separator + body_bytes

    def sign(self, private_key: Ed25519PrivateKey) -> None:
        """Sign the canonical document bytes.

        Sets ``self.signature`` to the uppercase hex Ed25519 signature.
        The private_key must be an ``Ed25519PrivateKey`` instance from
        ``cryptography``.
        """
        canonical = self._canonical()
        sig = sign_bytes(private_key, canonical)
        object.__setattr__(self, "signature", sig)

    def verify(self, public_key: Ed25519PublicKey) -> bool:
        """Verify the Ed25519 signature against canonical document bytes.

        Returns True if the signature matches the canonical content and
        public key. Always checks SECUREMD_ENABLED first.
        """
        if not _securemd_enabled():
            return True
        if not self.signature:
            return False
        canonical = self._canonical()
        return verify_signature(public_key, canonical, self.signature)

    def verify_and_get_body(self, public_key: Ed25519PublicKey) -> str:
        """Return the verified body or raise.

        Gates body access behind signature verification. When
        SECUREMD_ENABLED is false, returns the body with a warning and
        no verification.
        """
        if not _securemd_enabled():
            log.warning("SECUREMD_ENABLED=false — skipping signature verification")
            return self.body
        if not self.verify(public_key):
            raise ValueError(
                "SecureMD signature verification failed — document may be tampered"
            )
        return self.body
