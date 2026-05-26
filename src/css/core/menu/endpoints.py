"""Menu endpoints."""

from fastapi import APIRouter, HTTPException, Query

from css.core.db.models.menu import MenuItem, sync_default_menu_items

router = APIRouter(prefix="/api/menu", tags=["menu"])

VALID_MENU_IDS = {"sidebar", "settings", "topnav"}


@router.get("/items")
async def list_menu_items(menu_id: str | None = Query(None)) -> dict[str, object]:
    await sync_default_menu_items()

    # Validate menu_id parameter if provided
    if menu_id is not None and menu_id not in VALID_MENU_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid menu_id. Allowed values: {', '.join(sorted(VALID_MENU_IDS))}",
        )

    # Fetch roots, filtered by menu_id if provided
    if menu_id is not None:
        items = await MenuItem.manager.roots(menu_id=menu_id)
    else:
        items = await MenuItem.manager.roots()

    async def serialize(item: MenuItem) -> dict[str, object]:
        children = await item.ordered_children()
        return {
            "id": int(item.id),
            "parent_id": item.parent_id,
            "menu_id": item.menu_id,
            "name": item.name,
            "url": item.url,
            "icon_path": item.icon_path,
            "icon_url": item.icon_url,
            "order": int(item.order),
            "children": [await serialize(child) for child in children],
        }

    return {
        "items": [await serialize(item) for item in items]
    }
