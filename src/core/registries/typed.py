"""
TypedRegistry — a generic, type-validated registry implementation.

Provides a concrete registry implementation with full Pydantic validation,
caching, and search capabilities. Use this for registries that need strong
typing and automatic validation.

Example::

    from pydantic import BaseModel
    from registries.typed import TypedRegistry
    
    class Skill(BaseModel):
        id: str
        name: str
        tags: list[str] = []
    
    registry = TypedRegistry[Skill](
        name="skills",
        item_type=Skill,
    )
    
    skill = Skill(id="web-search", name="Web Search")
    registry.add(skill)
    
    results = registry.find(tags=["web"])
"""

import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from .base import BaseRegistry, RegistryConfig

logger = logging.getLogger("registries.typed")

T = TypeVar("T", bound=BaseModel)


class TypedRegistry(BaseRegistry[T]):
    """
    Generic registry with Pydantic validation and type safety.
    
    Supports:
    - Automatic validation of items against Pydantic model
    - Attribute-based filtering (find by any model field)
    - Caching of query results
    - ID validation (kebab-case)
    - Full-text search
    
    Type Parameters:
        T: Pydantic BaseModel subclass defining item schema
    
    Attributes:
        name: Human-readable registry name (e.g., "skills", "models")
        item_type: Pydantic model class for items
        config: Registry configuration
    """
    
    def __init__(
        self,
        name: str,
        item_type: Type[T],
        config: Optional[RegistryConfig] = None,
    ) -> None:
        """
        Initialize typed registry.
        
        Args:
            name: Registry name for logging/discovery
            item_type: Pydantic model class for items
            config: Optional registry configuration
        """
        super().__init__(config)
        self.name = name
        self.item_type = item_type
        self._items: Dict[str, T] = {}
        self._cache: Dict[str, List[T]] = {}
        logger.debug("Initialized TypedRegistry(%s) for type %s", name, item_type.__name__)
    
    # ── Abstract Methods (Implementation) ─────────────────────────────────────
    
    def list(self) -> List[T]:
        """Return all items sorted by ID."""
        return sorted(self._items.values(), key=lambda x: getattr(x, "id", ""))
    
    def get(self, item_id: str) -> Optional[T]:
        """
        Get item by ID.
        
        Args:
            item_id: Item identifier
            
        Returns:
            Item if found, None otherwise
            
        Raises:
            ValueError: If item_id format is invalid
        """
        self.validate_id(item_id)
        return self._items.get(item_id)
    
    def find(self, **filters: Any) -> List[T]:
        """
        Find items matching all given filter criteria.
        
        Filters are matched against item attributes (model fields).
        
        Examples:
            registry.find(status="active")
            registry.find(provider="claude", tags=["vision"])
        
        Args:
            **filters: Attribute-value pairs to match
            
        Returns:
            List of matching items
        """
        # Return all items if no filters
        if not filters:
            return self.list()
        
        # Check cache first if caching enabled
        cache_key = f"find_{tuple(sorted(filters.items()))}"
        if self.config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]
        
        # Filter items
        results = []
        for item in self._items.values():
            match = True
            for key, value in filters.items():
                if not hasattr(item, key):
                    match = False
                    break
                
                item_value = getattr(item, key)
                # Handle list matching (all items in list must be in filter value)
                if isinstance(item_value, list) and isinstance(value, list):
                    if not all(v in item_value for v in value):
                        match = False
                        break
                # Handle direct matching
                elif item_value != value:
                    match = False
                    break
            
            if match:
                results.append(item)
        
        # Cache results if caching enabled
        if self.config.cache_enabled:
            self._cache[cache_key] = results
        
        return results
    
    def add(self, item: T) -> T:
        """
        Add item to registry with validation.
        
        Args:
            item: Item to add (Pydantic model instance)
            
        Returns:
            The added item
            
        Raises:
            ValueError: If item is invalid or ID format is wrong
            ValidationError: If item fails Pydantic validation
        """
        # Validate item type
        if not isinstance(item, self.item_type):
            raise ValueError(
                f"Item must be instance of {self.item_type.__name__}, "
                f"got {type(item).__name__}"
            )
        
        # Validate item ID if it has one
        if hasattr(item, "id"):
            item_id = getattr(item, "id")
            self.validate_id(item_id)
        else:
            raise ValueError("Item must have 'id' attribute")
        
        # Add to registry
        item_id = getattr(item, "id")
        self._items[item_id] = item
        
        # Invalidate cache
        self._cache.clear()
        
        logger.debug("Added item to %s: %s", self.name, item_id)
        return item
    
    def remove(self, item_id: str) -> bool:
        """
        Remove item from registry.
        
        Args:
            item_id: Item identifier
            
        Returns:
            True if removed, False if not found
        """
        self.validate_id(item_id)
        
        if item_id in self._items:
            del self._items[item_id]
            self._cache.clear()
            logger.debug("Removed item from %s: %s", self.name, item_id)
            return True
        
        return False
    
    # ── Concrete Methods (Overrides) ──────────────────────────────────────────
    
    def search(self, query: str) -> List[T]:
        """
        Full-text search across all string fields.
        
        Args:
            query: Search query
            
        Returns:
            List of matching items
        """
        if not query or not isinstance(query, str):
            return self.list()
        
        q = query.strip().lower()
        results = []
        
        for item in self._items.values():
            # Search in all string fields
            for field_name, field_info in item.model_fields.items():
                value = getattr(item, field_name)
                if isinstance(value, str) and q in value.lower():
                    results.append(item)
                    break
                # Also search in list of strings (e.g., tags)
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, str) and q in v.lower():
                            results.append(item)
                            break
        
        return results
    
    def clear(self) -> None:
        """Clear all items from registry."""
        count = len(self._items)
        self._items.clear()
        self._cache.clear()
        logger.info("Cleared %s: removed %d items", self.name, count)
    
    def summary(self) -> Dict[str, Any]:
        """Get registry summary with type info."""
        return {
            **super().summary(),
            "name": self.name,
            "item_type": self.item_type.__name__,
        }


__all__ = ["TypedRegistry"]
