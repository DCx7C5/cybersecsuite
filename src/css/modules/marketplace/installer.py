"""Marketplace package installation — uses models.py for DB operations."""

from typing import Optional

from .models import MarketplaceItem


class InstallationResult:
    """Result of a package installation operation."""

    def __init__(
        self,
        success: bool,
        item_id: Optional[str] = None,
        install_path: Optional[str] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.item_id = item_id
        self.install_path = install_path
        self.error = error


class PackageInstaller:
    """Installs marketplace items using Tortoise ORM."""

    async def install_package(
        self, item_id: str, force: bool = False
    ) -> InstallationResult:
        """Install a marketplace item.

        Args:
            item_id: The ID of the item to install
            force: If True, reinstall even if already installed

        Returns:
            InstallationResult with success status and details
        """
        item = await MarketplaceItem.get_or_none(slug=item_id)
        if not item:
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=f"Package not found: {item_id}",
            )

        if item.installed_at and not force:
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=f"Package already installed: {item_id}",
            )

        # TODO: Implement actual installation logic
        # - Download from source_url
        # - Verify checksums
        # - Extract to install_path
        # - Update DB record

        return InstallationResult(
            success=True,
            item_id=item_id,
            install_path=item.install_path,
        )

    async def uninstall_package(
        self, item_id: str, purge_config: bool = False
    ) -> InstallationResult:
        """Uninstall a marketplace item.

        Args:
            item_id: The ID of the item to uninstall
            purge_config: If True, also remove configuration

        Returns:
            InstallationResult with success status and details
        """
        item = await MarketplaceItem.get_or_none(slug=item_id)
        if not item:
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=f"Package not found: {item_id}",
            )

        # TODO: Implement actual uninstallation logic
        # - Remove installation files
        # - Optionally remove configuration
        # - Update DB record

        return InstallationResult(
            success=True,
            item_id=item_id,
        )
