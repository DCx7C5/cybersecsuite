# @types — Core Type Definitions

**Tracking rule**: `.plan/session.db` is authoritative for todo state. This
local document is the executable implementation specification for `core/types`;
this documentation-movement pass intentionally does not edit the tracker.

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

**Note**: `BaseRegistry` (in this file) uses `AsyncSafeSingletonMeta` for async-safe singleton pattern.

```python
class BaseRegistry(ABC, Generic[T], metaclass=AsyncSafeSingletonMeta):
    """Abstract base class for singleton registries.
    
    Uses AsyncSafeSingletonMeta for async-safe singleton pattern.
    Subclasses like ModelRegistry, MarketplaceItemRegistry inherit this.
    """
    ...

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

**Registry Classes Using AsyncSafeSingletonMeta**:
- `BaseRegistry` (`core/types/base_registry.py`) - metaclass=AsyncSafeSingletonMeta, no ABC
- `ModelRegistry` (`core/models/registry.py`) - metaclass=AsyncSafeSingletonMeta directly
- `MarketplaceItemRegistry` (`core/marketplace/registry.py`) - inherits BaseRegistry
- `ProviderRegistry` (`api_services/registry.py`) - metaclass=AsyncSafeSingletonMeta
- `BaseToolRegistry` (`core/tools/base.py`) - metaclass=AsyncSafeSingletonMeta, no ABC
- `ToolRegistry` (`modules/tools/registry.py`) - inherits BaseToolRegistry
- `SkillRegistry` (`modules/skills/registry.py`) - metaclass=AsyncSafeSingletonMeta
- `McpRuntimeRegistry` (`modules/mcps/registry.py`) - metaclass=AsyncSafeSingletonMeta

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
"""Core types.py for CyberSecSuite — base classes, enums, data models."""

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
- **Workflow contracts**: `base_workflow.py` defines `BaseTask` and `BaseTaskScope` as `msgspec.Struct` base contracts used by task/workflow modules.

---

## Phase 12 - QoL Output Controls

QoL controls change output behavior per resolved scope and must be represented
in cache keys and model requests. `qol.py` already provides the immutable
`QoLToggle` enum and `QoLSettings` value type; the persistence, validation,
injection, API, and telemetry layers remain separate implementation work.

### Implemented Type Surface

| Type | Current contract |
|------|------------------|
| `QoLToggle` | Eight values: `no_thinking`, `no_chat`, `minimal`, `file_only`, `no_markdown`, `structured_only`, `redact_secrets`, `append_audit_trail`. |
| `QoLSettings` | Immutable `msgspec.Struct` with `enabled_toggles`, `scope`, and optional `preset_name`; supports activate/deactivate and dictionary serialization. |

### Required Execution Contract

```text
resolve settings: session -> project -> global
  -> validate incompatible toggle combinations
  -> QoLInjector injects system/message directives
  -> PromptCacheManager computes key including toggle_hash
  -> UnifiedLLMClient sends request through selected adapter
  -> emit sanitized injection telemetry
```

| Surface | Requirement |
|---------|-------------|
| Presets | Load five built-ins: `silent`, `code-only`, `structured`, `audit`, `plain-text`; support user presets and per-agent binding. |
| Validation | Reject dangerous combinations, including `file_only` with `append_audit_trail`, before prompt injection. |
| Scope storage | Persist per-scope settings through a manager/ORM layer; do not use JSON files as runtime truth. |
| Injection | Stateless injector builds cached fragments and injects before provider dispatch for both completion and streaming calls. |
| Cache safety | `toggle_hash = blake2b(sorted(active_toggle_values))`; include it in prompt-cache keys; use an empty value only when no toggles are active. |
| Propagation | Publish/receive changes through the A2A runtime where multi-agent requests share scope configuration. |
| Visibility | Provide CRUD/preset/binding REST operations and emit OpenObserve-safe injection metrics without leaking output secrets. |

### Phase 12 Work Order

| Todo ID | Live status | Deliverable | Dependency |
|---------|-------------|-------------|------------|
| `qol-models-msgspec` | done | `QoLToggle` and `QoLSettings` value types. | Implemented surface to validate against tracker. |
| `qol-dangerous-combos-validator` | pending | Toggle-combination validator and security error. | Types. |
| `qol-builtin-presets` | pending | Built-in preset definitions. | Types and validator. |
| `qol-tortoise-model` | pending | Persisted scoped settings and manager. | ORM conventions. |
| `qol-preset-registry` | pending | Startup-loaded built-in/user preset registry. | Persistence and presets. |
| `qol-injector-service` | pending | Prompt directive construction and fragment cache. | Validator/settings resolution. |
| `qol-unified-client-middleware` | pending | Pre-request integration in unified client. | Injector and Phase 10 client. |
| `qol-cache-key-toggle-hash` | pending | Output-control-sensitive prompt-cache key. | Phase 11 prompt cache and injector. |
| `qol-a2a-integration` | pending | Scope change propagation. | A2A runtime. |
| `qol-openobserve-metrics` | pending | Injection events/metrics. | Observability surface. |
| `qol-rest-endpoints` | pending | Toggle, preset, and agent-binding API. | Persistence/registry. |

## Executable Owner Contract

### File And Symbol Map

The table below supersedes older filename examples in the historical audit
record later in this file. Current source uses split `base_*` files and
`qol.py`; implementers must not recreate historical `base.py`, `headers.py`,
`entities.py`, or `sdk_local.py` modules from prose examples.

| Path | Current or planned symbols |
|------|----------------------------|
| `src/css/core/types/qol.py` | Existing `QoLToggle`, `QoLSettings`; add `BUILTIN_PRESETS`, `QoLSecurityError`, `validate_toggle_combo()`. |
| `src/css/core/types/qol_injector.py` | Planned `QoLInjector.build_fragment_block()`, `inject_into_messages()`, `inject_into_system()`. |
| `src/css/core/types/qol_registry.py` | Planned `QoLPresetRegistry.get()`, `list_all()`, `reload()`, `invalidate()`. |
| `src/css/core/types/qol_settings.py` | Planned `QoLSettingsManager.get_for_scope()`, `save_settings()`, `cascade_resolve()`. |
| `src/css/core/types/qol_endpoints.py` | Planned core-owned QoL settings/preset router if ASGI mounting policy confirms this location. |
| `src/css/core/db/models/qol.py` | Planned `QoLSettingsModel` persistence record. |
| `src/css/core/sdks/css_client.py` | Planned injection point in `CSSLLMClient.call()` and `call_buffered()`. |
| `src/css/core/prompt_cache/exact_cache.py` | Planned prompt-cache key consumer of `toggle_hash(settings)` once the cache runtime is created. |
| `src/css/modules/a2a_internal/dispatcher.py` | Planned change propagation; transport never becomes settings truth. |

### Numbered Per-Todo Contract

1. `qol-dangerous-combos-validator` and `qol-builtin-presets` first extend
   `qol.py`, while correcting touched-file policy issues such as module-level
   `__all__`; validate forbidden combinations and exact built-in presets.
2. `qol-tortoise-model` and `qol-preset-registry` provide persisted scoped
   settings and an async-safe resolved registry; validate session/project/global
   precedence and invalidation.
3. `qol-injector-service`, `qol-unified-client-middleware`, and
   `qol-cache-key-toggle-hash` inject immutable deterministic directives before
   cache-key generation; validate no-op, ordering, mutation safety, and
   toggle-sensitive cache separation.
4. `qol-a2a-integration`, `qol-openobserve-metrics`, and `qol-rest-endpoints`
   expose synchronization, sanitized telemetry, and authorized writes only
   after the settings/registry contract is available.
5. Run focused unit/integration tests and `ruff`/`basedpyright` for touched
   files; inspect mounted routes and dependency direction before marking any
   todo complete in `.plan/session.db`.

---

## Historical Audit Record (2026-05-03; Not The Execution Contract)

**Agent 2 Core Infrastructure Audit**

### 5-File Pattern Compliance
⚠️ **EXPANDED PATTERN** — 13 root files (oversized module)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `__init__.py` | Module exports | 54 | ✅ |
| `base.py` | Core abstractions (BaseApiServiceClient, etc) | 200+ | ✅ |
| `capabilities.py` | Capability discovery types | 100+ | ✅ |
| `context.py` | Execution context types | 80+ | ✅ |
| `entities.py` | Domain entities — **DELETED** (Phase 4 migration) | — | ✅ Migrated to modules |
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
- **Audit Reference**: local implementation document; query `.plan/session.db` for current task status
- **Refactor Plan**: Split into base/, api/, events/, providers/ subdirs (effort: 3-4h)

---

## Sync Reminder

> `.plan/session.db` is the status authority. Update it when implementation
> work changes todo state, then keep this area document technically accurate.
> This information-movement pass is an explicit no-tracker-change exception.
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
