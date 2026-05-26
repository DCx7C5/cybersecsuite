"""Marketplace package installation and uninstallation."""

import asyncio
from datetime import UTC, datetime
import hashlib
import io
from pathlib import Path
import shutil
import tarfile
import zipfile

import aiohttp


from css.core.db.models.marketplace import MarketplaceItem
from css.core.enums import MarketplaceItemStatus

from .cache import marketplace_cache
from .registry import emit_marketplace_item_changed
from ..settings.config import MARKETPLACE_CONFIG


class InstallationResult:
    """Result of a package installation operation."""

    def __init__(
        self,
        success: bool,
        item_id: str | None = None,
        install_path: str | None = None,
        error: str | None = None,
    ):
        self.success = success
        self.item_id = item_id
        self.install_path = install_path
        self.error = error


class PackageInstaller:
    """Installs marketplace items using Tortoise ORM."""

    def __init__(self) -> None:
        self._install_root = Path(MARKETPLACE_CONFIG["install_root"]).expanduser()
        self._download_timeout = int(MARKETPLACE_CONFIG["download_timeout"])

    def _get_item_target_dir(self, item: MarketplaceItem) -> Path:
        kind_dir = str(item.kind.value if hasattr(item.kind, "value") else item.kind)
        return self._install_root / kind_dir / item.slug

    async def _download_package(self, source_url: str) -> bytes:
        timeout = aiohttp.ClientTimeout(total=self._download_timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(source_url) as response:
                response.raise_for_status()
                return await response.read()

    @staticmethod
    def _verify_sha512(payload: bytes, expected_sha512: str) -> bool:
        if not expected_sha512:
            return True
        return hashlib.sha512(payload).hexdigest().lower() == expected_sha512.strip().lower()

    @staticmethod
    def _is_within_directory(base_dir: Path, target: Path) -> bool:
        try:
            target.resolve().relative_to(base_dir.resolve())
            return True
        except ValueError:
            return False

    def _safe_extract_zip(self, payload: bytes, target_dir: Path) -> None:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            for member in archive.namelist():
                member_path = target_dir / member
                if not self._is_within_directory(target_dir, member_path):
                    raise ValueError(f"Unsafe zip path detected: {member}")
            archive.extractall(target_dir)

    def _safe_extract_tar(self, payload: bytes, target_dir: Path, mode: str) -> None:
        with tarfile.open(fileobj=io.BytesIO(payload), mode=mode) as archive:
            for member in archive.getmembers():
                member_path = target_dir / member.name
                if not self._is_within_directory(target_dir, member_path):
                    raise ValueError(f"Unsafe tar path detected: {member.name}")
            archive.extractall(target_dir)

    def _write_payload(self, item: MarketplaceItem, payload: bytes, target_dir: Path) -> Path:
        source_url = item.source_url or ""
        lower_url = source_url.lower()

        if lower_url.endswith(".zip"):
            self._safe_extract_zip(payload, target_dir)
            return target_dir
        if lower_url.endswith((".tar.gz", ".tgz")):
            self._safe_extract_tar(payload, target_dir, "r:gz")
            return target_dir
        if lower_url.endswith(".tar"):
            self._safe_extract_tar(payload, target_dir, "r:")
            return target_dir

        artifact_name = Path(source_url).name or f"{item.slug}.pkg"
        artifact_path = target_dir / artifact_name
        artifact_path.write_bytes(payload)
        return artifact_path

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
                success=True,
                item_id=item_id,
                install_path=item.install_path,
            )

        if not item.source_url:
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=f"Missing source_url for package: {item_id}",
            )

        target_dir = self._get_item_target_dir(item)
        if force and target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)

        try:
            payload = await self._download_package(item.source_url)

            expected_sha512 = item.sha512 or (item.meta.get("sha512") if item.meta else "")
            if not self._verify_sha512(payload, expected_sha512):
                return InstallationResult(
                    success=False,
                    item_id=item_id,
                    error=f"Checksum verification failed for package: {item_id}",
                )

            installed_path = self._write_payload(item=item, payload=payload, target_dir=target_dir)

            item.install_path = str(installed_path)
            item.installed_at = datetime.now(UTC)
            item.status = MarketplaceItemStatus.installed
            await item.save()
            await emit_marketplace_item_changed(item_slug=item.slug, operation="install")

            marketplace_cache.invalidate(f"item:{item.slug}")
            marketplace_cache.invalidate_prefix("items:")

            return InstallationResult(
                success=True,
                item_id=item_id,
                install_path=item.install_path,
            )
        except Exception as exc:
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=f"Installation failed for {item_id}: {exc}",
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

        try:
            if item.install_path:
                installed_path = Path(item.install_path).expanduser()
                if installed_path.exists():
                    if installed_path.is_dir():
                        shutil.rmtree(installed_path)
                    else:
                        installed_path.unlink()

            if purge_config:
                package_dir = self._get_item_target_dir(item)
                if package_dir.exists() and package_dir.is_dir():
                    shutil.rmtree(package_dir)

            item.install_path = None
            item.installed_at = None
            item.status = MarketplaceItemStatus.disabled
            await item.save()
            await emit_marketplace_item_changed(item_slug=item.slug, operation="uninstall")

            marketplace_cache.invalidate(f"item:{item.slug}")
            marketplace_cache.invalidate_prefix("items:")

            return InstallationResult(
                success=True,
                item_id=item_id,
            )
        except Exception as exc:
            return InstallationResult(
                success=False,
                item_id=item_id,
                error=f"Uninstallation failed for {item_id}: {exc}",
            )

    async def install_multiple(
        self,
        item_ids: list[str],
        force: bool = False,
        max_parallel: int = 3,
    ) -> dict[str, InstallationResult]:
        """Install multiple packages with bounded parallelism."""
        semaphore = asyncio.Semaphore(max_parallel)
        results: dict[str, InstallationResult] = {}

        async def _install_one(item_id: str) -> None:
            async with semaphore:
                results[item_id] = await self.install_package(item_id=item_id, force=force)

        await asyncio.gather(*(_install_one(item_id) for item_id in item_ids))
        return results
