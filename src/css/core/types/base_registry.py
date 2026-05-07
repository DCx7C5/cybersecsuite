"""Singleton base registry pattern for CyberSecSuite."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T', bound='BaseRegistry')


class BaseRegistry(ABC, Generic[T]):
    """Abstract base class for singleton registries.

    Implements thread-safe singleton pattern suitable for async Python.
    Subclasses should implement abstract methods for specific registry behavior.

    Usage:
        class MyRegistry(BaseRegistry):
            def _setup(self):
                self.items = {}

            def register(self, key, value):
                self.items[key] = value

        # Get singleton instance
        registry = MyRegistry.get_instance()
    """

    _instance: T | None = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the registry (runs setup only once)."""
        if not self._initialized:
            self._initialized = True
            self._setup()

    def _setup(self) -> None:
        """Setup method called once during first initialization.

        Override this method to perform registry-specific setup.
        """
        pass

    @classmethod
    def get_instance(cls: type[T]) -> T | None:
        """Get the singleton instance.

        Returns:
            The singleton instance of the registry.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (useful for testing).

        This allows fresh state for each test.
        """
        cls._instance = None
        cls._initialized = False

    @abstractmethod
    async def register(self, *args, **kwargs):
        """Register an item in the registry.

        Must be implemented by subclasses.
        """
        ...

    @abstractmethod
    async def unregister(self, *args, **kwargs):
        """Unregister an item from the registry.

        Must be implemented by subclasses.
        """
        ...

    @abstractmethod
    async def get(self, *args, **kwargs):
        """Get an item from the registry.

        Must be implemented by subclasses.
        """
        ...

    @abstractmethod
    async def list_all(self, *args, **kwargs):
        """List all items in the registry.

        Must be implemented by subclasses.
        """
        ...
