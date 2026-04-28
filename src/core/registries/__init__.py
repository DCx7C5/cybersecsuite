"""
Unified registries module — consolidated registry implementations.

Provides a single location for all registry types in CyberSecSuite:
- Agents (A2A agent discovery)
- Accounts (API account index)
- Providers (AI provider configuration)
- Marketplace (installable items)
- Tools (MCP/SDK tool registry)
- API Services (LLM/Public API service configuration)
- Typed (generic type-safe registries)
- Settings (application configuration management)

All registries inherit from BaseRegistry and follow a consistent interface.

Usage::

    from registries import BaseRegistry, get_registry
    from registries.agents import AgentRegistry
    from registries.marketplace import MarketplaceRegistry
    from registries.typed import TypedRegistry
    from registries.settings import SettingsRegistry
    
    # Direct instantiation
    agents = AgentRegistry()
    all_agents = agents.list()
    
    # Or use factory
    agents = get_registry("agents")  # Returns AgentRegistry instance
    marketplace = get_registry("marketplace")

See Also:
    - registries.base — BaseRegistry abstract class and utilities
    - registries.agents — Agent registry for A2A discovery
    - registries.accounts — Account registry for API credentials
    - registries.providers — Provider registry for AI services
    - registries.marketplace — Marketplace registry with update/upgrade
    - registries.typed — Generic TypedRegistry for Pydantic models
    - registries.settings — Settings/config registry with scope hierarchy
    - registries.tools — Tool/skill registry for MCP/SDK tools
"""


# Base registry and utilities
from .base import (
    BaseRegistry,
    RegistryConfig,
    get_registry,
    list_registries,
    normalize_item_id,
    register_registry_type,
    validate_item_id,
)

# Core registries (no external dependencies)
from .typed import TypedRegistry
from .settings import SettingsRegistry, Setting, SettingScope

# Individual registry types (lazy import to avoid circular deps)
def _lazy_import_agents():
    """Lazy import of AgentRegistry to avoid circular dependencies."""
    from .agents import AgentRegistry  # noqa: F401
    return AgentRegistry

def _lazy_import_accounts():
    """Lazy import of AccountRegistry to avoid circular dependencies."""
    from .accounts import AccountRegistry  # noqa: F401
    return AccountRegistry

def _lazy_import_marketplace():
    """Lazy import of MarketplaceRegistry to avoid circular dependencies."""
    from .marketplace import MarketplaceRegistry  # noqa: F401
    return MarketplaceRegistry

# providers is module-level functions
from . import providers

__all__ = [
    # Base class and config
    "BaseRegistry",
    "RegistryConfig",
    # Factory functions
    "get_registry",
    "list_registries",
    "register_registry_type",
    # Utilities
    "validate_item_id",
    "normalize_item_id",
    # Registry types
    "TypedRegistry",
    "SettingsRegistry",
    "Setting",
    "SettingScope",
    "providers",
]
