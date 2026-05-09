"""Marketplace seeder — seeds DB from remote index on first startup."""

from css.core.logger import getLogger
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path

import aiohttp

from css.core.config import MARKETPLACE_CONFIG, MARKETPLACE_SEEDER_HTTP_TIMEOUT
from css.core.db.models.marketplace import MarketplaceItem, MarketplaceMeta
from css.core.enums import MarketplaceItemType
from css.core.marketplace.registry import emit_marketplace_item_changed
from .exceptions import MarketplaceSeedingError

log = getLogger(__name__)

# Load URLs from configuration
INDEX_URL = MARKETPLACE_CONFIG['index_url']
INDEX_SHA512_URL = MARKETPLACE_CONFIG['index_hash_url']
MARKETPLACE_BASE_URL = MARKETPLACE_CONFIG['base_url']


class MarketplaceSeeder:
    """Seeds marketplace items from remote index."""

    def __init__(self, base_url: str | None = None):
        """Initialize seeder.

        Args:
            base_url: Override base URL for marketplace items (default: MARKETPLACE_BASE_URL)
        """
        self.base_url = base_url or MARKETPLACE_BASE_URL
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession | None:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=MARKETPLACE_SEEDER_HTTP_TIMEOUT))
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def fetch_index(self) -> dict:
        """Fetch the marketplace index from remote.

        Returns:
            Parsed JSON index

        Raises:
            MarketplaceSeedingError: If fetch fails
        """
        try:
            session = await self._get_session()
            async with session.get(INDEX_URL) as resp:
                resp.raise_for_status()
                return await resp.json()
        except Exception as e:
            raise MarketplaceSeedingError(
                message=f"Failed to fetch index: {e}",
                context={"url": INDEX_URL, "error": str(e)},
            )

    async def fetch_index_hash(self) -> str:
        """Fetch the expected SHA512 hash of the index.

        Returns:
            SHA512 hash as hex string

        Raises:
            MarketplaceSeedingError: If fetch fails
        """
        try:
            session = await self._get_session()
            async with session.get(INDEX_SHA512_URL) as resp:
                resp.raise_for_status()
                return (await resp.text()).strip()
        except Exception as e:
            raise MarketplaceSeedingError(
                message=f"Failed to fetch index hash: {e}",
                context={"url": INDEX_SHA512_URL, "error": str(e)},
            )

    async def verify_index(self, index_data: dict, expected_hash: str) -> bool:
        """Verify index integrity using SHA512.

        Args:
            index_data: Parsed index JSON
            expected_hash: Expected SHA512 hash

        Returns:
            True if hash matches
        """
        try:
            index_bytes = json.dumps(index_data, sort_keys=True).encode("utf-8")
            actual_hash = hashlib.sha512(index_bytes).hexdigest()
            return actual_hash == expected_hash.strip()
        except Exception as e:
            log.warning(f"Hash verification failed: {e}")
            return False

    def _get_install_path(self, item_kind: MarketplaceItemType, slug: str) -> str:
        install_root = Path(MARKETPLACE_CONFIG["install_root"]).expanduser()
        return str((install_root / item_kind.value / slug).resolve())

    async def _seed_type(
        self,
        seed_items: list[dict],
        item_kind: MarketplaceItemType,
        force: bool,
    ) -> tuple[int, int]:
        created = 0
        skipped = 0

        for seed_item in seed_items:
            try:
                item_id = seed_item.get("name", "")
                if not item_id:
                    skipped += 1
                    continue

                existing = await MarketplaceItem.get_or_none(slug=item_id)
                if existing and not force:
                    skipped += 1
                    continue

                file_path = seed_item.get("file", "")
                source_url = f"{self.base_url}/{file_path}" if file_path else ""
                install_path = self._get_install_path(item_kind=item_kind, slug=item_id)
                description = seed_item.get("description", "")

                meta = {
                    "file": file_path,
                    "sha512": seed_item.get("sha512", ""),
                    "tags": seed_item.get("tags", []),
                }

                if existing:
                    existing.name = (description or item_id)[:255]
                    existing.description = description
                    existing.source_url = source_url
                    existing.install_path = install_path
                    existing.meta = {**(existing.meta or {}), **meta}
                    await existing.save()
                    await emit_marketplace_item_changed(item_slug=existing.slug, operation="updated")
                else:
                    created_item = await MarketplaceItem.create(
                        slug=item_id,
                        name=(description or item_id)[:255],
                        description=description,
                        kind=item_kind,
                        source_url=source_url,
                        install_path=install_path,
                        meta=meta,
                    )
                    await emit_marketplace_item_changed(item_slug=created_item.slug, operation="updated")
                created += 1
            except Exception as e:
                log.error(f"Failed to seed {item_kind.value} item {seed_item.get('name', 'unknown')}: {e}")
                skipped += 1

        return created, skipped

    async def seed_if_empty(self, force: bool = False) -> tuple[int, int]:
        """Seed marketplace if DB is empty (or if force=True).

        Args:
            force: If True, reseed even if items exist

        Returns:
            Tuple of (created_count, skipped_count)

        Raises:
            MarketplaceSeedingError: If seeding fails
        """
        existing_count = await MarketplaceItem.all().count()

        if existing_count > 0 and not force:
            log.info(f"Marketplace already has {existing_count} items, skipping seed")
            return 0, 0

        if force:
            log.info("Force seeding marketplace...")
        else:
            log.info("Marketplace is empty, seeding from remote index...")

        # Fetch and verify index
        index_data = await self.fetch_index()
        expected_hash = await self.fetch_index_hash()

        if not await self.verify_index(index_data, expected_hash):
            log.warning("Index hash verification failed, proceeding anyway...")

        created = 0
        skipped = 0

        type_key_map: list[tuple[str, MarketplaceItemType]] = [
            ("agents", MarketplaceItemType.agent),
            ("skills", MarketplaceItemType.skill),
            ("workflows", MarketplaceItemType.workflow),
            ("prompts", MarketplaceItemType.prompt),
            ("templates", MarketplaceItemType.template),
            ("mcps", MarketplaceItemType.mcp),
        ]
        for index_key, item_kind in type_key_map:
            seed_items = index_data.get(index_key, [])
            if not isinstance(seed_items, list):
                continue
            type_created, type_skipped = await self._seed_type(
                seed_items=seed_items,
                item_kind=item_kind,
                force=force,
            )
            created += type_created
            skipped += type_skipped

        log.info(f"Seeding complete: created={created}, skipped={skipped}")
        return (created, skipped)

    async def check_for_updates(self) -> str | None:
        """Check if remote index has been updated.

        Returns:
            New version string if update available, None otherwise
        """
        try:
            index_data = await self.fetch_index()
            remote_hash = await self.fetch_index_hash()
            local_items = await MarketplaceItem.all().order_by("slug").values(
                "slug", "version", "sha512", "meta", "updated_at",
            )
            local_hash = hashlib.sha512(
                json.dumps(local_items, sort_keys=True, default=str).encode("utf-8"),
            ).hexdigest()

            meta, _ = await MarketplaceMeta.get_or_create(
                id=1,
                defaults={
                    "name": "default",
                    "description": "Marketplace metadata",
                    "version": index_data.get("version", "0.1.0"),
                },
            )
            meta.remote_index_hash = remote_hash
            meta.local_index_hash = local_hash
            meta.last_index_check = datetime.now(UTC)
            meta.update_available = local_hash != remote_hash
            if index_data.get("version"):
                meta.version = index_data["version"]
            await meta.save()

            return index_data.get("version") if meta.update_available else None
        except Exception as e:
            log.error(f"Failed to check for updates: {e}")
            return None


async def seed_marketplace_on_startup():
    """Convenience function to seed marketplace on startup.

    Usage in manager.py or startup hook:
        from .seeder import seed_marketplace_on_startup
        await seed_marketplace_on_startup()
    """
    async with MarketplaceSeeder() as seeder:
        created, skipped = await seeder.seed_if_empty()
        return {"created": created, "skipped": skipped}
