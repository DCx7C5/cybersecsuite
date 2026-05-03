# @types — Core Type Definitions

**Location**: `src/css/core/types/`

**Responsibility**: Base classes, enums, data models, Pydantic schemas used across all modules.

---

## Overview

Core types module exports:
- **Base classes** — Entities, communicators, contexts
- **Enums** — Capability types, message roles, provider types
- **Data models** — Pydantic models for API requests/responses
- **Specialized types** — Headers, hooks, query models

---

## Key Modules

### 1. **base.py**

Core abstractions:

```python
class BaseApiServiceClient:
    """Base class for LLM API clients."""
    pass

class BaseCommunicator:
    """Base class for A2A communication."""
    pass

class BaseContext:
    """Base context for request execution."""
    pass

class ExecutorResult:
    """Result of task execution."""
    pass

class LLMResponse:
    """Response from LLM provider."""
    pass

class BaseMessage:
    """Message in conversation."""
    pass

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ModelMetadata:
    """Metadata about an LLM model."""
    pass

class ProviderType(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    # ... others

class StreamChunk:
    """Streamed response chunk."""
    pass

class StreamingHandler:
    """Handler for streaming responses."""
    pass

class Tool:
    """Tool available to agent."""
    pass
```

### 2. **capabilities.py**

Capability discovery types:

```python
class CapabilityType(str, Enum):
    STREAMING = "streaming"
    VISION = "vision"
    TOOL_USE = "tool_use"
    JSON_MODE = "json_mode"
    LONG_CONTEXT = "long_context"

class Capability:
    """Single capability."""
    name: str
    supported: bool

class ModelCapabilities:
    """All capabilities for a model."""
    model: str
    provider: str
    capabilities: dict[CapabilityType, bool]

class CapabilityRegistry:
    """Registry of model capabilities."""
    pass

DEFAULT_CAPABILITIES: dict[str, ModelCapabilities]
```

### 3. **context.py**

Execution context types:

```python
class ConversationContext:
    """Context for ongoing conversation."""
    pass

class ContextConfig:
    """Configuration for context."""
    pass

class ExecutionContext:
    """Context for task execution."""
    pass

class ModelContext:
    """Context for model calls."""
    pass
```

### 4. **entities.py**

Domain entities (Pydantic models):

```python
class BaseEntity:
    """Base entity model."""
    id: str
    created_at: datetime
    updated_at: datetime

class Account(BaseEntity):
    """User account."""
    username: str
    email: str

class Agent(BaseEntity):
    """Intelligent agent."""
    name: str
    role: str
    capabilities: list[str]

class BaseAgent(BaseEntity):
    """Base agent model."""
    pass

class Role(BaseEntity):
    """Agent role definition."""
    name: str
    permissions: list[str]

class BaseRole(BaseEntity):
    """Base role model."""
    pass

class Skill(BaseEntity):
    """Agent skill."""
    name: str
    description: str

class BaseSkill(BaseEntity):
    """Base skill model."""
    pass

class Tool(BaseEntity):
    """Tool available to agents."""
    name: str
    description: str
    parameters: dict

class BaseTool(BaseEntity):
    """Base tool model."""
    pass

class BaseToolHeader:
    """Header info for tool."""
    pass

def get_role(role_name: str) -> Role:
    """Get role by name."""
    pass
```

### 5. **headers.py**

Request/response header types:

```python
class BaseHeader:
    """Base header type."""
    pass

class BaseAccountHeader(BaseHeader):
    """Account header."""
    pass

class BaseAgentHeader(BaseHeader):
    """Agent header."""
    pass

class BaseRoleHeader(BaseHeader):
    """Role header."""
    pass

class BaseSkillHeader(BaseHeader):
    """Skill header."""
    pass
```

### 6. **hook_events.py**

Event/hook types:

```python
class HookContext:
    """Context for hook execution."""
    pass

class HookErrorStrategy:
    """Error handling strategy for hooks."""
    pass
```

### 7. **query.py**

Query/search types:

```python
class Query:
    """Query for searching."""
    pass

class QueryHeader:
    """Header for query."""
    pass
```

### 8. **sdk_local.py**

Local SDK base:

```python
class LocalSDKBase:
    """Base class for local SDK clients."""
    pass
```

---

## Import Structure

**File**: `src/css/core/types/__init__.py`

```python
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
from .query import Query, QueryHeader
from .sdk_local import LocalSDKBase

__all__ = [
    # base
    "BaseApiServiceClient",
    "BaseCommunicator",
    "BaseContext",
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
    # capabilities
    "Capability",
    "CapabilityRegistry",
    "CapabilityType",
    "DEFAULT_CAPABILITIES",
    "ModelCapabilities",
    # context
    "ConversationContext",
    "ContextConfig",
    "ExecutionContext",
    "ModelContext",
    # entities
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
    "BaseToolHeader",
    "get_role",
    # headers
    "BaseAccountHeader",
    "BaseAgentHeader",
    "BaseHeader",
    "BaseRoleHeader",
    "BaseSkillHeader",
    # hook_events
    "HookContext",
    "HookErrorStrategy",
    # query
    "Query",
    "QueryHeader",
    # sdk_local
    "LocalSDKBase",
]
```

---

## Usage Patterns

**In modules**:

```python
# src/css/modules/capabilities/__init__.py
from css.core.types import CapabilityType, ModelCapabilities

# Create capability check
caps = ModelCapabilities(
    model="gpt-4",
    provider="openai",
    capabilities={
        CapabilityType.STREAMING: True,
        CapabilityType.VISION: True,
        CapabilityType.TOOL_USE: True,
    }
)
```

**In API endpoints**:

```python
# src/css/modules/chat/endpoints.py
from css.core.types import BaseMessage, MessageRole

# Receive message
class ChatRequest(BaseModel):
    message: BaseMessage
    role: MessageRole

# Return response
class ChatResponse(BaseModel):
    message: BaseMessage
    role: MessageRole = MessageRole.ASSISTANT
```

---

## Integration Points

- **All modules**: Import base classes, enums, data models
- **API endpoints**: Use for request/response validation
- **ORM models**: Extend BaseEntity for Tortoise models
- **Type hints**: Used throughout for type safety

---

**Status**: 🟢 Implemented | **Priority**: 🔴 High | **Last Updated**: 2026-05-03
