from collections.abc import Callable
from typing import Any

from .types import ToolMetadata

_A2A_TOOLS: list[ToolMetadata] = []


def register_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
) -> Callable[[Callable], Callable]:
    """Decorator — registers an async callable as an A2A tools.

    Usage::

        @register_tool("ping", "Check agents liveness", {"type": "object", "properties": {}})
        async def ping(args: dict) -> dict:
            return {"status": "ok"}
    """
    def decorator(fn: Callable) -> Callable:
        _A2A_TOOLS.append(ToolMetadata(name=name, description=description, schema=input_schema, fn=fn))
        fn._a2a_tool_name = name
        fn._a2a_tool_description = description
        fn._a2a_tool_schema = input_schema
        return fn

    return decorator


def get_all_tools() -> list[ToolMetadata]:
    """Return all tools registered via @register_tool."""
    return list(_A2A_TOOLS)
