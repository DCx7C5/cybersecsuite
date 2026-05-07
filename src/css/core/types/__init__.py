"""Core types for CyberSecSuite — flat structure (Phase 6 P1).

Provider headers will be YAML-driven (Phase 6 P2), not Python files.
"""

# Base protocol and abstract classes (from base_client.py)
from .base_client import (  # noqa: F401
    ProviderType,
    BaseMessage,
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    StreamingHandler,
    BaseApiServiceClient,
)

# Base communicator protocol
from .base_protocols import BaseCommunicator  # noqa: F401

# Base registry
from .base_registry import BaseRegistry  # noqa: F401

# Protocol classes (Phase 6 P1)
from .protocols import (  # noqa: F401
    AgentLike,
    SkillLike,
    ToolLike,
    TeamMemberLike,
)

# Base entity types (msgspec.Struct, Phase 6 P1)
from .base_entity import (  # noqa: F401
    BaseEntity,
    BaseAgent,
    BaseTool,
    BaseSkill,
    BaseRole,
)

# Entity headers (msgspec.Struct, Phase 6 P1)
from .base_headers import (  # noqa: F401
    BaseHeader,
    BaseAgentHeader,
    BaseSkillHeader,
    BaseAccountHeader,
    BaseToolHeader,
    BaseRoleHeader,
)

# Capabilities
from .capabilities import (  # noqa: F401
    Capability,
    CapabilityType,
    CapabilityRegistry,
    DEFAULT_CAPABILITIES,
    ModelCapabilities,
)

# Context types (msgspec.Struct)
from .context import (  # noqa: F401
    ConversationContext,
    ModelContext,
    ExecutionContext,
    ContextConfig,
)

# Hook events
from .hook_events import HookContext, HookErrorStrategy  # noqa: F401

# Core entities (concrete, from module locations)
from css.core.accounts.types import Account  # noqa: F401

__all__ = [
    # Base
    "HookErrorStrategy",
    # Query
    "Query",
    "QueryHeader",
    # SDK
    "LocalSDKBase",
    # Universal client
    "UnifiedLLMClient",
    "LLMAdapter",
]
