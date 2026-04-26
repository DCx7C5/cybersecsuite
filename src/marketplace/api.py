"""Marketplace API endpoints — CRUD operations with listing, filtering, and installation.

Referenz:
    plan.md T033 — Marketplace API
    src/marketplace/models.py — MarketplaceItem, MarketplaceItemStatus
    src/marketplace/registry.py — MarketplaceRegistry
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from marketplace.models import MarketplaceItem, MarketplaceItemStatus
from marketplace.registry import get_registry

logger = logging.getLogger("marketplace.api")

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


class MarketplaceListResponse(BaseModel):
    """Response model for marketplace listing."""

    items: list[MarketplaceItem]
    total: int
    page: int
    size: int
    has_more: bool


class MarketplaceInstallRequest(BaseModel):
    """Request to install a marketplace item."""

    item_id: str = Field(..., description="Kebab-case marketplace item ID")
    install_path: str | None = Field(
        default=None, description="Optional custom installation path"
    )


class MarketplaceInstallResponse(BaseModel):
    """Response after successful installation."""

    item: MarketplaceItem
    message: str


@router.get("/items", response_model=MarketplaceListResponse, status_code=status.HTTP_200_OK)
async def list_marketplace_items(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=500, description="Items per page"),
    kind: str | None = Query(None, description="Filter by kind (agent, skill, combo, template)"),
    provider: str | None = Query(None, description="Filter by provider"),
    status: str | None = Query(None, description="Filter by status"),
    search: str | None = Query(None, description="Search by name or description"),
) -> MarketplaceListResponse:
    """
    List marketplace items with optional filtering.

    Args:
        page: Pagination page number
        size: Items per page
        kind: Optional kind filter
        provider: Optional provider filter
        status: Optional status filter
        search: Optional search term

    Returns:
        Paginated marketplace items

    Raises:
        HTTPException: If query parameters are invalid
    """
    registry = get_registry()

    # Validate enum values
    if kind and kind not in ["agent", "skill", "combo", "template"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid kind: {kind}. Must be one of: agent, skill, combo, template",
        )

    if status and status not in [s.value for s in MarketplaceItemStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {status}",
        )

    # Get all items and apply filters
    all_items = registry.list_items()

    filtered_items = all_items
    if kind:
        filtered_items = [item for item in filtered_items if item.kind == kind]
    if provider:
        filtered_items = [item for item in filtered_items if item.provider == provider]
    if status:
        filtered_items = [item for item in filtered_items if item.status.value == status]
    if search:
        search_lower = search.lower()
        filtered_items = [
            item
            for item in filtered_items
            if search_lower in item.name.lower() or search_lower in item.description.lower()
        ]

    # Apply pagination
    total = len(filtered_items)
    offset = (page - 1) * size
    paginated_items = filtered_items[offset : offset + size]
    has_more = (page * size) < total

    return MarketplaceListResponse(
        items=paginated_items,
        total=total,
        page=page,
        size=size,
        has_more=has_more,
    )


@router.get("/items/{item_id}", response_model=MarketplaceItem, status_code=status.HTTP_200_OK)
async def get_marketplace_item(item_id: str) -> MarketplaceItem:
    """
    Get a single marketplace item by ID.

    Args:
        item_id: Kebab-case item identifier

    Returns:
        MarketplaceItem

    Raises:
        HTTPException: 404 if item not found
    """
    registry = get_registry()
    item = registry.get_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marketplace item not found: {item_id}",
        )

    return item


@router.post(
    "/items/{item_id}/install",
    response_model=MarketplaceInstallResponse,
    status_code=status.HTTP_200_OK,
)
async def install_marketplace_item(
    item_id: str,
    request: MarketplaceInstallRequest,
) -> MarketplaceInstallResponse:
    """
    Install a marketplace item to local workspace.

    Args:
        item_id: Kebab-case item identifier
        request: Installation request with optional custom path

    Returns:
        Installation response with updated item

    Raises:
        HTTPException: 404 if item not found, 400 if already installed, 500 if installation fails
    """
    registry = get_registry()
    item = registry.get_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marketplace item not found: {item_id}",
        )

    if item.status == MarketplaceItemStatus.installed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item already installed: {item_id}",
        )

    try:
        # Perform installation (placeholder for actual implementation)
        updated_item = registry.install_item(
            item_id, custom_path=request.install_path
        )

        logger.info(f"Marketplace item installed: {item_id} → {updated_item.install_path}")

        return MarketplaceInstallResponse(
            item=updated_item,
            message=f"Successfully installed {item.name} to {updated_item.install_path}",
        )
    except Exception as e:
        logger.error(f"Failed to install marketplace item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Installation failed: {str(e)}",
        )


@router.post(
    "/items/{item_id}/uninstall",
    response_model=MarketplaceItem,
    status_code=status.HTTP_200_OK,
)
async def uninstall_marketplace_item(item_id: str) -> MarketplaceItem:
    """
    Uninstall a marketplace item from local workspace.

    Args:
        item_id: Kebab-case item identifier

    Returns:
        Updated item with status reverted to available

    Raises:
        HTTPException: 404 if not found, 400 if not installed, 500 if uninstall fails
    """
    registry = get_registry()
    item = registry.get_item(item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Marketplace item not found: {item_id}",
        )

    if item.status != MarketplaceItemStatus.installed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Item not installed: {item_id}",
        )

    try:
        updated_item = registry.uninstall_item(item_id)
        logger.info(f"Marketplace item uninstalled: {item_id}")
        return updated_item
    except Exception as e:
        logger.error(f"Failed to uninstall marketplace item {item_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Uninstallation failed: {str(e)}",
        )


@router.get(
    "/providers", response_model=dict[str, Any], status_code=status.HTTP_200_OK
)
async def get_marketplace_providers() -> dict[str, Any]:
    """
    Get list of supported providers and their capabilities.

    Returns:
        Dict with provider information
    """
    return {
        "providers": [
            "claude",
            "copilot",
            "cursor",
            "openai",
            "gemini",
            "grok",
            "universal",
        ],
        "kinds": ["agent", "skill", "combo", "template"],
        "statuses": [s.value for s in MarketplaceItemStatus],
    }
