"""Registry for marketplace items (DB-backed)."""

from css.core.types.meta import singleton
from css.core.db.models.marketplace import MarketplaceItem
from css.core.enums import MarketplaceItemStatus, MarketplaceItemType


MARKETPLACE_ITEM_CHANGED_EVENT = "marketplace.item.changed"


@singleton
class MarketplaceItemRegistry:
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
        items = await MarketplaceItem.manager.all_items()
        self._items = {item.slug: item for item in items}

    async def reload(self) -> None:
        """Rebuild the in-memory cache from authoritative DB state."""
        await self._load_all()

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
        item = await MarketplaceItem.manager.by_slug(item_id)
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

    # ------------------------------------------------------------------
    # Cache-aware list helpers (T5.1 integration-cache-marketplace)
    # ------------------------------------------------------------------

    async def list_all_cached(
        self,
        kind: MarketplaceItemType | None = None,
        status: MarketplaceItemStatus | None = None,
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
        if isinstance(payload, dict):
            slug = payload.get("item_slug") or payload.get("slug") or payload.get("item_id")
            if isinstance(slug, str) and slug:
                await registry.invalidate_item_cache(slug)
                return
        await registry.invalidate_all()

    event_bus.register(MARKETPLACE_ITEM_CHANGED_EVENT, _on_marketplace_change)
    event_bus.register("marketplace.install", _on_marketplace_change)
    event_bus.register("marketplace.uninstall", _on_marketplace_change)
    event_bus.register("marketplace.updated", _on_marketplace_change)


async def emit_marketplace_item_changed(item_slug: str, operation: str) -> None:
    """Emit cache-invalidation events after marketplace DB writes."""

    from css.core.events.event_bus import event_bus

    payload = {
        "item_slug": item_slug,
        "item_id": item_slug,
        "operation": operation,
    }
    await event_bus.emit(MARKETPLACE_ITEM_CHANGED_EVENT, payload)
    await event_bus.emit(f"marketplace.{operation}", payload)
