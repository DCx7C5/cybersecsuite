"""Core types for CyberSecSuite — flat re-export surface (Phase 6 P1)."""

# ── Enums (single source of truth) ──────────────────────────────────────────
from .base_enums import (
    MessageRole,
    ProviderType,
    CapabilityType,
    MemorySupportMode,
    HookErrorStrategy,
)

# ── Base protocol interfaces ─────────────────────────────────────────────────
from .base_protocols import (
    BaseCommunicator,
    BaseAgentLike,
    BaseSkillLike,
    BaseToolLike,
    BaseTeamMemberLike,
    BaseLLMAdapter,
)

# ── Module protocol ──────────────────────────────────────────────────────────
from .base_module_protocol import CSSModule

# ── Base message/API value objects ───────────────────────────────────────────
from .base_messages import BaseMessage
from css.core.messages.types import (
    Tool,
    ModelMetadata,
    StreamChunk,
    LLMResponse,
    ExecutorResult,
)

# ── Thinking config (extended thinking/reasoning) ───────────────────────────
from css.core.sdks.thinking import ThinkingConfig

# ── Base entity + header types ───────────────────────────────────────────────
from .base_entity import (
    BaseEntity,
    BaseAgent,
    BaseTool,
    BaseSkill,
    BaseRole,
)

from .base_entity import (
    BaseAgentHeader,
    BaseSkillHeader,
    BaseAccountHeader,
    BaseToolHeader,
    BaseRoleHeader,
)

# ── Base serializers ─────────────────────────────────────────────────────────
from css.core.db.serializers import (
    SerializerValidationError,
    BaseSerializer,
    BaseModelSerializer,
    BaseListSerializer,
)

# ── Base client + SDK ────────────────────────────────────────────────────────
from .base_client import (
    BaseStreamingHandler,
    BaseApiServiceClient,
)

from .base_sdk import BaseLocalSDK

# ── Base emitter ──────────────────────────────────────────────────────────────
from .base_emitter import BaseEmitterClass

# ── Base registry + universal client ────────────────────────────────────────
from .base_registry import BaseRegistry

from css.core.sdks import (
    SDKRegistry,
    CSSLLMClient,
    register_sdk,
    get_sdk,
    clear_sdk_cache,
    list_registered_sdks,
)
from css.core.sdks.adapters import (
    AnthropicNativeAdapter,
    COMPUTER_USE_TOOLS,
    OpenAINativeAdapter,
    BUILTIN_TOOLS,
    HttpProviderAdapter,
    OllamaAdapter,
)
from css.core.sdks.model_mapper import ModelNameMapper

# ── Capabilities ─────────────────────────────────────────────────────────────
from css.core.capabilities.models import (
    Capability,
    CapabilityRegistry,
    ModelCapabilities,
)

# ── Context types ─────────────────────────────────────────────────────────────
from css.core.sdks.context import (
    ConversationContext,
    ModelContext,
    ExecutionContext,
    ContextConfig,
)

# ── Hook event types ─────────────────────────────────────────────────────────
from css.core.events.hook_events import HookContext

# ── Query types ───────────────────────────────────────────────────────────────
from css.core.query import Query, QueryHeader

# ── Provider spec types ───────────────────────────────────────────────────────
from .providers import (
    ProviderAuth,
    ProviderOAuthFlow,
    ProviderEndpoint,
    ProviderCapabilities,
    ProviderSpec,
    decode_provider_spec_yaml,
    decode_provider_spec_file,
)

# ── Base workflow types ───────────────────────────────────────────────────────
from .base_workflow import BaseTask, BaseTaskScope

# ── Error mappers ─────────────────────────────────────────────────────────────
from .base_error_mapper import BaseErrorMapper
from css.core.errors.mappers import (
    AnthropicErrorMapper,
    OpenAIErrorMapper,
    OllamaErrorMapper,
    GeminiErrorMapper,
    GroqErrorMapper,
    XAIErrorMapper,
    ERROR_MAPPERS,
    map_provider_error,
)

# ── QoL output controls ───────────────────────────────────────────────────────
from css.core.settings.qol import (
    QoLToggle,
    QoLSettings,
    toggle_description,
)

# Lazy import to break circular dependency chain:
#   types.__init__ → adapter_bridge → registry → core.tools.base → executor → events → emitter → base_emitter → types.__init__
def __getattr__(name: str):
    if name == "register_adapter_tools":
        from css.modules.tools.adapter_bridge import register_adapter_tools
        return register_adapter_tools
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return __all__


__all__ = [
    # enums
    "MessageRole",
    "ProviderType",
    "CapabilityType",
    "MemorySupportMode",
    "HookErrorStrategy",
    # protocols
    "BaseCommunicator",
    "BaseAgentLike",
    "BaseSkillLike",
    "BaseToolLike",
    "BaseTeamMemberLike",
    "BaseLLMAdapter",
    "CSSModule",
    # messages
    "BaseMessage",
    "Tool",
    "ModelMetadata",
    "StreamChunk",
    "LLMResponse",
    "ExecutorResult",
    # thinking/reasoning
    "ThinkingConfig",
    # entities
    "BaseEntity",
    "BaseAgent",
    "BaseTool",
    "BaseSkill",
    "BaseRole",
    # headers
    "BaseAgentHeader",
    "BaseSkillHeader",
    "BaseAccountHeader",
    "BaseToolHeader",
    "BaseRoleHeader",
    # serializers
    "SerializerValidationError",
    "BaseSerializer",
    "BaseModelSerializer",
    "BaseListSerializer",
    # client/SDK
    "BaseStreamingHandler",
    "BaseApiServiceClient",
    "BaseLocalSDK",
    "BaseEmitterClass",
    "BaseRegistry",
    "SDKRegistry",
    "CSSLLMClient",
    "register_sdk",
    "get_sdk",
    "clear_sdk_cache",
    "list_registered_sdks",
    # capabilities
    "Capability",
    "CapabilityRegistry",
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
    # provider specs
    "ProviderAuth",
    "ProviderOAuthFlow",
    "ProviderEndpoint",
    "ProviderCapabilities",
    "ProviderSpec",
    "decode_provider_spec_yaml",
    "decode_provider_spec_file",
    # workflow bases (task only — team lives in modules/teams)
    "BaseTask",
    "BaseTaskScope",
    # adapters
    "AnthropicNativeAdapter",
    "COMPUTER_USE_TOOLS",
    "OpenAINativeAdapter",
    "BUILTIN_TOOLS",
    "HttpProviderAdapter",
    "OllamaAdapter",
    # model mapper
    "ModelNameMapper",
    # tool bridge
    "register_adapter_tools",  # pyright: ignore[reportUnsupportedDunderAll]
    # qol
    "QoLToggle",
    "QoLSettings",
    "toggle_description",
    # error mappers
    "BaseErrorMapper",
    "AnthropicErrorMapper",
    "OpenAIErrorMapper",
    "OllamaErrorMapper",
    "GeminiErrorMapper",
    "GroqErrorMapper",
    "XAIErrorMapper",
    "ERROR_MAPPERS",
    "map_provider_error",
]
