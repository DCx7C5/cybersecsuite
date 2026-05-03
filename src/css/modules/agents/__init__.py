"""Agent management and orchestration."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .manager import AgentRegistry, AgentExecutor
from .models import AgentConfig, AgentMetrics, AgentState, AgentMessage
from .enums import AgentStatus, AgentType
from .exceptions import (
    BaseAgentException,
    AgentNotFoundError,
    AgentExecutionError,
    AgentConfigurationError,
)

__all__ = [
    # Manager
    "AgentRegistry",
    "AgentExecutor",
    
    # Models
    "AgentConfig",
    "AgentMetrics",
    "AgentState",
    "AgentMessage",
    
    # Enums
    "AgentStatus",
    "AgentType",
    
    # Exceptions
    "BaseAgentException",
    "AgentNotFoundError",
    "AgentExecutionError",
    "AgentConfigurationError",
]

logger.info("Agents module loaded")
