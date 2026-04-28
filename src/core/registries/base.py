"""
Base registry pattern for unified registry implementations.

Provides:
- Abstract BaseRegistry class with standard interface
- Shared validation utilities (item_id formatting)
- Registry configuration dataclass
- Factory pattern helpers for registry discovery
- Type hints and comprehensive documentation

All registries (agents, accounts, providers, marketplace, tools) should inherit from
BaseRegistry to ensure consistent API across the codebase.

Example::

    from registries.base import BaseRegistry, get_registry
    from registries.agents import AgentRegistry
    
    # Direct instantiation
    agents = AgentRegistry()
    all_agents = agents.list()
    
    # Or use factory
    agents = get_registry("agents")  # Returns AgentRegistry instance
"""


import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, TypeVar

# Type variable for items in registry
T = TypeVar("T")


# ── Configuration ────────────────────────────────────────────────────────────

@dataclass
class RegistryConfig:
    """
    Common registry configuration.
    
    Attributes:
        cache_enabled: Whether to cache query results in memory.
        persist_enabled: Whether to persist registry state to disk.
        persist_path: Path to persistence file (JSON, YAML, etc.).
        auto_load: Whether to auto-load persisted state on init.
        auto_save: Whether to auto-save after modifications.
    """
    cache_enabled: bool = True
    persist_enabled: bool = False
    persist_path: Optional[Path] = None
    auto_load: bool = True
    auto_save: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)


# ── Validation utilities ─────────────────────────────────────────────────────

def validate_item_id(item_id: str) -> bool:
    """
    Validate that item_id is in kebab-case format.
    
    Kebab-case: lowercase letters, numbers, hyphens only.
    Examples: "claude-forensic-analyst", "skill-1", "provider-openai"
    
    Args:
        item_id: Item identifier to validate.
        
    Returns:
        True if valid kebab-case, False otherwise.
    """
    if not item_id or not isinstance(item_id, str):
        return False
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return bool(re.match(pattern, item_id))


def normalize_item_id(item: str) -> str:
    """
    Convert string to kebab-case format.
    
    Args:
        item: String to normalize.
        
    Returns:
        Normalized kebab-case string.
        
    Example:
        normalize_item_id("Claude Forensic Analyst") → "claude-forensic-analyst"
        normalize_item_id("skill_1") → "skill-1"
    """
    # Convert to lowercase
    s = item.lower()
    # Replace spaces, underscores with hyphens
    s = re.sub(r"[\s_]+", "-", s)
    # Remove any non-alphanumeric characters except hyphens
    s = re.sub(r"[^a-z0-9-]", "", s)
    # Remove leading/trailing hyphens
    s = s.strip("-")
    # Collapse multiple hyphens
    s = re.sub(r"-+", "-", s)
    return s


# ── Base Registry Class ──────────────────────────────────────────────────────

class BaseRegistry(ABC, Generic[T]):
    """
    Abstract base class for all registries in CyberSecSuite.
    
    Defines the standard interface that all registries must implement:
    list(), get(), find(), add(), remove(). Optional methods with defaults
    include search(), clear().
    
    Subclasses should:
    1. Implement all abstract methods
    2. Provide type hints for generic T
    3. Add registry-specific methods (e.g., find_by_name, find_by_tags)
    4. Handle persistence if needed
    5. Provide singleton factory if appropriate
    
    Example::
    
        class MyRegistry(BaseRegistry[MyItem]):
            def __init__(self, config: RegistryConfig | None = None):
                self.config = config or RegistryConfig()
                self._items: Dict[str, MyItem] = {}
            
            def list(self) -> List[MyItem]:
                return list(self._items.values())
            
            def get(self, item_id: str) -> MyItem | None:
                if not validate_item_id(item_id):
                    raise ValueError(f"Invalid item ID: {item_id}")
                return self._items.get(item_id)
            
            # ... implement other abstract methods
    """
    
    # ── Lifecycle ────────────────────────────────────────────────────────────
    
    def __init__(self, config: Optional[RegistryConfig] = None) -> None:
        """
        Initialize registry with optional configuration.
        
        Args:
            config: Registry configuration. If None, defaults are used.
        """
        self.config = config or RegistryConfig()
    
    # ── Abstract Methods (must be implemented by subclasses) ──────────────────
    
    @abstractmethod
    def list(self) -> List[T]:
        """
        List all items in the registry.
        
        Returns:
            List of all registered items, typically sorted.
        """
        pass
    
    @abstractmethod
    def get(self, item_id: str) -> Optional[T]:
        """
        Get a single item by its unique ID.
        
        Args:
            item_id: Unique item identifier (should be kebab-case).
            
        Returns:
            The item if found, None otherwise.
            
        Raises:
            ValueError: If item_id format is invalid (optional).
        """
        pass
    
    @abstractmethod
    def find(self, **filters: Any) -> List[T]:
        """
        Find items matching given filter criteria.
        
        Filter keys are registry-specific. Examples:
        - find(status="active", type="agent")
        - find(provider="claude", tags=["forensic"])
        
        Args:
            **filters: Registry-specific filter criteria.
            
        Returns:
            List of items matching all filters.
        """
        pass
    
    @abstractmethod
    def add(self, item: T) -> T:
        """
        Add or register a new item.
        
        Args:
            item: Item to add/register.
            
        Returns:
            The added item (potentially with modified/auto-generated fields).
            
        Raises:
            ValueError: If item is invalid or already exists.
        """
        pass
    
    @abstractmethod
    def remove(self, item_id: str) -> bool:
        """
        Remove an item from the registry.
        
        Args:
            item_id: Unique item identifier.
            
        Returns:
            True if item was removed, False if it didn't exist.
        """
        pass
    
    # ── Concrete Methods (optional overrides) ─────────────────────────────────
    
    def search(self, query: str) -> List[T]:
        """
        Search items by query string (default: substring, case-insensitive).
        
        This is a default implementation that can be overridden for more
        sophisticated search (fuzzy matching, full-text search, etc.).
        
        Default behavior: Substring search on item string representation.
        
        Args:
            query: Search query string.
            
        Returns:
            List of items matching query.
        """
        if not query or not isinstance(query, str):
            return self.list()
        
        q = query.strip().lower()
        results = []
        for item in self.list():
            if q in str(item).lower():
                results.append(item)
        return results
    
    def clear(self) -> None:
        """
        Clear all items from the registry.
        
        Warning: This is destructive. Consider implementing a dry-run mode
        or requiring confirmation in subclasses.
        """
        # Default implementation: no-op
        # Subclasses should implement if supporting clear operations
        raise NotImplementedError("clear() not implemented for this registry")
    
    def exists(self, item_id: str) -> bool:
        """
        Check if an item exists in the registry.
        
        Args:
            item_id: Unique item identifier.
            
        Returns:
            True if item exists, False otherwise.
        """
        return self.get(item_id) is not None
    
    def count(self) -> int:
        """
        Get total number of items in registry.
        
        Returns:
            Number of items.
        """
        return len(self.list())
    
    # ── Persistence Helpers ────────────────────────────────────────────────────
    
    def save(self) -> None:
        """
        Save registry state to persistent storage (if enabled).
        
        This is a no-op by default. Subclasses should implement if they
        support persistence (e.g., JSON, YAML files).
        """
        if not self.config.persist_enabled or not self.config.persist_path:
            return
        # Implement in subclasses
    
    def load(self) -> None:
        """
        Load registry state from persistent storage (if enabled).
        
        This is a no-op by default. Subclasses should implement if they
        support persistence (e.g., JSON, YAML files).
        """
        if not self.config.persist_enabled or not self.config.persist_path:
            return
        # Implement in subclasses
    
    # ── Utility Methods ───────────────────────────────────────────────────────
    
    def validate_id(self, item_id: str) -> None:
        """
        Validate item ID format (kebab-case).
        
        Args:
            item_id: Item identifier to validate.
            
        Raises:
            ValueError: If item_id is not valid kebab-case.
        """
        if not validate_item_id(item_id):
            raise ValueError(
                f"Invalid item ID format: {item_id!r}. "
                f"Expected kebab-case (lowercase letters, numbers, hyphens only)."
            )
    
    def summary(self) -> Dict[str, Any]:
        """
        Get registry summary (count, status, etc.).
        
        Default implementation returns basic stats. Subclasses can override
        for more detailed information.
        
        Returns:
            Dictionary with registry statistics.
        """
        return {
            "type": self.__class__.__name__,
            "count": self.count(),
            "cache_enabled": self.config.cache_enabled,
            "persist_enabled": self.config.persist_enabled,
        }


# ── Registry Factory ────────────────────────────────────────────────────────

_REGISTRIES: Dict[str, Any] = {}


def register_registry_type(name: str, registry_cls: type) -> None:
    """
    Register a registry class by name for factory discovery.
    
    Called by each registry module during initialization.
    
    Args:
        name: Short name for registry (e.g., "agents", "marketplace").
        registry_cls: Registry class (should inherit from BaseRegistry).
    """
    _REGISTRIES[name] = registry_cls


def get_registry(name: str) -> Optional[BaseRegistry]:
    """
    Get a registry instance by name (factory pattern).
    
    Args:
        name: Registry name (agents, accounts, providers, marketplace, tools).
        
    Returns:
        Registry instance if found, None otherwise.
        
    Example:
        agents = get_registry("agents")
        marketplace = get_registry("marketplace")
    """
    registry_cls = _REGISTRIES.get(name)
    if registry_cls is None:
        return None
    # Instantiate with default config
    return registry_cls()


def list_registries() -> List[str]:
    """
    List all registered registry types.
    
    Returns:
        Sorted list of registry names.
    """
    return sorted(_REGISTRIES.keys())


# ── Exports ──────────────────────────────────────────────────────────────────

__all__ = [
    "BaseRegistry",
    "RegistryConfig",
    "validate_item_id",
    "normalize_item_id",
    "register_registry_type",
    "get_registry",
    "list_registries",
]

