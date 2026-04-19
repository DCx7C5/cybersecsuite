"""
Artifact model with SSL signature tracking and version history.
"""
from tortoise.models import Model
from tortoise import fields


class Artifact(Model):
    """
    Represents a versioned, cryptographically-signed artifact.
    Each change generates a new signature automatically.
    """
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=512, db_index=True)
    description = fields.TextField(default="")

    # Content and checksums
    content = fields.JSONField(default={})
    content_hash = fields.CharField(max_length=64, db_index=True)  # SHA256
    body_hash = fields.CharField(max_length=64, default="")  # Computed by signer

    # SSL/RSA Signature
    signature = fields.TextField()  # JWT-like: header.payload.signature
    signature_valid = fields.BooleanField(default=False, db_index=True)
    signed_at = fields.DatetimeField(auto_now_add=True)
    signature_expires_at = fields.DatetimeField(null=True)
    key_id = fields.CharField(max_length=128, default="default", db_index=True)

    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    version = fields.IntField(default=1, db_index=True)

    # Relations
    parent_version = fields.ForeignKeyField(
        "models.Artifact",
        related_name="versions",
        null=True,
        on_delete=fields.SET_NULL
    )

    # Audit trail
    created_by = fields.CharField(max_length=256, default="system")
    modified_by = fields.CharField(max_length=256, default="system")
    change_reason = fields.TextField(default="")

    class Meta:
        table = "artifacts"
        ordering = ["-updated_at"]
        indexes = [
            ("workspace", "name"),
            ("signature_valid", "created_at"),
        ]

    async def compute_hash(self) -> str:
        """Compute SHA256 hash of current content."""
        import hashlib
        import json
        content_str = json.dumps(self.content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()


class ArtifactSignatureLog(Model):
    """
    Audit log for all signature operations on artifacts.
    """
    id = fields.IntField(primary_key=True)
    artifact = fields.ForeignKeyField(
        "models.Artifact",
        related_name="signature_logs",
        on_delete=fields.CASCADE
    )

    # Signature details
    signature = fields.TextField()
    signature_valid = fields.BooleanField()
    signature_algorithm = fields.CharField(max_length=64, default="RSA-HMAC-SHA256")
    key_id = fields.CharField(max_length=128)

    # Verification
    verified_at = fields.DatetimeField(null=True)
    verification_status = fields.CharField(
        max_length=64,
        choices=["valid", "invalid", "expired", "tampered", "pending"],
        default="pending"
    )
    verification_error = fields.TextField(default="")

    # Metadata
    created_at = fields.DatetimeField(auto_now_add=True)
    action = fields.CharField(
        max_length=64,
        choices=["sign", "verify", "re_sign", "revoke"],
        default="sign"
    )
    operator = fields.CharField(max_length=256, default="system")

    class Meta:
        table = "artifact_signature_logs"
        ordering = ["-created_at"]

