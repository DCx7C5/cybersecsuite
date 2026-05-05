"""CyberSecSuite core — agents framework, entity system, databases, and infrastructure."""

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

# Base entity classes (from core)
from .types.base import BaseEntity, BaseAgent, BaseRole, BaseSkill, BaseTool

# Concrete entities (from modules)
from css.modules.accounts.types import Account
from css.modules.agents.types import Agent
from css.modules.permissions.types import Role, get as get_role
from css.modules.skills.types import Skill
from css.modules.tools.types import Tool

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
