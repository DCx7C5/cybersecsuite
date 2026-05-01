"""Core types for CyberSecSuite — base classes, enums, data models."""

from .a2a_streaming import (
    A2AConfig,
    PauseRequest,
    ResponseInjection,
    ResponseInjectionStrategy,
    StreamingController,
    StreamingState,
    StreamState,
)
from .api_services import (
    BaseApiServiceClient,
    ErrorStrategy,
    ExecutorResult,
    LLMResponse,
    Message,
    MessageRole,
    ModelMetadata,
    ProviderType,
    StreamChunk,
    StreamingHandler,
    Tool,
)
from .base_protocols import BaseCommunicator
from .capabilities import (
    Capability,
    CapabilityRegistry,
    CapabilityType,
    DEFAULT_CAPABILITIES,
    ModelCapabilities,
)
from .context import (
    ConversationContext,
    ContextConfig,
    ExecutionContext,
    ModelContext,
)
from .entities import (
    Account,
    Agent,
    BaseAgent,
    BaseEntity,
    BaseRole,
    BaseSkill,
    BaseTool,
    Role,
    Skill,
    Tool as ToolEntity,
    ToolHeader,
    get_role,
)
from .headers import (
    BaseAccountHeader,
    BaseAgentHeader,
    BaseHeader,
    BaseRoleHeader,
    BaseSkillHeader,
    BaseToolHeader,
)
from .hook_events import HookContext, HookErrorStrategy
from .sdk_local import LocalSDKBase
from .ollama import (
    OllamaCapabilities,
    OllamaConfig,
    OllamaExecutionContext,
    OllamaHealthCheck,
    OllamaModel,
)
from .endpoints import mount_app_routers, router as marketplace_router

__all__ = [
    # A2A Streaming
    "A2AConfig",
    "PauseRequest",
    "ResponseInjection",
    "ResponseInjectionStrategy",
    "StreamingController",
    "StreamingState",
    "StreamState",
    # Base protocols
    "BaseCommunicator",
    # API Service models
    "BaseApiServiceClient",
    "ErrorStrategy",
    "ExecutorResult",
    "LLMResponse",
    "Message",
    "MessageRole",
    "ModelMetadata",
    "ProviderType",
    "StreamChunk",
    "StreamingHandler",
    "Tool",
    # Capabilities
    "Capability",
    "CapabilityRegistry",
    "CapabilityType",
    "DEFAULT_CAPABILITIES",
    "ModelCapabilities",
    # Context
    "ConversationContext",
    "ContextConfig",
    "ExecutionContext",
    "ModelContext",
    # Entities
    "Account",
    "Agent",
    "BaseAgent",
    "BaseEntity",
    "BaseRole",
    "BaseSkill",
    "BaseTool",
    "Role",
    "Skill",
    "ToolEntity",
    "ToolHeader",
    "get_role",
    # Entity headers
    "BaseAccountHeader",
    "BaseAgentHeader",
    "BaseHeader",
    "BaseRoleHeader",
    "BaseSkillHeader",
    "BaseToolHeader",
    # Hook events
    "HookContext",
    "HookErrorStrategy",
    # LocalSDK base (Issue #5)
    "LocalSDKBase",
    # Ollama
    "OllamaCapabilities",
    "OllamaConfig",
    "OllamaExecutionContext",
    "OllamaHealthCheck",
    "OllamaModel",
    # Endpoints
    "mount_app_routers",
    "marketplace_router",
]
