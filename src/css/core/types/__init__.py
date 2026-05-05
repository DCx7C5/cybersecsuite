"""Core types for CyberSecSuite — base classes, enums, data models."""

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
from .base import (
    BaseAgent,
    BaseEntity,
    BaseRole,
    BaseSkill,
    BaseTool,
)
from .base.base_header import BaseToolHeader
from css.modules.permissions.types import get as get_role
from css.modules.accounts.types import Account
from css.modules.agents.types import Agent
from css.modules.permissions.types import Role
from css.modules.skills.types import Skill
from css.modules.tools.types import Tool as ToolEntity
from .headers import (
    BaseAccountHeader,
    BaseAgentHeader,
    BaseHeader,
    BaseRoleHeader,
    BaseSkillHeader,
)
from .hook_events import HookContext, HookErrorStrategy
from .query import Query, QueryHeader
from .sdk_local import LocalSDKBase
from .providers import (
    APIHeader,
    APIProviderBase,
    AnthropicHeader,
    AuthRefreshStrategy,
    CohereHeader,
    GeminiHeader,
    GroqHeader,
    LocalHeader,
    LocalProviderBase,
    MistralHeader,
    NScaleLocalHeader,
    OllamaHeader,
    OllamaLocalHeader,
    OllamaProviderBase,
    OpenAIHeader,
    PerplexityHeader,
    RateLimitConfig,
    VLLMLocalHeader,
)

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
    # Query types (Task types are in modules.tasks)
    "Query",
    "QueryHeader",
    # LocalSDK base (Issue #5)
    "LocalSDKBase",
    # Provider base classes (Phase 2)
    "APIProviderBase",
    "LocalProviderBase",
    "OllamaProviderBase",
    # Provider utilities (Phase 2)
    "RateLimitConfig",
    "AuthRefreshStrategy",
    # API headers (Phase 2)
    "APIHeader",
    "OpenAIHeader",
    "AnthropicHeader",
    "GeminiHeader",
    "GroqHeader",
    "MistralHeader",
    "CohereHeader",
    "PerplexityHeader",
    # Local headers (Phase 2)
    "LocalHeader",
    "OllamaLocalHeader",
    "NScaleLocalHeader",
    "VLLMLocalHeader",
    # Ollama-specific (Phase 2)
    "OllamaHeader",
    # Note: Ollama types moved to api_services.ollama (Phase 2 migration)
]
