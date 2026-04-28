"""
Artifact manager with automatic SSL signing on every change.
Integrates with ssl_signer for Ed25519-based signatures.
"""
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from db.models.artifact import Artifact, ArtifactSignatureLog
from crypto.ssl_signer import SSLArtifactSigner


class ArtifactManager:
    """
    Manages lifecycle of SSL-signed artifacts:
    - Auto-signs on creation and updates
    - Tracks signature history
    - Verifies signatures
    - Manages versions
    """

    def __init__(self, signer: SSLArtifactSigner):
        """Initialize with configured SSL signer."""
        self.signer = signer

    async def create_artifact(
        self,
        name: str,
        content: Dict[str, Any],
        workspace_id: Optional[int] = None,
        description: str = "",
        created_by: str = "system",
        reason: str = "",
        **kwargs
    ) -> Artifact:
        """
        Create and sign a new artifact.

        Args:
            name: Artifact name
            content: JSON-serializable content to sign
            workspace_id: Parent workspace
            description: Artifact description
            created_by: User who created it
            reason: Change reason for audit trail
            **kwargs: Additional fields

        Returns:
            Created and signed Artifact instance
        """
        # Compute content hash with BLAKE2b
        content_hash = hashlib.blake2b(
            json.dumps(content, sort_keys=True).encode(),
            digest_size=32  # 256-bit output
        ).hexdigest()

        # Sign the content
        token = self.signer.sign_artifact(
            artifact_data=content,
            expires_in_hours=8760,  # 1 year
            custom_claims={
                "name": name,
                "version": 1,
            }
        )

        # Create artifact
        artifact = await Artifact.create(
            name=name,
            content=content,
            content_hash=content_hash,
            signature=token,
            signature_valid=True,
            key_id=self.signer.key_id,
            workspace_id=workspace_id,
            description=description,
            created_by=created_by,
            change_reason=reason,
            **kwargs
        )

        # Log signature
        await self._log_signature(
            artifact=artifact,
            token=token,
            action="sign",
            operator=created_by
        )

        return artifact

    async def update_artifact(
        self,
        artifact_id: int,
        content: Dict[str, Any],
        modified_by: str = "system",
        reason: str = "",
    ) -> Artifact:
        """
        Update artifact content and re-sign automatically.

        Args:
            artifact_id: Artifact to update
            content: New content
            modified_by: User who modified it
            reason: Change reason

        Returns:
            Updated and re-signed Artifact
        """
        artifact = await Artifact.get(id=artifact_id)

        # Create version history
        parent = artifact
        artifact.version += 1

        # Compute new hash with BLAKE2b
        new_hash = hashlib.blake2b(
            json.dumps(content, sort_keys=True).encode(),
            digest_size=32  # 256-bit output
        ).hexdigest()

        # Sign new content
        token = self.signer.sign_artifact(
            artifact_data=content,
            expires_in_hours=8760,
            custom_claims={
                "name": artifact.name,
                "version": artifact.version,
            }
        )

        # Update artifact
        artifact.content = content
        artifact.content_hash = new_hash
        artifact.signature = token
        artifact.signature_valid = True
        artifact.modified_by = modified_by
        artifact.change_reason = reason
        artifact.parent_version = parent

        await artifact.save()

        # Log signature
        await self._log_signature(
            artifact=artifact,
            token=token,
            action="re_sign",
            operator=modified_by
        )

        return artifact

    async def verify_artifact(
        self,
        artifact_id: int,
        operator: str = "system"
    ) -> Dict[str, Any]:
        """
        Verify artifact signature and log result.

        Args:
            artifact_id: Artifact to verify
            operator: User performing verification

        Returns:
            Verification result dict
        """
        artifact = await Artifact.get(id=artifact_id)

        is_valid, payload = self.signer.verify_artifact(artifact.signature)

        # Update artifact validity
        artifact.signature_valid = is_valid

        if is_valid and payload:
            artifact.body_hash = payload.get("body_hash", "")
            exp_iso = payload.get("exp")
            if exp_iso and isinstance(exp_iso, str):
                artifact.signature_expires_at = datetime.fromisoformat(exp_iso)

        await artifact.save()

        # Log verification
        status = "valid" if is_valid else "invalid"
        if is_valid and artifact.signature_expires_at:
            if datetime.now(timezone.utc) > artifact.signature_expires_at:
                status = "expired"

        await self._log_signature(
            artifact=artifact,
            token=artifact.signature,
            action="verify",
            operator=operator,
            status=status
        )

        return {
            "artifact_id": artifact.id,
            "valid": is_valid,
            "payload": payload,
            "status": status,
        }

    async def get_artifact_history(
        self,
        artifact_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get version history of an artifact.

        Args:
            artifact_id: Artifact to get history for
            limit: Max results

        Returns:
            List of artifact versions with metadata
        """
        artifact = await Artifact.get(id=artifact_id)

        # Get all versions (forward chain)
        versions = []
        current = artifact

        while current and len(versions) < limit:
            versions.append({
                "id": current.id,
                "version": current.version,
                "content_hash": current.content_hash,
                "signature_valid": current.signature_valid,
                "created_at": current.created_at.isoformat(),
                "modified_by": current.modified_by,
                "change_reason": current.change_reason,
            })
            # Get parent
            current = current.parent_version

        return versions

    async def list_artifacts(
        self,
        workspace_id: Optional[int] = None,
        valid_only: bool = False,
        limit: int = 100
    ) -> List[Artifact]:
        """
        List artifacts with optional filtering.

        Args:
            workspace_id: Filter by workspace
            valid_only: Only return valid signatures
            limit: Max results

        Returns:
            List of Artifact models
        """
        query = Artifact.all()

        if workspace_id:
            query = query.filter(workspace_id=workspace_id)

        if valid_only:
            query = query.filter(signature_valid=True)

        return await query.limit(limit)

    async def bulk_verify(
        self,
        artifact_ids: List[int],
        operator: str = "system"
    ) -> Dict[str, Any]:
        """
        Verify multiple artifacts and return summary.

        Args:
            artifact_ids: IDs to verify
            operator: User performing verification

        Returns:
            Verification summary
        """
        errors: List[Dict[str, Any]] = []
        results: Dict[str, Any] = {
            "total": len(artifact_ids),
            "valid": 0,
            "invalid": 0,
            "expired": 0,
            "errors": errors
        }

        for artifact_id in artifact_ids:
            try:
                result = await self.verify_artifact(artifact_id, operator)
                if result["status"] == "valid":
                    results["valid"] += 1
                elif result["status"] == "expired":
                    results["expired"] += 1
                else:
                    results["invalid"] += 1
            except Exception as e:
                errors.append({"artifact_id": artifact_id, "error": str(e)})
                results["invalid"] += 1

        return results

    async def get_signature_metadata(
        self,
        artifact_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Extract signature headers metadata without verification.

        Args:
            artifact_id: Artifact to inspect

        Returns:
            Header metadata or None
        """
        artifact = await Artifact.get(id=artifact_id)
        return self.signer.get_signature_metadata(artifact.signature)

    async def _log_signature(
        self,
        artifact: Artifact,
        token: str,
        action: str = "sign",
        operator: str = "system",
        status: str = "valid"
    ) -> ArtifactSignatureLog:
        """
        Internal: Log signature operation to audit trail.

        Args:
            artifact: Artifact being logged
            token: Signature token
            action: Operation type
            operator: User performing operation
            status: Verification status

        Returns:
            Created log entry
        """

        log_entry = await ArtifactSignatureLog.create(
            artifact=artifact,
            signature=token,
            signature_valid=(status == "valid"),
            key_id=self.signer.key_id,
            action=action,
            operator=operator,
            verification_status=status,
        )

        return log_entry

    async def get_signature_logs(
        self,
        artifact_id: int,
        limit: int = 100
    ) -> List[ArtifactSignatureLog]:
        """
        Get signature audit trail for an artifact.

        Args:
            artifact_id: Artifact to get logs for
            limit: Max results

        Returns:
            List of signature log entries
        """
        return await ArtifactSignatureLog.filter(
            artifact_id=artifact_id
        ).limit(limit)

