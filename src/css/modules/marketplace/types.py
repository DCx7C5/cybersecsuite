"""Marketplace module types for install/uninstall/toggle/upgrade operations.

This module contains all Pydantic types used by the marketplace API.
It is the canonical location for marketplace data models.

Includes:
- API request/response models
- Pydantic base classes for ORM integration
- CRUD schemas (create/update)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import MarketplaceItemType, MarketplaceItemStatus


# ── Pydantic Base Classes ────────────────────────────────────────────────────────


class MarketplaceBase(BaseModel):
    """Base for all marketplace Pydantic models."""

    class Config:
        from_attributes = True  # ORM mode
        arbitrary_types_allowed = True


# ── Marketplace Meta Models ──────────────────────────────────────────────────────


class MarketplaceMetaBase(MarketplaceBase):
    """Base fields for marketplace metadata."""

    name: str
    description: str
    version: str = "0.1.0"
    sha512: Optional[str] = None
    remote_index_hash: Optional[str] = None
    local_index_hash: Optional[str] = None
    update_available: bool = False
    last_index_check: Optional[datetime] = None


class MarketplaceMetaResponse(MarketplaceMetaBase):
    """Response model for marketplace metadata."""

    id: int
    status: str


# ── Marketplace Item Models ──────────────────────────────────────────────────────


class MarketplaceItemBase(MarketplaceBase):
    """Base fields shared by all marketplace item Pydantic models."""

    id: str
    name: str
    description: str
    kind: MarketplaceItemType
    version: str = "0.1.0"
    tags: list[str] = Field(default_factory=list)
    status: MarketplaceItemStatus = MarketplaceItemStatus.disabled
    meta: dict = Field(default_factory=dict)


class MarketplaceItemCreate(MarketplaceItemBase):
    """Schema for creating a new marketplace item."""

    source_url: Optional[str] = None


class MarketplaceItemUpdate(MarketplaceBase):
    """Schema for updating an existing marketplace item."""

    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    kind: Optional[MarketplaceItemType] = None
    tags: Optional[list[str]] = None
    status: Optional[MarketplaceItemStatus] = None
    meta: Optional[dict] = None


# ── API Response Models ───────────────────────────────────────────────────────────


class MarketplaceItemResponse(MarketplaceItemBase):
    """Response for a marketplace item (extends base with API-specific fields)."""

    provider: str
    chksum: str
    enabled: bool = True
    installed: bool = False


# ── API Request/Response Models ─────────────────────────────────────────────────


class InstallRequest(BaseModel):
    """Request to install a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    source_url: Optional[str] = Field(default=None, description="Override source URL")


class InstallResponse(BaseModel):
    """Response for install operation."""

    success: bool
    item_id: str
    message: str
    installed_path: Optional[str] = None
    error: Optional[str] = None


class UninstallRequest(BaseModel):
    """Request to uninstall a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    purge_config: bool = Field(default=False, description="Remove item configuration")


class UninstallResponse(BaseModel):
    """Response for uninstall operation."""

    success: bool
    item_id: str
    message: str
    error: Optional[str] = None


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
    error: Optional[str] = None


class UpgradeRequest(BaseModel):
    """Request to upgrade a marketplace item."""

    item_id: str = Field(..., description="Kebab-case item ID")
    target_version: Optional[str] = Field(
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
    backup_path: Optional[str] = None
    error: Optional[str] = None
