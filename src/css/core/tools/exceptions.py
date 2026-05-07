"""Tool-related exceptions — shared across all tool modules."""

from css.core.exceptions import BaseModuleException


class BaseToolException(BaseModuleException):
    """Base exception for the tool module."""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="tool", **kwargs)


class ToolNotFoundError(BaseToolException):
    """Raised when tool is not found."""
    def __init__(self, tool_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if tool_id:
            ctx["tool_id"] = tool_id
        super().__init__(
            f"Tool not found: {tool_id}" if tool_id else "Tool not found",
            context=ctx,
            **kwargs
        )


class ToolExecutionError(BaseToolException):
    """Raised when tool execution fails."""
    def __init__(self, message: str = None, tool_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if tool_id:
            ctx["tool_id"] = tool_id
        super().__init__(
            message or "Tool execution failed",
            context=ctx,
            **kwargs
        )
