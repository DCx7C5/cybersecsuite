import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from modules.marketplace.types import (
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
        from core.db.models.marketplace import (
            Agent,
            Skill,
            MarketplaceMCP,
        )

        items = []

        # Query all models
        agents = await Agent.all() if not kind or kind == "agent" else []
        skills = await Skill.all() if not kind or kind == "skill" else []
        mcps = await MarketplaceMCP.all() if not kind or kind == "mcp" else []

        # Combine all items
        for agent in agents:
            item_dict = {
                "id": agent.name.lower().replace(" ", "-"),
                "name": agent.name,
                "description": agent.description,
                "kind": "agent",
                "status": agent.status,
                "enabled": agent.status != "disabled",
                "installed": agent.status == "installed",
                "version": agent.version,
                "category": agent.category,
                "tags": agent.tags or [],
            }
            if not enabled_only or agent.status != "disabled":
                if not installed_only or agent.status == "installed":
                    items.append(item_dict)

        for skill in skills:
            item_dict = {
                "id": skill.name.lower().replace(" ", "-"),
                "name": skill.name,
                "description": skill.description,
                "kind": "skill",
                "status": skill.status,
                "enabled": skill.status != "disabled",
                "installed": skill.status == "installed",
                "version": skill.version,
                "category": skill.category,
                "tags": skill.tags or [],
            }
            if not enabled_only or skill.status != "disabled":
                if not installed_only or skill.status == "installed":
                    items.append(item_dict)

        for mcp in mcps:
            item_dict = {
                "id": mcp.name.lower().replace(" ", "-"),
                "name": mcp.name,
                "description": mcp.description,
                "kind": "mcp",
                "status": mcp.status,
                "enabled": mcp.status != "disabled",
                "installed": mcp.status == "installed",
                "version": mcp.version,
                "category": mcp.category,
                "tags": mcp.tags or [],
                "tools_count": mcp.tools_count,
            }
            if not enabled_only or mcp.status != "disabled":
                if not installed_only or mcp.status == "installed":
                    items.append(item_dict)

        return {
            "items": items,
            "total": len(items),
            "page": 1,
            "per_page": len(items),
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
        from models import (
            MarketplaceAgent,
            MarketplaceSkill,
            MarketplaceMCP,
            MarketplacePrompt,
            MarketplaceTemplate,
        )

        # Convert kebab-case to title case for search
        title_case = " ".join(w.capitalize() for w in item_id.split("-"))

        # Try to find in each model
        agent = await Agent.get_or_none(name=title_case)
        if agent:
            return {
                "item": {
                    "id": item_id,
                    "name": agent.name,
                    "description": agent.description,
                    "kind": "agent",
                    "status": agent.status,
                    "enabled": agent.status != "disabled",
                    "installed": agent.status == "installed",
                    "version": agent.version,
                    "category": agent.category,
                    "model": agent.model,
                    "max_turns": agent.max_turns,
                    "tags": agent.tags or [],
                    "created_at": agent.created_at.isoformat() if agent.created_at else None,
                },
                "found": True,
            }

        skill = await Skill.get_or_none(name=title_case)
        if skill:
            return {
                "item": {
                    "id": item_id,
                    "name": skill.name,
                    "description": skill.description,
                    "kind": "skill",
                    "status": skill.status,
                    "enabled": skill.status != "disabled",
                    "installed": skill.status == "installed",
                    "version": skill.version,
                    "category": skill.category,
                    "tags": skill.tags or [],
                    "created_at": skill.created_at.isoformat() if skill.created_at else None,
                },
                "found": True,
            }

        mcp = await MarketplaceMCP.get_or_none(name=title_case)
        if mcp:
            return {
                "item": {
                    "id": item_id,
                    "name": mcp.name,
                    "description": mcp.description,
                    "kind": "mcp",
                    "status": mcp.status,
                    "enabled": mcp.status != "disabled",
                    "installed": mcp.status == "installed",
                    "version": mcp.version,
                    "category": mcp.category,
                    "tags": mcp.tags or [],
                    "tools_count": mcp.tools_count,
                    "repository_url": mcp.repository_url,
                    "documentation_url": mcp.documentation_url,
                    "created_at": mcp.created_at.isoformat() if mcp.created_at else None,
                },
                "found": True,
            }

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
