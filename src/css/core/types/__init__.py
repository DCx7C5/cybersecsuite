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

# ── Capabilities ─────────────────────────────────────────────────────────────
from css.core.capabilities.models import (
    Capability,
    CapabilityRegistry,
    ModelCapabilities,
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
    BUILTIN_PRESETS,
    QoLSecurityError,
    validate_toggle_combo,
    toggle_description,
)
from .context_management import ContextManagementConfig
from .qol_injector import QoLInjector, FRAGMENTS

# Lazy imports to break circular dependency chains:
#   types.__init__ → sdks.* → ... → api_services → types.__init__
#   types.__init__ → adapter_bridge → registry → core.tools.base → executor → events → emitter → base_emitter → types.__init__
_lazy: dict[str, tuple[str, str]] = {
    # sdks
    "ThinkingConfig": ("css.core.sdks.thinking", "ThinkingConfig"),
    "SDKRegistry": ("css.core.sdks.registry", "SDKRegistry"),
    "CSSLLMClient": ("css.core.sdks.css_client", "CSSLLMClient"),
    "register_sdk": ("css.core.sdks.registry", "register_sdk"),
    "get_sdk": ("css.core.sdks.registry", "get_sdk"),
    "clear_sdk_cache": ("css.core.sdks.registry", "clear_sdk_cache"),
    "list_registered_sdks": ("css.core.sdks.registry", "list_registered_sdks"),
    # sdks adapters
    "AnthropicNativeAdapter": ("css.core.sdks.adapters.anthropic", "AnthropicNativeAdapter"),
    "COMPUTER_USE_TOOLS": ("css.core.sdks.adapters.anthropic", "COMPUTER_USE_TOOLS"),
    "OpenAINativeAdapter": ("css.core.sdks.adapters.openai", "OpenAINativeAdapter"),
    "BUILTIN_TOOLS": ("css.core.sdks.adapters.openai", "BUILTIN_TOOLS"),
    "HttpProviderAdapter": ("css.core.sdks.adapters.http_provider", "HttpProviderAdapter"),
    "OllamaAdapter": ("css.core.sdks.adapters.ollama", "OllamaAdapter"),
    # sdks model mapper
    "ModelNameMapper": ("css.core.sdks.model_mapper", "ModelNameMapper"),
    # sdks context
    "ConversationContext": ("css.core.sdks.context", "ConversationContext"),
    "ModelContext": ("css.core.sdks.context", "ModelContext"),
    "ExecutionContext": ("css.core.sdks.context", "ExecutionContext"),
    "ContextConfig": ("css.core.sdks.context", "ContextConfig"),
    # tool bridge
    "register_adapter_tools": ("css.modules.tools.adapter_bridge", "register_adapter_tools"),
}


def __getattr__(name: str):
    if name in _lazy:
        mod_path, attr = _lazy[name]
        import importlib
        mod = importlib.import_module(mod_path)
        return getattr(mod, attr)
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
    # context management
    "ContextManagementConfig",
    # qol
    "QoLToggle",
    "QoLSettings",
    "BUILTIN_PRESETS",
    "QoLSecurityError",
    "validate_toggle_combo",
    "toggle_description",
    "QoLInjector",
    "FRAGMENTS",
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
