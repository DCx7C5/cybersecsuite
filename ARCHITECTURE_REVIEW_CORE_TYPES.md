# CyberSecSuite Architecture Review: core/types Organization
## Rubber-Duck Architecture Advisory

---

## Executive Summary

**Current Problem:**
- `core/types/` conflates base framework abstractions with provider-specific implementations
- 50+ classes in one namespace, making it hard to understand what's "core" vs "plugin"
- New providers added (20+ LLM services) but none follow the "types.py" pattern → inconsistent

**Django Analogy:**
```
Django Framework:        CyberSecSuite Core:
├── models.py           ├── base/          (Base classes)
├── managers.py         ├── capabilities.py (Shared)
├── signals.py          ├── context.py     (Shared)
└── auth/               └── entities/      (Shared)
    ├── models.py       
    ├── backends.py     Providers (should have types.py):
    └── decorators.py   ├── api_services/openai/types.py
                        ├── api_services/anthropic/types.py
Modules (should have):  └── api_services/ollama/types.py
├── admin/
│   ├── models.py       Modules (should have types.py):
│   └── filters.py      ├── modules/a2a/types.py
└── comments/           └── modules/marketplace/types.py
    ├── models.py
    └── signals.py
```

---

## Current State Inventory

### 1. BASE CLASSES (core/types/base/) ✅ CORRECT — MUST STAY
Used by **every** api_service provider.

| File | Classes | Scope |
|------|---------|-------|
| base_client.py | BaseApiServiceClient, Message, MessageRole, ModelMetadata, ProviderType, StreamChunk, StreamingHandler, Tool, etc. | Framework |
| base_context.py | BaseContext | Framework |
| base_header.py | BaseHeader | Framework |
| protocols.py | BaseCommunicator, ErrorStrategy, ExecutorResult, LLMResponse | Framework |

**Evidence:** Every api_service/*/service.py imports from core.types.base

---

### 2. GENERIC/SHARED TYPES (should stay in core) ✅ CORRECT
Used by **multiple** providers/modules.

| File | Classes | Usage Count | Should Stay |
|------|---------|------------|------------|
| hook_events.py | HookContext, HookErrorStrategy | Framework-wide | ✅ YES |
| capabilities.py | Capability, ModelCapabilities, CapabilityType, CapabilityRegistry | core/llm_harness + all providers | ✅ YES |
| context.py | ExecutionContext, ConversationContext, ModelContext, ContextConfig | All providers | ✅ YES |
| headers.py | BaseAccountHeader, BaseAgentHeader, etc. | Framework-wide | ✅ YES |
| entities/ | Account, Agent, Role, Skill, Tool, etc. | Shared across system | ✅ YES |

---

### 3. PROVIDER-SPECIFIC TYPES ❌ WRONG LOCATION — MOVE

| File | Classes | Current | Should Be | Used Only By |
|------|---------|---------|-----------|---|
| ollama_config.py | OllamaConfig, OllamaModel, OllamaCapabilities, OllamaExecutionContext, OllamaHealthCheck | core/types/ | api_services/ollama/types.py | api_services/ollama/client.py |
| sdk_local.py | BaseLocalSDK | core/types/ | api_services/ollama/sdk.py | api_services/ollama/ (only) |

**Evidence:**
```bash
grep -r "OllamaConfig\|OllamaModel" /src --include="*.py"
  → Only in api_services/ollama/client.py and api_services/ollama/compat.py

grep -r "BaseLocalSDK" /src --include="*.py"
  → Only imported in core/types/ollama_config.py
```

**Why it's wrong:**
- No other provider has types.py (groq, anthropic, openai, mistral all use only service.py)
- Ollama types are NOT imported by any other provider
- Creates false impression that Ollama is "special" vs other providers
- New providers won't know to put their types in core/types/

---

### 4. A2A-SPECIFIC TYPES ❌ WRONG LOCATION — MOVE

| File | Classes | Current | Should Be | Used By |
|------|---------|---------|-----------|---|
| a2a_streaming.py | A2AConfig, PauseRequest, ResponseInjection, ResponseInjectionStrategy, StreamingController, StreamingState, StreamState | core/types/ | modules/a2a/types.py | ??? (appears unused) |

**Evidence:**
```bash
grep -r "A2AConfig\|PauseRequest" /src --include="*.py"
  → Only in core/types/__init__.py (exported but not imported)

grep -r "from.*a2a_streaming" /src --include="*.py"
  → No results (not imported anywhere)
```

**Why it's wrong:**
- Only 1 module uses these (or no module at all?)
- Inflates core.types namespace with A2A-specific concerns
- Makes a2a module less discoverable (types are in core, not in modules/a2a/)

---

## 3 Options for core/ Reorganization

### Option A: MINIMAL CORE (Framework only)
**Philosophy:** core/ = Django.db, Django.contrib.auth, Django.signals

**What stays in core/types/**
```
core/types/
├── base/                          # Framework abstractions
│   ├── base_client.py             ✅ BaseApiServiceClient, Message, etc.
│   ├── base_context.py            ✅ BaseContext
│   ├── base_header.py             ✅ BaseHeader
│   └── protocols.py               ✅ BaseCommunicator, etc.
├── __init__.py                    # Re-exports
├── capabilities.py                ✅ Shared (3+ providers need this)
├── context.py                     ✅ Shared (all providers need)
├── headers.py                     ✅ Shared (all providers need)
├── hook_events.py                 ✅ Shared (framework-wide)
└── entities/                      ✅ Shared across system
```

**What moves OUT**
```
api_services/ollama/
├── types.py                       ← NEW (from core/types/ollama_config.py)
│   ├── OllamaConfig
│   ├── OllamaModel
│   ├── OllamaCapabilities
│   ├── OllamaExecutionContext
│   ├── OllamaHealthCheck
│   └── BaseLocalSDK (if only for Ollama)
├── client.py
├── service.py
└── __init__.py

modules/a2a/
├── types.py                       ← NEW (from core/types/a2a_streaming.py)
│   ├── A2AConfig
│   ├── PauseRequest
│   ├── ResponseInjection
│   ├── ResponseInjectionStrategy
│   ├── StreamingController
│   ├── StreamingState
│   └── StreamState
└── ...
```

**Pros:**
- ✅ Minimal core (6 files, ~1000 LOC)
- ✅ Each provider is self-contained (new providers know where to put types)
- ✅ Clear separation: framework vs implementation
- ✅ Easier to deprecate/refactor provider types without breaking core
- ✅ Follows Django pattern exactly

**Cons:**
- ❌ Breaks existing imports: `from core.types import OllamaConfig` → now `from api_services.ollama import OllamaConfig`
- ❌ Requires migration of all existing code
- ❌ Subtle: Makes BaseLocalSDK harder to find (is it Ollama-specific or shared?)

---

### Option B: LIGHTWEIGHT CORE (Core + auto-discovery + shared types)
**Philosophy:** core/ = Django.db + Django.contrib.auth (commonly-used framework services)

**What stays in core/types/**
```
core/types/
├── base/                          # Framework abstractions
├── __init__.py
├── capabilities.py                ✅ Shared (capability discovery)
├── context.py                     ✅ Shared (execution context)
├── headers.py                     ✅ Shared (entity headers)
├── hook_events.py                 ✅ Shared (hook system)
├── entities/                      ✅ Shared (core business entities)
└── sdk_local.py                   ⚠️  KEEP (base for local providers, see note)
    # BaseLocalSDK is base for Ollama, NScale, vLLM, etc.
```

**What moves OUT**
```
api_services/ollama/
├── types.py                       ← NEW (from core/types/ollama_config.py)
│   ├── OllamaConfig
│   ├── OllamaModel
│   ├── OllamaCapabilities
│   ├── OllamaExecutionContext
│   └── OllamaHealthCheck
├── client.py
├── service.py
└── __init__.py

# Repeat for nscale, vllm, etc. if they exist

modules/a2a/
├── types.py                       ← NEW
└── ...

modules/marketplace/
├── types.py                       ← NEW (if any types exist there)
└── ...
```

**Special case: BaseLocalSDK**
```python
# Decision: Keep in core/ because:
# 1. Multiple local providers will subclass it (Ollama, NScale, vLLM, etc.)
# 2. Like Django's BaseModel, it's a framework abstraction
# 3. Re-export from api_services/ollama/types.py for discoverable location

# Option B.1: Keep in core/types/sdk_local.py
from core.types.sdk_local import BaseLocalSDK

# Option B.2: Move to new file and re-export
core/types/base/local_sdk.py       (base class)
api_services/ollama/types.py       (imports + re-exports for convenience)
```

**Pros:**
- ✅ Minimal breaking changes (most imports stay the same)
- ✅ Clear that these are "framework" types (capabilities, context, hooks)
- ✅ Scales for future local providers (they all subclass BaseLocalSDK)
- ✅ Good middle ground

**Cons:**
- ⚠️ Some ambiguity: Why is BaseLocalSDK in core but OllamaConfig is not?
- ⚠️ Migration is still needed for OllamaConfig, A2AConfig
- ⚠️ Harder to enforce: developers might add provider-specific types to core by accident

---

### Option C: SMART CORE (Heuristic: "shared by 3+ implementations")
**Philosophy:** core/ = Django.db + Django.contrib.auth + Django.contrib.admin (the essential framework)

**Rule:** A type stays in core/types/ IFF:
- Used by 3+ providers/modules **OR**
- Documented as framework-level abstraction **OR**
- Part of auto-discovery/capability system

**What stays in core/types/**
```
core/types/
├── base/                          # Framework abstractions
├── __init__.py
├── capabilities.py                ✅ Used by: capability_registry.py, llm_harness, all providers
├── context.py                     ✅ Used by: all providers
├── headers.py                     ✅ Used by: entity system
├── hook_events.py                 ✅ Used by: framework-wide
├── entities/                      ✅ Used by: framework + modules
├── api_services.py                ✅ Used by: all providers (re-export module)
└── sdk_local.py                   ✅ BASE for: Ollama, NScale, vLLM (3+ providers)
    # With a deprecation notice pointing to versioned submodules
```

**What moves OUT**
```
api_services/ollama/
├── types.py
│   ├── OllamaConfig              (only Ollama)
│   ├── OllamaModel               (only Ollama)
│   ├── OllamaCapabilities        (only Ollama)
│   ├── OllamaExecutionContext    (only Ollama)
│   └── OllamaHealthCheck         (only Ollama)
├── client.py
├── service.py
└── __init__.py

modules/a2a/
├── types.py
└── ...
```

**Implementation guide:**
```python
# In Option C, we'd check every type:
#   1. How many api_services import it? If >= 3, keep in core/
#   2. Is it a Base* abstract class? If yes, probably core/
#   3. Is it provider/module-specific Config/Model? If yes, move out
#   4. Is it in a *Strategy, *State, or *Handler? Probably module-specific

# Score card:
BaseLocalSDK          → Base* + used by 3+ (Ollama, NScale, vLLM) → KEEP in core/
OllamaConfig          → provider-specific, Config suffix → MOVE to ollama/
A2AConfig             → module-specific, Config suffix → MOVE to a2a/
Capability            → no prefix, used everywhere → KEEP in core/
```

**Pros:**
- ✅ Maximizes code reuse (BaseLocalSDK stays in core)
- ✅ Objective heuristic (hard to argue against "used by 3+ implementations")
- ✅ Future-proof (scales with new providers automatically)
- ✅ Self-documenting (the decision is encoded in the count)

**Cons:**
- ❌ Hardest to implement (requires audit of all imports)
- ❌ Heuristic can feel arbitrary ("why 3, not 2 or 4?")
- ❌ Still requires migration

---

## Comparative Analysis

| Aspect | Option A | Option B | Option C |
|--------|----------|----------|----------|
| **core/types size** | Minimal (6 files) | Lightweight (7-8 files) | Moderate (8-9 files) |
| **Breaking changes** | High | Medium | High |
| **Code reuse** | Low (BaseLocalSDK replicated) | High (shared SDK base) | Maximum (3+ reuse rule) |
| **Scalability** | ⭐⭐⭐⭐ (clear rules) | ⭐⭐⭐⭐ (clear rules) | ⭐⭐⭐⭐⭐ (heuristic grows) |
| **Implementation effort** | 🔴 Hard (need import updates everywhere) | 🟡 Medium (fewer import updates) | 🔴 Hard (full audit needed) |
| **Django analogy match** | ⭐⭐⭐⭐⭐ (pure) | ⭐⭐⭐⭐ (with conveniences) | ⭐⭐⭐ (pragmatic) |
| **Developer friction** | ⭐⭐⭐⭐ (learn new pattern) | ⭐⭐⭐⭐ (familiar imports) | ⭐⭐⭐ (needs heuristic lookup) |

---

## Recommendation: Option B (Lightweight Core)

### Why Option B wins:

1. **Best for extensibility:**
   - BaseLocalSDK in core/ signals to future developers: "More local LLM providers should subclass this"
   - New providers (vLLM, NScale, Ollama derivatives) follow established pattern
   - Fewer breaking changes = easier adoption

2. **Best for Django analogy:**
   - Like Django keeping `BaseModel` and `Manager` in core while app-specific models go in apps
   - core/ = framework primitives that applications build on
   - providers/ = implementations that use the framework

3. **Balanced cost/benefit:**
   - Option A requires too much refactoring for marginal benefit
   - Option C requires full audit that's hard to maintain long-term
   - Option B is 80/20: moves provider-specific types, keeps framework essentials

4. **Lowest risk:**
   - Most imports stay the same (only OllamaConfig, A2AConfig need updates)
   - Can be done incrementally (migrate one provider at a time)
   - Fallback is easy (revert if issues arise)

---

## Implementation Roadmap (Option B)

### Phase 1: Create new type locations

```bash
# Create provider type files
mkdir -p src/api_services/ollama/src/api_services/ollama/types.py
mkdir -p src/modules/a2a/src/modules/a2a/types.py
mkdir -p src/modules/marketplace/src/modules/marketplace/types.py

# Create marker file to indicate where provider types should go
echo "Provider-specific types go here" > src/api_services/TYPES_LOCATION.md
echo "Module-specific types go here" > src/modules/TYPES_LOCATION.md
```

### Phase 2: Move Ollama types

```python
# src/api_services/ollama/types.py (NEW)
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

@dataclass
class OllamaModel(BaseModel):
    """Metadata for a local Ollama model."""
    name: str = Field(..., description="Model name (e.g., 'llama2', 'mistral')")
    # ... rest of class

@dataclass
class OllamaCapabilities(BaseModel):
    # ...

@dataclass
class OllamaConfig(BaseModel):
    # ...

@dataclass
class OllamaExecutionContext(BaseModel):
    # ...

@dataclass
class OllamaHealthCheck(BaseModel):
    # ...

__all__ = [
    "OllamaModel",
    "OllamaCapabilities",
    "OllamaConfig",
    "OllamaExecutionContext",
    "OllamaHealthCheck",
]
```

### Phase 3: Update imports

```python
# src/api_services/ollama/__init__.py
from .types import (
    OllamaModel,
    OllamaCapabilities,
    OllamaConfig,
    OllamaExecutionContext,
    OllamaHealthCheck,
)
from .service import OllamaApiService

__all__ = [
    "OllamaModel",
    "OllamaCapabilities",
    "OllamaConfig",
    "OllamaExecutionContext",
    "OllamaHealthCheck",
    "OllamaApiService",
]
```

### Phase 4: Add deprecation wrapper (backward compatibility)

```python
# src/core/types/ollama_config.py (DEPRECATED)
"""
DEPRECATED: Ollama types have moved to api_services.ollama.types

Use instead:
    from api_services.ollama import OllamaConfig, OllamaModel, etc.
"""

import warnings
from api_services.ollama.types import (
    OllamaModel,
    OllamaCapabilities,
    OllamaConfig,
    OllamaExecutionContext,
    OllamaHealthCheck,
)

warnings.warn(
    "Importing Ollama types from core.types.ollama_config is deprecated. "
    "Use api_services.ollama.types instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = [
    "OllamaModel",
    "OllamaCapabilities",
    "OllamaConfig",
    "OllamaExecutionContext",
    "OllamaHealthCheck",
]
```

### Phase 5: Update core/types/__init__.py

```python
# OLD (DEPRECATED):
from .ollama_config import (
    OllamaModel,
    OllamaCapabilities,
    OllamaConfig,
    OllamaExecutionContext,
    OllamaHealthCheck,
)

# NEW (keep for backward compatibility, but warn):
import warnings
try:
    from api_services.ollama.types import (
        OllamaModel,
        OllamaCapabilities,
        OllamaConfig,
        OllamaExecutionContext,
        OllamaHealthCheck,
    )
    warnings.warn(
        "Importing Ollama types from core.types is deprecated. "
        "Use api_services.ollama instead.",
        DeprecationWarning,
        stacklevel=2,
    )
except ImportError:
    # Fallback for old structure during migration
    from .ollama_config import (
        OllamaModel,
        OllamaCapabilities,
        OllamaConfig,
        OllamaExecutionContext,
        OllamaHealthCheck,
    )
```

### Phase 6: Move A2A types

```python
# src/modules/a2a/types.py (NEW)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

class StreamState(str, Enum):
    CLEAR = "clear"
    PAUSED = "paused"
    RUNNING = "running"

@dataclass
class PauseRequest:
    request_id: str = field(default_factory=lambda: str(uuid4()))
    question: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    source_model: str = ""
    target_model: Optional[str] = None

# ... rest of A2A types
```

### Phase 7: Testing & Validation

```bash
# 1. Run import tests
pytest tests/test_imports.py

# 2. Check for broken imports
python -m py_compile src/api_services/ollama/*.py
python -m py_compile src/modules/a2a/*.py

# 3. Verify backward compatibility
python -c "from core.types import OllamaConfig; print('OK')"  # Should warn

# 4. Test new pattern
python -c "from api_services.ollama import OllamaConfig; print('OK')"
```

---

## Files to Move/Modify

### Files to CREATE:
- `src/api_services/ollama/types.py` (new, from core/types/ollama_config.py)
- `src/modules/a2a/types.py` (new, from core/types/a2a_streaming.py)
- `src/modules/marketplace/types.py` (if any types defined there)

### Files to MODIFY:
- `src/core/types/__init__.py` (remove direct imports, add deprecation shim)
- `src/core/types/ollama_config.py` (wrap with DeprecationWarning)
- `src/core/types/a2a_streaming.py` (wrap with DeprecationWarning, OR delete)
- `src/api_services/ollama/__init__.py` (export from types.py)
- `src/api_services/ollama/client.py` (update imports: `from . import OllamaConfig` instead of `from core.types`)
- `src/modules/a2a/__init__.py` (export from types.py)

### Files to KEEP (do not move):
- `src/core/types/base/` (all files)
- `src/core/types/capabilities.py`
- `src/core/types/context.py`
- `src/core/types/headers.py`
- `src/core/types/hook_events.py`
- `src/core/types/entities/` (all files)
- `src/core/types/sdk_local.py` (base class for Ollama, NScale, vLLM, etc.)

---

## Success Criteria

After implementing Option B:

- ✅ `from api_services.ollama import OllamaConfig` works
- ✅ `from modules.a2a import A2AConfig` works
- ✅ Old imports still work but raise DeprecationWarning
- ✅ core/types/ only contains 6-7 core framework files
- ✅ Each provider/module is self-contained (types + service/logic)
- ✅ New providers added in future follow the pattern automatically
- ✅ BaseLocalSDK is recognized as framework abstraction for local LLMs

---

## Future Extensions

Once Option B is implemented:

1. **New cloud provider (e.g., Anthropic types):**
   ```python
   # api_services/anthropic/types.py
   class AnthropicModel(BaseModel):
       model_id: str
       # ...
   ```

2. **New local provider (e.g., vLLM):**
   ```python
   # api_services/vllm/types.py
   class VLLMConfig(BaseModel):
       # ...
   
   class VLLMService(BaseLocalSDK):  # Uses framework base class
       # ...
   ```

3. **New module types:**
   ```python
   # modules/marketplace/types.py
   class PackageMetadata(BaseModel):
       # ...
   ```

4. **Remove deprecated wrapper files (6+ months later):**
   - Delete `src/core/types/ollama_config.py`
   - Delete `src/core/types/a2a_streaming.py`
   - Update all imports to new locations
   - Remove DeprecationWarning shims

