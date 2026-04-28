"""Marketplace REST API endpoints — install, uninstall, toggle, upgrade."""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


# ============================================================================
# Pydantic models
# ============================================================================


class MarketplaceItemResponse(BaseModel):
    """Response for a marketplace item."""

    id: str
    name: str
    description: str
    kind: str
    provider: str
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
    target_version: Optional[str] = Field(default=None, description="Specific version to upgrade to")
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


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/items/install", response_model=InstallResponse)
async def install_item(request: InstallRequest) -> InstallResponse:
    """Install a marketplace item.
    
    The installer will:
    1. Download the item from source URL (or marketplace CDN)
    2. Verify integrity (checksums, signatures)
    3. Extract to appropriate location
    4. Register with local registry
    5. Return installation path
    """
    from core.marketplace.installer import PackageInstaller

    try:
        installer = PackageInstaller()
        result = await installer.install_package(
            item_id=request.item_id,
        )

        if result.success:
            return InstallResponse(
                success=True,
                item_id=request.item_id,
                message=f"Successfully installed {request.item_id}",
                installed_path=result.install_path,
            )
        else:
            return InstallResponse(
                success=False,
                item_id=request.item_id,
                message="Installation failed",
                error=result.error or "Unknown error",
            )
    except Exception as e:
        log.exception(f"Install endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Installation failed: {str(e)}",
        )


@router.post("/items/uninstall", response_model=UninstallResponse)
async def uninstall_item(request: UninstallRequest) -> UninstallResponse:
    """Uninstall a marketplace item.
    
    The uninstaller will:
    1. Check for item existence
    2. Disable the item (if not already disabled)
    3. Remove installation files
    4. Optionally remove configuration
    5. Deregister from registry
    """
    from core.marketplace.installer import PackageInstaller

    try:
        installer = PackageInstaller()
        result = await installer.uninstall_package(
            item_id=request.item_id,
        )

        if result.success:
            return UninstallResponse(
                success=True,
                item_id=request.item_id,
                message=f"Successfully uninstalled {request.item_id}",
            )
        else:
            return UninstallResponse(
                success=False,
                item_id=request.item_id,
                message="Uninstallation failed",
                error=result.error or "Unknown error",
            )
    except Exception as e:
        log.exception(f"Uninstall endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Uninstallation failed: {str(e)}",
        )


@router.post("/items/toggle", response_model=ToggleResponse)
async def toggle_item(request: ToggleRequest) -> ToggleResponse:
    """Enable or disable a marketplace item.
    
    Disabling an item:
    - Removes it from active loaders (agents, skills, MCPs)
    - Preserves installation and configuration
    - Can be re-enabled later
    
    Enabling an item:
    - Registers with loaders
    - Makes it available to the application
    """
    try:
        from core.marketplace.toggle import set_item_enabled
        
        result = await set_item_enabled(request.item_id, request.enabled)
        
        if result.get("success"):
            action = "enabled" if request.enabled else "disabled"
            return ToggleResponse(
                success=True,
                item_id=request.item_id,
                enabled=request.enabled,
                message=f"Successfully {action} {request.item_id}",
            )
        else:
            return ToggleResponse(
                success=False,
                item_id=request.item_id,
                enabled=request.enabled,
                message="Toggle failed",
                error=result.get("error", "Unknown error"),
            )
    except Exception as e:
        log.exception(f"Toggle endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Toggle failed: {str(e)}",
        )


@router.post("/items/upgrade", response_model=UpgradeResponse)
async def upgrade_item(request: UpgradeRequest) -> UpgradeResponse:
    """Upgrade a marketplace item to a newer version.
    
    The upgrader will:
    1. Check if upgrade is available
    2. Create backup of current version (if enabled)
    3. Download new version
    4. Verify integrity
    5. Atomically swap installations
    6. Keep backup for rollback if needed
    """
    # TODO: Implement upgrade logic (not yet in PackageInstaller)
    # For now, return not implemented
    log.warning(f"Upgrade requested for {request.item_id} but not yet implemented")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Marketplace item upgrade is not yet implemented",
    )


@router.get("/items", response_model=dict)
async def list_marketplace_items(
    kind: Optional[str] = Query(None, description="Filter by kind (agent, skill, mcp, combo, template)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    installed_only: bool = Query(False, description="Show only installed items"),
    enabled_only: bool = Query(False, description="Show only enabled items"),
) -> dict:
    """List all marketplace items with optional filtering.
    
    Returns paginated list of marketplace items with metadata.
    """
    try:
        # TODO: Query marketplace registry/database
        # For now, return stub response
        return {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "filters": {
                "kind": kind,
                "provider": provider,
                "installed_only": installed_only,
                "enabled_only": enabled_only,
            },
        }
    except Exception as e:
        log.exception(f"List endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Listing failed: {str(e)}",
        )


@router.get("/items/{item_id}", response_model=dict)
async def get_marketplace_item(item_id: str) -> dict:
    """Get details for a specific marketplace item.
    
    Returns full metadata, installation status, version info, etc.
    """
    try:
        # TODO: Fetch item from registry/database
        return {
            "item": None,
            "found": False,
            "message": f"Item {item_id} not found",
        }
    except Exception as e:
        log.exception(f"Get item endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}",
        )
