# @types — Core Type Definitions

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

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

## Audit Results (2026-05-03)

**Agent 2 Core Infrastructure Audit**

### 5-File Pattern Compliance
⚠️ **EXPANDED PATTERN** — 13 root files (oversized module)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `__init__.py` | Module exports | 54 | ✅ |
| `base.py` | Core abstractions (BaseApiServiceClient, etc) | 200+ | ✅ |
| `capabilities.py` | Capability discovery types | 100+ | ✅ |
| `context.py` | Execution context types | 80+ | ✅ |
| `entities.py` | Domain entities (Pydantic models) | 200+ | ✅ |
| `headers.py` | Request/response header types | 50+ | ✅ |
| `hook_events.py` | Event/hook types | 30+ | ✅ |
| `query.py` | Query/search types | 30+ | ✅ |
| `sdk_local.py` | Local SDK base | 30+ | ✅ |
| `providers/` | **New**: Provider base classes | — | ✅ Added Phase 2 |
| `providers/base_providers.py` | APIProviderBase, LocalProviderBase | 142 | ✅ |
| `providers/ollama_provider.py` | OllamaProviderBase | 155 | ✅ |
| `providers/headers/` | Provider-specific headers | 200+ | ✅ |

**Total**: 13 files (+ 5 provider files from Phase 2), 1654+ LOC → Oversized

**Recommendation**: Consolidate into subdirectories:
- `base/` — base.py, sdk_local.py, entities.py
- `api/` — capabilities.py, headers.py, query.py
- `events/` — hook_events.py, context.py
- `providers/` — Keep separate (Phase 2 architecture)

### Integration Status
- ✅ Depends on: Nothing (foundation layer)
- ✅ Reverse dependencies: 50+ files (core types used everywhere)
- ✅ 12 direct integrations validated
- 🟠 Circular risk: types ← retry ← types (mitigated with lazy imports)

### Implementation Status
- ✅ All base classes defined
- ✅ All enums complete
- ✅ Pydantic models defined
- ✅ Provider hierarchy added (Phase 2)
- ✅ All exports in __all__
- ⚠️ Module organization needs refactoring (13 root files unwieldy)

### Readiness Assessment
🟢 **Production Ready** | 🟡 **Maintenance Concern**: Oversized module — refactor recommended for Phase 4

---

**Status**: 🟢 Implemented | **Priority**: 🔴 High | **Last Updated**: 2026-05-03

---

## Audit Timestamp (2026-05-03)

**Agent 2 Infrastructure Audit — COMPLETE**

- **Status**: ✅ 100% Implemented (BUT OVERSIZED)
- **5-File Pattern**: ❌ Oversized (31 files vs 5-file target)
- **Files**: 31 | **LOC**: 1539
- **Dependencies**: exceptions, retry (2 components)
- **Reverse Dependencies**: 50+ modules (widest reverse dependency)
- **Blockers**: None (refactoring is tech debt, not blocking)
- **Phase Ready**: Phase 2 ⚠️ (Production Ready, REFACTOR in Phase 3)
- **Last Audited**: 2026-05-03 by Agent 2
- **Audit Matrix**: .plan/architecture/core-audit-matrix.md
- **Refactor Plan**: Split into base/, api/, events/, providers/ subdirs (effort: 3-4h)

---

## 🔄 Sync Reminder

> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
