"""FastAPI endpoints for MCP server lifecycle management."""

from fastapi import APIRouter, HTTPException, status

from css.core.logger import getLogger

from .models import McpServerConfigRecord
from .registry import get_mcp_registry

logger = getLogger(__name__)

router = APIRouter(prefix="/mcp/servers", tags=["mcp"])

# Get the global MCP runtime registry singleton
_registry = get_mcp_registry()


@router.post(
    "/{server_id}/start",
    response_model=dict[str, object],
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_mcp_server(server_id: str) -> dict[str, object]:
    """
    Start an MCP server connection.

    Loads configuration from database, connects client, and registers
    in the MCP runtime registry.

    Args:
        server_id: Unique server identifier

    Returns:
        Operation status and server metadata

    Raises:
        HTTPException 404: Server configuration not found
        HTTPException 409: Server already connected
        HTTPException 500: Connection failed
    """
    try:
        # Load persisted config from database
        record = await McpServerConfigRecord.get_or_none(server_id=server_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP server configuration not found: {server_id}",
            )

        config = record.to_schema()

        # Check if already connected
        if server_id in _registry._connections:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"MCP server already connected: {server_id}",
            )

        # Register config if not already registered
        if server_id not in _registry._servers:
            await _registry.register(server_id, config)

        # Connect to server
        await _registry.connect(server_id)

        logger.info(f"Started MCP server: {server_id}")
        return {
            "status": "started",
            "server_id": server_id,
            "name": config.name,
            "transport": config.transport.value,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to start MCP server {server_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start MCP server: {str(exc)}",
        ) from exc


@router.post(
    "/{server_id}/stop",
    response_model=dict[str, object],
    status_code=status.HTTP_200_OK,
)
async def stop_mcp_server(server_id: str) -> dict[str, object]:
    """
    Stop an MCP server connection.

    Disconnects the client and removes from runtime registry.

    Args:
        server_id: Unique server identifier

    Returns:
        Operation status

    Raises:
        HTTPException 404: Server not connected
        HTTPException 500: Disconnection failed
    """
    try:
        if server_id not in _registry._connections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP server not connected: {server_id}",
            )

        # Disconnect from server
        await _registry.disconnect(server_id)

        logger.info(f"Stopped MCP server: {server_id}")
        return {
            "status": "stopped",
            "server_id": server_id,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to stop MCP server {server_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop MCP server: {str(exc)}",
        ) from exc


@router.post(
    "/{server_id}/restart",
    response_model=dict[str, object],
    status_code=status.HTTP_202_ACCEPTED,
)
async def restart_mcp_server(server_id: str) -> dict[str, object]:
    """
    Restart an MCP server connection (stop then start).

    Args:
        server_id: Unique server identifier

    Returns:
        Operation status and server metadata

    Raises:
        HTTPException 404: Server configuration not found
        HTTPException 500: Restart failed
    """
    try:
        # Stop if connected
        if server_id in _registry._connections:
            await _registry.disconnect(server_id)

        # Load persisted config from database
        record = await McpServerConfigRecord.get_or_none(server_id=server_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"MCP server configuration not found: {server_id}",
            )

        config = record.to_schema()

        # Register config if not already registered
        if server_id not in _registry._servers:
            await _registry.register(server_id, config)

        # Connect to server
        await _registry.connect(server_id)

        logger.info(f"Restarted MCP server: {server_id}")
        return {
            "status": "restarted",
            "server_id": server_id,
            "name": config.name,
            "transport": config.transport.value,
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception(f"Failed to restart MCP server {server_id}: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to restart MCP server: {str(exc)}",
        ) from exc


@router.get(
    "/{server_id}/status",
    response_model=dict[str, object],
    status_code=status.HTTP_200_OK,
)
async def get_mcp_server_status(server_id: str) -> dict[str, object]:
    """
    Get status of an MCP server.

    Args:
        server_id: Unique server identifier

    Returns:
        Server status and metadata

    Raises:
        HTTPException 404: Server configuration not found
    """
    # Load persisted config from database
    record = await McpServerConfigRecord.get_or_none(server_id=server_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCP server configuration not found: {server_id}",
        )

    config = record.to_schema()
    is_connected = server_id in _registry._connections

    return {
        "server_id": server_id,
        "name": config.name,
        "status": config.status.value,
        "connected": is_connected,
        "transport": config.transport.value,
        "enabled": config.enabled,
        "timeout_seconds": config.timeout_seconds,
    }


@router.get(
    "/",
    response_model=list[dict[str, object]],
    status_code=status.HTTP_200_OK,
)
async def list_mcp_servers() -> list[dict[str, object]]:
    """
    List all MCP server configurations.

    Returns:
        List of server configurations with their current status
    """
    records = await McpServerConfigRecord.all()

    result = []
    for record in records:
        config = record.to_schema()
        is_connected = record.server_id in _registry._connections

        result.append({
            "server_id": record.server_id,
            "name": config.name,
            "status": config.status.value,
            "connected": is_connected,
            "transport": config.transport.value,
            "enabled": config.enabled,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        })

    return result
