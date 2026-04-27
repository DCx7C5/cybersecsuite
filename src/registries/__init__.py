"""
Unified registries module — consolidated registry implementations.

Provides a single location for all registry types in CyberSecSuite:
- Agents (A2A agent discovery)
- Accounts (API account index)
- Providers (AI provider configuration)
- Marketplace (installable items)
- Tools (MCP/SDK tool registry)
- API Services (LLM/Public API service configuration)

All registries inherit from BaseRegistry and follow a consistent interface.

Usage::

    from registries import BaseRegistry, get_registry
    from registries.agents import AgentRegistry
    from registries.marketplace import MarketplaceRegistry
    
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
]
