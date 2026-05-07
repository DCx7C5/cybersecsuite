"""Marketplace module types — install/uninstall/toggle/upgrade operations.

Flat DTO models for marketplace API endpoints.
No inheritance chains. Each class = one API endpoint response or request.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from css.core.enums import MarketplaceItemStatus, MarketplaceItemType


# ── Base Models ───────────────────────────────────────────────────


class MarketplaceBase(BaseModel):
    """Base model for marketplace operations."""

    class Config:
        from_attributes = True


class MarketplaceMetaBase(BaseModel):
    """Base model for marketplace metadata."""

    name: str
    version: str


class MarketplaceItemBase(BaseModel):
    """Base model for marketplace items."""

    name: str
    description: str
    kind: MarketplaceItemType


class MarketplaceItemCreate(BaseModel):
    """Request to create/seed a marketplace item."""

    name: str
    description: str
    kind: MarketplaceItemType
    source_url: str
    slug: str = Field(..., description="Unique external identifier (kebab-case)")


class MarketplaceItemUpdate(BaseModel):
    """Request to update a marketplace item."""

    name: str | None = None
    description: str | None = None


class MarketplaceItemResponse(BaseModel):
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
    meta: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


# ── Marketplace Status ────────────────────────────────────────────


class MarketplaceMetaResponse(BaseModel):
    """Marketplace status response."""

    id: int
    name: str
    version: str
    update_available: bool
    last_index_check: datetime | None = None


# ── Item List/Detail ──────────────────────────────────────────────


class ItemListResponse(BaseModel):
    """Item summary for list endpoints."""

    id: str
    name: str
    kind: MarketplaceItemType
    version: str
    installed: bool


class ItemDetailResponse(BaseModel):
    """Full item details."""

    id: str
    name: str
    description: str
    kind: MarketplaceItemType
    version: str
    status: MarketplaceItemStatus
    installed: bool
    installed_at: datetime | None = None
    meta: dict = Field(default_factory=dict)


# ── Install/Uninstall ────────────────────────────────────────────


class InstallRequest(BaseModel):
    """Request to install a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    source_url: str | None = Field(
        default=None, description="Override source URL"
    )


class InstallResponse(BaseModel):
    """Response for install operation."""

    success: bool
    item_id: str
    message: str
    installed_path: str | None = None
    error: str | None = None


class UninstallRequest(BaseModel):
    """Request to uninstall a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    purge_config: bool = Field(
        default=False, description="Remove item configuration"
    )


class UninstallResponse(BaseModel):
    """Response for uninstall operation."""

    success: bool
    item_id: str
    message: str
    error: str | None = None


# ── Toggle Enable/Disable ────────────────────────────────────────


class ToggleRequest(BaseModel):
    """Request to enable/disable a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    enabled: bool = Field(..., description="Enable (True) or disable (False)")


class ToggleResponse(BaseModel):
    """Response for toggle operation."""

    success: bool
    item_id: str
    enabled: bool
    message: str
    error: str | None = None


# ── Upgrade Version ──────────────────────────────────────────────


class UpgradeRequest(BaseModel):
    """Request to upgrade a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    target_version: str | None = Field(
        default=None, description="Specific version to upgrade to"
    )
    backup: bool = Field(default=True, description="Create backup before upgrade")


class UpgradeResponse(BaseModel):
    """Response for upgrade operation."""

    success: bool
    item_id: str
    old_version: str
    new_version: str
    message: str
    backup_path: str | None = None
    error: str | None = None
