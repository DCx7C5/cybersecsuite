"""Registry Protocol — pure in-memory registry interface (no DB)."""

from collections.abc import Callable
from typing import Protocol, TypeVar

T = TypeVar('T')


class BaseRegistry(Protocol[T]):
    """Protocol for pure in-memory registries.

    Concrete registries use their own singleton pattern
    (AsyncSafeSingletonMeta) independently.  This Protocol
    defines the structural interface only — no base class
    inheritance, no singleton boilerplate, no DB writes.
    """

    async def get(self, identifier: str) -> T | None:
        """Retrieve an item by identifier, or None."""
        ...

    async def list(self, predicate: Callable[[T], bool] | None = None) -> list[T]:
        """List registry items, optionally filtered by predicate."""
        ...

    async def invalidate(self, identifier: str | None = None) -> None:
        """Invalidate one cached item or the entire registry cache."""
        ...

    async def reload(self) -> None:
        """Rebuild the in-memory cache from the authoritative source."""
        ...
