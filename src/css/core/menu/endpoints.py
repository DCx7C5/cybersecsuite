"""Menu endpoints."""

from fastapi import APIRouter, HTTPException, Query

from css.core.db.models.menu import MenuItem, sync_default_menu_items
from .serializers import MenuItemSerializer

router = APIRouter(prefix="/api/menu", tags=["menu"])

VALID_MENU_IDS = {"sidebar", "settings", "topnav"}


@router.get("/items")
async def list_menu_items(menu_id: str | None = Query(None)) -> dict[str, object]:
    await sync_default_menu_items()

    if menu_id is not None and menu_id not in VALID_MENU_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid menu_id. Allowed values: {', '.join(sorted(VALID_MENU_IDS))}",
        )

    if menu_id is not None:
        items = await MenuItem.manager.roots(menu_id=menu_id)
    else:
        items = await MenuItem.manager.roots()

    ser = MenuItemSerializer()
    return {
        "items": [await ser.async_to_representation(item) for item in items]
    }
