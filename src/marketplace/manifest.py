"""Marketplace manifest parser — YAML/JSON manifest handling.

Parses agent/skill manifests in both YAML and JSON formats, validates
structure, and extracts provider-specific frontmatter and metadata.

Referenz:
    plan.md T033 — Marketplace manifest parser
    src/marketplace/models.py — ProviderMeta
    src/marketplace/installer.py — ManifestParser usage
"""


import json
import logging
from typing import Any

try:
    import yaml

    HAS_YAML = True
except ImportError:
    yaml = None
    HAS_YAML = False

logger = logging.getLogger("marketplace.manifest")


class ManifestParser:
    """Parse and validate marketplace item manifests (YAML/JSON).

    Supports both YAML and JSON manifest formats. Extracts structured
    metadata for provider integration.

    Usage::

        parser = ManifestParser()
        data = parser.parse_yaml(yaml_content)
        if parser.validate(data):
            print(f"Valid manifest: {data['id']}")
    """

    def __init__(self) -> None:
        """Initialize the manifest parser."""
        if not HAS_YAML:
            logger.warning("PyYAML not installed; YAML parsing will fail")

    def parse_yaml(self, content: str) -> dict[str, Any]:
        """Parse YAML manifest content.

        Args:
            content: YAML string content.

        Returns:
            Parsed manifest as dictionary.

        Raises:
            ValueError: If YAML parsing fails or PyYAML not available.
        """
        if not HAS_YAML:
            raise ValueError("PyYAML is required to parse YAML manifests")

        try:
            data = yaml.safe_load(content)
            if not isinstance(data, dict):
                raise ValueError("YAML content must be a dictionary")
            return data
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML manifest: {e}")

    def parse_json(self, content: str) -> dict[str, Any]:
        """Parse JSON manifest content.

        Args:
            content: JSON string content.

        Returns:
            Parsed manifest as dictionary.

        Raises:
            ValueError: If JSON parsing fails.
        """
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                raise ValueError("JSON content must be a dictionary")
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON manifest: {e}")

    def parse(self, content: str, format: str = "auto") -> dict[str, Any]:
        """Auto-detect and parse manifest content.

        Args:
            content: Manifest string content.
            format: "auto" (detect), "yaml", or "json".

        Returns:
            Parsed manifest as dictionary.

        Raises:
            ValueError: If format not supported or parsing fails.
        """
        if format == "auto":
            # Try to detect format by content
            content_stripped = content.strip()
            if content_stripped.startswith("{"):
                return self.parse_json(content)
            else:
                return self.parse_yaml(content)
        elif format == "yaml":
            return self.parse_yaml(content)
        elif format == "json":
            return self.parse_json(content)
        else:
            raise ValueError(f"Unknown manifest format: {format}")

    def validate(self, manifest: dict[str, Any]) -> bool:
        """Validate manifest structure against schema.

        Checks for required fields and valid value types.

        Args:
            manifest: Parsed manifest dictionary.

        Returns:
            True if manifest is valid.
        """
        required_fields = {"id", "name", "description", "kind"}
        if not all(field in manifest for field in required_fields):
            missing = required_fields - set(manifest.keys())
            logger.warning("Manifest missing required fields: %s", missing)
            return False

        # Validate field types
        if not isinstance(manifest.get("id"), str):
            logger.warning("Manifest 'id' must be string")
            return False
        if not isinstance(manifest.get("name"), str):
            logger.warning("Manifest 'name' must be string")
            return False
        if not isinstance(manifest.get("description"), str):
            logger.warning("Manifest 'description' must be string")
            return False

        # Validate kind is one of expected values
        valid_kinds = {"agent", "skill", "combo", "template"}
        if manifest.get("kind") not in valid_kinds:
            logger.warning(
                "Manifest 'kind' must be one of: %s", valid_kinds
            )
            return False

        # Validate provider if present
        if "provider" in manifest:
            valid_providers = {
                "claude",
                "copilot",
                "cursor",
                "openai",
                "gemini",
                "grok",
                "universal",
            }
            if manifest.get("provider") not in valid_providers:
                logger.warning(
                    "Manifest 'provider' must be one of: %s",
                    valid_providers,
                )
                return False

        # Validate version format if present
        if "version" in manifest:
            if not isinstance(manifest.get("version"), str):
                logger.warning("Manifest 'version' must be string")
                return False
            # Basic semver check
            if not self._is_valid_version(manifest.get("version")):
                logger.warning(
                    "Manifest 'version' appears invalid: %s",
                    manifest.get("version"),
                )

        # Validate tags if present
        if "tags" in manifest:
            if not isinstance(manifest.get("tags"), list):
                logger.warning("Manifest 'tags' must be list")
                return False

        # Validate meta if present
        if "meta" in manifest:
            if not isinstance(manifest.get("meta"), dict):
                logger.warning("Manifest 'meta' must be dictionary")
                return False

        return True

    @staticmethod
    def _is_valid_version(version: str) -> bool:
        """Check if version string looks like semver.

        Args:
            version: Version string to check.

        Returns:
            True if version appears to be valid semver.
        """
        parts = version.split(".")
        if len(parts) < 3:
            return False
        try:
            for part in parts[:3]:
                int(part.split("-")[0])  # Handle pre-release
            return True
        except (ValueError, AttributeError):
            return False

    def extract_frontmatter(self, manifest: dict[str, Any]) -> dict[str, Any]:
        """Extract provider-specific frontmatter from manifest.

        Returns structured metadata suitable for provider-specific
        agent registration (e.g., SKILL.md, AGENTS.md).

        Args:
            manifest: Parsed manifest dictionary.

        Returns:
            Frontmatter dict with provider-specific fields.
        """
        meta = manifest.get("meta", {})
        return {
            "id": manifest.get("id"),
            "name": manifest.get("name"),
            "description": manifest.get("description"),
            "kind": manifest.get("kind"),
            "provider": manifest.get("provider", "universal"),
            "version": manifest.get("version", "0.1.0"),
            "tags": manifest.get("tags", []),
            "model": meta.get("model"),
            "tools": meta.get("tools", []),
            "max_turns": meta.get("max_turns"),
            "domain": meta.get("domain"),
            "mitre_attack": meta.get("mitre_attack", []),
            "capec": meta.get("capec", []),
            "nist_csf": meta.get("nist_csf", []),
        }

    def merge_manifests(
        self, manifest1: dict[str, Any], manifest2: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge two manifests (for multi-format or override support).

        Later manifest values override earlier ones.

        Args:
            manifest1: Base manifest.
            manifest2: Override manifest.

        Returns:
            Merged manifest dictionary.
        """
        merged = manifest1.copy()
        for key, value in manifest2.items():
            if key == "tags":
                # Merge tags (union)
                existing_tags = set(merged.get("tags", []))
                new_tags = set(value or [])
                merged["tags"] = list(existing_tags | new_tags)
            elif key == "meta" and isinstance(value, dict):
                # Merge meta dicts
                existing_meta = merged.get("meta", {})
                if isinstance(existing_meta, dict):
                    merged["meta"] = {**existing_meta, **value}
                else:
                    merged["meta"] = value
            else:
                # Direct override
                merged[key] = value
        return merged


# ── Manifest templates for common agent types ──────────────────────────────────


AGENT_MANIFEST_TEMPLATE = """id: "{id}"
name: "{name}"
description: "{description}"
kind: "agent"
provider: "{provider}"
version: "0.1.0"
tags:
  - "agent"
  - "cybersecurity"
meta:
  domain: "security"
  tools: []
  mitre_attack: []
  capec: []
  nist_csf: []
"""

SKILL_MANIFEST_TEMPLATE = """id: "{id}"
name: "{name}"
description: "{description}"
kind: "skill"
provider: "{provider}"
version: "0.1.0"
tags:
  - "skill"
  - "utility"
meta:
  tools: []
  domain: null
"""

TEMPLATE_MANIFEST_TEMPLATE = """id: "{id}"
name: "{name}"
description: "{description}"
kind: "template"
provider: "{provider}"
version: "0.1.0"
tags:
  - "template"
meta:
  domain: null
"""


def generate_manifest(
    item_id: str,
    name: str,
    description: str,
    kind: str = "agent",
    provider: str = "universal",
) -> str:
    """Generate a basic manifest for a new marketplace item.

    Args:
        item_id: Kebab-case unique identifier.
        name: Human-readable name.
        description: Item description.
        kind: Type of item (agent, skill, combo, template).
        provider: Target provider.

    Returns:
        YAML manifest string.
    """
    if kind == "agent":
        template = AGENT_MANIFEST_TEMPLATE
    elif kind == "skill":
        template = SKILL_MANIFEST_TEMPLATE
    elif kind == "template":
        template = TEMPLATE_MANIFEST_TEMPLATE
    else:
        template = AGENT_MANIFEST_TEMPLATE

    return template.format(
        id=item_id,
        name=name,
        description=description,
        provider=provider,
    )
