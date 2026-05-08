"""Singleton base registry pattern for CyberSecSuite."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from .meta import AsyncSafeSingletonMeta

T = TypeVar('T')
# TODO: Proper Type Implementation

class BaseRegistry(ABC, Generic[T], metaclass=AsyncSafeSingletonMeta):
    """Abstract base class for singleton registries.

    Uses AsyncSafeSingletonMeta for async-safe singleton pattern.
    Subclasses should implement the _setup method for initialization.

    Usage:
        class MyRegistry(BaseRegistry[MyItem]):
            def _setup(self):
                self._items: dict[str, MyItem] = {}

            async def register(self, key: str, item: MyItem):
                self._items[key] = item

        # Get singleton instance
        registry = MyRegistry()
    """

    _instances = None

    def __init__(self):
        """Initialize the registry (runs setup only once)."""
        if not getattr(self, '_initialized', False):
            self._initialized = True
            self._setup()

    def _setup(self) -> None:
        """Setup method called once during first initialization.

        Override this method to perform registry-specific setup.
        """
        pass

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        if hasattr(cls, "_instances") and cls in cls._instances:
            del cls._instances[cls]
        cls._initialized = False

    @abstractmethod
    async def register(self, *args, **kwargs):
        """Register an item in the registry.

        Must be implemented by subclasses.
        """
        ...
