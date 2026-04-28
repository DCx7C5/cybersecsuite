"""Marketplace — lazy-loading agent/skill registry with provider frontmatter standards.

Referenz:
    plan.md T033 — Marketplace module
    src/marketplace/registry.py — MarketplaceRegistry, get_registry
    src/marketplace/models.py — MarketplaceItem, MarketplaceItemStatus
"""


from core.registries.marketplace import MarketplaceRegistry, get_registry
from core.marketplace.models import MarketplaceItem, MarketplaceItemStatus

__all__ = [
    "MarketplaceRegistry",
    "get_registry",
    "MarketplaceItem",
    "MarketplaceItemStatus",
]
