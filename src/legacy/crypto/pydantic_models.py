"""
Pydantic models for artifacts with Ed25519 signatures and BLAKE2b integrity checking.
Supports frontmatter-based signature embedding.
"""
import hmac
import hashlib
import json
import base64
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend


class Ed25519Signer:
    """Ed25519 signature operations for artifact integrity."""

    @staticmethod
    def _base64_encode(data: bytes) -> str:
        """URL-safe base64 encoding."""
        return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

    @staticmethod
    def _base64_decode(data: str) -> bytes:
        """URL-safe base64 decoding."""
        padding = 4 - (len(data) % 4)
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def sign(data: Dict[str, Any], private_key: ed25519.Ed25519PrivateKey) -> str:
        """
        Sign data with Ed25519 and return base64-encoded signature.

        Args:
            data: Dictionary to sign
            private_key: Ed25519 private key

        Returns:
            Base64-encoded signature
        """
        content_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        signature = private_key.sign(content_bytes)
        return Ed25519Signer._base64_encode(signature)

    @staticmethod
    def verify(
        data: Dict[str, Any],
        signature: str,
        public_key: ed25519.Ed25519PublicKey
    ) -> bool:
        """
        Verify Ed25519 signature.

        Args:
            data: Dictionary that was signed
            signature: Base64-encoded signature
            public_key: Ed25519 public key

        Returns:
            True if signature valid, False otherwise
        """
        try:
            content_bytes = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
            sig_bytes = Ed25519Signer._base64_decode(signature)
            public_key.verify(sig_bytes, content_bytes)
            return True
        except Exception:
            return False

    @staticmethod
    def load_private_key(pem_data: bytes) -> ed25519.Ed25519PrivateKey:
        """Load Ed25519 private key from PEM bytes."""
        key = serialization.load_pem_private_key(
            pem_data, password=None, backend=default_backend()
        )
        if not isinstance(key, ed25519.Ed25519PrivateKey):
            raise TypeError("Expected Ed25519 private key")
        return key

    @staticmethod
    def load_public_key(pem_data: bytes) -> ed25519.Ed25519PublicKey:
        """Load Ed25519 public key from PEM bytes."""
        key = serialization.load_pem_public_key(pem_data, backend=default_backend())
        if not isinstance(key, ed25519.Ed25519PublicKey):
            raise TypeError("Expected Ed25519 public key")
        return key


class ArtifactChecksum:
    """Compute and verify BLAKE2b checksums for artifact integrity."""

    @staticmethod
    def compute(data: Dict[str, Any], key: str = "artifact_integrity") -> str:
        """
        Compute keyed BLAKE2b checksum of data.

        Args:
            data: Dictionary to checksum
            key: BLAKE2b key (default: "artifact_integrity")

        Returns:
            Hex-encoded BLAKE2b-256
        """
        content_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.blake2b(
            content_str.encode(),
            key=key.encode()[:64],  # BLAKE2b key max 64 bytes
            digest_size=32  # 256-bit output
        ).hexdigest()

    @staticmethod
    def verify(data: Dict[str, Any], checksum: str, key: str = "artifact_integrity") -> bool:
        """
        Verify BLAKE2b checksum.

        Args:
            data: Dictionary to verify
            checksum: Expected BLAKE2b hex
            key: BLAKE2b key (must match compute())

        Returns:
            True if checksum valid, False otherwise
        """
        expected = ArtifactChecksum.compute(data, key)
        return hmac.compare_digest(expected, checksum)


class ArtifactMetadata(BaseModel):
    """Metadata for artifact."""

    name: str = Field(..., min_length=1, max_length=512)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = Field(default="system", max_length=256)
    description: str = Field(default="", max_length=2048)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "deployment.yaml",
                "version": 1,
                "created_at": "2026-04-10T00:00:00Z",
                "created_by": "admin",
                "description": "Production deployment config"
            }
        }


class ArtifactContent(BaseModel):
    """Main artifact content - fully flexible."""

    data: Dict[str, Any] = Field(..., description="Artifact data (any structure)")
    metadata: ArtifactMetadata = Field(default_factory=ArtifactMetadata)

    class Config:
        json_schema_extra = {
            "example": {
                "data": {
                    "config": {"env": "production"},
                    "status": "active"
                },
                "metadata": {
                    "name": "config.yaml",
                    "version": 1,
                    "created_by": "admin"
                }
            }
        }


class ArtifactWithIntegrity(BaseModel):
    """Artifact with Ed25519 signature and HMAC integrity check."""

    id: Optional[str] = Field(default=None, description="Artifact ID")
    content: ArtifactContent = Field(..., description="Artifact data + metadata")
    checksum: str = Field(..., description="BLAKE2b-256 checksum (hex)")
    signature: Optional[str] = Field(default=None, description="Ed25519 signature (base64)")
    frontmatter: Optional[Dict[str, Any]] = Field(default=None, description="Signature frontmatter")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @model_validator(mode="after")
    def validate_checksum(self) -> "ArtifactWithIntegrity":
        """Optionally validate checksum on load."""
        # Don't enforce - allow both valid and unverified
        # Call verify_integrity() explicitly if needed
        return self

    def verify_integrity(self, key: str = "artifact_integrity") -> bool:
        """
        Verify HMAC checksum matches content.

        Args:
            key: HMAC key (must match when created)

        Returns:
            True if checksum valid
        """
        expected = ArtifactChecksum.compute(
            self.content.model_dump(),
            key
        )
        return hmac.compare_digest(expected, self.checksum)

    def verify_signature(self, public_key: ed25519.Ed25519PublicKey) -> bool:
        """
        Verify Ed25519 signature.

        Args:
            public_key: Ed25519 public key for verification

        Returns:
            True if signature valid
        """
        if not self.signature:
            return False
        return Ed25519Signer.verify(
            self.content.model_dump(),
            self.signature,
            public_key
        )

    def sign(self, private_key: ed25519.Ed25519PrivateKey, key_id: str = "default") -> None:
        """
        Sign artifact with Ed25519 and embed signature in frontmatter.

        Args:
            private_key: Ed25519 private key
            key_id: Key identifier for frontmatter
        """
        self.signature = Ed25519Signer.sign(self.content.model_dump(), private_key)
        self.frontmatter = {
            "alg": "Ed25519",
            "kid": key_id,
            "sig": self.signature,
            "signed_at": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def create(
        cls,
        data: Dict[str, Any],
        name: str,
        created_by: str = "system",
        description: str = "",
        key: str = "artifact_integrity",
        artifact_id: Optional[str] = None,
        private_key: Optional[ed25519.Ed25519PrivateKey] = None,
        key_id: str = "default",
    ) -> "ArtifactWithIntegrity":
        """
        Create new artifact with computed checksum and optional Ed25519 signature.

        Args:
            data: Artifact data
            name: Artifact name
            created_by: Creator user
            description: Optional description
            key: HMAC key for checksum
            artifact_id: Optional ID (auto-generated if not provided)
            private_key: Optional Ed25519 private key for signing
            key_id: Key identifier for signature frontmatter

        Returns:
            New ArtifactWithIntegrity instance
        """
        metadata = ArtifactMetadata(
            name=name,
            created_by=created_by,
            description=description
        )
        content = ArtifactContent(data=data, metadata=metadata)
        checksum = ArtifactChecksum.compute(content.model_dump(), key)

        instance = cls(
            id=artifact_id,
            content=content,
            checksum=checksum
        )

        # Sign if private key provided
        if private_key:
            instance.sign(private_key, key_id)

        return instance

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict (for JSON serialization)."""
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()


class SignedArtifact(BaseModel):
    """Artifact with Ed25519 signature embedded in frontmatter."""

    frontmatter: Dict[str, Any] = Field(..., description="Signature frontmatter with 'sig' field")
    payload: Dict[str, Any] = Field(..., description="Artifact payload")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def verify(self, public_key: ed25519.Ed25519PublicKey) -> bool:
        """
        Verify Ed25519 signature from frontmatter.

        Args:
            public_key: Ed25519 public key

        Returns:
            True if signature valid
        """
        signature = self.frontmatter.get("sig")
        if not signature or not isinstance(signature, str):
            return False
        return Ed25519Signer.verify(self.payload, signature, public_key)

    @classmethod
    def create(
        cls,
        payload: Dict[str, Any],
        private_key: ed25519.Ed25519PrivateKey,
        key_id: str = "default",
    ) -> "SignedArtifact":
        """
        Create signed artifact with signature in frontmatter.

        Args:
            payload: Data to sign
            private_key: Ed25519 private key
            key_id: Key identifier

        Returns:
            New SignedArtifact with signature in frontmatter
        """
        signature = Ed25519Signer.sign(payload, private_key)
        frontmatter = {
            "alg": "Ed25519",
            "typ": "ARTIFACT",
            "kid": key_id,
            "sig": signature,
            "signed_at": datetime.now(timezone.utc).isoformat(),
        }
        return cls(frontmatter=frontmatter, payload=payload)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict."""
        return self.model_dump(mode="json")


class CachedMessage(BaseModel):
    """Cached JSON message with BLAKE2b integrity."""

    message_id: str = Field(..., description="Unique message ID")
    request: Dict[str, Any] = Field(..., description="Original request")
    response: Dict[str, Any] = Field(..., description="Cached response")
    checksum: str = Field(..., description="BLAKE2b-256 of response")
    cached_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = Field(default=None, description="Cache expiration")
    hit_count: int = Field(default=0, description="Number of cache hits")

    def verify_integrity(self, key: str = "cache_integrity") -> bool:
        """
        Verify response hasn't been tampered with.

        Args:
            key: HMAC key

        Returns:
            True if checksum valid
        """
        expected = ArtifactChecksum.compute(self.response, key)
        return hmac.compare_digest(expected, self.checksum)

    def is_expired(self) -> bool:
        """Check if cache has expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    @classmethod
    def create(
        cls,
        message_id: str,
        request: Dict[str, Any],
        response: Dict[str, Any],
        expires_in_hours: Optional[int] = None,
        key: str = "cache_integrity",
    ) -> "CachedMessage":
        """
        Create cached message with checksum.

        Args:
            message_id: Unique ID for this message
            request: Original request
            response: Response to cache
            expires_in_hours: Optional TTL
            key: HMAC key

        Returns:
            New CachedMessage instance
        """
        checksum = ArtifactChecksum.compute(response, key)
        expires_at = None
        if expires_in_hours:
            from datetime import timedelta
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        return cls(
            message_id=message_id,
            request=request,
            response=response,
            checksum=checksum,
            expires_at=expires_at
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict."""
        return self.model_dump(mode="json")


class ArtifactBatch(BaseModel):
    """Batch of artifacts for bulk operations."""

    batch_id: str = Field(..., description="Batch identifier")
    artifacts: list[ArtifactWithIntegrity] = Field(..., min_length=1)
    batch_checksum: str = Field(..., description="BLAKE2b of entire batch")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def verify_batch_integrity(self, key: str = "batch_integrity") -> bool:
        """
        Verify entire batch hasn't been tampered with.

        Args:
            key: HMAC key

        Returns:
            True if all artifacts and batch valid
        """
        # Verify batch checksum
        batch_data = {
            "artifacts": [a.model_dump() for a in self.artifacts],
            "batch_id": self.batch_id
        }
        expected = ArtifactChecksum.compute(batch_data, key)
        if not hmac.compare_digest(expected, self.batch_checksum):
            return False

        # Verify each artifact
        for artifact in self.artifacts:
            if not artifact.verify_integrity(key):
                return False

        return True

    @classmethod
    def create(
        cls,
        batch_id: str,
        artifacts: list[ArtifactWithIntegrity],
        key: str = "batch_integrity",
    ) -> "ArtifactBatch":
        """
        Create artifact batch with checksums.

        Args:
            batch_id: Batch ID
            artifacts: List of artifacts
            key: HMAC key

        Returns:
            New ArtifactBatch instance
        """
        batch_data = {
            "artifacts": [a.model_dump() for a in artifacts],
            "batch_id": batch_id
        }
        batch_checksum = ArtifactChecksum.compute(batch_data, key)

        return cls(
            batch_id=batch_id,
            artifacts=artifacts,
            batch_checksum=batch_checksum
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to plain dict."""
        return self.model_dump(mode="json")

