"""Base registry contract for in-memory read/cache registries."""

from collections.abc import Callable
from typing import Protocol, TypeVar


TItem = TypeVar("TItem")


class BaseRegistry(Protocol[TItem]):
    """Structural async contract for registry-like components.

    This contract models read/cache lifecycle semantics:
    `get`, `list`, `invalidate`, and `reload`.
    """

    async def get(self, identifier: str) -> TItem | None:
        """Retrieve an item by identifier, or None."""
        ...

    async def list(self, predicate: Callable[[TItem], bool] | None = None) -> list[TItem]:
        """List registry items, optionally filtered by predicate."""
        ...

    async def invalidate(self, identifier: str | None = None) -> None:
        """Invalidate one cached item or the entire registry cache."""
        ...

    async def reload(self) -> None:
        """Rebuild the in-memory cache from the authoritative source."""
        ...


class BaseToggleRegistry(Protocol[TItem]):
    """Registry contract for components with enable/disable semantics."""

    async def get(self, identifier: str) -> TItem | None:
        """Retrieve an item by identifier, or None."""
        ...

    async def list(self, predicate: Callable[[TItem], bool] | None = None) -> list[TItem]:
        """List registry items, optionally filtered by predicate."""
        ...

    async def invalidate(self, identifier: str | None = None) -> None:
        """Invalidate one cached item or the entire registry cache."""
        ...

    async def reload(self) -> None:
        """Rebuild the in-memory cache from the authoritative source."""
        ...

    async def enable(self, identifier: str) -> None:
        """Enable an item by identifier."""
        ...

    async def disable(self, identifier: str) -> None:
        """Disable an item by identifier."""
        ...

    async def is_enabled(self, identifier: str) -> bool:
        """Check whether an item is enabled."""
        ...
