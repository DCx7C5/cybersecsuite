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
from .base import (
    BaseApiServiceClient,
    BaseCommunicator,
    BaseContext,
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

# Note: loader is in core/loader.py, marketplace router is in modules/marketplace/endpoints.py
# These are accessible via core.loader and modules.marketplace respectively

__all__ = [
    # A2A Streaming
    "A2AConfig",
    "PauseRequest",
    "ResponseInjection",
    "ResponseInjectionStrategy",
    "StreamingController",
    "StreamingState",
    "StreamState",
    # Base layer (abstract)
    "BaseCommunicator",
    "BaseContext",
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
]
