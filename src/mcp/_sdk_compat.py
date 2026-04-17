"""SDK compatibility shim for claude_agent_sdk.

Provides @tool decorator and create_sdk_mcp_server() factory that work both
with and without the official claude_agent_sdk package installed.

When the SDK IS installed, real SDK objects are used.
When not installed, a lightweight shim enables the same API surface.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

try:
    from claude_agent_sdk import tool as sdk_tool, create_sdk_mcp_server as sdk_create_server
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


@dataclass
class ToolMetadata:
    name: str
    description: str
    schema: dict[str, Any]
    fn: Callable


class SdkMcpServer:
    """Lightweight in-process MCP server shim."""

    def __init__(self, name: str, version: str, tools: list[ToolMetadata]) -> None:
        self.name = name
        self.version = version
        self._tools: dict[str, ToolMetadata] = {t.name: t for t in tools}

    @property
    def tool_names(self) -> list[str]:
        return [f"mcp__{self.name}__{t}" for t in self._tools]

    async def call_tool(self, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if tool is None:
            return {"content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {tool_name}"})}], "isError": True}
        try:
            import asyncio, inspect
            if inspect.iscoroutinefunction(tool.fn):
                return await tool.fn(args)
            return tool.fn(args)
        except Exception as exc:
            return {"content": [{"type": "text", "text": json.dumps({"error": str(exc)})}], "isError": True}

    def __repr__(self) -> str:
        return f"SdkMcpServer(name={self.name!r}, tools={list(self._tools)!r})"


_REGISTERED_TOOLS: list[ToolMetadata] = []


def tool(name: str, description: str, schema: dict[str, Any]) -> Callable:
    """Register a function as an SDK MCP tool."""
    if _SDK_AVAILABLE:
        return sdk_tool(name, description, schema)

    def decorator(fn: Callable) -> Callable:
        _REGISTERED_TOOLS.append(ToolMetadata(name=name, description=description, schema=schema, fn=fn))
        fn._sdk_tool_name = name
        fn._sdk_tool_description = description
        fn._sdk_tool_schema = schema
        return fn

    return decorator


def create_sdk_mcp_server(
    name: str,
    version: str,
    tools: list[Callable],
) -> SdkMcpServer:
    """Build an in-process MCP server from a list of @tool-decorated functions."""
    if _SDK_AVAILABLE:
        return sdk_create_server(name=name, version=version, tools=tools)

    meta_list: list[ToolMetadata] = []
    for fn in tools:
        if hasattr(fn, "_sdk_tool_name"):
            meta_list.append(ToolMetadata(
                name=fn._sdk_tool_name,
                description=fn._sdk_tool_description,
                schema=fn._sdk_tool_schema,
                fn=fn,
            ))
        else:
            registered = {t.fn: t for t in _REGISTERED_TOOLS}
            if fn in registered:
                meta_list.append(registered[fn])
    return SdkMcpServer(name=name, version=version, tools=meta_list)
