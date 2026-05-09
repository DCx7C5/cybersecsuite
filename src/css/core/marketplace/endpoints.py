"""Marketplace endpoints — install/uninstall/toggle/upgrade operations."""


from css.core.logger import getLogger
from fastapi import APIRouter, HTTPException, Query, status

from css.core.db.models.marketplace import MarketplaceItem, MarketplaceMeta
from css.core.enums import MarketplaceItemStatus, MarketplaceItemType
from css.core.marketplace.seeder import MarketplaceSeeder
from css.core.marketplace.registry import emit_marketplace_item_changed
from css.core.marketplace.types import (
    InstallRequest,
    InstallResponse,
    ToggleRequest,
    ToggleResponse,
    UninstallRequest,
    UninstallResponse,
    UpgradeRequest,
    UpgradeResponse,
)

log = getLogger(__name__)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.post("/items/install", response_model=InstallResponse)
@router.post("/install", response_model=InstallResponse)
async def install_item(request: InstallRequest) -> InstallResponse:
    """Install a marketplace item.

    The installer will:
    1. Download the item from source URL (or marketplace CDN)
    2. Verify integrity (checksums, signatures)
    3. Extract to appropriate location
    4. Register with local registry
    5. Return installation path
    """
    from css.core.marketplace.installer import PackageInstaller

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
@router.post("/uninstall", response_model=UninstallResponse)
async def uninstall_item(request: UninstallRequest) -> UninstallResponse:
    """Uninstall a marketplace item.

    The uninstaller will:
    1. Check for item existence
    2. Disable the item (if not already disabled)
    3. Remove installation files
    4. Optionally remove configuration
    5. Deregister from registry
    """
    from css.core.marketplace.installer import PackageInstaller

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
@router.post("/toggle", response_model=ToggleResponse)
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
        await emit_marketplace_item_changed(item_slug=item.slug, operation="updated")

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
@router.post("/upgrade", response_model=UpgradeResponse)
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
    kind: MarketplaceItemType | None = Query(None, description="Filter by kind (agents, skills, mcp)"),
    provider: str | None = Query(None, description="Filter by provider"),
    installed_only: bool = Query(False, description="Show only installed items"),
    enabled_only: bool = Query(False, description="Show only enabled items"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
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

        if installed_only:
            query = query.filter(installed_at__not_isnull=True)
        if enabled_only:
            query = query.exclude(status=MarketplaceItemStatus.disabled)

        # Execute query + pagination
        offset = (page - 1) * per_page
        total = await query.count()
        results = await query.offset(offset).limit(per_page)

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
                "tags": item.meta.get("tags", []) if item.meta else [],
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

            if provider and (item.meta or {}).get("provider") != provider:
                continue
            items.append(item_dict)

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
        }

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
                "tags": item.meta.get("tags", []) if item.meta else [],
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


@router.get("/items/by-tags", response_model=dict)
async def list_items_by_tags(
    tags: str = Query(..., description="Comma-separated tag slugs, e.g. 'python,security'"),
    kind: MarketplaceItemType | None = Query(None),
    match_all: bool = Query(False, description="True = item must have ALL tags; False = ANY tag"),
) -> dict:
    """Filter marketplace items by one or more tags.

    Query params:
    - **tags**: comma-separated tag slugs, e.g. ``python,security``
    - **kind**: optional item type filter
    - **match_all**: if True items must carry ALL supplied tags; default is ANY

    Returns:
        ``{"items": [...], "count": int}``
    """
    from css.core.marketplace.cache import marketplace_cache

    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    cache_key = f"tags:{','.join(sorted(tag_list))}:{kind or 'any'}:{match_all}"
    cached = marketplace_cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        query = MarketplaceItem.all()
        if kind:
            query = query.filter(kind=kind)

        all_items = await query
        results = []
        for item in all_items:
            item_tags = set(item.meta.get("tags", []) if item.meta else [])
            tag_set = set(tag_list)
            if match_all:
                matched = tag_set.issubset(item_tags)
            else:
                matched = bool(tag_set & item_tags)

            if matched:
                results.append({
                    "id": item.slug,
                    "name": item.name,
                    "kind": item.kind,
                    "status": item.status,
                    "tags": list(item_tags),
                    "version": item.version,
                })

        response = {"items": results, "count": len(results)}
        marketplace_cache.set(cache_key, response)
        return response

    except Exception as e:
        log.exception("Tags filter error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tag filter failed: {str(e)}",
        )


@router.get("/status", response_model=dict)
async def marketplace_status() -> dict:
    """Get marketplace metadata and aggregate item status."""
    try:
        total_items = await MarketplaceItem.all().count()
        installed_items = await MarketplaceItem.filter(installed_at__not_isnull=True).count()
        enabled_items = await MarketplaceItem.exclude(status=MarketplaceItemStatus.disabled).count()
        meta = await MarketplaceMeta.get_or_none(id=1)

        return {
            "total_items": total_items,
            "installed_items": installed_items,
            "enabled_items": enabled_items,
            "update_available": bool(meta.update_available) if meta else False,
            "last_index_check": meta.last_index_check.isoformat() if meta and meta.last_index_check else None,
            "remote_index_hash": meta.remote_index_hash if meta else None,
            "local_index_hash": meta.local_index_hash if meta else None,
            "version": meta.version if meta else None,
        }
    except Exception as e:
        log.exception("Marketplace status endpoint error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status check failed: {str(e)}",
        )


@router.post("/update-check", response_model=dict)
async def marketplace_update_check() -> dict:
    """Trigger immediate marketplace update check against remote index."""
    try:
        async with MarketplaceSeeder() as seeder:
            version = await seeder.check_for_updates()
        meta = await MarketplaceMeta.get_or_none(id=1)
        return {
            "update_available": bool(meta.update_available) if meta else False,
            "version": version or (meta.version if meta else None),
            "remote_index_hash": meta.remote_index_hash if meta else None,
            "local_index_hash": meta.local_index_hash if meta else None,
        }
    except Exception as e:
        log.exception("Marketplace update-check endpoint error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Update check failed: {str(e)}",
        )


@router.post("/reseed", response_model=dict)
async def marketplace_reseed(force: bool = Query(True, description="Force reseed even if items exist")) -> dict:
    """Reseed marketplace items from remote index."""
    try:
        async with MarketplaceSeeder() as seeder:
            created, skipped = await seeder.seed_if_empty(force=force)
        return {
            "success": True,
            "created": created,
            "skipped": skipped,
            "force": force,
        }
    except Exception as e:
        log.exception("Marketplace reseed endpoint error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reseed failed: {str(e)}",
        )
