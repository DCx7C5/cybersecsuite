"""REST API endpoints for tool registry (hybrid and regular tools).

Provides CRUD operations for hybrid tools and smart resolution endpoints.
All endpoints use async aiohttp patterns.
"""

from css.core.logger import getLogger
from fastapi import APIRouter, HTTPException, Query

from css.modules.tools.service import (
    HybridToolPayload,
    create_hybrid_tool as create_hybrid_tool_service,
    delete_hybrid_tool as delete_hybrid_tool_service,
    get_hybrid_tool as get_hybrid_tool_service,
    get_tool as get_tool_service,
    list_hybrid_tools as list_hybrid_tools_service,
    list_tools as list_tools_service,
    resolve_tool as resolve_tool_service,
    update_hybrid_tool as update_hybrid_tool_service,
)
from css.modules.tools.exceptions import ToolNotFoundError

logger = getLogger(__name__)
router = APIRouter(prefix="/api/tools", tags=["tools"])


@router.get("/hybrid")
async def list_hybrid_tools(strategy: str | None = Query(None), enabled_only: bool = Query(True)) -> dict:
    """List all registered hybrid tools.
    
    Query params:
    - strategy: Optional filter by composition strategy (sequential, parallel, etc.)
    - enabled_only: If true, only return enabled tools (default: true)
    """
    tools = list_hybrid_tools_service(strategy=strategy, enabled_only=enabled_only)
    return {
        "count": len(tools),
        "tools": tools,
    }


@router.get("")
async def list_tools(provider: str | None = Query(None), enabled_only: bool = Query(True)) -> dict:
    """List regular provider tools, optionally filtered by provider."""
    tools = list_tools_service(provider=provider, enabled_only=enabled_only)
    return {
        "count": len(tools),
        "tools": tools,
    }


@router.get("/provider/{provider}")
async def list_provider_tools(provider: str, enabled_only: bool = Query(True)) -> dict:
    """List tools for one provider (e.g. OpenAI, anthropic)."""
    tools = list_tools_service(provider=provider, enabled_only=enabled_only)
    return {
        "provider": provider,
        "count": len(tools),
        "tools": tools,
    }


@router.get("/hybrid/{tool_id}")
async def get_hybrid_tool(tool_id: str) -> dict:
    """Get specific hybrid tool by ID.
    
    Args:
        tool_id: Hybrid tool identifier (format: "hybrid:name")
    """
    try:
        return get_hybrid_tool_service(tool_id)
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{tool_id}")
async def get_tool(tool_id: str) -> dict:
    """Get one regular tool by ID (format: provider:name)."""
    try:
        return get_tool_service(tool_id)
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/hybrid")
async def create_hybrid_tool(schema: HybridToolPayload) -> dict:
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
        tool_id = await create_hybrid_tool_service(schema)
        return {"status": "created", "tool_id": tool_id}
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create hybrid tool: {e}")
        raise HTTPException(status_code=500, detail="Failed to create hybrid tool")


@router.put("/hybrid/{tool_id}")
async def update_hybrid_tool(tool_id: str, schema: HybridToolPayload) -> dict:
    """Update existing hybrid tool.
    
    Args:
        tool_id: Hybrid tool identifier
        schema: Updated tool schema
    """
    try:
        updated_tool_id = await update_hybrid_tool_service(tool_id=tool_id, schema_payload=schema)
        return {"status": "updated", "tool_id": updated_tool_id}
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
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
        deleted = await delete_hybrid_tool_service(tool_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Hybrid tool not found: {tool_id}")
        return {"status": "deleted", "tool_id": tool_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resolve/{tool_id}")
async def resolve_tool(tool_id: str) -> dict:
    """Smart resolver: returns details for any tool (regular or hybrid).
    
    Args:
        tool_id: Tool identifier (format: "provider:name" or "hybrid:name")
    """
    try:
        return resolve_tool_service(tool_id)
    except ToolNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
