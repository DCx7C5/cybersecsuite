# Phase 0.2-FIX: Implementation Dependency Graph

**Last Updated:** 2026-04-30  
**Status:** LOCKED — All decisions confirmed

---

## Critical Path (Blocking Dependencies)

```
FOUNDATION (Week 1)
├─ Issue #2: Retry Logic (Custom Hybrid) ✓ LOCKED
├─ Issue #3: Error Code Mapping
└─ Structural: core/enums/ directory

    ↓ (unblocks PROVIDER layer)

PROVIDER LAYER (Week 2)
├─ Issue #4: Ollama Backward Compat
└─ Issue #5: LocalSDK Base Class
    
    ↓ (unblocks ARCHITECTURE layer)

ARCHITECTURE (Week 3)
├─ Issue #10: Extract ModelExecutor
│   ├─ Impacts: Headers Layer 1 (concrete headers need ModelExecutor shape)
│   ├─ Impacts: Issue #6 (StreamController uses ModelExecutor)
│   └─ Blocks: Issue #11 (Agent refactor depends on ModelExecutor)
│
└─ Issue #11: Agent Refactor (uses ModelExecutor)
    ├─ Impacts: Headers Layer 2 (integration layer)
    └─ Enables: ToolAwareModel Protocol
    
    ↓ (unblocks STREAMING layer)

STREAMING (Week 4)
├─ Issue #1: StreamChunk v2 + Token Counting Field
├─ Issue #6: StreamController (AsyncIO Queue-based)
│   ├─ Uses: StreamChunk (from Issue #1)
│   ├─ Uses: core/enums/ (Transport enum)
│   └─ Enables: Stream Checkpoint (feature)
│
└─ Feature: Stream Checkpoint (auto-resume with configurable intervals)
    
    ↓ (unblocks ORCHESTRATION layer)

ORCHESTRATION (Week 5)
├─ Issue #8: Token Counting Framework
│   ├─ Uses: StreamChunk.token_estimate (from Issue #1)
│   ├─ Uses: core/enums/ (health status)
│   └─ Enables: SLA Controller
│
├─ Issue #9: FallbackChain (Health Metrics + Config) ✓ LOCKED
│   ├─ Both + Config: error_rate + latency (configurable per provider)
│   ├─ State machine: healthy→sick→recovering
│   ├─ Uses: core/enums/health.py
│   └─ Blocks: Feature: SLA Controller (depends on fallback health)
│
└─ Feature: SLA Controller (auto-degrade on latency breach)
    └─ Uses: FallbackChain + Token Counting
    
    ↓ (unblocks RESOURCES layer)

RESOURCES & FINALIZATION (Week 6)
├─ Issue #7: Resource Cleanup + Connection Pooling
│   └─ Uses: core/enums/transport.py
│
└─ Issue #12: ToolAwareModel Protocol
    └─ Uses: ModelExecutor (from Issue #10)
```

---

## Cross-Cutting Dependencies (Non-Linear)

### Headers Architecture (Depends On Streaming + Architecture)

```
Headers Layer 0 (Exists):
  └─ BaseHeader, BaseAgentHeader, BaseSkillHeader, etc.

Headers Layer 1 (CREATE after Issue #10):
  ├─ AgentHeader (after ModelExecutor extracted)
  ├─ MCPHeader (uses core/enums/transport.py)
  ├─ SkillHeader
  ├─ A2AAgentHeader
  └─ Requires: Issue #10 (ModelExecutor) + Issue #6 (StreamController shape)

Headers Layer 2 (CREATE after Layer 1 + Issue #11):
  ├─ A2AAgentHeader
  ├─ AgentMCPRequirements
  └─ SkillDependencies
  └─ Requires: Issue #11 (Agent refactor)

Headers Migration (After all layers):
  └─ Move core/entities/headers/ → core/types/headers/
  └─ Update imports: core.entities.headers → core.types.headers
```

**When to Start:** After Issue #10 (ModelExecutor extraction)  
**Critical for:** Phase 0.3 (marketplace integration)  
**Parallel OK:** Yes, can draft while Issues #1-#9 in flight

---

### Database Restructuring (Parallel, Gradual Migration)

```
Phase 1 (Immediate + Parallel):
  ├─ core/database/models/base.py
  ├─ core/database/managers/base.py
  └─ core/database/config.py
  └─ Depends: Issue #10 (ModelExecutor shape for query context)

Phase 2 (During Week 1-3 of Phase 0.2-FIX):
  ├─ Migrate models one-by-one (MarketplaceMCP, Agent, Skill, Tool)
  ├─ Implement dual-write to legacy/db and core/database/
  └─ All writes to BOTH layers, reads from legacy/db (safe fallback)
  └─ Depends: Phase 1 complete

Phase 3 (After Phase 0.2-FIX Complete):
  ├─ Verify all critical queries work on new layer
  ├─ Flip reads to core/database/
  ├─ Deprecate legacy/db/
  └─ Final integrity checks

Risk if Not Gradual:
  ✗ A2A worker state depends on session/cache/marketplace managers
  ✗ Flag-day migration = workers crash if queries fail
  ✗ Gradual = can rollback any query to legacy/db immediately
```

**When to Start:** Immediately (Phase 1), in parallel with Week 1  
**Critical for:** Worker stability during Phase 0.2-FIX  
**Parallel OK:** Yes, non-blocking on streaming layer

---

## Decision Dependencies (Must Be Locked Before Implementation)

| Decision | Locks | Impact |
|----------|-------|--------|
| **Retry Logic: Custom Hybrid** | Issue #2 start | Affects: all SDK wrappers, error handling |
| **StreamController: AsyncIO Queue** | Issue #6 start | Affects: buffering strategy, backpressure semantics |
| **FallbackChain: Both + Config** | Issue #9 start | Affects: health metric collection, provider config |
| **DB Migration: Gradual** | Phase DB Phase 1-2 | Affects: query implementation, rollback strategy |
| **Token Counting: Exact** | Issue #1, #8 start | Affects: token estimation accuracy, SLA thresholds |
| **core/enums/ directory** | Week 1 | Affects: all enum usage, import paths |

**Status:** ✅ **ALL LOCKED** (User + Rubber-Duck approved)

---

## Weekly Implementation Sequence

### Week 1 (Foundation)
```
Day 1-2: Issue #2 (Retry Logic)
  └─ Design: How to detect + wrap SDK retry selectively
  └─ Output: Custom retry orchestrator class

Day 3-4: Issue #3 (Error Code Mapping)
  └─ Depends on: Issue #2 (error context)
  └─ Output: Exception hierarchy + per-SDK mappers

Day 5: Structural (core/enums/)
  └─ Depends on: None (can start Day 1 parallel)
  └─ Output: models.py, transport.py, health.py, roles.py, execution.py, common.py
  └─ Note: Can be drafted in advance, finalized after #2 + #3 decide enum names
```

### Week 2 (Providers)
```
Day 1-2: Issue #4 (Ollama Backward Compat)
  └─ Depends on: Issue #2, #3 (retry, errors)
  └─ Output: ApiService + deprecated Client (both return AsyncIterator[StreamChunk])

Day 3-5: Issue #5 (LocalSDK Base Class)
  └─ Depends on: Issue #3 (error handling)
  └─ Output: Base SDK for all local LLMs
```

### Week 3 (Architecture)
```
Day 1-3: Issue #10 (Extract ModelExecutor)
  └─ Depends on: Nothing (can start immediately after design)
  └─ Output: ModelExecutor class, decoupled from Agent
  └─ Note: CRITICAL PATH — many issues depend on this

Day 4-5: Issue #11 (Agent Refactor)
  └─ Depends on: Issue #10 (ModelExecutor exists)
  └─ Output: Agent composes ModelExecutor (dependency injection)
```

### Week 4 (Streaming)
```
Day 1-2: Issue #1 (StreamChunk v2 + Token Counting Field)
  └─ Depends on: Issue #10 (ModelExecutor shape)
  └─ Output: token_estimate field, per-provider parsers

Day 3-5: Issue #6 (StreamController AsyncIO Queue)
  └─ Depends on: Issue #1 (uses StreamChunk), core/enums/ (Transport)
  └─ Output: True pause/resume, asyncio.Queue buffering
  └─ Note: Also enables Stream Checkpoint feature
```

### Week 5 (Orchestration)
```
Day 1-2: Issue #8 (Token Counting Framework)
  └─ Depends on: Issue #1 (token_estimate), core/enums/health.py
  └─ Output: Per-provider token counters, accuracy config

Day 3-5: Issue #9 (FallbackChain Health Metrics)
  └─ Depends on: Issue #8 (token counting), core/enums/health.py
  └─ Output: Health tracking, provider-specific configs, state machine
  └─ Note: Unblocks SLA Controller feature
```

### Week 6 (Resources + SLA)
```
Day 1-2: Issue #7 (Resource Cleanup + Connection Pooling)
  └─ Depends on: Issue #6 (StreamController)
  └─ Output: AsyncContext manager, graceful shutdown

Day 3-4: Issue #12 (ToolAwareModel Protocol)
  └─ Depends on: Issue #10 (ModelExecutor), Issue #11 (Agent refactor)
  └─ Output: Type-safe model+tools interface

Day 5: Features: SLA Controller + Stream Checkpoint
  └─ SLA: Depends on: Issue #9 (FallbackChain), Issue #8 (Token Counting)
  └─ Checkpoint: Depends on: Issue #6 (StreamController), Issue #1 (StreamChunk)
  └─ Output: Graceful degradation + cost-effective resumption
```

---

## Parallel Work (Non-Blocking)

### Database Restructuring (Gradual Migration)
- **Start:** Week 1 (Phase 1)
- **Dependency:** None (legacy/db is reference)
- **Sync Point:** After Issue #10 (know ModelExecutor shape for query context)
- **Dual-Write Window:** Weeks 1-3 (Phase 2)
- **Cutover:** After Phase 0.2-FIX (Phase 3)

### core/enums/ Directory
- **Start:** Week 1 (can draft Day 1)
- **Dependency:** None (define as you discover enum names)
- **Finalize:** After Issue #2, #3, #9 (know health, retry, transport enums)
- **Impact:** All week 1-6 issues use enums from here

### Headers Architecture (Pre-Phase 0.3)
- **Start:** After Issue #10 (ModelExecutor shape known)
- **Dependency:** Issue #10, #11, Issue #1, #6, #9
- **Layer 1 Start:** Week 3 (after Issue #10)
- **Layer 2 Start:** Week 4 (after Issue #11)
- **Migration:** Week 5-6

---

## Critical Path Analysis

**Longest Path to Completion:**
```
Issue #2 (Retry) → Issue #3 (Errors) 
  → [Issue #4, #5 parallel] 
  → Issue #10 (ModelExecutor)
  → Issue #11 (Agent)
  → Issue #1 (StreamChunk)
  → Issue #6 (StreamController)
  → Issue #8 (Token Counting)
  → Issue #9 (FallbackChain)
  → [Features: SLA + Checkpoint]
  → [Headers: Layer 1 + Layer 2]

Total: ~6 weeks + 1 week headers = 7 weeks

**Non-Critical Path (Can Slip):**
- Headers Layer 1 (blocked on Issue #10, starts Week 3)
- Headers Layer 2 (blocked on Issue #11, starts Week 4)
- Headers Migration (after all layers, Week 5-6)
- Database Phase 3 (after Phase 0.2-FIX, Week 7+)
```

**Compression Opportunity:**
- If Headers Layer 1 drafting starts Day 1, can have first cut by end of Week 3
- If Database Phase 1-2 parallel to Week 1-3, migration plan ready earlier

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| ModelExecutor extraction complexity | Block entire Week 3 if needed; don't compress |
| StreamController buffering bugs | Extensive unit tests (pause/resume/drain safety) |
| Database dual-write inconsistency | Version queries, keep legacy/db read fallback until Phase 3 |
| Token counting accuracy | Test against 3 real models (±5% tolerance), configurable in config.py |
| FallbackChain race conditions | Use immutable snapshots, not mutable registry |

---

## Success Criteria

- [ ] Week 1: Retry + Errors + Enums complete
- [ ] Week 2: Ollama + LocalSDK complete, all return `AsyncIterator[StreamChunk]`
- [ ] Week 3: ModelExecutor extracted, Agent refactored
- [ ] Week 4: StreamChunk v2, StreamController working (pause/resume/drain safe)
- [ ] Week 5: Token counting + FallbackChain (health metrics working)
- [ ] Week 6: Resource cleanup, ToolAwareModel, SLA + Checkpoint features
- [ ] Post-Week 6: Headers Layer 1+2, Database Phase 1-2 parallel, ready for Phase 0.3

---

## Document Cross-References

| When You Need... | See Document |
|---|---|
| How to implement Issue #X | → 01_Core_Stream_Lifecycle.md, 02_Reliability_Layer.md, 03_Orchestration.md |
| Headers architecture details | → Headers_Architecture.md (after headers docs created) |
| Database migration plan | → Database_Restructuring.md (after db docs created) |
| Design decisions rationale | → DESIGN_DECISIONS.md (after decisions docs created) |
| Full roadmap + status | → plan.md (main index) |
| This dependency graph | → You are here (IMPLEMENTATION_GRAPH.md) |

