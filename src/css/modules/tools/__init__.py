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

def __getattr__(name: str) -> object:
    if name == "ToolCallLoop":
        module = import_module("css.modules.tools.tool_call_loop")
        return getattr(module, name)
    if name == "register_adapter_tools":
        module = import_module("css.modules.tools.adapter_bridge")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
