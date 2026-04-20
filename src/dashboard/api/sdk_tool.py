"""SDK tool call endpoint - allows direct MCP tool calls from JS."""
from __future__ import annotations

from starlette.requests import Request
from starlette.responses import JSONResponse


async def api_sdk_tool(request: Request) -> JSONResponse:
    """POST /api/sdk-tool — call any cybersec MCP tool directly."""
    body = await request.json()
    tool_name = body.get("tool", "")
    args = body.get("args", {})

    if not tool_name:
        return JSONResponse({"error": "tool name required"}, status=400)

    from csmcp.cybersec import cybersec_server

    tool = next((t for t in cybersec_server.tools if t.name == tool_name), None)
    if not tool:
        return JSONResponse({"error": f"tool {tool_name} not found"}, status=404)

    try:
        result = await tool.handler(args)
        return JSONResponse(result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status=500)