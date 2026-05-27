"""Read/cache registry for marketplace items."""

from collections.abc import Callable
from typing import override

from css.core.db.models.marketplace import MarketplaceItem
from css.core.enums import MarketplaceItemStatus, MarketplaceItemType
from css.core.events.emitter import emit_events, get_event_bus
from css.core.types import BaseRegistry
from css.core.types.base_meta import singleton


MARKETPLACE_UPDATES_AVAILABLE_EVENT = "marketplace.updates.available"
MARKETPLACE_UPDATES_INSTALLED_EVENT = "marketplace.updates.installed"
MARKETPLACE_ITEM_INSTALL_EVENT = "marketplace.item.install"
MARKETPLACE_ITEM_UNINSTALL_EVENT = "marketplace.item.uninstall"
MARKETPLACE_ITEM_UPDATE_EVENT = "marketplace.item.update"
MARKETPLACE_ITEM_NEW_VERSION_EVENT = ""


@singleton
class MarketplaceItemRegistry(BaseRegistry[MarketplaceItem]):
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

    @override
    async def reload(self) -> None:
        """Rebuild the in-memory cache from authoritative DB state."""
        await self._load_all()

    @override
    async def get(self, identifier: str) -> MarketplaceItem | None:
        """Get a marketplace item by slug — read-through cache.

        Checks in-memory cache first, falls back to DB on miss.

        Args:
            identifier: The slug of the item to retrieve

        Returns:
            MarketplaceItem instance or None if not found
        """
        if identifier in self._items:
            return self._items[identifier]
        item = await MarketplaceItem.manager.by_slug(identifier)
        if item is not None:
            self._items[identifier] = item
        return item

    @override
    async def list(
        self,
        predicate: Callable[[MarketplaceItem], bool] | None = None,
    ) -> list[MarketplaceItem]:
        """List cached items with optional predicate filtering."""
        if not self._items:
            await self._load_all()
        items = list(self._items.values())
        if predicate is None:
            return items
        return [item for item in items if predicate(item)]

    async def list_items(
        self,
        kind: MarketplaceItemType | None = None,
        status: MarketplaceItemStatus | None = None,
        installed_only: bool = False,
    ) -> list[MarketplaceItem]:
        """List marketplace items with optional domain filters."""
        def _matches(item: MarketplaceItem) -> bool:
            if kind is not None and item.kind != kind:
                return False
            if status is not None and item.status != status:
                return False
            if installed_only and item.installed_at is None:
                return False
            return True

        return await self.list(predicate=_matches)

    # ------------------------------------------------------------------
    # Cache-aware list helpers (T5.1 integration-cache-marketplace)
    # ------------------------------------------------------------------

    @override
    async def invalidate(self, identifier: str | None = None) -> None:
        """Invalidate one cached item or all cached items."""
        from .cache import marketplace_cache

        if identifier is None:
            self._items.clear()
            marketplace_cache.invalidate_all()
            return

        self._items.pop(identifier, None)
        marketplace_cache.invalidate(f"item:{identifier}")
        marketplace_cache.invalidate_prefix("items:")


def wire_registry_events() -> None:
    """Subscribe registry cache invalidation to marketplace events on the EventBus.

    Call once at startup so that in-memory registry caches are invalidated
    whenever marketplace items are installed/uninstalled/updated.
    """
    event_bus = get_event_bus()
    registry = MarketplaceItemRegistry()

    async def _on_marketplace_change(event_type: str, payload: object) -> None:
        if isinstance(payload, dict):
            slug = payload.get("item_slug") or payload.get("slug") or payload.get("item_id")
            if isinstance(slug, str) and slug:
                await registry.invalidate(slug)
                return
        await registry.invalidate()

    event_bus.register(MARKETPLACE_UPDATES_AVAILABLE_EVENT, _on_marketplace_change)
    event_bus.register("marketplace.install", _on_marketplace_change)
    event_bus.register("marketplace.uninstall", _on_marketplace_change)
    event_bus.register("marketplace.updated", _on_marketplace_change)


async def emit_marketplace_updates_available(item_slug: str, operation: str) -> None:
    """Emit cache-invalidation events after marketplace DB writes."""
    payload = {
        "item_slug": item_slug,
        "item_id": item_slug,
        "operation": operation,
    }
    await emit_events(
        [MARKETPLACE_UPDATES_AVAILABLE_EVENT, f"marketplace.{operation}"],
        payload,
    )


async def emit_marketplace_item_changed(item_slug: str, operation: str) -> None:
    """Canonical marketplace mutation emitter used by installer/seeder."""
    await emit_marketplace_updates_available(item_slug=item_slug, operation=operation)
