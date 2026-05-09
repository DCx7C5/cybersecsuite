"""Marketplace module types — install/uninstall/toggle/upgrade operations.

Flat DTO models for marketplace API endpoints.
No inheritance chains. Each class = one API endpoint response or request.
"""

from datetime import datetime

import msgspec

from css.core.enums import MarketplaceItemStatus, MarketplaceItemType


# ── Base Models ───────────────────────────────────────────────────


class MarketplaceBase(msgspec.Struct, frozen=True):
    """Base model for marketplace operations."""
    pass


class MarketplaceMetaBase(msgspec.Struct, frozen=True):
    """Base model for marketplace metadata."""

    name: str
    version: str


class MarketplaceItemBase(msgspec.Struct, frozen=True):
    """Base model for marketplace items."""

    name: str
    description: str
    kind: MarketplaceItemType


class MarketplaceItemCreate(msgspec.Struct, frozen=True):
    """Request to create/seed a marketplace item."""

    name: str
    description: str
    kind: MarketplaceItemType
    source_url: str
    slug: str


class MarketplaceItemUpdate(msgspec.Struct, frozen=True):
    """Request to update a marketplace item."""

    name: str | None = None
    description: str | None = None


class MarketplaceItemResponse(msgspec.Struct, frozen=True):
    """Complete marketplace item response."""

    id: int
    slug: str
    name: str
    description: str
    kind: MarketplaceItemType
    status: MarketplaceItemStatus
    source_url: str
    install_path: str | None = None
    installed_at: datetime | None = None
    meta: dict = {}


# ── Marketplace Status ────────────────────────────────────────────


class MarketplaceMetaResponse(msgspec.Struct, frozen=True):
    """Marketplace status response."""

    id: int
    name: str
    version: str
    update_available: bool
    last_index_check: datetime | None = None


# ── Item List/Detail ──────────────────────────────────────────────


class ItemListResponse(msgspec.Struct, frozen=True):
    """Item summary for list endpoints."""

    id: str
    name: str
    kind: MarketplaceItemType
    version: str
    installed: bool


class ItemDetailResponse(msgspec.Struct, frozen=True):
    """Full item details."""

    id: str
    name: str
    description: str
    kind: MarketplaceItemType
    version: str
    status: MarketplaceItemStatus
    installed: bool
    installed_at: datetime | None = None
    meta: dict = {}


# ── Install/Uninstall ────────────────────────────────────────────


class InstallRequest(msgspec.Struct, frozen=True):
    """Request to install a marketplace item."""

    item_id: str
    source_url: str | None = None


class InstallResponse(msgspec.Struct, frozen=True):
    """Response for install operation."""

    success: bool
    item_id: str
    message: str
    installed_path: str | None = None
    error: str | None = None


class UninstallRequest(msgspec.Struct, frozen=True):
    """Request to uninstall a marketplace item."""

    item_id: str
    purge_config: bool = False


class UninstallResponse(msgspec.Struct, frozen=True):
    """Response for uninstall operation."""

    success: bool
    item_id: str
    message: str
    error: str | None = None


# ── Toggle Enable/Disable ────────────────────────────────────────


class ToggleRequest(msgspec.Struct, frozen=True):
    """Request to enable/disable a marketplace item."""

    item_id: str
    enabled: bool


class ToggleResponse(msgspec.Struct, frozen=True):
    """Response for toggle operation."""

    success: bool
    item_id: str
    enabled: bool
    message: str
    error: str | None = None


# ── Upgrade Version ──────────────────────────────────────────────


class UpgradeRequest(msgspec.Struct, frozen=True):
    """Request to upgrade a marketplace item."""

    item_id: str
    target_version: str | None = None
    backup: bool = True


class UpgradeResponse(msgspec.Struct, frozen=True):
    """Response for upgrade operation."""

    success: bool
    item_id: str
    old_version: str
    new_version: str
    message: str
    backup_path: str | None = None
    error: str | None = None
