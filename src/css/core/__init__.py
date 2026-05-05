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

# Communication protocol
from .types.base import BaseCommunicator

# NOTE: Concrete entities (Account, Agent, Role, Skill, Tool) import from modules
# and should NOT be re-exported from core to avoid circular imports.
# Modules depend on core/types.base, so core/__init__ must not import from modules.
# Users should import entities directly: from css.modules.accounts.types import Account

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
    # Base entity framework (abstract)
    "BaseEntity",
    "BaseAgent",
    "BaseRole",
    "BaseSkill",
    "BaseTool",
    # Infrastructure
    "BaseCommunicator",
]
