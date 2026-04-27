"""
Template renderer for artifact markdown files.
Renders artifact.md template with Ed25519 signatures in frontmatter.
"""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


def _render_template_string(source: str, ctx: dict) -> str:
    """Render a Jinja2-style {{ var }} template using regex substitution."""
    def replace(m):
        key = m.group(1).strip()
        return str(ctx.get(key, ""))
    return re.sub(r'\{\{\s*(\w+)\s*\}\}', replace, source)


class ArtifactTemplateRenderer:
    """Render artifact plugins with signature data."""

    TEMPLATE_PATH = Path(__file__).parent.parent.parent / ".claude" / "templates" / "artifact.md"

    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize renderer.

        Args:
            template_path: Custom template path (default: plugins/artifact.md)
        """
        if template_path:
            self.template_path = Path(template_path)
        else:
            self.template_path = self.TEMPLATE_PATH

        self._template: Optional[str] = None

    @property
    def template(self) -> str:
        """Load and cache template."""
        if self._template is None:
            if self.template_path.exists():
                self._template = self.template_path.read_text()
            else:
                from cybersecsuite.scaffold import get_embedded_template
                embedded = get_embedded_template("artifact.md")
                if embedded is None:
                    raise FileNotFoundError(
                        f"Template not found at {self.template_path} and no embedded fallback"
                    )
                self._template = embedded
        return self._template

    def render(
        self,
        name: str,
        content: Dict[str, Any],
        signature: str,
        key_id: str = "default",
        version: int = 1,
        description: str = "",
        created_by: str = "system",
        created_at: Optional[datetime] = None,
        content_hash: Optional[str] = None,
        body_hash: str = "",
        signature_valid: bool = True,
        expires_at: Optional[datetime] = None,
        signature_log: Optional[List[Dict[str, Any]]] = None,
        checksum: Optional[str] = None,
    ) -> str:
        """
        Render artifact template with provided data.

        Args:
            name: Artifact name
            content: Artifact content dict
            signature: Ed25519 signature (base64)
            key_id: Signing key ID
            version: Artifact version
            description: Artifact description
            created_by: Creator identifier
            created_at: Creation timestamp
            content_hash: BLAKE2b hash of content
            body_hash: Body hash from signature payload
            signature_valid: Whether signature is valid
            expires_at: Signature expiration
            signature_log: List of signature audit entries
            checksum: Overall BLAKE2b checksum

        Returns:
            Rendered markdown string
        """
        now = created_at or datetime.now(timezone.utc)

        if content_hash is None:
            content_hash = hashlib.blake2b(
                json.dumps(content, sort_keys=True).encode(),
                digest_size=32
            ).hexdigest()

        content_json = json.dumps(content, indent=2, sort_keys=True)

        if signature_log:
            log_lines = ["| Action | Operator | Status | Timestamp |",
                        "|--------|----------|--------|-----------|"]
            for entry in signature_log:
                log_lines.append(
                    f"| {entry.get('action', '-')} | "
                    f"{entry.get('operator', '-')} | "
                    f"{entry.get('status', '-')} | "
                    f"{entry.get('timestamp', '-')} |"
                )
            log_text = "\n".join(log_lines)
        else:
            log_text = "_No audit entries_"

        if checksum is None:
            checksum_data = {
                "name": name,
                "version": version,
                "content_hash": content_hash,
                "signature": signature,
            }
            checksum = hashlib.blake2b(
                json.dumps(checksum_data, sort_keys=True).encode(),
                digest_size=32
            ).hexdigest()

        ctx = {
            "artifact_name": name,
            "artifact_version": str(version),
            "artifact_description": description,
            "created_at": now.isoformat(),
            "created_by": created_by,
            "key_id": key_id,
            "signature": signature,
            "artifact_content": content_json,
            "content_hash": content_hash,
            "body_hash": body_hash or "-",
            "signature_valid": "✅ Yes" if signature_valid else "❌ No",
            "expires_at": expires_at.isoformat() if expires_at else "Never",
            "signature_log": log_text,
            "checksum": checksum,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

        return _render_template_string(self.template, ctx)

    def render_from_artifact(
        self,
        artifact: Any,
        signature_logs: Optional[List[Any]] = None,
    ) -> str:
        """
        Render template from Artifact database model.

        Args:
            artifact: Artifact model instance
            signature_logs: Optional list of ArtifactSignatureLog entries

        Returns:
            Rendered markdown string
        """
        log_dicts = None
        if signature_logs:
            log_dicts = [
                {
                    "action": log.action,
                    "operator": log.operator,
                    "status": log.verification_status,
                    "timestamp": log.created_at.isoformat() if hasattr(log, 'created_at') else "-",
                }
                for log in signature_logs
            ]

        return self.render(
            name=artifact.name,
            content=artifact.content,
            signature=artifact.signature,
            key_id=artifact.key_id,
            version=artifact.version,
            description=getattr(artifact, 'description', ''),
            created_by=artifact.created_by,
            created_at=artifact.created_at,
            content_hash=artifact.content_hash,
            body_hash=getattr(artifact, 'body_hash', ''),
            signature_valid=artifact.signature_valid,
            expires_at=getattr(artifact, 'signature_expires_at', None),
            signature_log=log_dicts,
        )

    def save(
        self,
        output_path: str,
        **render_kwargs
    ) -> Path:
        """
        Render and save artifact to file.

        Args:
            output_path: Output file path
            **render_kwargs: Arguments for render()

        Returns:
            Path to saved file
        """
        rendered = self.render(**render_kwargs)
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered)
        return path


def render_artifact(
    name: str,
    content: Dict[str, Any],
    signature: str,
    **kwargs
) -> str:
    """
    Render artifact template.

    Args:
        name: Artifact name
        content: Artifact content
        signature: Ed25519 signature
        **kwargs: Additional render arguments

    Returns:
        Rendered markdown
    """
    renderer = ArtifactTemplateRenderer()
    return renderer.render(name=name, content=content, signature=signature, **kwargs)
