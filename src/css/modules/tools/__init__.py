"""Tool management module."""

from importlib import import_module
from typing import TYPE_CHECKING

from .types import (
    Tool,
    ToolParameter,
    ToolReturnType,
    ToolSchema,
    HybridToolSchema,
    ManagedTool,
)

if TYPE_CHECKING:
    from .tool_call_loop import ToolCallLoop

__all__ = [
    "Tool",
    "ToolParameter",
    "ToolReturnType",
    "ToolSchema",
    "HybridToolSchema",
    "ManagedTool",
    "ToolCallLoop",
]


def __getattr__(name: str) -> object:
    if name == "ToolCallLoop":
        module = import_module("css.modules.tools.tool_call_loop")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
