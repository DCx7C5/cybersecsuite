"""Marketplace module for CyberSecSuite."""

from css.core.config import MARKETPLACE_CACHE_TTL_SECONDS, MARKETPLACE_MAX_RESULTS, MARKETPLACE_PAGE_SIZE
from css.core.enums import MarketplaceStatus, MarketplaceItemStatus, MarketplaceItemType
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
from .package_manager import (
    ExtractionError,
    HashVerificationError,
    MarketplaceError,
    PackageInstallResult,
    PackageMetadata,
    PackageNotFoundError,
    batch_install,
    check_for_updates,
    fetch_index,
    install_package,
    verify_hash,
)

# Import seeder and models
try:
    from css.core.db.models.marketplace import MarketplaceItem, MarketplaceMeta
    from .seeder import MarketplaceSeeder, seed_marketplace_on_startup
except ImportError:
    # Models may not be available during initial import phase
    pass

# Module-level configuration switches — override via environment variables.
# These are the single reference point for marketplace tuning.
MARKETPLACE_CACHE_TTL = MARKETPLACE_CACHE_TTL_SECONDS
MARKETPLACE_MAX_RESULTS = MARKETPLACE_MAX_RESULTS
MARKETPLACE_PAGE_SIZE = MARKETPLACE_PAGE_SIZE

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
    "PackageMetadata",
    "PackageInstallResult",
    "MarketplaceError",
    "PackageNotFoundError",
    "HashVerificationError",
    "ExtractionError",
    "fetch_index",
    "verify_hash",
    "check_for_updates",
    "install_package",
    "batch_install",
    "MarketplaceSeeder",
    "seed_marketplace_on_startup",
    "MarketplaceItem",
    "MarketplaceMeta",
]
