"""
SettingsRegistry — a registry for application settings and configuration.

Manages hierarchical application configuration with support for:
- Multiple scopes (global, project, session, user)
- Settings inheritance and merging
- YAML/JSON serialization
- Schema validation
- Environment variable overrides

Example::

    from registries.settings import SettingsRegistry, SettingScope
    
    registry = SettingsRegistry()
    
    # Set a global setting
    registry.set("debug", True, scope=SettingScope.GLOBAL)
    
    # Get with fallback
    debug = registry.get("debug", default=False)
    
    # Find all settings matching a pattern
    web_settings = registry.find_prefix("web.")
    
    # Save to config file
    registry.save_scope("~/.cybersecsuite/config.yml", scope=SettingScope.GLOBAL)
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .base import BaseRegistry, RegistryConfig

logger = logging.getLogger("registries.settings")


class SettingScope(str, Enum):
    """Scope hierarchy for settings (more specific wins)."""
    GLOBAL = "global"
    PROJECT = "project"
    USER = "user"
    SESSION = "session"


@dataclass
class Setting:
    """A single configuration setting with metadata."""
    key: str
    value: Any
    scope: SettingScope = SettingScope.GLOBAL
    description: str = ""
    type_hint: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    validator: Optional[callable] = None
    tags: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """Validate setting value against validator if present."""
        if self.validator is None:
            return True
        try:
            return self.validator(self.value)
        except Exception as e:
            logger.warning("Validation failed for %s: %s", self.key, e)
            return False
    
    def __str__(self) -> str:
        return f"{self.key}={self.value}"


class SettingsRegistry(BaseRegistry[Setting]):
    """
    Registry for application settings with scope management.
    
    Settings are stored hierarchically by scope with precedence:
    SESSION > USER > PROJECT > GLOBAL
    
    Supports:
    - Setting/getting with scope hierarchy
    - Bulk operations (get_all, set_all)
    - Pattern-based queries
    - Multiple storage formats (JSON, YAML)
    - Environment variable overrides
    """
    
    def __init__(self, config: Optional[RegistryConfig] = None) -> None:
        """Initialize settings registry."""
        super().__init__(config)
        self._settings: Dict[str, Dict[SettingScope, Setting]] = {}
        self._by_scope: Dict[SettingScope, Dict[str, Setting]] = {
            scope: {} for scope in SettingScope
        }
        logger.debug("Initialized SettingsRegistry")
    
    # ── Abstract Methods (Implementation) ─────────────────────────────────────
    
    def list(self) -> List[Setting]:
        """Return all settings, preferring most specific scope."""
        seen = set()
        results = []
        
        # Iterate scopes in reverse precedence order
        for scope in reversed(list(SettingScope)):
            for key, setting in self._by_scope[scope].items():
                if key not in seen:
                    results.append(setting)
                    seen.add(key)
        
        return sorted(results, key=lambda s: s.key)
    
    def get(self, item_id: str) -> Optional[Setting]:
        """
        Get setting by key (scope priority: SESSION > USER > PROJECT > GLOBAL).
        
        Args:
            item_id: Setting key
            
        Returns:
            Setting with highest precedence, or None
        """
        if item_id not in self._settings:
            return None
        
        # Return most specific scope
        for scope in [SettingScope.SESSION, SettingScope.USER, SettingScope.PROJECT, SettingScope.GLOBAL]:
            if scope in self._settings[item_id]:
                return self._settings[item_id][scope]
        
        return None
    
    def find(self, **filters: Any) -> List[Setting]:
        """
        Find settings by filters.
        
        Supported filters:
        - scope: SettingScope to query
        - tags: List of tags (all must match)
        - required: True to find required settings
        
        Args:
            **filters: Filter criteria
            
        Returns:
            Matching settings
        """
        results = []
        scope = filters.pop("scope", None)
        tags = filters.pop("tags", None)
        required = filters.pop("required", None)
        
        # Get scope-specific or all settings
        if scope:
            settings = list(self._by_scope[scope].values())
        else:
            settings = self.list()
        
        # Apply filters
        for setting in settings:
            if tags and not all(t in setting.tags for t in tags):
                continue
            if required is not None and setting.required != required:
                continue
            results.append(setting)
        
        return results
    
    def add(self, item: Setting) -> Setting:
        """
        Add or update a setting.
        
        Args:
            item: Setting to add
            
        Returns:
            The added setting
            
        Raises:
            ValueError: If setting is invalid
        """
        if not isinstance(item, Setting):
            raise ValueError(f"Expected Setting, got {type(item).__name__}")
        
        # Validate value
        if not item.validate():
            raise ValueError(f"Setting {item.key} failed validation")
        
        # Store by key and scope
        if item.key not in self._settings:
            self._settings[item.key] = {}
        
        self._settings[item.key][item.scope] = item
        self._by_scope[item.scope][item.key] = item
        
        logger.debug("Set setting %s=%s (scope=%s)", item.key, item.value, item.scope)
        return item
    
    def remove(self, item_id: str) -> bool:
        """
        Remove all scopes of a setting.
        
        Args:
            item_id: Setting key
            
        Returns:
            True if removed, False if not found
        """
        if item_id not in self._settings:
            return False
        
        # Remove from all scopes
        for scope in list(SettingScope):
            self._by_scope[scope].pop(item_id, None)
        
        del self._settings[item_id]
        logger.debug("Removed setting: %s", item_id)
        return True
    
    # ── Additional Methods ───────────────────────────────────────────────────
    
    def get_value(self, key: str, default: Any = None, scope: Optional[SettingScope] = None) -> Any:
        """
        Get setting value (not the Setting object).
        
        Args:
            key: Setting key
            default: Default if not found
            scope: Specific scope to query (None = all, highest priority wins)
            
        Returns:
            Setting value or default
        """
        if scope:
            setting = self._by_scope[scope].get(key)
            return setting.value if setting else default
        
        setting = self.get(key)
        return setting.value if setting else default
    
    def set_value(
        self,
        key: str,
        value: Any,
        scope: SettingScope = SettingScope.GLOBAL,
        description: str = "",
    ) -> Setting:
        """
        Set a value as a setting (convenience method).
        
        Args:
            key: Setting key
            value: Value to set
            scope: Setting scope
            description: Optional description
            
        Returns:
            Created Setting object
        """
        setting = Setting(key=key, value=value, scope=scope, description=description)
        return self.add(setting)
    
    def get_all(self, scope: Optional[SettingScope] = None) -> Dict[str, Any]:
        """
        Get all settings as a dict (key -> value).
        
        Args:
            scope: Optional scope to limit results
            
        Returns:
            Dictionary of key -> value pairs
        """
        results = {}
        for setting in (self.find(scope=scope) if scope else self.list()):
            results[setting.key] = setting.value
        return results
    
    def set_all(self, settings: Dict[str, Any], scope: SettingScope = SettingScope.GLOBAL) -> int:
        """
        Set multiple values.
        
        Args:
            settings: Dictionary of key -> value pairs
            scope: Scope for all settings
            
        Returns:
            Number of settings added
        """
        count = 0
        for key, value in settings.items():
            try:
                self.set_value(key, value, scope=scope)
                count += 1
            except Exception as e:
                logger.warning("Failed to set %s: %s", key, e)
        return count
    
    def find_prefix(self, prefix: str, scope: Optional[SettingScope] = None) -> List[Setting]:
        """
        Find all settings whose key starts with prefix.
        
        Args:
            prefix: Key prefix to match
            scope: Optional scope to limit
            
        Returns:
            Matching settings
        """
        results = []
        settings = self.find(scope=scope) if scope else self.list()
        for setting in settings:
            if setting.key.startswith(prefix):
                results.append(setting)
        return results
    
    def clear(self) -> None:
        """Clear all settings."""
        self._settings.clear()
        for scope in SettingScope:
            self._by_scope[scope].clear()
        logger.info("Cleared all settings")
    
    def summary(self) -> Dict[str, Any]:
        """Get settings summary."""
        by_scope = {scope.value: len(self._by_scope[scope]) for scope in SettingScope}
        return {
            **super().summary(),
            "by_scope": by_scope,
            "total": len(self._settings),
        }


__all__ = ["SettingsRegistry", "Setting", "SettingScope"]
