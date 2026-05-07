"""REST API endpoints for tag management and M2M relationships."""

import logging
from fastapi import APIRouter, HTTPException, Query
from tortoise.expressions import Q

from css.core.db.models.marketplace import MarketplaceItemTag, MarketplaceItem
from css.modules.tags.models import Tag
from css.modules.tools.models import HybridToolDefinitionTag, HybridToolDefinition

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("")
async def list_tags(name_filter: str | None = Query(None)) -> dict:
    """List all tags, optionally filtered by name."""
    query = Tag.all()
    if name_filter:
        query = query.filter(name__icontains=name_filter)
    tags = await query
    return {"count": len(tags), "tags": [t.to_dict() if hasattr(t, "to_dict") else {"id": t.id, "name": t.name} for t in tags]}


@router.get("/suggest")
async def suggest_tags(prefix: str = Query(...), limit: int = Query(10, ge=1, le=50)) -> dict:
    """Suggest tags for autocomplete by matching name/slug prefix."""
    prefix = prefix.strip()
    if not prefix:
        return {"count": 0, "suggestions": []}

    tags = await Tag.filter(Q(name__istartswith=prefix) | Q(slug__istartswith=prefix)).limit(limit)
    return {
        "count": len(tags),
        "suggestions": [{"id": t.id, "name": t.name, "slug": t.slug} for t in tags],
    }


@router.post("")
async def create_tag(name: str, slug: str, color: str = "gray", description: str = "") -> dict:
    """Create new tag."""
    tag = await Tag.create(
        name=name,
        slug=slug,
        color=color,
        description=description
    )
    return {"id": tag.id, "name": tag.name, "slug": tag.slug}


@router.post("/marketplace/{item_id}")
async def add_tag_to_marketplace_item(item_id: str, tag_id: int) -> dict:
    """Add tag to marketplace item."""
    item = await MarketplaceItem.get_or_none(slug=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Marketplace item not found")
    
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    rel, created = await MarketplaceItemTag.get_or_create(
        marketplace_item=item,
        tag=tag
    )
    return {"status": "created" if created else "exists", "item_id": item_id, "tag_id": tag_id}


@router.post("/hybrid-tools/{tool_id}")
async def add_tag_to_hybrid_tool(tool_id: int, tag_id: int) -> dict:
    """Add tag to hybrid tool."""
    tool = await HybridToolDefinition.get_or_none(id=tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Hybrid tool not found")
    
    tag = await Tag.get_or_none(id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    rel, created = await HybridToolDefinitionTag.get_or_create(
        hybrid_tool=tool,
        tag=tag
    )
    return {"status": "created" if created else "exists", "tool_id": tool_id, "tag_id": tag_id}


@router.get("/marketplace")
async def filter_marketplace_by_tags(tags: str = Query(...)) -> dict:
    """Filter marketplace items by tags (comma-separated tag names)."""
    tag_names = [t.strip() for t in tags.split(",")]
    items = await MarketplaceItem.all()
    
    filtered = []
    for item in items:
        item_tags = await item.tags_m2m.all()
        if any(t.tag.name in tag_names for t in item_tags):
            filtered.append({"id": item.slug, "name": item.name})
    
    return {"count": len(filtered), "items": filtered}
