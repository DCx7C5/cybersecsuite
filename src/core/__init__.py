"""CyberSecSuite core — agent framework, entity system, databases, and infrastructure."""

# Import a2a compatibility module first (registers sys.modules['a2a'] → legacy.a2a)
import a2a  # noqa: F401

# Custom exceptions
from .exceptions import (
    CSSException,
    LLMApiServiceError,
    ApiKeyMissingError,
    ApiKeyInvalidError,
    ProviderConnectionError,
    RateLimitError,
    ModelNotFoundError,
    FeatureNotSupportedError,
    InvalidParameterError,
    StreamingError,
    ProviderTimeoutError,
    LLMHarnessError,
    ContextError,
    CapabilityDiscoveryError,
    ProviderRegistryError,
    A2AStreamingError,
    ResponseInjectionError,
    ModelExecutionError,
    ConfigurationError,
    ValidationError,
    OllamaError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaModelLoadError,
)

# Entity framework & base classes
from .types.entities import (
    Account,
    Agent,
    BaseEntity,
    BaseAgent,
    BaseRole,
    BaseSkill,
    BaseTool,
    Role,
    Skill,
    Tool,
    get_role,
)

# Communication protocol
from .types.base import BaseCommunicator

# Core database (once exported by core.db)
# from .db import DB

# Registry system
# from .registries import BaseRegistry, get_registry

# Hooks & execution context
# from .hooks import (
#     HookContext,
#     HookOutput,
#     PostToolUseEvent,
#     PreToolUseEvent,
# )

__all__ = [
    # Exceptions (Layer 1-2-3)
    "CSSException",
    "LLMApiServiceError",
    "ApiKeyMissingError",
    "ApiKeyInvalidError",
    "ProviderConnectionError",
    "RateLimitError",
    "ModelNotFoundError",
    "FeatureNotSupportedError",
    "InvalidParameterError",
    "StreamingError",
    "ProviderTimeoutError",
    "LLMHarnessError",
    "ContextError",
    "CapabilityDiscoveryError",
    "ProviderRegistryError",
    "A2AStreamingError",
    "ResponseInjectionError",
    "ModelExecutionError",
    "ConfigurationError",
    "ValidationError",
    "OllamaError",
    "OllamaConnectionError",
    "OllamaModelNotFoundError",
    "OllamaModelLoadError",
    # Entity framework
    "Account",
    "Agent",
    "BaseEntity",
    "BaseAgent",
    "BaseRole",
    "BaseSkill",
    "BaseTool",
    "Role",
    "Skill",
    "Tool",
    "get_role",
    # Infrastructure
    "BaseCommunicator",
    # Registries
    # "BaseRegistry",
    # "get_registry",
    # Hooks
    # "HookContext",
    # "HookOutput",
    # "PreToolUseEvent",
    # "PostToolUseEvent",
]
