"""Menu endpoints."""

from fastapi import APIRouter

from css.core.db.models.menu import MenuItem, sync_default_menu_items

router = APIRouter(prefix="/api/menu", tags=["menu"])


@router.get("/items")
async def list_menu_items() -> dict[str, object]:
    items = await sync_default_menu_items()

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
