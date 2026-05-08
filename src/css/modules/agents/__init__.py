"""Agent management module."""

from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import AgentExecutor, BaseAgent
    from .executor import AgentToolExecutor
    from .models import AgentConfig, AgentResult, AgentTurn, ConversationContext, TokenUsage
    from .types import Agent

__all__ = [
    "BaseAgent",
    "AgentExecutor",
    "AgentResult",
    "Agent",
    "AgentToolExecutor",
    "get_executor",
    "AgentConfig",
    "AgentTurn",
    "ConversationContext",
    "TokenUsage",
]


def __getattr__(name: str) -> object:
    if name in {"BaseAgent", "AgentExecutor"}:
        module = import_module("css.modules.agents.base")
        return getattr(module, name)
    if name in {"AgentToolExecutor", "get_executor"}:
        module = import_module("css.modules.agents.executor")
        return getattr(module, name)
    if name in {"AgentConfig", "AgentResult", "AgentTurn", "ConversationContext", "TokenUsage"}:
        module = import_module("css.modules.agents.models")
        return getattr(module, name)
    if name == "Agent":
        module = import_module("css.modules.agents.types")
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
