# Architecture Recommendation: core/types Reorganization

## Quick Summary

**Problem:** core/types/ mixes framework abstractions with provider-specific types (Ollama, A2A). This creates confusion about what's "core" vs "plugin."

**Solution:** Move provider-specific types to their respective packages (following Django pattern).

---

## Current Mess

```
core/types/ contains:
✅ Base classes (BaseApiServiceClient, Message, etc.)      → Framework
✅ Shared types (Capability, Context, HookEvents)          → Framework
❌ OllamaConfig, OllamaModel, etc.                          → PROVIDER-SPECIFIC
❌ BaseLocalSDK (local LLM base)                            → Shared abstraction
❌ A2AConfig, PauseRequest, etc.                            → MODULE-SPECIFIC

Result: 50+ classes in one namespace. Hard to know where to put new types.
```

---

## The 3 Options Evaluated

| Option | What Stays in core/ | What Moves | Best For |
|--------|-------------------|-----------|----------|
| **A: Minimal** | Base classes only | Everything else | Purists, long-term refactoring |
| **B: Lightweight** ⭐ | Base + shared + BaseLocalSDK | OllamaConfig, A2AConfig | **Recommended (80/20)** |
| **C: Smart** | Same as B, using heuristics | Same as B | Data-driven teams |

---

## Recommendation: Option B (Lightweight Core)

### Why B Wins:
1. **Minimal breaking changes** - Only 2 files move (OllamaConfig, A2AConfig)
2. **Scales for future** - BaseLocalSDK in core/ signals to future devs: "Subclass this for local LLMs"
3. **Matches Django** - Like Django keeping BaseModel in core, apps put models in app packages
4. **Easy migration** - Can be done incrementally, deprecation warnings provided

### What Happens

```
BEFORE:                              AFTER:
core/types/                          core/types/
├── base/            ✅ STAY         ├── base/                ✅ STAY
├── capabilities.py  ✅ STAY         ├── capabilities.py      ✅ STAY
├── context.py       ✅ STAY         ├── context.py           ✅ STAY
├── headers.py       ✅ STAY         ├── headers.py           ✅ STAY
├── hook_events.py   ✅ STAY         ├── hook_events.py       ✅ STAY
├── entities/        ✅ STAY         ├── entities/            ✅ STAY
├── sdk_local.py     ✅ STAY         └── sdk_local.py         ✅ STAY (base for locals)
├── ollama_config.py ❌ MOVE
└── a2a_streaming.py ❌ MOVE         api_services/ollama/
                                    └── types.py             ← NEW (from ollama_config.py)
                                    
                                    modules/a2a/
                                    └── types.py             ← NEW (from a2a_streaming.py)
```

### Step-by-Step Plan

1. **Create new type files**
   - `api_services/ollama/types.py` - Move OllamaConfig, OllamaModel, etc.
   - `modules/a2a/types.py` - Move A2AConfig, PauseRequest, etc.

2. **Update imports**
   - `api_services/ollama/__init__.py` - Export from types.py
   - `api_services/ollama/client.py` - Use local imports

3. **Add deprecation wrappers** (backward compatibility)
   - Keep `core/types/ollama_config.py` but wrap with DeprecationWarning
   - Keep `core/types/a2a_streaming.py` but wrap with DeprecationWarning

4. **Test & validate**
   - Old imports still work (with warnings)
   - New imports work
   - No broken code

5. **Remove deprecated files** (6+ months later)
   - Delete wrappers once codebase fully migrated

---

## Expected Result

✅ core/types/ becomes lean framework package (7 files, ~1000 LOC)  
✅ Each provider is self-contained (types + service in same folder)  
✅ New providers automatically know where to put types (provider/types.py)  
✅ BaseLocalSDK stays in core/ as framework abstraction for local LLMs  
✅ Backward compatibility maintained during transition  

---

## Files Affected

### To CREATE:
- `src/api_services/ollama/types.py`
- `src/modules/a2a/types.py`

### To MODIFY:
- `src/core/types/__init__.py`
- `src/core/types/ollama_config.py` (add DeprecationWarning)
- `src/core/types/a2a_streaming.py` (add DeprecationWarning)
- `src/api_services/ollama/__init__.py`
- `src/api_services/ollama/client.py`
- `src/modules/a2a/__init__.py`

### To KEEP (unchanged):
- `src/core/types/base/` - all files
- `src/core/types/capabilities.py`
- `src/core/types/context.py`
- `src/core/types/headers.py`
- `src/core/types/hook_events.py`
- `src/core/types/entities/` - all files
- `src/core/types/sdk_local.py` - base class stays

---

## Success Criteria

After implementation:

- ✅ `from api_services.ollama import OllamaConfig` works (preferred)
- ✅ `from core.types import OllamaConfig` still works but warns (backward compat)
- ✅ `from modules.a2a import A2AConfig` works (preferred)
- ✅ core/types contains only framework abstractions
- ✅ Each provider/module is self-contained
- ✅ New providers automatically follow the pattern

---

## Full Analysis

See `ARCHITECTURE_REVIEW_CORE_TYPES.md` for:
- Detailed inventory of what's currently in core/types/
- Complete pros/cons of all 3 options
- Django framework analogy explained
- Evidence of what's actually used where
- Implementation roadmap with code examples

