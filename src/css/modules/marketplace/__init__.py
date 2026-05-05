"""Marketplace module for CyberSecSuite."""

from css.core.config import MarketplaceConfig
from .enums import MarketplaceStatus, MarketplaceItemStatus, MarketplaceItemType
from .types import (
    MarketplaceBase,
    MarketplaceMetaBase,
    MarketplaceMetaResponse,
    MarketplaceItemBase,
    MarketplaceItemCreate,
    MarketplaceItemUpdate,
    MarketplaceItemResponse,
    InstallRequest,
    InstallResponse,
    UninstallRequest,
    UninstallResponse,
    ToggleRequest,
    ToggleResponse,
    UpgradeRequest,
    UpgradeResponse,
)

# Import seeder and models
try:
    from .seeder import MarketplaceSeeder, seed_marketplace_on_startup
    from .models import MarketplaceItem, MarketplaceMeta
except ImportError:
    # Models may not be available during initial import phase
    pass

# Module-level configuration switches — override via environment variables.
# These are the single reference point for marketplace tuning.
MARKETPLACE_CACHE_TTL = MarketplaceConfig.CACHE_TTL_SECONDS
MARKETPLACE_MAX_RESULTS = MarketplaceConfig.MAX_RESULTS
MARKETPLACE_PAGE_SIZE = MarketplaceConfig.PAGE_SIZE

__all__ = [
    "MARKETPLACE_CACHE_TTL",
    "MARKETPLACE_MAX_RESULTS",
    "MARKETPLACE_PAGE_SIZE",
    "MarketplaceStatus",
    "MarketplaceItemStatus",
    "MarketplaceItemType",
    "MarketplaceBase",
    "MarketplaceMetaBase",
    "MarketplaceMetaResponse",
    "MarketplaceItemBase",
    "MarketplaceItemCreate",
    "MarketplaceItemUpdate",
    "MarketplaceItemResponse",
    "InstallRequest",
    "InstallResponse",
    "UninstallRequest",
    "UninstallResponse",
    "ToggleRequest",
    "ToggleResponse",
    "UpgradeRequest",
    "UpgradeResponse",
    "MarketplaceSeeder",
    "seed_marketplace_on_startup",
    "MarketplaceItem",
    "MarketplaceMeta",
]
