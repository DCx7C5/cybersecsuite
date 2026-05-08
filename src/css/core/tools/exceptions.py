"""Core tool exceptions."""

from css.core.exceptions import BaseCoreException


class BaseToolException(BaseCoreException):
    """Base exception for core tool-layer failures."""

    def __init__(
        self,
        message: str,
        *,
        context: dict[str, object] | None = None,
        capture_traceback: bool = False,
    ) -> None:
        super().__init__(
            message=message,
            dir_name="tools",
            capture_traceback=capture_traceback,
            context=context,
        )


class ToolNotFoundError(BaseToolException):
    """Raised when a requested tool identifier does not exist."""

    def __init__(
        self,
        tool_id: str | None = None,
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        merged_context: dict[str, object] = {}
        if context is not None:
            merged_context.update(context)
        if tool_id is not None:
            merged_context["tool_id"] = tool_id
        message = f"Tool not found: {tool_id}" if tool_id is not None else "Tool not found"
        super().__init__(message=message, context=merged_context)


class ToolExecutionError(BaseToolException):
    """Raised when tool execution fails."""

    def __init__(
        self,
        message: str | None = None,
        tool_id: str | None = None,
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        merged_context: dict[str, object] = {}
        if context is not None:
            merged_context.update(context)
        if tool_id is not None:
            merged_context["tool_id"] = tool_id
        resolved_message = message
        if resolved_message is None:
            resolved_message = (
                f"Tool execution failed: {tool_id}" if tool_id is not None else "Tool execution failed"
            )
        super().__init__(message=resolved_message, context=merged_context)


class ToolConfigurationError(BaseToolException):
    """Raised when tool configuration is invalid or incomplete."""

    def __init__(
        self,
        message: str | None = None,
        config_key: str | None = None,
        *,
        context: dict[str, object] | None = None,
    ) -> None:
        merged_context: dict[str, object] = {}
        if context is not None:
            merged_context.update(context)
        if config_key is not None:
            merged_context["config_key"] = config_key
        resolved_message = message
        if resolved_message is None:
            resolved_message = (
                f"Tool configuration error: {config_key}"
                if config_key is not None
                else "Tool configuration error"
            )
        super().__init__(message=resolved_message, context=merged_context)
