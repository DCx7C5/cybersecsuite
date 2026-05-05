"""Marketplace endpoints — install/uninstall/toggle/upgrade operations."""

from typing import Optional

import logging
from fastapi import APIRouter, HTTPException, Query, status
from css.modules.marketplace.models import MarketplaceItem
from css.modules.marketplace.enums import MarketplaceItemType, MarketplaceItemStatus
from css.modules.marketplace.types import (
    InstallRequest,
    InstallResponse,
    ToggleRequest,
    ToggleResponse,
    UninstallRequest,
    UninstallResponse,
    UpgradeRequest,
    UpgradeResponse,
)

log = logging.getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


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
    from css.modules.marketplace.installer import PackageInstaller

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
    from css.modules.marketplace.installer import PackageInstaller

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
    """Toggle enabled state of a marketplace item."""
    try:
        item = await MarketplaceItem.get_or_none(slug=request.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {request.item_id}",
            )

        item.status = (
            MarketplaceItemStatus.enabled
            if request.enabled
            else MarketplaceItemStatus.disabled
        )
        await item.save()

        return ToggleResponse(
            success=True,
            item_id=request.item_id,
            enabled=request.enabled,
            message=f"Item {'enabled' if request.enabled else 'disabled'} successfully",
        )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Toggle endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Toggle failed: {str(e)}",
        )


@router.post("/items/upgrade", response_model=UpgradeResponse)
async def upgrade_item(request: UpgradeRequest) -> UpgradeResponse:
    """Upgrade a marketplace item.

    Currently not implemented.
    """
    log.warning(f"Upgrade requested for {request.item_id} but not yet implemented")
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Marketplace item upgrade is not yet implemented",
    )


@router.get("/items", response_model=dict)
async def list_marketplace_items(
    kind: Optional[MarketplaceItemType] = Query(None, description="Filter by kind (agents, skills, mcp)"),
    provider: Optional[str] = Query(None, description="Filter by provider"),
    installed_only: bool = Query(False, description="Show only installed items"),
    enabled_only: bool = Query(False, description="Show only enabled items"),
) -> dict:
    """List all marketplace items with optional filtering.

    Returns paginated list of marketplace items with metadata.
    """
    try:
        items = []

        # Build query
        query = MarketplaceItem.all()

        if kind:
            query = query.filter(kind=kind)

        # Execute query
        results = await query.all()

        # Format items
        for item in results:
            item_dict = {
                "id": item.slug,
                "name": item.name,
                "description": item.description,
                "kind": item.kind,
                "status": item.status,
                "enabled": item.status != MarketplaceItemStatus.disabled,
                "installed": item.status == MarketplaceItemStatus.installed,
                "version": item.version,
                "tags": item.tags or [],
            }
            # Add kind-specific fields from meta
            if item.meta:
                if item.kind == MarketplaceItemType.agent and "model" in item.meta:
                    item_dict["model"] = item.meta["model"]
                if item.kind == MarketplaceItemType.agent and "max_turns" in item.meta:
                    item_dict["max_turns"] = item.meta["max_turns"]
                if item.kind == MarketplaceItemType.mcp and "tools_count" in item.meta:
                    item_dict["tools_count"] = item.meta["tools_count"]
                if item.kind == MarketplaceItemType.skill and "repository_url" in item.meta:
                    item_dict["repository_url"] = item.meta["repository_url"]

            items.append(item_dict)

        return {"items": items, "total": len(items)}

    except Exception as e:
        log.exception(f"List items endpoint error: {e}")
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
        # Convert kebab-case to title case for search
        title_case = " ".join(w.capitalize() for w in item_id.split("-"))

        # Try to find in MarketplaceItem
        item = await MarketplaceItem.get_or_none(name=title_case)

        if not item:
            item = await MarketplaceItem.get_or_none(slug=item_id)

        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found: {item_id}",
            )

        return {
            "item": {
                "id": item.slug,
                "name": item.name,
                "description": item.description,
                "kind": item.kind,
                "status": item.status,
                "enabled": item.status != MarketplaceItemStatus.disabled,
                "installed": item.status == MarketplaceItemStatus.installed,
                "version": item.version,
                "tags": item.tags or [],
                "installed_at": item.installed_at.isoformat() if item.installed_at else None,
                "source_url": item.source_url,
                "meta": item.meta,
            },
            "found": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Get item endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Retrieval failed: {str(e)}",
        )
