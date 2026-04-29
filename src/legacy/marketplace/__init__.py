"""Marketplace — lazy-loading agent/skill registry with provider frontmatter standards.

Referenz:
    plan.md T033 — Marketplace module
    src/marketplace/registry.py — MarketplaceRegistry, get_registry
    src/marketplace/models.py — MarketplaceItem, MarketplaceItemStatus
"""


from core.registries.marketplace import MarketplaceRegistry, get_registry
from core.marketplace.models import MarketplaceItem, MarketplaceItemStatus
from core.marketplace.seeder import seed_marketplace_index
from core.marketplace.toggle import (
    set_item_enabled,
    get_enabled_agents as query_enabled_agents,
    get_enabled_skills as query_enabled_skills,
    get_enabled_mcps as query_enabled_mcps,
)
from core.marketplace.agent_loader import (
    get_enabled_agents as load_enabled_agents,
    filter_enabled_agents,
)
from core.marketplace.skill_loader import (
    get_enabled_skills as load_enabled_skills,
    filter_enabled_skills,
    get_enabled_mcps as load_enabled_mcps,
)

__all__ = [
    "MarketplaceRegistry",
    "get_registry",
    "MarketplaceItem",
    "MarketplaceItemStatus",
    "seed_marketplace_index",
    "set_item_enabled",
    # Query functions (from toggle module)
    "query_enabled_agents",
    "query_enabled_skills",
    "query_enabled_mcps",
    # Loader functions (agent_loader module)
    "load_enabled_agents",
    "filter_enabled_agents",
    # Loader functions (skill_loader module)
    "load_enabled_skills",
    "filter_enabled_skills",
    "load_enabled_mcps",
]
