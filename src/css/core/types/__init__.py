"""Core types for CyberSecSuite — flat structure (Phase 6 P1).

All types at root level (no base/ or providers/ subdirectories).
Provider headers will be YAML-driven (Phase 6 P2), not Python files.
"""

# Base protocol and abstract classes (from base_client.py)
from .base_client import (
    ProviderType,
    MessageRole,
    BaseMessage,
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    ExecutorResult,
    ErrorStrategy,
    StreamingHandler,
    BaseApiServiceClient,
)

# Base communicator protocol
from .base_protocols import BaseCommunicator

# Base registry
from .base_registry import BaseRegistry

# Protocol classes (Phase 6 P1)
from .protocols import (
    AgentLike,
    SkillLike,
    ToolLike,
    TeamMemberLike,
)

# Base entity types (msgspec.Struct, Phase 6 P1)
from .base_entity import (
    BaseEntity,
    BaseAgent,
    BaseTool,
    BaseSkill,
    BaseRole,
)

# Entity headers (msgspec.Struct, Phase 6 P1)
from .headers import (
    BaseHeader,
    BaseAgentHeader,
    BaseSkillHeader,
    BaseAccountHeader,
    BaseToolHeader,
    BaseRoleHeader,
)

# Capabilities
from .capabilities import (
    Capability,
    CapabilityType,
    CapabilityRegistry,
    DEFAULT_CAPABILITIES,
    ModelCapabilities,
)

# Context types (msgspec.Struct)
from .context import (
    ConversationContext,
    ModelContext,
    ExecutionContext,
    ContextConfig,
)

# Hook events
from .hook_events import HookContext, HookErrorStrategy

__all__ = [
    # Base
    "HookErrorStrategy",
    "ProviderType",
    "MessageRole",
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    "ErrorStrategy",
    "StreamingHandler",
    "BaseApiServiceClient",
    "BaseCommunicator",
    "BaseRegistry",
    "AgentLike",
    "SkillLike",
    "ToolLike",
    "TeamMemberLike",
    # Entities (msgspec.Struct)
    "BaseEntity",
    "BaseAgent",
    "BaseTool",
    "BaseSkill",
    "BaseRole",
    # Headers (msgspec.Struct)
    "BaseHeader",
    "BaseAgentHeader",
    "BaseSkillHeader",
    "BaseAccountHeader",
    "BaseToolHeader",
    "BaseRoleHeader",
    # Capabilities
    "Capability",
    "CapabilityType",
    "CapabilityRegistry",
    "DEFAULT_CAPABILITIES",
    "ModelCapabilities",
    # Context
    "ConversationContext",
    "ModelContext",
    "ExecutionContext",
    "ContextConfig",
    # Messages
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    # Hook events
    "HookContext",
    "HookBlockedError",
    # Query
    "Query",
    "QueryHeader",
    # SDK
    "LocalSDKBase",
    # Universal client
    "UnifiedLLMClient",
    "LLMAdapter",
]
