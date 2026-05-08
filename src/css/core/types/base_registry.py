"""Registry Protocol — pure in-memory registry interface (no DB)."""

from typing import Protocol, TypeVar

T = TypeVar('T', covariant=True)


class BaseRegistry(Protocol[T]):
    """Protocol for pure in-memory registries.

    Concrete registries use their own singleton pattern
    (AsyncSafeSingletonMeta) independently.  This Protocol
    defines the structural interface only — no base class
    inheritance, no singleton boilerplate, no DB writes.
    """

    async def register(self, item: T) -> None:
        """Register an item in the registry."""
        ...

    async def unregister(self, identifier: str) -> None:
        """Remove an item from the registry by identifier."""
        ...

    async def get(self, identifier: str) -> T | None:
        """Retrieve an item by identifier, or None."""
        ...

    async def list_all(self) -> list[T]:
        """List all registered items."""
        ...
