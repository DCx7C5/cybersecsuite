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
    DataPart,
    FileContent,
    FilePart,
    JSONRPCError,
    JSONRPCRequest,
    JSONRPCResponse,
    Message,
    Part,
    PauseRequest,
    ResponseInjection,
    StreamingState,
    StreamingController,
    Task,
    TaskArtifact,
    TaskStatus,
    TextPart,
    ToolMetadata,
)
from .urls import init_a2a_routes

logger = getLogger(__name__)
