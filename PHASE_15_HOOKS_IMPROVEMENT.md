# Phase 15: Hooks Improvement with anthropic-sdk

## Problem Statement
Current hook system uses claude-agent-sdk's HookMatcher with 11 event types, pattern matching on tool names, and fire-and-forget async logging. Key limitations:
- No type safety in hook signatures
- Limited context (tool-level only, no correlation IDs)
- Silent failures in fire-and-forget patterns
- Mixed SDK callbacks + CLI script hooks (two models)
- No visibility into message-level or streaming events
- No performance instrumentation

## Solution Direction
Introduce a **typed, observable, backward-compatible** hook layer that:
1. Wraps existing SDK hooks with type safety
2. Adds correlation IDs and lightweight context
3. Enables error handling strategies without breaking existing behavior
4. Preserves all 38 existing hooks unchanged
5. Creates foundation for future streaming/message/recovery hooks

---

## Revised MVP Scope (4-5 hours) — NARROWED

### Phase 1: Map & Test (1 hour)
**Goals:** Inventory current hooks, establish regression tests, document contracts

1. **Inventory hook surfaces:**
   - Document which 38 hooks are SDK callbacks vs CLI scripts
   - Map each hook to its event type
   - Identify mutual dependencies

2. **Write contract tests (do NOT implement):**
   - Test `build_python_hooks()` event map structure
   - Test matcher precedence and pattern matching
   - Test hook output schema per event (PreToolUse, PostToolUse, etc.)
   - Test "hook exception does not block execution"
   - Test backward compatibility by running existing hooks

3. **Document SDK event I/O:**
   - Create a contract table for each event:
     - Input payload shape (from SDK)
     - Matcher behavior rules
     - Output schema (what SDK expects)
     - Failure semantics (what happens if hook throws)

### Phase 2: Type-Safe Wrapper (1.5 hours)
**Goals:** Introduce typed layer WITHOUT changing behavior

1. **Create src/hooks/core.py (120L):**
   - TypedDict + dataclasses for event inputs
   - Hook context dataclass (basic: correlation_id, session_id, timestamp, tool_use_id)
   - Error strategy enum (PRESERVE_EXISTING, LOG, WARN)
   - Hook output types per event (match SDK schema exactly)

2. **Create src/hooks/registry.py (150L):**
   - HookRegistry wrapper around existing matchers
   - Type validation only (no runtime transformation)
   - Immutable/stateless design (no caching per-run state)
   - Backward compat: existing hook return dicts still work

3. **No behavioral changes:**
   - Hook execution still async
   - Return payloads still the same shape
   - Error handling defaults to existing behavior

### Phase 3: Instrumentation (1.5 hours)
**Goals:** Add timing + error tracking without latency

1. **Create src/hooks/instrumentation.py (100L):**
   - Hook timing capture (perf_counter, minimal overhead)
   - Error/exception logging per hook
   - Absolute latency budget: <2ms for no-op, <10ms for validated hooks
   - Performance report generation

2. **Integrate into registry:**
   - Wrap hook execution with try/except + timing
   - Preserve error handling semantics (no new failures)

3. **Add metrics export:**
   - Per-hook duration stats
   - Success/failure counts
   - Slow hook detection (>10ms)

### Phase 4: Integration & Testing (1 hour)
**Goals:** Integrate into agent_sdk, verify backward compatibility

1. **Update src/a2a/agent_sdk.py:**
   - Use new registry wrapper instead of direct `build_python_hooks()`
   - No change to ClaudeAgentOptions behavior
   - Stateless registry (no per-run state leakage)

2. **Run regression tests:**
   - All 38 hooks execute unchanged
   - No new exceptions or blocking
   - Performance within budget

3. **Update exports in src/hooks/__init__.py**

---

## What's NOT in MVP (Deferred)

❌ **Message history context** — Defer until capture source is clear
❌ **Streaming event hooks** — Defer to Phase 16
❌ **Pre/post message interception** — Defer to Phase 16
❌ **Error recovery hooks** — Defer to Phase 16
❌ **YAML declarative config** — Defer to Phase 16
❌ **Pydantic for validation** — Use TypedDict/dataclasses instead

---

## Architecture Decisions (RubberDuck Feedback Applied)

### 1. Hook Contracts Table (REQUIRED before coding)
Document exact I/O for each event:

| Event | Input Shape | Matchers | Output Schema | Failure |
|-------|------------|----------|---------------|---------|
| PreToolUse | {tool_name, tool_input, ...} | Write\|Edit\|Bash | {hookSpecificOutput: {permissionDecision, reason}} | Audit only |
| PermissionRequest | {permission_type, ...} | Read\|Write | {hookSpecificOutput: {decision: {...}}} | Fail closed |
| PostToolUse | {tool_name, tool_response} | .* | {} | Audit only |
| (... 8 more) | | | | |

### 2. Script Hooks vs SDK Hooks (TWO MODELS)
- **SDK hooks** (src/hooks/sdk_hooks.py): Python async callbacks → wrap in typed registry ✓
- **CLI hooks** (src/hooks/*.py): Subprocess scripts (pre_tool_call.py, etc.) → leave untouched in MVP
- **New adapter pattern:** TypedRegistry wraps SDK path only

### 3. Stateless Registry (NO CONTEXT LEAKAGE)
- Hook matchers/registry: immutable, shared
- Hook state (timing, context): NOT stored on registry
- Per-run timing: local scope only (not cached between runs)
- ClaudeAgentOptions caching unaffected

### 4. TypedDict Over Pydantic (PERFORMANCE)
- Internal: TypedDict/dataclasses (zero overhead)
- Return types: match SDK payload shapes exactly
- Validation: optional, at boundaries only
- Perf budget: absolute (2–10ms), not percentage

### 5. Error Semantics Preserved (NO BEHAVIOR CHANGE)
- Audit/notification hooks: fail-open (exceptions don't block)
- Security/permission hooks: existing decision logic unchanged
- New metrics/logging: side-effects only, no runtime behavior change

---

## File Changes (MVP)

**Create (3 files):**
- `/src/hooks/core.py` (120L) — Event types, context, error strategies
- `/src/hooks/registry.py` (150L) — TypedRegistry wrapper
- `/src/hooks/instrumentation.py` (100L) — Timing + metrics

**Modify (3 files):**
- `/src/hooks/sdk_hooks.py` (+20L) — Use new registry in build_python_hooks()
- `/src/a2a/agent_sdk.py` (+10L) — Stateless integration
- `/src/hooks/__init__.py` (+20L) — Export new types

**Add (1 test file):**
- `/tests/hooks/test_contracts.py` (200L) — Regression + contract tests

**Delete:** None

---

## Success Criteria (MVP)

✅ All 38 existing hooks execute unchanged
✅ No new blocking exceptions introduced
✅ Type information available for IDE support (TypedDict)
✅ Hook timing captured (<2ms overhead for no-op)
✅ Error handling semantics preserved
✅ Backward compatible with cached ClaudeAgentOptions
✅ Regression tests pass (contracts verified)
✅ Performance within budget (2–10ms per hook)
✅ Foundation ready for Phase 16 (streaming/interception/recovery)

---

## Phase 15 → Phase 16 (Full Implementation, 6–7 hours)

Once MVP is stable, Phase 16 adds:

**Phase 16a: Streaming Events (2 hours)**
- on_message_start, on_content_block_delta, on_message_stop
- Real-time token counting, error detection

**Phase 16b: Message Interception (1.5 hours)**
- on_before_message() for request validation/injection
- on_after_message() for response transformation

**Phase 16c: Error Recovery (1.5 hours)**
- on_api_error() for smart retries
- on_tool_error() for auto-correction

**Phase 16d: YAML Config (1 hour)**
- Declarative hook setup, no code changes

---

## Estimation

- **Phase 15 MVP: 4–5 hours**
  - Mapping + tests: 1 hour
  - Type-safe wrapper: 1.5 hours
  - Instrumentation: 1.5 hours
  - Integration + testing: 1 hour

- **Phase 16 Full: 6–7 hours**
  - Streaming: 2 hours
  - Interception: 1.5 hours
  - Error recovery: 1.5 hours
  - YAML: 1 hour

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Backward compatibility broken | Contract tests + regression suite before refactor |
| CLI script hooks affected | Leave untouched, only wrap SDK path |
| Context leakage across sessions | Stateless registry, per-run scope for timing |
| Performance regression | Absolute latency budget, benchmark fast/slow tools |
| Silent failures continue | Error metrics logged, but semantics preserved |
| Partial refactor | Narrow MVP scope, clear Phase 15 vs 16 boundary |

---

## Next Steps (When Ready)

1. **Review and approve MVP scope** (narrowed from original plan)
2. **Create contract test file** (src/hooks/test_contracts.py)
3. **Document SDK event I/O table** (in code comments)
4. **Implement Phase 1** (map + tests)
5. **Implement Phase 2** (type-safe wrapper)
6. **Implement Phase 3** (instrumentation)
7. **Integrate Phase 4** (agent_sdk + verify)
8. **Commit and document Phase 15 complete**
9. **Plan Phase 16** (streaming/interception/recovery)

---

## Key Insights (From Rubber Duck)

1. **Two hook models** (SDK + CLI) must be treated separately
2. **Backward compatibility must be explicit**, not assumed
3. **Stateless design prevents context leakage** in cached options
4. **Absolute performance budgets** more useful than percentages
5. **Contracts first** (test before code) prevents I/O mismatches
6. **Defer rich context** until capture source is clear
7. **TypedDict over Pydantic** in hot path (performance)
8. **Don't start with streaming** — stabilize existing events first
