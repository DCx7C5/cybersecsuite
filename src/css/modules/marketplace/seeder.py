"""Marketplace seeder — seeds DB from remote index on first startup."""

import hashlib
import json
import logging
from typing import Optional

import aiohttp

from css.core.config import MarketplaceConfig
from .enums import MarketplaceItemType
from .models import MarketplaceItem
from .exceptions import MarketplaceSeedingError

log = logging.getLogger(__name__)

INDEX_URL = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json"
INDEX_SHA512_URL = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json.sha512"
MARKETPLACE_BASE_URL = "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main"


class MarketplaceSeeder:
    """Seeds marketplace items from remote index."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize seeder.

        Args:
            base_url: Override base URL for marketplace items (default: MARKETPLACE_BASE_URL)
        """
        self.base_url = base_url or MARKETPLACE_BASE_URL
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=MarketplaceConfig.SEEDER_HTTP_TIMEOUT))
        return self._session

    async def close(self):
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
            return (0, 0)

        if force:
            log.info("Force seeding marketplace...")
        else:
            log.info("Marketplace is empty, seeding from remote index...")

        # Fetch and verify index
        index_data = await self.fetch_index()
        expected_hash = await self.fetch_index_hash()

        if not await self.verify_index(index_data, expected_hash):
            log.warning("Index hash verification failed, proceeding anyway...")

        agents = index_data.get("agents", [])
        created = 0
        skipped = 0

        for agent in agents:
            try:
                item_id = agent.get("name", "")
                if not item_id:
                    skipped += 1
                    continue

                # Check if item already exists
                existing = await MarketplaceItem.get_or_none(slug=item_id)
                if existing and not force:
                    skipped += 1
                    continue

                # Build source URL from file path
                file_path = agent.get("file", "")
                source_url = f"{self.base_url}/{file_path}" if file_path else ""

                # Create or update item
                if existing:
                    existing.name = agent.get("description", item_id)[:255]
                    existing.description = agent.get("description", "")
                    existing.source_url = source_url
                    existing.meta = {
                        "file": file_path,
                        "sha512": agent.get("sha512", ""),
                    }
                    await existing.save()
                else:
                    await MarketplaceItem.create(
                        slug=item_id,
                        name=agent.get("description", item_id)[:255],
                        description=agent.get("description", ""),
                        kind=MarketplaceItemType.agent,
                        source_url=source_url,
                        meta={
                            "file": file_path,
                            "sha512": agent.get("sha512", ""),
                        },
                    )
                created += 1

            except Exception as e:
                log.error(f"Failed to seed item {agent.get('name', 'unknown')}: {e}")
                skipped += 1

        log.info(f"Seeding complete: created={created}, skipped={skipped}")
        return (created, skipped)

    async def check_for_updates(self) -> Optional[str]:
        """Check if remote index has been updated.

        Returns:
            New version string if update available, None otherwise
        """
        try:
            index_data = await self.fetch_index()
            return index_data.get("version", None)
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
