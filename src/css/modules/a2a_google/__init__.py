"""Google A2A protocol integration module."""


from .endpoints import init_a2a_endpoints, root_router, router
from .enums import A2AErrorCode, MessageRole, PartType, ResponseInjectionStrategy, StreamState, TaskState
from css.core.logger import getLogger
from .exceptions import (
    A2AAgentError,
    A2ACommunicationError,
    A2ATimeoutError,
    BaseA2AExceptions,
    PauseRequestError,
)
from .tools import get_all_tools, register_tool
from .types import (
    A2AConfig,
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    PauseRequest,
    ResponseInjection,
    StreamingState,
    StreamingController,
    ToolMetadata,
)
from .urls import init_a2a_routes

logger = getLogger(__name__)

__all__ = [
    "router",
    "root_router",
    "init_a2a_endpoints",
    "init_a2a_routes",
    "TaskState",
    "MessageRole",
    "PartType",
    "A2AErrorCode",
    "StreamState",
    "ResponseInjectionStrategy",
    "A2AConfig",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCError",
    "PauseRequest",
    "ResponseInjection",
    "StreamingState",
    "StreamingController",
    "ToolMetadata",
    "register_tool",
    "get_all_tools",
    "BaseA2AExceptions",
    "A2AAgentError",
    "A2ACommunicationError",
    "A2ATimeoutError",
    "PauseRequestError",
]
