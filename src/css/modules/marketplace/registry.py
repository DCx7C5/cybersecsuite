"""Registry for marketplace items (DB-backed), adapted to use BaseRegistry."""

from typing import Optional, List

from css.core.types.base import BaseRegistry

from .models import MarketplaceItem
from .enums import MarketplaceItemType, MarketplaceItemStatus
from .exceptions import PackageNotFoundError


class MarketplaceItemRegistry(BaseRegistry['MarketplaceItemRegistry']):
    """Singleton registry for marketplace items backed by Tortoise ORM.

    Inherits from BaseRegistry to provide singleton pattern and standard interface.
    Use MarketplaceItemRegistry.get_instance() to get the singleton.
    """

    def _setup(self) -> None:
        """Setup method called once during first initialization."""
        pass  # No special setup needed for DB-backed registry

    async def register(self, item: MarketplaceItem) -> MarketplaceItem:
        """Register (save) a marketplace item.

        Implements BaseRegistry.register().

        Args:
            item: The MarketplaceItem to register

        Returns:
            The saved MarketplaceItem instance
        """
        await item.save()
        return item

    async def unregister(self, item_id: str) -> None:
        """Unregister (delete) a marketplace item.

        Implements BaseRegistry.unregister().

        Args:
            item_id: The ID of the item to unregister

        Raises:
            PackageNotFoundError: If item not found
        """
        item = await MarketplaceItem.get_or_none(slug=item_id)
        if not item:
            raise PackageNotFoundError(item_id=item_id)
        await item.delete()

    async def get(self, item_id: str) -> Optional[MarketplaceItem]:
        """Get a marketplace item by ID.

        Implements BaseRegistry.get().

        Args:
            item_id: The ID of the item to retrieve

        Returns:
            MarketplaceItem instance or None if not found
        """
        return await MarketplaceItem.get_or_none(slug=item_id)

    async def list_all(
        self,
        kind: Optional[MarketplaceItemType] = None,
        status: Optional[MarketplaceItemStatus] = None,
        installed_only: bool = False,
    ) -> List[MarketplaceItem]:
        """List all marketplace items with optional filtering.

        Implements BaseRegistry.list_all().

        Args:
            kind: Filter by item type (agent, skill, etc.)
            status: Filter by status
            installed_only: Only return installed items

        Returns:
            List of MarketplaceItem instances
        """
        query = MarketplaceItem.all()

        if kind:
            query = query.filter(kind=kind)
        if status:
            query = query.filter(status=status)
        if installed_only:
            query = query.filter(installed_at__isnull=False)

        return await query.all()

    # Convenience methods that wrap the base interface

    async def get_item(self, item_id: str) -> Optional[MarketplaceItem]:
        """Get a marketplace item by ID (convenience wrapper)."""
        return await self.get(item_id)

    async def list_items(
        self,
        kind: Optional[MarketplaceItemType] = None,
        status: Optional[MarketplaceItemStatus] = None,
        installed_only: bool = False,
    ) -> List[MarketplaceItem]:
        """List marketplace items with optional filtering (convenience wrapper)."""
        return await self.list_all(kind=kind, status=status, installed_only=installed_only)

    async def list_installed(self) -> List[MarketplaceItem]:
        """List all installed marketplace items."""
        return await self.list_all(installed_only=True)

    async def list_by_kind(self, kind: MarketplaceItemType) -> List[MarketplaceItem]:
        """List all items of a specific kind."""
        return await self.list_all(kind=kind)

    async def update_item_status(
        self, item_id: str, status: MarketplaceItemStatus
    ) -> MarketplaceItem:
        """Update the status of a marketplace item.

        Args:
            item_id: The ID of the item to update
            status: The new status

        Returns:
            The updated MarketplaceItem instance

        Raises:
            PackageNotFoundError: If item not found
        """
        item = await self.get(item_id)
        if not item:
            raise PackageNotFoundError(item_id=item_id)

        item.status = status
        await item.save()
        return item
