"""Marketplace module types for install/uninstall/toggle/upgrade operations.

This module contains all Pydantic types used by the marketplace API.
It is the canonical location for marketplace data models.
"""

from typing import Optional

from pydantic import BaseModel, Field


class MarketplaceItemResponse(BaseModel):
    """Response for a marketplace item."""

    id: str
    name: str
    description: str
    kind: str
    provider: str
    chksum: str
    version: str = "0.1.0"
    status: str = "available"
    enabled: bool = True
    installed: bool = False


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


__all__ = [
    "MarketplaceItemResponse",
    "InstallRequest",
    "InstallResponse",
    "UninstallRequest",
    "UninstallResponse",
    "ToggleRequest",
    "ToggleResponse",
    "UpgradeRequest",
    "UpgradeResponse",
]
