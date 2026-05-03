from css.core.exceptions import BaseModuleException


class BaseAgentException(BaseModuleException):
    """Base exception for the agent module."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, module_name="agent", **kwargs)


class AgentNotFoundError(BaseAgentException):
    """Raised when agent is not found."""

    def __init__(self, agent_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if agent_id:
            ctx["agent_id"] = agent_id
        super().__init__(
            f"Agent not found: {agent_id}" if agent_id else "Agent not found",
            context=ctx,
            **kwargs
        )


class AgentExecutionError(BaseAgentException):
    """Raised when agent execution fails."""

    def __init__(self, message: str = None, agent_id: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if agent_id:
            ctx["agent_id"] = agent_id
        super().__init__(
            message or f"Agent execution failed: {agent_id}" if agent_id else "Agent execution failed",
            context=ctx,
            **kwargs
        )


class AgentConfigurationError(BaseAgentException):
    """Raised when agent configuration is invalid."""

    def __init__(self, message: str = None, config_key: str = None, **kwargs):
        ctx = kwargs.get("context", {})
        if config_key:
            ctx["config_key"] = config_key
        super().__init__(
            message or f"Agent configuration error: {config_key}" if config_key else "Agent configuration error",
            context=ctx,
            **kwargs
        )
