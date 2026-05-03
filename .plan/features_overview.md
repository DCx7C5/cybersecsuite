# Features Overview: What We're Implementing

**Status**: 📋 Core Features + 4 Implementation Tracks  
**Updated**: 2026-05-03  
**Total Todos**: 115 (107 pending, 8 done)

---

## 🔄 Implementation Roadmap (4 Parallel Tracks)

| Track | Focus | Todos | Est. Impact |
|-------|-------|-------|------------|
| **Track 1: Architecture** | Phases 0-6 (Multi-Orch + TeamScope) | 10 | Highest |
| **Track 2: SDK Pattern** | response.py + 4 SDKs + unified client | 15 | High |
| **Track 3: Module Consistency** | 5-file pattern for 19 modules (95 files) | 42 | High |
| **Track 4: Core Consistency** | 5-file pattern for 8 core subdirs (28 files) | 38 | High |
| **Track 5: Other** | Inspection, consolidation, docs | 10 | Medium |

**Estimated Total Effort**: 
- Code files to create: 67 (modules) + 28 (core) = 95 files
- Code files to refactor: 24 (api_services) + 15 (modules) = 39 files
- Tests & docs: 20+ files
- **Grand Total**: ~160 files across all tracks

---

## 🎯 FEATURE 1: Multiple Orchestrator Processes

### Problem
Currently: 1 orchestrator per session → **Serial execution** (slow)

### Solution
Enable N concurrent orchestrators on same SessionScope for **parallel execution** with automatic scaling, fault tolerance, and result merging.

### Key Capabilities
- ✅ Parallel execution (3-10 tasks running simultaneously)
- ✅ Pull-based task allocation (PostgreSQL queue)
- ✅ Automatic orchestrator scaling (spawn/kill dynamically)
- ✅ Crash detection & recovery (heartbeat monitoring: 5s check, 300s timeout)
- ✅ Atomic result merging (idempotency keys prevent duplicates)
- ✅ Health monitoring (detect & recover from failures)

### Architecture
```
PostgreSQL Task Queue (pull-based)
    ├─ Task 1 → Orchestrator-1 (running)
    ├─ Task 2 → Orchestrator-2 (running)
    ├─ Task 3 → Orchestrator-3 (running)
    ├─ Task 4 → Orchestrator-1 (after first completes)
    └─ Task 5 → Orchestrator-2 (after first completes)

Each orchestrator independently pulls tasks, executes, reports results
Results merged atomically with idempotency (no duplicates)
Batched merge reduces DB writes
```

### API: CLI Commands
```bash
css orchestrator spawn --session 123 --count 5
css orchestrator list --session 123
css orchestrator health --session 123
css orchestrator shutdown --session 123 --orch-id 1
```

### API: REST Endpoints
```
GET    /sessions/{id}/orchestrators
GET    /sessions/{id}/orchestrators/{orch_id}/health
POST   /sessions/{id}/orchestrators/spawn
DELETE /sessions/{id}/orchestrators/{orch_id}
```

### Success Criteria
- ✅ 3-5 concurrent orchestrators on same session
- ✅ <5% performance overhead vs single orchestrator
- ✅ Zero data loss under normal operations
- ✅ Automatic recovery from crashed orchestrator
- ✅ All 1000+ existing tests pass

---

## 🎭 FEATURE 2: TeamScope (Nested Session Scopes)

### Problem
Currently: All tasks in same queue → **Monolithic execution**  
Goal: Tasks grouped by teams with **complete isolation** and resource quotas

### Solution
Add TeamScope as a sub-level within SessionScope where each team operates independently with separate orchestrators, task queues, and resource limits.

### Scope Hierarchy (NEW)
```
Level 1: ProjectScope (organizational container)
Level 2: ApplicationScope (application instance)
Level 3: SessionScope (forensic investigation)
Level 4: TeamScope (NEW) ← Sub-division of session
         └─ Independent orchestrators + task queue per team
```

Example:
```
SessionScope
    ├─→ TeamScope-1 (Engineering, max 3 orch, priority 2)
    ├─→ TeamScope-2 (Security, max 10 orch, priority 1)
    └─→ TeamScope-3 (Compliance, max 1 orch, priority 3)
```

### Key Capabilities
- ✅ Complete team isolation (Team A crash ≠ Team B affected)
- ✅ Resource quotas (max_concurrent_orchestrators per team)
- ✅ Priority scheduling (high-priority teams get more resources)
- ✅ Independent lifecycle (teams can pause/complete separately)
- ✅ Logical grouping (organize by role: engineering, security, compliance)
- ✅ Per-team task queues (no contention between teams)

### Team Data Model
```python
@dataclass
class Team:
    id: int
    session_id: int
    name: str                          # "engineering", "security", etc.
    team_type: str = "general"
    max_concurrent_orchestrators: int = 3
    orchestrator_timeout_sec: int = 300
    orchestrator_count: int = 0
    status: str = "active"             # "active", "paused", "completed"
    priority: int = 1                  # 1-10, higher = more resources
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
```

### Team Execution Example
```
Session: "Forensic Investigation ABC"
├─ Team-1 (Engineering, 5 orch): 50 forensic tasks in parallel
├─ Team-2 (Security, 8 orch): 80 threat detections in parallel
└─ Team-3 (Compliance, 2 orch): 20 compliance checks in parallel

Total: 15 orchestrators, 150 tasks, all running in parallel
If Team-1 crashes → Teams 2 & 3 continue unaffected
```

### Team Lifecycle
```
States: active (running) → paused (frozen) → completed (done)
Transitions:
  active → paused (manual)
  active → completed (manual or on-timeout)
  paused → active (manual resume)
```

### API: CLI Commands
```bash
css team create --session 123 --name engineering --max-orch 3 --priority 2
css team list --session 123
css team status --team 456
css team pause --team 456
css team resume --team 456
css team complete --team 456
css team metrics --team 456
```

### API: REST Endpoints
```
POST   /sessions/{id}/teams
GET    /sessions/{id}/teams
GET    /sessions/{id}/teams/{team_id}
PATCH  /sessions/{id}/teams/{team_id}
DELETE /sessions/{id}/teams/{team_id}
GET    /sessions/{id}/teams/{team_id}/metrics
```

### Success Criteria
- ✅ Create 5 teams on same session
- ✅ Each team spawns up to 10 orchestrators independently
- ✅ One team crash doesn't affect others
- ✅ Team pause/resume works
- ✅ Results isolated per team
- ✅ All 1000+ existing tests pass

---

## 🔄 How They Work Together

**Multi-Orchestrator** (Feature 1)
- Provides: Pull-based task queue, crash detection, atomic result merge

**TeamScope** (Feature 2)
- Enhances: Separate queues per team, resource quotas, priority scheduling

**Combined Result**
```
N teams × M orchestrators per team = NM parallel execution
With complete isolation + automatic scaling + fault tolerance
```

---

## 📊 Database Schema Changes

### New Tables
- **teams** — Team metadata (session_id, name, max_orch, priority, status, is_active, created_at, updated_at, deleted_at)
- **orchestrator_instances** — Active orchestrators (id, session_id, team_id, process_id, heartbeat_at, status, assigned_task_count)
- **task_assignments** — Task ownership (id, session_id, team_id, orchestrator_id, task_id, status, idempotency_key, created_at, started_at, completed_at)

### Extended Columns
- **sessions** — Add: orchestrator_mode, max_teams, team_count, enable_team_isolation
- **scoped_entry** — Add: team_id FK, extend scope_level to include "team"

### Indexes
- (team_id, is_active)
- (session_id, status)
- (priority DESC, status)
- (team_id, status)
- (task_id, status)
- (idempotency_key)

---

## 📊 Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Concurrency** | 1 orch, serial | N orch, parallel |
| **Throughput** | 1 task/sec | 10-50 tasks/sec |
| **Latency** | 1000 tasks = 1000s | 1000 tasks = 50-100s |
| **Failure resilience** | Crash = lose session | Crash = auto-recover |
| **Team isolation** | N/A | Complete isolation |
| **Resource quotas** | N/A | Per-team limits |

---

## 🔧 FEATURE 3: Config Integration (CONFIG_SPEC Pattern)

### Problem Statement
- config.py only loads ~8 env vars (incomplete)
- Type inconsistencies (ports as strings, not ints)
- No validation of required variables
- .env.example manually maintained (hard to keep in sync)
- manager.py has hardcoded defaults instead of using config

### Solution: CONFIG_SPEC Metadata Pattern

**Key Decision**: `config.py` IS SOURCE OF TRUTH (not `.env.example`)

1. Define **CONFIG_SPEC** dict in config.py with all options
2. Each option: env var name, type, default, required flag, docstring
3. Implement 6 dataclasses from CONFIG_SPEC (PostgresConfig, RedisConfig, etc.)
4. **Generate .env.example** from CONFIG_SPEC (never manual edit)
5. Integrate with manager.py to use CONFIG defaults

### Implementation (5 Phases)
- **Phase 1**: Create CONFIG_SPEC with all 20+ config options
- **Phase 2**: Implement dataclasses (PostgresConfig, RedisConfig, A2AServerConfig, etc.)
- **Phase 3**: Backwards-compatible dict access (POSTGRES_DATABASE, etc.)
- **Phase 4**: Generate .env.example from CONFIG_SPEC
- **Phase 5**: Integrate with manager.py + tests

**Result**: Single source of truth (config.py), proper types, auto-generated docs

**Related Section**: See plan.md § PHASES & MILESTONES for Phase 5 details

---

## 🤖 FEATURE 4: SDK Architecture (4 Layer Implementation)

### Layer 1: response.py Pattern (All 24 Providers)
Add `response.py` to centralize response parsing and request mapping:
- Request format mapping (generic → provider-specific)
- Response parsing (provider → generic StreamChunk)
- Error extraction and transformation
- Streaming format handling (SSE, JSON chunks, etc.)

### Layer 2: Custom SDKs (4 Types)
1. **Unified REST Client SDK** — For providers without official SDKs (DeepSeek, Perplexity, etc.)
2. **Ollama Local SDK** — Enhanced local model inference
3. **WebLLM Browser SDK** — Browser-based LLM inference
4. **response.py Pattern** — Provider-specific format mapping (already covered above)

### Layer 3: Universal LLM Client (Meta-SDK)
After all 4 SDKs complete, create **one unified client** that handles routing:
```python
client = UniversalLLMClient(provider_type)  # Works for ANY provider
await client.call_llm(model, messages)      # Transparent SDK routing
```

Routes automatically to:
- Official SDKs (anthropic, openai, groq, etc.)
- REST-mapped providers (deepseek, perplexity, etc. via response.py)
- Local models (ollama)
- Browser-based (webllm)

### Benefits
- Single entry point for orchestrator
- No import logic needed
- Transparent SDK selection
- Consistent interface across all providers
- Easy to add new providers

### Implementation Sequence
1. ✅ Analyze all 24 providers + create response.py base template
2. ⏳ Implement response.py for each provider (10 sub-tasks)
3. ⏳ Create 4 custom SDKs (REST, Ollama, WebLLM, response mappers)
4. ⏳ **NEW:** Create UniversalLLMClient (routes to correct SDK)
5. ⏳ Integrate into orchestrator + registry
6. ⏳ Validate with tests

**Related Section**: See architecture.md § COMPLETE SDK TOOLS REFERENCE for provider tool matrix

---

## 📦 FEATURE 5: Module Consistency Pattern & Auto-Loader Enhancement

### Problem Statement
**Current State** (fact-checked):
- 19 modules in `css/modules/` (after llm_harness consolidation and memory move)
- 24 providers in `css/api_services/`
- Module compliance: 2/19 fully compliant (11%)
- 17 modules non-compliant (89%)
- Missing ~60+ files total (types.py, enums.py, exceptions.py per module)

**Why This Matters**:
1. Loader.py can only auto-discover existing files (models.py, endpoints.py)
2. No consistency pattern = scattered code, duplicated exceptions/types
3. Makes orchestrator integration harder (can't reliably import module constants)
4. New modules created without template = inconsistent structure

### Solution: 5-File Module Pattern

Every module should have:
```
modules/<app_name>/
├── __init__.py           # Package marker
├── models.py             # Tortoise ORM models (auto-discovered IF present)
├── endpoints.py          # FastAPI routes (auto-discovered IF present)
├── enums.py              # Module enumerations (organizational structure only)
├── types.py              # Dataclasses, types (organizational structure only)
└── exceptions.py         # Custom exceptions (organizational structure only)
```

### 19 Current Modules

agents, cache, capabilities, chat, events, google_a2a, llm_models, llm_proxy, marketplace, memory, permissions, roles, scopes, skills, streaming, tags, teams, tools, working_dir

**Note**: Only `models.py` and `endpoints.py` are auto-discovered by loader.py. Both are optional (if missing, module is silently skipped). The other 3 files (types, enums, exceptions) provide organization and consistency but are NOT auto-discovered—they must be manually imported where needed.

### Implementation Phases

**Phase 1: Audit & Documentation** (DONE)
- Fact-checked all 19 modules
- Created compliance matrix
- Documented implementation guide

**Phase 2: Fill Missing Files (39 todos)**
- High priority: agents, llm_models, llm_proxy (13 files)
- Medium priority: teams, scope, permissions, cache, chat, streaming (27 files)
- Low priority: events, tools, tags (10 files)

**Phase 3: Loader Enhancement (4 todos)**
- Add auto-discovery for enums.py, types.py, exceptions.py
- Add validation (fail-fast if files missing)
- Create factory methods for lazy-loading module constants

**Phase 4: API Services Consistency (5 todos)**
- Audit all 24 providers for same pattern
- Create missing types.py, enums.py, exceptions.py

**Phase 5: Testing & Docs (8 todos)**
- Unit tests for loader auto-discovery
- Mock modules for error testing
- Module creation template + checklist
- Migration guide for existing code

### Total New Todos: 42 (module consistency implementation)

### Success Criteria
- [ ] All 19 modules have 5-file structure (models, endpoints, types, enums, exceptions) for organization
- [ ] loader.py auto-discovers endpoints.py + models.py (if present)
- [ ] Types/enums/exceptions manually imported where needed (no auto-discovery)
- [ ] 0 import errors from modules/ on app startup
- [ ] Module creation template + checklist provided
- [ ] Tests for endpoint/model discovery (>80% coverage)

### Key Decision
**Preserve Existing Structure**: Add files only, no directory reorganization. Adapt to existing layout per project rules.

**Related Section**: See rules.md § MODULE PATTERN for consistency rules

---

## 🏗️ FEATURE 6: Core/ Directory Pattern Consistency

### Fact-Checked Audit (9 subdirs)

**Current State**:
- ✓ 1 subdir has pattern (db/ has enums.py, exceptions.py)
- ✗ 8 subdirs non-compliant (asgi, database, llm_harness, memory, orchestration, redis, retry, types)
- Missing 28 files total

**Key Issues**:
1. **Types scattered** — types/ has 7 files + 2 subdirs, no central API
2. **No consistency pattern** — only db/ follows structure, others ad-hoc
3. **Missing models** — orchestration/, redis/, retry/ manage state with no models.py
4. **Unclear boundaries** — who owns what? database/ vs db/, asgi/ vs orchestration/?

### Solution: Apply 5-File Pattern to Core

Same pattern as modules/:
```
core/<subdir>/
├── models.py             # Data models (Tortoise)
├── types.py              # Dataclasses, types
├── enums.py              # Enumerations
├── exceptions.py         # Custom exceptions
└── [existing files]      # Keep as-is
```

### Implementation Plan

**Phase 2: Fill Missing Files (28 files)**
- orchestration/: 4 files (models, types, enums, exceptions)
- redis/: 4 files (models, types, enums, exceptions)
- retry/: 4 files (models, types, enums, exceptions)
- llm_harness/: 3 files (types, enums, exceptions)
- memory/: 3 files (types, enums, exceptions)
- database/: 3 files (types, enums, exceptions)
- asgi/: 3 files (types, enums, exceptions)
- types/: Consolidate (move entities/* to entity_types.py, add __init__.py index)

**Phase 3: Update loader.py**
- Add auto-discovery for core/*/types.py, core/*/enums.py, core/*/exceptions.py
- Validate files exist at startup

**Phase 4: Documentation**
- Document responsibility boundaries
- Create core/ architecture guide
- Add tests for type discovery

### Success Criteria
- [ ] All 8 core subdirs have 5-file structure (models, types, enums, exceptions) for organization
- [ ] loader.py auto-discovers models.py (if present) in core/*/
- [ ] Types/enums/exceptions manually imported where needed
- [ ] 0 import errors from core/ on startup
- [ ] Types are centralized and well-documented
- [ ] 28 organizational files created/consolidated

**Related Section**: See rules.md § MODULE PATTERN for consistency rules (applies to core/ as well)

---

## 🎬 Next Steps

1. Review **plan.md** for 7-phase timeline & milestones
2. Check **session.db** for todo tracking (133 todos across 7 phases, 36 tasks)
3. Read **development-workflow.md** for development process (TODO/TASK/PHASE workflows)
4. Read **architecture.md** for system design & scope hierarchy
5. Start **Phase 0**: Create TeamScope model (4 tasks, 10 days)
