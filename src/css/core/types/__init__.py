"""Core types for CyberSecSuite — flat re-export surface (Phase 6 P1)."""

# ── Enums (single source of truth) ──────────────────────────────────────────
from .enums import (  # noqa: F401
    MessageRole,
    ProviderType,
    CapabilityType,
    HookErrorStrategy,
)

# ── Base protocol interfaces ─────────────────────────────────────────────────
from .base_protocols import (  # noqa: F401
    BaseCommunicator,
    BaseAgentLike,
    BaseSkillLike,
    BaseToolLike,
    BaseTeamMemberLike,
)

# ── Base message/API value objects ───────────────────────────────────────────
from .base_messages import (  # noqa: F401
    BaseMessage,
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    ExecutorResult,
)

# ── Base entity + header types ───────────────────────────────────────────────
from .base_entity import (  # noqa: F401
    BaseEntity,
    BaseAgent,
    BaseTool,
    BaseSkill,
    BaseRole,
)

from .base_headers import (  # noqa: F401
    BaseHeader,
    BaseAgentHeader,
    BaseSkillHeader,
    BaseAccountHeader,
    BaseToolHeader,
    BaseRoleHeader,
)

# ── Base client + SDK ────────────────────────────────────────────────────────
from .base_client import (  # noqa: F401
    StreamingHandler,
    BaseApiServiceClient,
)

from .base_sdk import LocalSDKBase  # noqa: F401

# ── Base registry + universal client ────────────────────────────────────────
from .base_registry import BaseRegistry  # noqa: F401

from .base_universal import (  # noqa: F401
    SDKRegistry,
    UniversalLLMClient,
    register_sdk,
    get_sdk,
    clear_sdk_cache,
    list_registered_sdks,
)

# ── Capabilities ─────────────────────────────────────────────────────────────
from .capabilities import (  # noqa: F401
    Capability,
    CapabilityRegistry,
    DEFAULT_CAPABILITIES,
    ModelCapabilities,
)

# ── Context types ─────────────────────────────────────────────────────────────
from .context import (  # noqa: F401
    ConversationContext,
    ModelContext,
    ExecutionContext,
    ContextConfig,
)

# ── Hook event types ─────────────────────────────────────────────────────────
from .hook_events import HookContext  # noqa: F401

# ── Query types ───────────────────────────────────────────────────────────────
from .query import Query, QueryHeader  # noqa: F401

# ── Base workflow types ───────────────────────────────────────────────────────
from .base_workflow import BaseTeam, BaseTeamScope, BaseTask, BaseTaskScope  # noqa: F401

# ── Core domain entities ──────────────────────────────────────────────────────
from css.core.accounts.types import Account  # noqa: F401

__all__ = [
    # enums
    "MessageRole",
    "ProviderType",
    "CapabilityType",
    "HookErrorStrategy",
    # protocols
    "BaseCommunicator",
    "BaseAgentLike",
    "BaseSkillLike",
    "BaseToolLike",
    "BaseTeamMemberLike",
    # messages
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    # entities
    "BaseEntity",
    "BaseAgent",
    "BaseTool",
    "BaseSkill",
    "BaseRole",
    # headers
    "BaseHeader",
    "BaseAgentHeader",
    "BaseSkillHeader",
    "BaseAccountHeader",
    "BaseToolHeader",
    "BaseRoleHeader",
    # client/SDK
    "StreamingHandler",
    "BaseApiServiceClient",
    "LocalSDKBase",
    "BaseRegistry",
    "SDKRegistry",
    "UniversalLLMClient",
    "register_sdk",
    "get_sdk",
    "clear_sdk_cache",
    "list_registered_sdks",
    # capabilities
    "Capability",
    "CapabilityType",
    "CapabilityRegistry",
    "DEFAULT_CAPABILITIES",
    "ModelCapabilities",
    # context
    "ConversationContext",
    "ModelContext",
    "ExecutionContext",
    "ContextConfig",
    # hooks
    "HookContext",
    "HookErrorStrategy",
    # query
    "Query",
    "QueryHeader",
    # workflow bases
    "BaseTeam",
    "BaseTeamScope",
    "BaseTask",
    "BaseTaskScope",
    # accounts
    "Account",
]
