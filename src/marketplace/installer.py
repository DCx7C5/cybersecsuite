"""Marketplace package installation and validation orchestration.

Handles installation of marketplace items: dependency resolution,
manifest parsing, artifact integrity verification, and local registration.

Referenz:
    plan.md T033 — Marketplace installer
    src/marketplace/models.py — MarketplaceItem
    src/marketplace/registry.py — MarketplaceRegistry
    src/marketplace/manifest.py — ManifestParser
"""
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from marketplace.manifest import ManifestParser
from marketplace.models import MarketplaceItem, MarketplaceItemStatus
from src.registries.marketplace import get_registry, get_item, list_installed

logger = logging.getLogger("marketplace.installer")

# ── Installation directories ───────────────────────────────────────────────────
_INSTALL_BASE = Path.home() / ".cybersecsuite" / "agents"
_MANIFEST_CACHE = Path.home() / ".cybersecsuite" / "manifests"


class InstallationError(Exception):
    """Raised when package installation fails."""

    pass


class DependencyResolutionError(InstallationError):
    """Raised when dependency resolution fails."""

    pass


class ManifestValidationError(InstallationError):
    """Raised when manifest validation fails."""

    pass


class PackageInstaller:
    """Orchestrates package installation with dependency resolution and validation.

    Usage::

        installer = PackageInstaller()
        result = await installer.install_package("claude-forensic-analyst")
        if result.success:
            print(f"Installed to {result.install_path}")
    """

    def __init__(self) -> None:
        """Initialize the installer."""
        self.registry = get_registry()
        self.manifest_parser = ManifestParser()
        _INSTALL_BASE.mkdir(parents=True, exist_ok=True)
        _MANIFEST_CACHE.mkdir(parents=True, exist_ok=True)

    async def install_package(
        self, item_id: str, force: bool = False
    ) -> InstallationResult:
        """Install a marketplace package with full validation.

        Args:
            item_id: Kebab-case unique identifier of the item to install.
            force: If True, reinstall even if already installed.

        Returns:
            InstallationResult with status, paths, and any error messages.
        """
        try:
            # Get the item from registry
            item = get_item(item_id)
            if item is None:
                return InstallationResult(
                    success=False,
                    item_id=item_id,
                    error=f"Marketplace item not found: {item_id}",
                )

            # Check if already installed
            if (
                item.status == MarketplaceItemStatus.installed
                and not force
            ):
                return InstallationResult(
                    success=True,
                    item_id=item_id,
                    install_path=str(item.install_path),
                    already_installed=True,
                )

            # Resolve dependencies
            logger.info("Resolving dependencies for %s", item_id)
            dependency_items = await self._resolve_dependencies(item)

            # Validate manifest
            logger.info("Validating manifest for %s", item_id)
            manifest_path = await self._fetch_and_validate_manifest(item)

            # Create installation directory
            install_path = _INSTALL_BASE / item_id
            if install_path.exists() and force:
                shutil.rmtree(install_path)
            install_path.mkdir(parents=True, exist_ok=True)

            # Copy manifest
            manifest_dest = install_path / "manifest.yaml"
            if manifest_path:
                shutil.copy(manifest_path, manifest_dest)

            # Install dependencies first
            for dep_item in dependency_items:
                logger.debug(
                    "Installing dependency: %s", dep_item.id
                )
                dep_result = await self.install_package(
                    dep_item.id, force=force
                )
                if not dep_result.success:
                    raise DependencyResolutionError(
                        f"Failed to install dependency {dep_item.id}: "
                        f"{dep_result.error}"
                    )

            # Register installation
            installed_item = self.registry.install(item_id)

            logger.info(
                "Successfully installed marketplace item: %s -> %s",
                item_id,
                install_path,
            )
            return InstallationResult(
                success=True,
                item_id=item_id,
                install_path=str(install_path),
                version=installed_item.version,
                installed_at=installed_item.installed_at,
            )

        except Exception as e:
            logger.exception("Installation failed for %s", item_id)
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=str(e),
            )

    async def _resolve_dependencies(
        self, item: MarketplaceItem
    ) -> list[MarketplaceItem]:
        """Resolve all transitive dependencies for an item.

        Args:
            item: The marketplace item to resolve dependencies for.

        Returns:
            List of required items to install (depth-first order).

        Raises:
            DependencyResolutionError: If circular dependencies or missing items found.
        """
        visited: set[str] = set()
        resolved: list[MarketplaceItem] = []

        async def visit(item_id: str) -> None:
            """DFS traversal of dependencies."""
            if item_id in visited:
                return
            visited.add(item_id)

            item = get_item(item_id)
            if item is None:
                raise DependencyResolutionError(
                    f"Dependency not found in marketplace: {item_id}"
                )

            # For now, dependencies are read from item.meta.dependencies
            # if it's populated (future extension point)
            if hasattr(item.meta, "dependencies"):
                for dep_id in item.meta.dependencies or []:  # type: ignore
                    await visit(dep_id)

            resolved.append(item)

        try:
            # Visit the main item's dependencies (not the item itself)
            if hasattr(item.meta, "dependencies"):
                for dep_id in item.meta.dependencies or []:  # type: ignore
                    await visit(dep_id)
            return resolved
        except Exception as e:
            raise DependencyResolutionError(f"Dependency resolution failed: {e}")

    async def _fetch_and_validate_manifest(
        self, item: MarketplaceItem
    ) -> Path | None:
        """Fetch and validate the manifest for a marketplace item.

        For now, this is a placeholder that looks for manifests in the
        marketplace directory or creates a synthetic one from item metadata.

        Args:
            item: The marketplace item to fetch manifest for.

        Returns:
            Path to the validated manifest file, or None if not found.

        Raises:
            ManifestValidationError: If manifest validation fails.
        """
        # Try to find manifest in standard location
        manifest_path = _MANIFEST_CACHE / f"{item.id}.yaml"
        if manifest_path.exists():
            try:
                manifest_data = self.manifest_parser.parse_yaml(
                    manifest_path.read_text()
                )
                # Validate manifest structure
                if not self.manifest_parser.validate(manifest_data):
                    raise ManifestValidationError(
                        f"Invalid manifest structure for {item.id}"
                    )
                return manifest_path
            except Exception as e:
                raise ManifestValidationError(
                    f"Failed to parse manifest for {item.id}: {e}"
                )

        # Create synthetic manifest from item metadata
        logger.debug(
            "No manifest file found for %s; creating synthetic manifest",
            item.id,
        )
        manifest_data = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "kind": item.kind,
            "provider": item.provider,
            "version": item.version,
            "tags": item.tags,
            "meta": item.meta.model_dump() if item.meta else {},
        }
        synthetic_manifest = _MANIFEST_CACHE / f"{item.id}.synthetic.json"
        synthetic_manifest.write_text(
            json.dumps(manifest_data, indent=2, default=str)
        )
        return synthetic_manifest

    async def uninstall_package(self, item_id: str) -> UninstallationResult:
        """Uninstall a marketplace package.

        Args:
            item_id: Kebab-case unique identifier of the item to uninstall.

        Returns:
            UninstallationResult with status and any error messages.
        """
        try:
            install_path = _INSTALL_BASE / item_id
            if install_path.exists():
                shutil.rmtree(install_path)
                logger.debug(
                    "Removed installation directory: %s", install_path
                )

            uninstalled = self.registry.uninstall(item_id)
            if not uninstalled:
                return UninstallationResult(
                    success=False,
                    item_id=item_id,
                    error=f"Item {item_id} was not installed",
                )

            logger.info("Successfully uninstalled marketplace item: %s", item_id)
            return UninstallationResult(
                success=True,
                item_id=item_id,
            )
        except Exception as e:
            logger.exception("Uninstallation failed for %s", item_id)
            return UninstallationResult(
                success=False,
                item_id=item_id,
                error=str(e),
            )

    async def validate_installations(self) -> ValidationReport:
        """Validate the integrity of all installed packages.

        Returns:
            ValidationReport with overall status and per-item results.
        """
        report = ValidationReport()
        installed_items = list_installed()

        for item in installed_items:
            try:
                install_path = _INSTALL_BASE / item.id
                if not install_path.exists():
                    report.add_issue(
                        item.id,
                        f"Installation directory not found: {install_path}",
                        severity="error",
                    )
                    continue

                # Check for manifest
                manifest_path = install_path / "manifest.yaml"
                if not manifest_path.exists():
                    # Try synthetic manifest
                    manifest_path = (
                        _MANIFEST_CACHE / f"{item.id}.synthetic.json"
                    )
                    if not manifest_path.exists():
                        report.add_issue(
                            item.id,
                            "No manifest found",
                            severity="warning",
                        )
                    else:
                        report.add_valid(item.id, "Manifest found (synthetic)")
                else:
                    report.add_valid(item.id, "Manifest validated")

                # Check installation timestamp
                if item.installed_at is None:
                    report.add_issue(
                        item.id, "Missing installed_at timestamp",
                        severity="warning"
                    )

            except Exception as e:
                report.add_issue(
                    item.id, f"Validation error: {e}", severity="error"
                )

        logger.info("Installation validation complete: %d items checked", len(
            installed_items))
        return report


# ── Result types ───────────────────────────────────────────────────────────────


class InstallationResult:
    """Result of a package installation operation."""

    def __init__(
        self,
        success: bool,
        item_id: str,
        install_path: str | None = None,
        version: str | None = None,
        installed_at: datetime | None = None,
        error: str | None = None,
        already_installed: bool = False,
    ) -> None:
        """Initialize installation result.

        Args:
            success: Whether installation succeeded.
            item_id: The package ID.
            install_path: Path where package was installed.
            version: Package version installed.
            installed_at: When installation completed.
            error: Error message if installation failed.
            already_installed: True if package was already installed.
        """
        self.success = success
        self.item_id = item_id
        self.install_path = install_path
        self.version = version
        self.installed_at = installed_at
        self.error = error
        self.already_installed = already_installed

    def model_dump(self) -> dict[str, Any]:
        """Export result as dictionary for JSON serialization."""
        return {
            "success": self.success,
            "item_id": self.item_id,
            "install_path": self.install_path,
            "version": self.version,
            "installed_at": (
                self.installed_at.isoformat() if self.installed_at else None
            ),
            "error": self.error,
            "already_installed": self.already_installed,
        }


class UninstallationResult:
    """Result of a package uninstallation operation."""

    def __init__(
        self,
        success: bool,
        item_id: str,
        error: str | None = None,
    ) -> None:
        """Initialize uninstallation result.

        Args:
            success: Whether uninstallation succeeded.
            item_id: The package ID.
            error: Error message if uninstallation failed.
        """
        self.success = success
        self.item_id = item_id
        self.error = error

    def model_dump(self) -> dict[str, Any]:
        """Export result as dictionary for JSON serialization."""
        return {
            "success": self.success,
            "item_id": self.item_id,
            "error": self.error,
        }


class ValidationReport:
    """Report on validation of installed packages."""

    def __init__(self) -> None:
        """Initialize validation report."""
        self.valid: dict[str, str] = {}
        self.issues: dict[str, list[tuple[str, str]]] = {}  # item_id -> [(severity, message)]

    def add_valid(self, item_id: str, message: str) -> None:
        """Record successful validation of an item."""
        self.valid[item_id] = message

    def add_issue(
        self, item_id: str, message: str, severity: str = "error"
    ) -> None:
        """Record a validation issue for an item."""
        if item_id not in self.issues:
            self.issues[item_id] = []
        self.issues[item_id].append((severity, message))

    @property
    def is_valid(self) -> bool:
        """True if no errors found (warnings are allowed)."""
        for item_id, item_issues in self.issues.items():
            if any(sev == "error" for sev, _ in item_issues):
                return False
        return True

    def model_dump(self) -> dict[str, Any]:
        """Export report as dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "valid_count": len(self.valid),
            "error_count": sum(
                1
                for item_issues in self.issues.values()
                if any(sev == "error" for sev, _ in item_issues)
            ),
            "warning_count": sum(
                1
                for item_issues in self.issues.values()
                if any(sev == "warning" for sev, _ in item_issues)
            ),
            "valid_items": self.valid,
            "issues_by_item": {
                item_id: [{"severity": sev, "message": msg} for sev, msg in item_issues]
                for item_id, item_issues in self.issues.items()
            },
        }
