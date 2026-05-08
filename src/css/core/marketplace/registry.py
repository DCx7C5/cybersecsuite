"""Registry for marketplace items (DB-backed)."""

from css.core.types.meta import AsyncSafeSingletonMeta
from css.core.db.models.marketplace import MarketplaceItem
from css.core.enums import MarketplaceItemStatus, MarketplaceItemType

from .exceptions import PackageNotFoundError


class MarketplaceItemRegistry(metaclass=AsyncSafeSingletonMeta):
    """Read-through cache registry for marketplace items.

    Uses AsyncSafeSingletonMeta for async-safe singleton pattern.
    Reads fall back to PostgreSQL via Tortoise ORM on cache miss.
    Persistence (writes) are handled by the service layer.
    """

    _initialized: bool = False

    def __init__(self) -> None:
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        self._items: dict[str, MarketplaceItem] = {}

    async def _load_all(self) -> None:
        """Load all marketplace items from DB into the in-memory cache."""
        items = await MarketplaceItem.all()
        self._items = {item.slug: item for item in items}

    async def register(self, item: MarketplaceItem) -> MarketplaceItem:
        """Register an item in the in-memory registry.

        Args:
            item: The MarketplaceItem to register

        Returns:
            The registered MarketplaceItem instance
        """
        self._items[item.slug] = item
        return item

    async def unregister(self, item_id: str) -> None:
        """Remove an item from the in-memory registry.

        Args:
            item_id: The slug of the item to unregister

        Raises:
            PackageNotFoundError: If item not found
        """
        if item_id not in self._items:
            raise PackageNotFoundError(item_id=item_id)
        del self._items[item_id]

    async def get(self, item_id: str) -> MarketplaceItem | None:
        """Get a marketplace item by slug — read-through cache.

        Checks in-memory cache first, falls back to DB on miss.

        Args:
            item_id: The slug of the item to retrieve

        Returns:
            MarketplaceItem instance or None if not found
        """
        if item_id in self._items:
            return self._items[item_id]
        item = await MarketplaceItem.get_or_none(slug=item_id)
        if item is not None:
            self._items[item_id] = item
        return item

    async def list_all(
        self,
        kind: MarketplaceItemType | None = None,
        status: MarketplaceItemStatus | None = None,
        installed_only: bool = False,
    ) -> list[MarketplaceItem]:
        """List marketplace items with optional filtering — read-through cache.

        If the in-memory cache is empty, loads all items from DB first.

        Args:
            kind: Filter by item type (agent, skill, etc.)
            status: Filter by status
            installed_only: Only return installed items

        Returns:
            List of MarketplaceItem instances
        """
        if not self._items:
            await self._load_all()
        items = list(self._items.values())

        if kind:
            items = [i for i in items if i.kind == kind]
        if status:
            items = [i for i in items if i.status == status]
        if installed_only:
            items = [i for i in items if i.installed_at is not None]

        return items

    # Convenience methods that wrap the base interface

    async def get_item(self, item_id: str) -> MarketplaceItem | None:
        """Get a marketplace item by ID (convenience wrapper)."""
        return await self.get(item_id)

    async def list_items(
        self,
        kind: MarketplaceItemType | None = None,
        status: MarketplaceItemStatus | None = None,
        installed_only: bool = False,
    ) -> list[MarketplaceItem]:
        """List marketplace items with optional filtering (convenience wrapper)."""
        return await self.list_all(kind=kind, status=status, installed_only=installed_only)

    async def list_installed(self) -> list[MarketplaceItem]:
        """List all installed marketplace items."""
        return await self.list_all(installed_only=True)

    async def list_by_kind(self, kind: MarketplaceItemType) -> list[MarketplaceItem]:
        """List all items of a specific kind."""
        return await self.list_all(kind=kind)

    async def update_item_status(
        self, item_id: str, status: MarketplaceItemStatus
    ) -> MarketplaceItem:
        """Update the status of a marketplace item in the cache.

        Args:
            item_id: The slug of the item to update
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
        return item

    # ------------------------------------------------------------------
    # Tools ↔ Marketplace integration (T5.1 integration-tools-marketplace)
    # ------------------------------------------------------------------

    async def get_tool_ids_for_item(self, item_slug: str) -> list[str]:
        """Return tool_ids stored in the item's meta JSON.

        Marketplace items of kind 'agent' or 'skill' may embed a list of
        tool_ids they require / expose in ``item.meta["tool_ids"]``.

        Args:
            item_slug: Unique slug of the marketplace item.

        Returns:
            List of tool_id strings (may be empty).
        """
        item = await self.get(item_slug)
        if item is None:
            return []
        return item.meta.get("tool_ids", [])

    async def set_tool_ids_for_item(
        self, item_slug: str, tool_ids: list[str]
    ) -> None:
        """Store *tool_ids* in the item's meta JSON and invalidate cache.

        Args:
            item_slug: Unique slug of the marketplace item.
            tool_ids: List of ``provider:name`` tool identifiers.

        Raises:
            PackageNotFoundError: If the item does not exist.
        """
        from .cache import marketplace_cache
        from .exceptions import PackageNotFoundError

        item = await self.get(item_slug)
        if item is None:
            raise PackageNotFoundError(item_id=item_slug)

        item.meta = {**item.meta, "tool_ids": tool_ids}
        marketplace_cache.invalidate(f"item:{item_slug}")
        marketplace_cache.invalidate_prefix("items:")

    async def find_items_by_tool_id(self, tool_id: str) -> list[MarketplaceItem]:
        """Return all marketplace items that reference *tool_id* in their meta.

        This is a full-table scan — suitable only in Phase 5.  Phase 7 should
        add a DB index on meta->'tool_ids'.

        Args:
            tool_id: Tool identifier in ``provider:name`` format.

        Returns:
            List of matching MarketplaceItem instances.
        """
        all_items = await self.list_all()
        return [
            item
            for item in all_items
            if tool_id in item.meta.get("tool_ids", [])
        ]

    # ------------------------------------------------------------------
    # Cache-aware list helpers (T5.1 integration-cache-marketplace)
    # ------------------------------------------------------------------

    async def list_all_cached(
        self,
        kind=None,
        status=None,
    ) -> list[MarketplaceItem]:
        """Cache-aware version of list_all().  Uses marketplace_cache TTL.

        Cache key: ``"items:{kind or 'all'}:{status or 'any'}"``.
        """
        from .cache import marketplace_cache

        cache_key = f"items:{kind.value if kind else 'all'}:{status.value if status else 'any'}"
        cached = marketplace_cache.get(cache_key)
        if cached is not None:
            return cached

        result = await self.list_all(kind=kind, status=status)
        marketplace_cache.set(cache_key, result)
        return result

    async def invalidate_item_cache(self, item_slug: str) -> None:
        """Invalidate all cache entries related to *item_slug*."""
        self._items.pop(item_slug, None)
        from .cache import marketplace_cache

        marketplace_cache.invalidate(f"item:{item_slug}")
        marketplace_cache.invalidate_prefix("items:")

    async def invalidate_all(self) -> None:
        """Clear the entire in-memory cache."""
        self._items.clear()
        from .cache import marketplace_cache

        marketplace_cache.invalidate_all()


def wire_registry_events() -> None:
    """Subscribe registry cache invalidation to marketplace events on the EventBus.

    Call once at startup so that in-memory registry caches are invalidated
    whenever marketplace items are installed/uninstalled/updated.
    """
    from css.core.events.event_bus import event_bus

    registry = MarketplaceItemRegistry()

    async def _on_marketplace_change(event_type: str, payload: object) -> None:
        await registry.invalidate_all()

    event_bus.register("marketplace.install", _on_marketplace_change)
    event_bus.register("marketplace.uninstall", _on_marketplace_change)
    event_bus.register("marketplace.updated", _on_marketplace_change)
