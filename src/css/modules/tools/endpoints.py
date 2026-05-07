"""REST API endpoints for tool registry (hybrid and regular tools).

Provides CRUD operations for hybrid tools and smart resolution endpoints.
All endpoints use async aiohttp patterns.
"""

import logging
from fastapi import APIRouter, HTTPException, Query

from css.modules.tools.registry import get_tool_registry
from css.modules.tools.types import HybridToolSchema
from css.modules.tools.exceptions import ToolNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("/hybrid")
async def list_hybrid_tools(strategy: str | None = Query(None), enabled_only: bool = Query(True)) -> dict:
    """List all registered hybrid tools.
    
    Query params:
    - strategy: Optional filter by composition strategy (sequential, parallel, etc.)
    - enabled_only: If true, only return enabled tools (default: true)
    """
    registry = get_tool_registry()
    tools = registry.list_hybrid_tools(filter_by_strategy=strategy, enabled_only=enabled_only)
    return {
        "count": len(tools),
        "tools": [t.to_dict() for t in tools],
    }


@router.get("")
async def list_tools(provider: str | None = Query(None), enabled_only: bool = Query(True)) -> dict:
    """List regular provider tools, optionally filtered by provider."""
    registry = get_tool_registry()
    tools = registry.list_tools(filter_by_provider=provider, enabled_only=enabled_only)
    return {
        "count": len(tools),
        "tools": [tool.to_dict() for tool in tools],
    }


@router.get("/provider/{provider}")
async def list_provider_tools(provider: str, enabled_only: bool = Query(True)) -> dict:
    """List tools for one provider (e.g. openai, anthropic)."""
    registry = get_tool_registry()
    tools = registry.get_provider_tools(provider)
    if enabled_only:
        tools = [tool for tool in tools if tool.enabled]
    return {
        "provider": provider,
        "count": len(tools),
        "tools": [tool.to_dict() for tool in tools],
    }


@router.get("/hybrid/{tool_id}")
async def get_hybrid_tool(tool_id: str) -> dict:
    """Get specific hybrid tool by ID.
    
    Args:
        tool_id: Hybrid tool identifier (format: "hybrid:name")
    """
    try:
        registry = get_tool_registry()
        tool = registry.get_hybrid_tool(tool_id)
        return tool.to_dict()
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{tool_id}")
async def get_tool(tool_id: str) -> dict:
    """Get one regular tool by ID (format: provider:name)."""
    try:
        registry = get_tool_registry()
        tool = registry.get_tool(tool_id)
        return tool.to_dict()
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/hybrid")
async def create_hybrid_tool(schema: dict) -> dict:
    """Register new hybrid tool.
    
    Body:
    - name: Hybrid tool name
    - description: Tool description
    - component_tools: list of tool_ids
    - composition_strategy: sequential|parallel|conditional|fallback|load_balanced
    - fallback_provider: Optional fallback provider
    - requires_coordination: Boolean
    """
    try:
        hybrid_schema = HybridToolSchema(**schema)
        registry = get_tool_registry()
        registry.register_hybrid_tool(hybrid_schema)
        
        # Persist to database
        await registry.save_hybrid_tool(hybrid_schema)
        
        return {"status": "created", "tool_id": hybrid_schema.tool_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create hybrid tool: {e}")
        raise HTTPException(status_code=500, detail="Failed to create hybrid tool")


@router.put("/hybrid/{tool_id}")
async def update_hybrid_tool(tool_id: str, schema: dict) -> dict:
    """Update existing hybrid tool.
    
    Args:
        tool_id: Hybrid tool identifier
        schema: Updated tool schema
    """
    try:
        registry = get_tool_registry()
        
        # Delete old, register new
        await registry._load_hybrid_tools_from_db()  # Refresh from DB
        
        hybrid_schema = HybridToolSchema(**schema)
        registry.hybrid_tools[tool_id].schema = hybrid_schema
        await registry.save_hybrid_tool(hybrid_schema)
        
        return {"status": "updated", "tool_id": tool_id}
    except Exception as e:
        logger.error(f"Failed to update hybrid tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/hybrid/{tool_id}")
async def delete_hybrid_tool(tool_id: str) -> dict:
    """Remove hybrid tool from registry.
    
    Args:
        tool_id: Hybrid tool identifier
    """
    try:
        registry = get_tool_registry()
        if tool_id not in registry.hybrid_tools:
            raise HTTPException(status_code=404, detail=f"Hybrid tool not found: {tool_id}")
        
        del registry.hybrid_tools[tool_id]
        logger.info(f"Deleted hybrid tool: {tool_id}")
        return {"status": "deleted", "tool_id": tool_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resolve/{tool_id}")
async def resolve_tool(tool_id: str) -> dict:
    """Smart resolver: returns details for any tool (regular or hybrid).
    
    Args:
        tool_id: Tool identifier (format: "provider:name" or "hybrid:name")
    """
    try:
        registry = get_tool_registry()
        tool = registry.resolve_tool(tool_id)
        return tool.to_dict()
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
