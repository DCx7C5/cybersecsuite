# Decision Matrix: core/types Reorganization

## Quick Reference Table

### Current Inventory

| Type | File | Used By | Category | Status |
|------|------|---------|----------|--------|
| **Base Classes** |
| BaseApiServiceClient | base/base_client.py | All 20+ providers | Framework | ✅ CORRECT |
| BaseContext | base/base_context.py | Framework | Framework | ✅ CORRECT |
| BaseHeader | base/base_header.py | Framework | Framework | ✅ CORRECT |
| BaseCommunicator | base/protocols.py | Framework | Framework | ✅ CORRECT |
| **Shared Types** |
| Message, MessageRole, Tool | base/base_client.py | All providers | Framework | ✅ CORRECT |
| ModelMetadata, ProviderType, StreamChunk | base/base_client.py | All providers | Framework | ✅ CORRECT |
| ExecutionContext, ConversationContext | context.py | All providers | Framework | ✅ CORRECT |
| Capability, ModelCapabilities, CapabilityRegistry | capabilities.py | All providers + core/llm_harness | Framework | ✅ CORRECT |
| HookContext, HookErrorStrategy | hook_events.py | Framework-wide | Framework | ✅ CORRECT |
| Account, Agent, Role, Skill, Tool entities | entities/ | Framework-wide | Framework | ✅ CORRECT |
| **Provider-Specific** |
| OllamaConfig, OllamaModel, OllamaCapabilities | ollama_config.py | api_services/ollama only | Provider | ❌ WRONG LOCATION |
| OllamaExecutionContext, OllamaHealthCheck | ollama_config.py | api_services/ollama only | Provider | ❌ WRONG LOCATION |
| BaseLocalSDK | sdk_local.py | Framework abstraction for local LLMs | Framework | ⚠️ AMBIGUOUS |
| **Module-Specific** |
| A2AConfig, PauseRequest, ResponseInjection | a2a_streaming.py | modules/a2a only | Module | ❌ WRONG LOCATION |
| StreamingController, StreamState, etc. | a2a_streaming.py | modules/a2a only | Module | ❌ WRONG LOCATION |

---

## Decision Framework

### Does a type belong in core/types/?

Answer these questions:

```
1. Is it a Base* abstract class?
   └─ YES → Likely framework. Ask Q2.
   └─ NO  → Go to Q3.

2. Will 3+ providers/modules subclass it?
   └─ YES → KEEP in core/. Example: BaseLocalSDK for Ollama, NScale, vLLM
   └─ NO  → Move to provider/module directory

3. Is it used by all (or almost all) providers?
   └─ YES → KEEP in core/. Example: Message, Tool, StreamChunk
   └─ NO  → Go to Q4.

4. Is it a Config, Model, or State type?
   └─ YES → Move to provider/module directory
   └─ NO  → Go to Q5.

5. Is it a shared domain model (Entities)?
   └─ YES → KEEP in core/. Example: Account, Agent, Role
   └─ NO  → Move to provider/module directory

Decision tree result: MOVE to provider/module directory
```

---

## Option B Decision Tree

### Core/Types Stays (7 files)
- [x] base/base_client.py
- [x] base/base_context.py
- [x] base/base_header.py
- [x] base/protocols.py
- [x] capabilities.py
- [x] context.py
- [x] headers.py
- [x] hook_events.py
- [x] entities/ (entire)
- [x] sdk_local.py ← Base for local SDKs

### Moves to api_services/ollama/types.py
- [ ] OllamaConfig
- [ ] OllamaModel
- [ ] OllamaCapabilities
- [ ] OllamaExecutionContext
- [ ] OllamaHealthCheck

### Moves to modules/a2a/types.py
- [ ] A2AConfig
- [ ] PauseRequest
- [ ] ResponseInjection
- [ ] ResponseInjectionStrategy
- [ ] StreamingController
- [ ] StreamingState
- [ ] StreamState

---

## Implementation Checklist

### Phase 1: Preparation
- [ ] Create `src/api_services/ollama/types.py`
- [ ] Create `src/modules/a2a/types.py`
- [ ] Add import documentation to both files

### Phase 2: Move Ollama
- [ ] Copy ollama_config.py content to api_services/ollama/types.py
- [ ] Update api_services/ollama/__init__.py to export from types.py
- [ ] Update api_services/ollama/client.py imports
- [ ] Update api_services/ollama/compat.py imports

### Phase 3: Move A2A
- [ ] Copy a2a_streaming.py content to modules/a2a/types.py
- [ ] Update modules/a2a/__init__.py to export from types.py
- [ ] Search for any other imports of A2AConfig
- [ ] Update dispatcher.py, etc. if needed

### Phase 4: Deprecation
- [ ] Keep core/types/ollama_config.py with DeprecationWarning wrapper
- [ ] Keep core/types/a2a_streaming.py with DeprecationWarning wrapper
- [ ] Update core/types/__init__.py to re-export with warnings

### Phase 5: Testing
- [ ] Unit tests for new import locations
- [ ] Verify backward compatibility (old imports work with warnings)
- [ ] Run full test suite
- [ ] Check for any missed imports

### Phase 6: Documentation
- [ ] Update CONTRIBUTING.md with new type location pattern
- [ ] Document BaseLocalSDK stays in core/ for future local SDKs
- [ ] Add migration guide for any public APIs

### Phase 7: Cleanup (after 6+ months)
- [ ] Remove deprecated wrapper files
- [ ] Remove all DeprecationWarnings
- [ ] Final migration verification

---

## Evidence for Decisions

### Why OllamaConfig moves:

```bash
# Only ollama uses it:
grep -r "OllamaConfig" /src --include="*.py"
  └─ api_services/ollama/client.py        ✓
  └─ api_services/ollama/compat.py        ✓
  └─ core/types/ollama_config.py         (source only)
  
# Not used by other providers:
grep -r "OllamaConfig" /src/api_services/anthropic --include="*.py"
  └─ (no results)

grep -r "OllamaConfig" /src/api_services/groq --include="*.py"
  └─ (no results)
```

### Why A2AConfig moves:

```bash
# Not imported anywhere:
grep -r "A2AConfig" /src --include="*.py" | grep -v "core/types/__init__"
  └─ (no results - appears unused!)

grep -r "from.*a2a_streaming" /src --include="*.py"
  └─ (no results - not imported)
```

### Why BaseLocalSDK stays in core/:

```bash
# Base class for multiple providers:
# 1. Ollama (api_services/ollama/client.py) - inherits
# 2. NScale (if it exists) - would inherit
# 3. vLLM (if added) - would inherit

# Like Django keeping BaseModel in core/db/models,
# framework keeps abstraction classes in core/ for apps to subclass
```

---

## Risk Assessment

| Change | Risk Level | Mitigation |
|--------|-----------|-----------|
| Move OllamaConfig | 🟢 LOW | Few imports, deprecation wrapper maintains backward compat |
| Move A2AConfig | 🟢 LOW | Appears unused, isolated in modules/a2a |
| Keep BaseLocalSDK in core/ | 🟢 LOW | Correct decision, no change needed |
| Update imports in ollama/ | 🟡 MEDIUM | Grep ensures all imports found |
| Deprecation warnings | 🟢 LOW | Optional, doesn't break anything |

---

## Success Metrics

After implementation, these should be true:

- **Code quality:** `pylint src/core/types/` shows fewer unrelated types
- **Discoverability:** New dev knows where to put provider types (provider/types.py)
- **Consistency:** All providers follow same pattern (no special case for Ollama)
- **Backward compatibility:** Old imports work (emit warnings)
- **Forward compatibility:** Future providers automatically fit pattern
- **Documentation:** New developers can onboard faster

---

## FAQ

**Q: Why keep BaseLocalSDK in core/?**
A: It's a framework abstraction, like Django's BaseModel. Multiple local providers will subclass it. Signals to future developers: "If you're adding a local LLM provider, inherit from this."

**Q: What about new providers?**
A: They should put their types in `api_services/<provider>/types.py`. This pattern becomes obvious once one provider does it.

**Q: Can we automate the import updates?**
A: Partially. Use `grep` to find all imports, then automated refactoring tools or scripts to update them. See Phase 2 for manual approach.

**Q: Will this break existing code?**
A: Not if we keep deprecation wrappers. Old code keeps working, but emits warnings. Developers migrate at their own pace.

**Q: When should we remove the deprecated files?**
A: 6+ months after implementation, once all code has migrated. Track with an issue.

**Q: What about documentation?**
A: Update CONTRIBUTING.md with: "Provider-specific types go in provider/types.py"

