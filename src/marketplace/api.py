"""Backward-compatibility re-export of marketplace API.

⚠️ DEPRECATED: Import from src.routes.marketplace instead.

This module is kept for backward compatibility. All functionality has been
relocated to src/routes/marketplace.py. Direct imports from this location
will continue to work via re-exports.

Referenz:
    src/routes/marketplace.py — New location for marketplace API
"""

# Re-export router and all models from new location
from src.routes.marketplace import (
    router,
    MarketplaceListResponse,
    MarketplaceInstallRequest,
    MarketplaceInstallResponse,
    list_marketplace_items,
    get_marketplace_item,
    install_marketplace_item,
    uninstall_marketplace_item,
    get_marketplace_providers,
)

__all__ = [
    "router",
    "MarketplaceListResponse",
    "MarketplaceInstallRequest",
    "MarketplaceInstallResponse",
    "list_marketplace_items",
    "get_marketplace_item",
    "install_marketplace_item",
    "uninstall_marketplace_item",
    "get_marketplace_providers",
]
