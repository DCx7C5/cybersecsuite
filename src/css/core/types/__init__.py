"""Core types for CyberSecSuite — base classes, enums, data models."""

# Note: A2A types moved to modules.google_a2a.types in Phase 2
# Import from there: from modules.google_a2a import A2AConfig, StreamState, ResponseInjection, etc.
from .base import (
    BaseApiServiceClient,
    BaseCommunicator,
    BaseContext,
    ErrorStrategy,
    ExecutorResult,
    LLMResponse,
    BaseMessage,
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
    BaseToolHeader,
    get_role,
)
from .headers import (
    BaseAccountHeader,
    BaseAgentHeader,
    BaseHeader,
    BaseRoleHeader,
    BaseSkillHeader,
)
from .hook_events import HookContext, HookErrorStrategy
from .query import Query, QueryHeader, Task
from .sdk_local import LocalSDKBase

# Note: Ollama types moved to api_services.ollama.types in Phase 2
# Import from there: from api_services.ollama import OllamaConfig, OllamaModel, etc.

# Note: loader is in core/loader.py, marketplace router is in modules/marketplace/endpoints.py
# These are accessible via core.loader and modules.marketplace respectively

__all__ = [
    # Note: A2A types moved to modules.google_a2a.types (Phase 2 migration)
    # Base layer (abstract)
    "BaseCommunicator",
    "BaseContext",
    # API Service models
    "BaseApiServiceClient",
    "ErrorStrategy",
    "ExecutorResult",
    "LLMResponse",
    "BaseMessage",
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
    # Query/Task types
    "Query",
    "QueryHeader",
    "Task",
    # LocalSDK base (Issue #5)
    "LocalSDKBase",
    # Note: Ollama types moved to api_services.ollama (Phase 2 migration)
]
