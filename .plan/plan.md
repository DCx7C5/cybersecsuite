# CyberSecSuite: Implementation Plan

**Main Workdir**: `/home/daen/Projects/cybersecsuite/.plan/`  
**Status**: 🟡 Mixed execution state | `session.db` is current | 5 Architecture Proposals Approved  
**Updated**: 2026-05-09 (plan.md cleanup — removed deprecated/completed sections)  
**Todos**: 832 total (447 done, 379 pending, 6 blocked, 0 in_progress) | PHASE > TASK > TODO enforced in session.db

**Consistent File Patterns**: Track exact compliance in Phase 3/4 todos and local module docs; do not treat this section as a live count source  
**Last Update**: Phase 10 SDK Architecture — 9 todos completed (T10.1-T10.4, T10.6)  
**Next**: pick the next ready todo from `session.db` by `sort_order`

### Normalization Status (2026-05-07)

- ✅ Active scope (`src/css` + `tests`) normalized to Python 3.14 typing rules.
- ✅ Active scope migrated from `@dataclass` to `msgspec.Struct`.
- ⛔ `src/legacy/**` excluded by explicit user directive until requested.

### ✅ Completed Phases

| Phase | Title | Todos |
|-------|-------|-------|
| 0 | Team Foundation | ✅ 12 done (teamscope-1–12) |
| 1 | Multi-Orchestrator Core | ✅ 10 done (orchestrator-1–10) |

### Module Status Snapshot

**Binding ownership note (2026-05-08)**:
- `accounts`, `events`, `marketplace`, and `memory` are core-owned packages.
- `accounts` now exists only under `src/css/core/accounts/`; do not recreate `src/css/modules/accounts/`.
- `rag_vector` is the remaining module-side migration surface; active shared retrieval runtime code is being consolidated in `src/css/core/rag_vector/`.
- `rag_graph` is the sibling core-owned graph retrieval package under `src/css/core/rag_graph/`.
- `working_dir` is retired terminology. Use `core/workspace/` and the general session/project directory structure.

**High-level package snapshot**:
- Core-owned, active: `marketplace`, `events`
- Core-owned, migration still incomplete: `memory`, `workspace`
- Business modules with stable patterns: `a2a_google`, `tasks`, `teams`, `tools`
- Business modules still aligning: `agents`, `chat`, `skills`, `tags`, `triage`, `workflows`, others
- Deprecated: `scopes`

### API Provider Status

**24 providers** in `src/css/api_services/` (per session.db and rules.md)

| Status | Providers |
|--------|-----------|
| ✅ Implemented | anthropic, openai, gemini, groq, mistral, ollama, openrouter, cohere, ai21, together, github |
| 🟡 Pending | cerebras, cloudflare, deepinfra, deepseek, fireworks, huggingface, lambda_api, nscale, nvidia, opencode, perplexity, sambanova, xai |

See this file's **Module Status Snapshot** and phase sections for current core infrastructure analysis.

---

## 🚨 ACTIVE BLOCKERS

### 🔴 BLOCKER #1: Event System Incomplete
- **Impact**: Audit trail missing, agent update notifications broken, OTEL bridge blocked
- **Location**: Canonical ownership is `src/css/core/events/`; legacy module package removed
- **Fix**: Finish the core event system and Phase 14 instrumentation/interceptor layers (todos: `events-*`)
- **Blocks**: Phase 6 CQRS event store, `notifications-module-create`, agent observability

### 🔴 BLOCKER #2: Permissions Stubs Only
- **Impact**: No RBAC, no path enforcement, no tool gating — security critical
- **Location**: `src/css/core/permissions/` — 4 files but no working enforcement
- **Fix**: Phase 15 `core/workspace/` + PathGrant/ToolGrant + PermissionChecker (todos: `perm-*`, legacy `working-dir-*`)
- **Blocks**: All session execution, Phase 16 native tools, Phase 19 sessions module

### 🟠 ACTIVE: 5-File Pattern Compliance
- **Current**: 5/25 modules fully compliant (`a2a_google`, `marketplace`, `tasks`, `teams`, `tools`)
- **Remaining**: 20 modules need endpoints.py, types.py or both
- **Phase**: Phase 3 (modules) + Phase 4 (core subdirs)

---

### Current State
```
~/.css/sessions/<session_id>/          ← centralized session dir (no scope hierarchy)
    │
    └── Session
            └── Orchestrator (1, serial)
                        └── Agents (sequential)

[optionally linked via ProjectManager]
~/.css/projects/<id>/metadata.json  →  project.source_dir (user's code)
```

> ⚠️ **`ProjectScope` / `ApplicationScope` / `SessionScope` are DELETED.** The old 5-level SaaS scope
> hierarchy never fit a cybersec tool. Replaced by: `SessionContext` struct + `core/workspace/` +
> `ProjectManager`. All session files live centrally at `~/.css/sessions/`.

### Target State (After Phase 1)
```
~/.css/sessions/<session_id>/          ← centralized session dir
    │
    └── Session  [optional: linked to project via ProjectManager]
            └── Team(s)
                    └── Orchestrator Pool  ← N parallel processes
                            ├── Agent 1 (parallel)
                            ├── Agent 2 (parallel)
                            └── Agent N (parallel)
```

---

## 📋 PHASES & MILESTONES

| Phase | Title | Status |
|-------|-------|--------|
| 0 | Team Foundation | ✅ Complete |
| 1 | Multi-Orchestrator Core | ✅ Complete |
| 2 | SDK Pattern & Response | 🟡 Pending |
| 3 | Module Consistency | 🟡 Pending |
| 4 | Core Consistency | 🟡 Pending |
| 5 | Config Integration | 🟡 Pending |
| 6 | Architecture Overhaul (5 Proposals) | 🟡 Pending |
| 7 | Integration & Polish | 🟡 Pending |
| 8 | AI Execution Layer | 🟡 Pending |
| 9 | ORM/Manager/Registry | 🟡 Pending |
| 10 | Unified SDK Architecture | 🟡 11/13 done (browser relay deferred) |
| 11 | Cross-Provider Prompt Caching | 🟡 Pending |
| 12 | QoL Output Controls Migration | 🟡 Pending |
| 13 | Provider Routing & Resilience | 🟡 Pending |
| 14 | Event Hooks & Entry/Exit Instrumentation | 🟡 Pending |
| 15 | Permissions + WorkingDir | 🟡 Pending |
| 16 | Provider SDK Features | 🟡 Pending |
| 17 | Settings & Projects | 🟡 Pending |
| 18 | Frontend Foundation | 🟡 Pending |
| 19 | Module Restructuring + Sessions | 🟡 Pending |
| 20 | Persistent Memory Layer | 🟡 Pending |
| 21 | Qwen3-0.6B Triage Intelligence | 🟡 Pending |
| 22 | MCP Protocol Layer | 🟡 Pending |
| 23 | Prompt Registry | 🟡 Pending |
| 24 | Git Tracking & Worktree Isolation | 🟡 Pending |
| 25 | Integration Hardening | 🟡 Pending |
| 26 | Human Approval Workflows | 🟡 Pending |
| 27 | Graph Visualization Engine | 🟡 Pending |
| 28 | Auth & Accounts | 🟡 Pending |
| 29 | Cybersec Domain Layer | 🟡 Pending |
| 30 | Workflow Engine + IPC | 🟡 Pending |
| 31 | Production Readiness | 🟡 Pending |
| 32 | Reports Module | 🟡 Pending |
| 33 | Ollama Native | 🟡 Pending |
| 34 | Dependency Map | 🟡 Pending |
| 35 | Telemetry Infrastructure | 🟡 Pending |
| 36 | Local Proxy & Transport Surfaces | 🟡 Pending |
| 37 | SIEM/EDR Integration | 🟡 Pending |
| 38 | IDE PyCharm Integration | 🟡 Pending |

### Phase 0: TeamScope Foundation (10 days)

✅ **What**: Add Team model, team management — sessions already use `~/.css/sessions/` (no scope hierarchy)
📦 **Deliverables**: Team ORM model, team lifecycle, task assignments with team isolation, 4 API endpoints
🎯 **Success**: Teams can be created/listed/updated/deleted, agents assignable to teams

**4 Tasks**:
1. Team Model Creation (`teams/models.py` + Tortoise ORM) — 2 days
2. Team Entity & Database (Team dataclass, DB schema, isolation) — 2 days
3. Team-Session Linking (Session FK → team_id, no `scope.py` — that file is deleted) — 3 days
4. Team API Endpoints (REST + CLI) — 3 days

🔗 **See**: [architecture/system-overview.md](./architecture/system-overview.md) for detailed architecture

---

### Phase 1: Multi-Orchestrator Core (14 days)

✅ **What**: Enable N concurrent orchestrators per session (parallel execution)  
📦 **Deliverables**: Orchestrator pool management, pull-based task queue, crash detection, health monitoring  
🎯 **Success**: 3-5 orchestrators running in parallel, automatic failover working  

**5 Tasks**:
1. Orchestrator Models & Schemas (Tortoise ORM) — 3 days
2. Multi-Orchestrator Endpoints (CRUD, list, health) — 3 days
3. Load Balancing Strategy (round-robin, least-busy, weighted) — 3 days
4. Redundancy & Failover (crash detection, auto-recovery) — 3 days
5. Orchestrator Health Checks (periodic polling, metrics) — 2 days

🔗 **See**: [architecture/multi-orchestrator.md](./architecture/multi-orchestrator.md) for detailed architecture

---

### Phase 2: SDK Pattern & Response (12 days)

✅ **What**: Full provider pipeline — response.py per provider, provider-agnostic routing  
📦 **Deliverables**: CSSResponse dataclass, per-provider response.py, 26 providers wired  
🎯 **Success**: All 26 providers callable through UniversalLLMClient (no hardcoded Claude)

> **Note**: `UniversalLLMClient` and `SDKRegistry` shell already exist (Phase 2 Completion Summary below). Gap: most providers still hardcode Claude or aren't wired. This phase completes the routing.

**5 Tasks**:
1. Unified Response Layer (CSSResponse dataclass, streaming) — 3 days
2. Async SDK Wrappers (Anthropic, OpenAI, Google, etc.) — 4 days
3. Streaming Support (SSE, chunked responses) — 2 days
4. Error Handling & Retry (exponential backoff, rate limits) — 2 days
5. SDK Tools Registry (discovery, capability matrix) — 3 days

---

### Phase 3: Module Consistency (14 days)

✅ **What**: Enforce 5-file pattern on all 25 modules  
📦 **Deliverables**: ~80 new files (models.py, endpoints.py, types.py, enums.py per module)  
🎯 **Success**: All 25 modules fully compliant with pattern (currently 5/25)  

**6 Tasks**:
1. Modules: models.py Pattern — 2 days
2. Modules: endpoints.py Pattern — 2 days
3. Modules: types.py Pattern (entity consolidation) — 3 days
4. Modules: enums.py Pattern — 1 day
5. Modules: exceptions.py Pattern — 1 day
6. Module Loader Validation — 2 days

🔗 **See**: [development-workflow.md](./development-workflow.md) for completion patterns

---

### Phase 4: Core Consistency (12 days)

✅ **What**: Enforce 5-file pattern on all 8 core subdirectories  
📦 **Deliverables**: 28 new files (types.py, enums.py, exceptions.py per subdir)  
🎯 **Success**: All 8 core subdirs fully compliant with pattern  

**7 Tasks**:
1. Core: models.py Pattern — 2 days
2. Core: endpoints.py Pattern — 2 days
3. Core: types.py Pattern — 2 days
4. Core: enums.py Pattern — 1 day
5. Core: exceptions.py Pattern — 1 day
6. Core Loader Validation — 2 days
7. ABC & @dataclass Consistency Fix — 2 days

🔗 **See**: [`src/css/core/types/plan.md`](../src/css/core/types/types.md) for core type patterns

---

### Phase 5: Config Integration (8 days)

✅ **What**: config.py as single source of truth  
📦 **Deliverables**: CONFIG_SPEC pattern, .env.example generation, manager.py integration  
🎯 **Success**: All config centralized, .env.example auto-generated  

**4 Tasks**:
1. CONFIG_SPEC Pattern — 2 days
2. .env.example Generation — 2 days
3. Runtime Config Loading — 2 days
4. Manager.py Integration — 1 day

🔗 **See**: [`src/css/core/db/plan.md`](../src/css/core/db/postgres-db.md) for database patterns

---

### Phase 6: Architecture Overhaul — 5 Proposals (NEW, APPROVED)

🚀 **What**: State-of-the-art architectural improvements across type system, provider layer, domain model, plugin system, and async pipeline  
📦 **Deliverables**: msgspec value types, YAML provider specs, CQRS event store, entry_points loader, async generator pipeline  
🎯 **Success**: 10-40× serialization performance, 26 providers → 26 YAML files, forensic replay, 20-line loader, composable pipeline  

**25 Todos across 5 Tasks** (all in session.db, phase=`Phase 6 — Architecture Overhaul`):

#### T6.1 Protocol-first + msgspec.Struct (Proposal 1)
Replace @dataclass+ABC mixing with `Protocol` for structural contracts and `msgspec.Struct` for value types.
- `p6-msgspec-install` — Add msgspec>=0.18 to pyproject.toml
- `p6-msgspec-struct-base` — Replace BaseMessage/Tool/ModelMetadata with msgspec.Struct
- `p6-msgspec-protocols` — Create core/types/protocols.py (AgentLike, SkillLike, ToolLike)
- `p6-msgspec-context` — Fix context.py @dataclass+BaseModel anti-pattern
- `p6-msgspec-ipc` — Replace json.dumps IPC with msgspec.msgpack binary transport

#### T6.2 YAML Providers + HttpProviderAdapter (Proposal 2)
Replace 24 Python provider classes (~4800 LOC) with 24 YAML specs + 1 generic adapter (~150 LOC).
- `p6-yaml-spec-schema` — Define ProviderSpec msgspec.Struct schema
- `p6-yaml-adapter` — Create HttpProviderAdapter(BaseApiServiceClient)
- `p6-yaml-write-openai-compat` — Write spec.yaml for 8 OpenAI-compat providers
- `p6-yaml-write-proprietary` — Write spec.yaml for 6 proprietary providers
- `p6-yaml-replace-registry` — Replace broken registry.py (src.api_services.* paths)

#### T6.3 CQRS Event Store (Proposal 3)
Every domain mutation → immutable DomainEvent in PostgreSQL. Tortoise models become projections.
- `p6-events-store-model` — DomainEventRecord Tortoise ORM model
- `p6-events-domain-event` — DomainEvent struct + EventStore.append/replay
- `p6-events-command-bus` — CommandBus + handlers for teams/tasks/agents
- `p6-events-projections` — PermissionProjection + AuditProjection from stream
- `p6-events-otel-bridge` — DomainEvent → OTEL spans (implements otel stub)

#### T6.4 entry_points Plugin System (Proposal 4)
Replace pkgutil.iter_modules() with importlib.metadata entry_points. Loader → 20 lines.
- `p6-entrypoints-pyproject` — Add css.modules + css.api_services entry_points groups
- `p6-entrypoints-loader` — Rewrite core/loader.py (20 lines)
- `p6-entrypoints-module-protocol` — CSSModule Protocol definition
- `p6-entrypoints-test-isolation` — conftest.py per-test entry_point loading (fixes 33 failures)

#### T6.6 Architecture Docs Update
Update all `.plan/architecture/*.md` files to reflect the new architecture decisions.
- `arch-sdks` ✅ — Rewrote sdks.md: YAML specs + HttpProviderAdapter replaces SDK matrix
- `arch-observability` ✅ — Rewrote observability.md: DomainEvent+EventStore+OtelBridge
- `arch-system-overview` — Update system-overview.md: msgspec IPC, pipeline, event store
- `arch-module-relationships` — Update module-relationships.md: EventStore as new integration hub
- `arch-multi-orchestrator` — Update multi-orchestrator.md: msgspec IPC + entry_points agents
- `arch-parallelisation` — Update parallelisation.md: async generator pipeline (Level 3)
- `arch-session-modes` — Update session-modes.md: msgspec.Struct IPC message types
- `arch-orchestrator-delegation` — Update orchestrator-delegation.md: msgspec messages
- `arch-tools-startup` — Update tools-startup.md: entry_points provider scanning
- `arch-services` — Update services-frontend-backend.md: YAML provider context
- `arch-filesystem` — Update filesystem-layout.md: spec.yaml in api_services layout
- `arch-core-matrix` — Update core audit sections in plan.md: Phase 4 types + Phase 6 otel bridge
- `arch-frontend` — Write frontend.md (currently empty, 0 bytes)

---

### Phase 7: Integration & Polish (14 days)

✅ **What**: Cross-module integration, testing, documentation, production readiness  
📦 **Deliverables**: Complete test suite, deployment guides, final documentation  
🎯 **Success**: Platform ready for production deployment  

**5 Tasks**:
1. Cross-Module Integration Testing — 3 days
2. Comprehensive Unit & Integration Tests — 4 days
3. Documentation Refresh — 3 days
4. Production Readiness Review — 2 days
5. Release & Changelog — 1 day

---

## 🎯 FEATURES (See [architecture/](./architecture/) docs for Details)

1. **Multi-Orchestrator** — Parallel execution with task queue
2. **TeamScope** — Team isolation & resource quotas
3. **Config Integration** — CONFIG_SPEC pattern, centralized config
4. **SDK Architecture** — Unified routing to 24+ LLM providers
5. **Module Consistency** — 5-file pattern for all modules
6. **Core Consistency** — 5-file pattern for all core subdirs

---

## 🚀 NEXT STEPS

### ✅ BLOCKING ISSUES RESOLVED [TRACK-0]

All 3 critical blockers completed via TASK workflow (3x syntax verification + git commit):

1. **ABC + @dataclass Violations** ✅
   - Fixed: base_entity.py, base_header.py, marketplace/base.py (5 violations)
   - Pattern: Removed @dataclass, converted to __init__-based ABC classes
   - Impact: Type system consistency restored

2. **Hardcoded Config Defaults** ✅
   - Fixed: manager.py lines 58-60, 97
   - Pattern: Updated to use config.py (POSTGRES_DATABASE, LOG_LEVEL)
   - Impact: Centralized config management enforced

3. **Cross-Module Import** ✅
   - Fixed: Moved client_pool.py to core/orchestration, updated streaming imports
   - Pattern: Allowed dependency (modules → core) enforced
   - Impact: Circular dependency risk eliminated

**Verification**: All files syntax-checked (3 passes), committed [TRACK-0]

### PHASE 0 + 1: ✅ COMPLETE

**Phase 0 — Team Foundation** (12 todos, committed [PHASE-0]):
- Team, TaskAssignment, TeamQuota ORM models
- TeamStatus/OrchestratorMode enums, lifecycle, pause/resume, orchestrator pool, results isolation, metrics, priority scheduler

**Phase 1 — Multi-Orchestrator Core** (10 todos, committed [PHASE-1]):
- OrchestratorInstance ORM, pull-based task queue, heartbeat, crash recovery, health metrics, load balancer (round-robin/least-busy/weighted), result merger

---

## ⏳ NEXT: Phase 2 — SDK Pattern & Response

**Goal**: Unified LLM client (UniversalLLMClient) routable to 26 providers  
See `src/css/core/orchestration/` for existing response_strategy_router.py + client_pool.py  
See [checkpoints.md](./checkpoints.md) for prior decisions

## 📈 PROGRESS TRACKING

```sql
-- Ready todos (no pending dependencies)
SELECT id, title FROM todos 
WHERE status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = todos.id AND dep.status != 'done'
)
LIMIT 10;

-- Phase progress
SELECT status, COUNT(*) FROM todos GROUP BY status;
```

See [development-workflow.md](./development-workflow.md) for completion workflows.

---

**Last Updated**: 2026-05-04T23:28  
**Working Directory**: [.plan/](file:///home/daen/Projects/cybersecsuite/.plan/)  
**Next Review**: Before Phase 2 start

---

## ✅ PHASE 2 COMPLETION SUMMARY (2026-05-03)

**Phase 2: Config Integration & SDK Architecture — COMPLETE**

See [checkpoints.md#phase-2](./checkpoints.md) for full details

### Deliverables (5 todos completed):

1. **Orchestration Roles** (modules/roles/)
   - OrchestrationRole base class + 3 concrete implementations
   - OrchestratorRole: Process-level coordinator (heartbeat 60s)
   - TeamLeaderRole: In-process coordinator (heartbeat 30s)
   - TeamMemberRole: In-process executor (heartbeat 15s)
   - Permissions + capabilities per role
   - Singletons + registry

2. **UniversalLLMClient** (core/types/universal_client.py)
   - SDKRegistry: Thread-safe provider → SDK routing
   - Lazy instantiation + caching
   - Concurrent init protection
   - Public API: register_sdk(), get_sdk(), clear_sdk_cache(), list_registered_sdks()

3. **API Services Consolidation** (core/types/api_services.py)
   - Single entry point: base types + UniversalLLMClient
   - 17 public exports
   - Clean separation: base abstractions vs. universal router

4. **Modules Auto-Discovery** (modules/__init__.py)
   - Dynamic module scanning
   - get_module(), list_modules(), list_failed_modules()
   - 16+ modules discovered
   - Graceful error handling

5. **Integration Test & Finalization**
   - 6-point verification (config, roles, registry, discovery, consolidation, infrastructure)
   - 3-pass syntax check: CLEAN ✅
   - All circular imports checked: None detected ✅

### Architecture Decisions Locked:

- CONFIG_SPEC = (b) Keep existing config.py
- UniversalLLMClient = (b) Registry + lazy-load pattern
- Orchestration Roles = (c) Define in modules/roles/
- Endpoints = Deferred to Phase 3
- Module Init = (6) Always auto-discover

### Code Quality: 3-Pass Verification

✅ PASS 1: Syntax verification (all files)
✅ PASS 2: Import structure (5 files, 20 definitions)
✅ PASS 3: Circular import detection (none found)

### Files Changed:

Created:
- modules/roles/role_types.py (140 lines)
- core/types/universal_client.py (220 lines)

Modified:
- modules/roles/__init__.py (30 lines)
- core/types/api_services.py (55 lines)
- modules/__init__.py (120 lines)

### Commits Made (5 total):

1. Feat: Orchestration-specific roles module
2. Feat: UniversalLLMClient registry + lazy-load router
3. Consolidate: Core API services root — base + universal client
4. Feat: Modules package auto-discovery
5. TASK: Phase 2 integration test & finalization

**Status**: ✅ COMPLETE  
**Impact**: Foundation for Phase 3 (SDK routing, query execution)

---

**Last Updated**: 2026-05-04T16:45  
**Next Review**: Before Phase 2 kickoff

**12 Critical Blockers Fixed** ✅ [BLOCKER-FIX]
- B1: Removed duplicate Task type from core/types/query.py
- B2: Enhanced TaskAssignment ORM with task_payload (JSON), priority, timeout_seconds  
- B3: Created TaskResult ORM model (1:1 FK → TaskAssignment)
- B4: Wired TaskLifecycle → TeamMember execution chain
- B5: Type-safe QueryExecutor → TeamLeader pipeline (Query objects)
- B6: Added asyncio.timeout() enforcement
- B7: Retry loop with exponential backoff (2^N capped @30s)
- B8: Exception handling with TaskLifecycle.fail_task() updates
- B9: ORM persistence in create_task() → TaskAssignment.create()
- B10: team_id/orchestrator_id validation in QueryExecutor
- B11: get_task() deserialization from TaskAssignment.task_payload
- B12: TeamMember.execute() accepts Task objects, returns Result

**Status**: All resolved, integration chain verified  
**Verification**: 3-pass syntax check CLEAN ✅  
**Impact**: Unlocks Phase 2 (Config Integration & SDK Architecture)

---

## 🤖 RUBBER-DUCK SYNCHRONIZATION PLAN (2026-05-03) — COMPLETED ✅

**Objective**: Synchronize all 48 local planning markdown files with session.db

**Three Parallel Agents** (All Completed):
1. **Agent 1: API Services Auditor** — Analyzed the provider planning set that is now consolidated in `src/css/api_services/api_services.md`
   - 12 providers ready for Phase 2 refactoring
   - 10 providers TBD (Q3 research)
   - Individual provider details in their local planning markdown files

2. **Agent 2: Core Infrastructure Auditor** — Analyzed the local core planning markdown files for the targeted core areas
   - 3/4 components production-ready
   - 1 stub (otel) for Phase 4
   - Individual component details in their local planning markdown files

3. **Agent 3: Module Consistency Auditor** — Analyzed the then-current `src/css/modules/*/<module>.md` set
   - 5 production-ready (23%)
   - 11 pending Phase 2-3 (50%)
   - 6 blocked/stubs (27%)
   - Individual module details in their local module markdown files

**Results**:
- ✅ 48/48 source planning markdown files synced with audit timestamps
- ✅ session.db: now 542 total (193 done, 348 pending, 1 blocked)
- ✅ Critical path determined (4-tier implementation strategy)
- ✅ Dependencies tracked (12 critical path dependencies)

**See**: `.plan/checkpoints.md` Checkpoint 002 for full rubber-duck coordination results

---

## 🔍 CORE INFRASTRUCTURE AUDIT RESULTS (2026-05-03)

**Agent**: rubber-duck-2-core-infra | **Status**: ✅ COMPLETE

### Executive Summary

**Audit Scope**: 4 core components (asgi, db, types, otel)

| Component | Status | Pattern | LOC | Priority |
|-----------|--------|---------|-----|----------|
| @asgi | 🟢 Implemented | ✅ 5/5 | 224 | 🔴 High |
| @db | 🟢 Implemented | ✅ 5/5 + models/ | 969 | 🔴 High |
| @types | 🟢 Implemented | ⚠️ 13/5 oversized | 1654 | 🔴 High |
| @otel | 🟡 Stub | ❌ 0/5 | 0 | 🟡 Medium |

**Total Integration Points**: 12 direct + 8 indirect → All working ✅

**Circular Dependencies**: 1 identified (types ↔ retry) → Mitigated ✅

---

### Key Findings

#### 🟢 STRONG: ASGI Module
- Perfect 5-file pattern compliance
- Clean dependency tree (4 core components)
- Single reverse dependency (main.py entry point)
- Production ready
- **Recommendation**: No changes needed

#### 🟢 STRONG: DB Module
- Solid 5-file pattern (+ models/ subdirectory reasonable)
- Complex model structure (4 model files, well-organized)
- Central to system (50+ files depend on it)
- Good separation of concerns
- **Recommendation**: Migrations strategy needs clarification (Tortoise vs Alembic)

#### 🟡 CONCERN: TYPES Module (Oversized)
- 13 root files + 5 provider files (Phase 2 additions)
- Violates 5-file pattern but expansion justified
- Foundation layer (no circular risks)
- **Urgent Refactoring**: Consolidate into subdirectories (base/, api/, events/, providers/)
- **Impact**: Phase 4 maintenance task
- **Effort**: 3 hours for reorganization
- **Recommendation**: Create subdirectories for better organization:
  ```
  types/
  ├─ base/              (base.py, sdk_local.py, entities.py)
  ├─ api/               (capabilities.py, headers.py, query.py)
  ├─ events/            (hook_events.py, context.py)
  ├─ providers/         (Phase 2: provider base classes)
  └─ __init__.py        (unified exports)
  ```

#### 🟡 CONCERN: OTEL Module (Empty Stub)
- 0 lines of code — not started
- Plan documented but implementation pending
- No blocking dependencies
- **Recommendation**: Phase 3-4 work; deferred for now
- **Priority**: Medium (observability, not critical path)

---

### Integration Analysis

#### Dependency Chain
```
ASGI
├─ loader (router discovery)
├─ types (request/response models)
├─ db (ORM initialization in lifespan)
└─ logger (request logging)

DB
├─ asgi (init in lifespan)
├─ logger (event logging)
├─ config (credentials)
└─ 50+ modules (model access)

TYPES (Foundation)
├─ Nothing (foundation layer)
└─ Used by: 50+ files across all modules

OTEL (Planned)
├─ (Future) asgi (trace requests)
└─ (Future) db (trace queries)
```

#### Circular Risk Assessment
- 🟠 **Risk 1 (MEDIUM)**: types ← retry ← types (indirect)
  - Status: ✅ **MITIGATED** via lazy imports
  - No blocking issues

- 🟢 **Risk 2 (LOW)**: db → types → retry
  - Status: ✅ **MEDIATED** through module structure
  - No action needed

---

### Phase 2 Impact Assessment

**Phase 2 Provider Refactoring** adds to @types:
- `providers/base_providers.py` (142 lines) — APIProviderBase, LocalProviderBase
- `providers/ollama_provider.py` (155 lines) — OllamaProviderBase
- `providers/headers/` (200+ lines) — Provider-specific headers
- `providers/__init__.py` (71 lines) — Provider re-exports

**Impact**: Makes @types even larger (now 1800+ lines)
**Mitigation**: Implement subdirectory consolidation before Phase 3

---

### Success Criteria Checklist (12/12 ✅)

- ✅ All 4 core components audited
- ✅ Dependency graph fully documented
- ✅ Circular import risks identified & assessed
- ✅ 5-file pattern compliance matrix created
- ✅ Every integration point validated
- ✅ Implementation status clear for each component
- ✅ Readiness assessment provided
- ✅ Phase 2 impact identified
- ✅ Recommendations prioritized
- ✅ Refactoring opportunities noted
- ✅ OTEL stub documented

---

### Action Items (Phase 4)

| Priority | Task | Effort | Risk |
|----------|------|--------|------|
| 1 | Consolidate @types into subdirectories | 3h | LOW |
| 2 | Implement @otel module (full stack) | 8h | NONE |
| 3 | Verify types↔retry cycle mitigation | 1h | LOW |
| 4 | Add @db model discovery caching | 4h | LOW |
| 5 | Cleanup/populate empty db/utils.py | 0.5h | LOW |

---

### Reference

- Updated plan files: `src/css/core/{asgi,db,types,otel}/plan.md`

---

---

## 🔍 API SERVICES AUDIT RESULTS (2026-05-03)

**Agent**: rubber-duck-1-api-services | **Status**: ✅ COMPLETE

### Executive Summary

**Audit Scope**: 22 API service providers

| Category | Count | Status |
|----------|-------|--------|
| **Fully Documented** | 12 | ✅ 54% (Ready for Phase 2) |
| **Pending Research** | 10 | ⏳ 46% (Q3 target) |
| **OpenAI-Compatible** | 6 | ✅ Standardized |
| **Proprietary APIs** | 10 | ✅ Feature-complete |
| **Local/Offline** | 1 | ✅ Ollama |
| **Cloud APIs** | 19 | ✅ Fully documented |

---

### ✅ READY FOR PHASE 2 (12 Providers)

| Provider | Type | Status | Tools | Vision | Streaming | OpenAI-Compat |
|----------|------|--------|-------|--------|-----------|----------------|
| **OpenAI** | Cloud | ✅ Reference | ✅ File Search, Code Interp | ✅ | ✅ | ✅ |
| **Anthropic** | Cloud | ✅ Complete | ✅ Computer Use | ✅ | ✅ | ❌ |
| **Groq** | Cloud | ✅ Complete | ✅ Chat | ❌ | ✅ | ✅ |
| **Mistral** | Cloud | ✅ Complete | ✅ Chat, Rerank | ✅ | ✅ | ❌ |
| **Together** | Cloud | ✅ Complete | ✅ Chat, Embed | ✅ | ✅ | ✅ |
| **OpenRouter** | Proxy | ✅ Complete | ✅ Chat, Embed | ✅ | ✅ | ✅ |
| **Cohere** | Cloud | ✅ Complete | ✅ Rerank, Embed | ❌ | ✅ | ❌ |
| **Gemini** | Cloud | ✅ Complete | ✅ Function Call | ✅ | ✅ | ❌ |
| **DeepInfra** | Cloud | ✅ Complete | ✅ Chat, Embed | ✅ | ✅ | ✅ |
| **AI21** | Cloud | ✅ Complete | ✅ Batch, Completion | ❌ | ✅ | ❌ |
| **Ollama** | Local | ✅ Complete | ✅ Generate, Embed | ✅ | ✅ | ⚠️ |
| **GitHub Copilot** | Mixed | ✅ Complete | ✅ Session, Tools | ✅ | ✅ | ❌ |

**Recommendation**: Begin Phase 2 refactoring with OpenAI (reference), then Anthropic, then OpenAI-compatible providers.

---

### ⏳ RESEARCH REQUIRED (10 Providers)

**High Priority (Quick Wins)**:
- 🔴 **DeepSeek** — OpenAI-compatible, popular, unclear docs
- 🔴 **Fireworks** — OpenAI-compatible, undocumented
- 🔴 **XAI** — Emerging, OpenAI-compatible, verify Grok access
- 🟡 **Perplexity** — Search + conversational, proprietary

**Medium Priority (Specialized Hardware)**:
- 🟡 **Cerebras** — Wafer-scale, proprietary API
- 🟡 **SambaNova** — RDU hardware, specialized rate limits

**Lower Priority (Emerging)**:
- 🟢 **HuggingFace** — **MISSING** plan.md (no entry found)
- 🟢 **Cloudflare** — Workers AI or separate service?
- 🟢 **LambdaAPI** — Scope unclear
- 🟢 **NScale** — Early stage, minimal public info
- 🟢 **OpenCode** — Code-specific or general LLM?

---

### KEY FINDINGS

#### 📊 Feature Coverage (12 Complete Providers)

| Feature | Coverage | Providers |
|---------|----------|-----------|
| **Streaming** | 12/12 | ✅ All |
| **Async/Await** | 12/12 | ✅ All |
| **Function Calling** | 11/12 | All except Ollama (limited) |
| **Vision** | 8/12 | Anthropic, Gemini, Mistral, DeepInfra, Together, OpenRouter, Ollama, GitHub |
| **JSON Mode** | 10/12 | All except Ollama (format param), Groq |
| **Embeddings** | 8/12 | Anthropic, Cohere, Mistral, DeepInfra, Gemini, Ollama, Together, OpenAI |
| **Batch API** | 4/12 | OpenAI, AI21, Cohere, Together |
| **Fine-tuning** | 3/12 | OpenAI, AI21, Cohere |

---

#### 🔐 Authentication Patterns

| Auth Type | Count | Providers |
|-----------|-------|-----------|
| **API Key** | 10 | Standard Bearer token or X-API-Key header |
| **OAuth** | 1 | GitHub Copilot (Copilot CLI + subscription) |
| **None** | 1 | Ollama (local-only) |
| **TBD** | 10 | Pending research |

---

#### 🚨 CRITICAL ISSUES

1. **GitHub Copilot Migration**: Copilot Extensions (Apps) sunset Nov 10, 2025 → migrate to MCP or SDK
2. **HuggingFace Missing**: No plan.md found; needs initial research
3. **10 TBD Providers**: Cannot begin Phase 2 integration without documentation
4. **Rate Limit Strategies**: Only 5 providers have documented limits; others TBD

---

### PHASE 2 REFACTORING ORDER

```
PRIORITY 1 (Reference + Complex):
├─ OpenAI          (reference implementation)
└─ Anthropic       (complex: computer_use tool)

PRIORITY 2 (OpenAI-Compatible Template):
├─ Groq            (simple, single-model)
├─ Mistral         (similar to OpenAI)
├─ Together        (open-source models)
├─ OpenRouter      (proxy pattern)
└─ DeepInfra       (multi-model)

PRIORITY 3 (Proprietary Variants):
├─ Cohere          (reranking unique)
├─ Gemini          (token counting unique)
├─ AI21            (research-focused)
└─ GitHub Copilot  (agentic workflows)

PRIORITY 4 (Local Deployment):
└─ Ollama          (offline alternative)
```

**Estimated Timeline**: ~4 weeks for all 12 providers

---

### RECOMMENDATIONS

1. **Create Unified Adapter Layer**
   - Location: `src/css/api_services/adapters/base_adapter.py`
   - Normalize: authentication, streaming, tool use, error handling
   - Pattern: One adapter per provider or generic OpenAI-compatible adapter

2. **Phase 2 Sprint Structure**
   - Week 1: OpenAI + Anthropic adapters (reference + complex)
   - Week 2: OpenAI-compatible batch (Groq, Mistral, Together, OpenRouter, DeepInfra)
   - Week 3: Proprietary variants (Cohere, Gemini, AI21)
   - Week 4: Local + GitHub (Ollama, Copilot)

3. **Research Sprint (Parallel, Weeks 2-3)**
   - Assign 1 engineer per TBD provider
   - High priority: DeepSeek, Fireworks, XAI (quick wins)
   - Output: plan.md for each TBD provider

4. **Documentation Standard**
   - Every provider plan.md must include:
     - Features matrix (tools, models, auth, rate limits)
     - Error handling strategy
     - Rate limit quotas
     - Example code

---

### ACTION ITEMS

| Item | Owner | Effort | Timeline |
|------|-------|--------|----------|
| Create base adapter interface | TBD | 2h | Week 1 |
| Research TBD providers | Distributed | 6h | Weeks 2-3 |
| Refactor OpenAI adapter | TBD | 3h | Week 1 |
| Refactor Anthropic adapter | TBD | 4h | Week 1 |
| Refactor OpenAI-compatible batch | TBD | 10h | Week 2 |
| Refactor proprietary variants | TBD | 8h | Week 3 |
| Test all 12 adapters | TBD | 4h | Week 4 |
| Integration tests | TBD | 3h | Week 4 |

---

### Reference

- Complete provider matrix (23 columns × 22 rows)
- Feature coverage analysis
- Phase 2 refactoring recommendations
- Research prioritization

---

---

## 🔍 MODULES AUDIT RESULTS (2026-05-03)

**Agent**: rubber-duck-3-modules | **Status**: ✅ COMPLETE

### Executive Summary

**Audit Scope**: 22 modules (23 total with strategies placeholder)

| Category | Count | % | Status |
|----------|-------|---|--------|
| **Ready (4/4 Pattern)** | 5 | 23% | ✅ Production ready |
| **Pending (2-3/4 Pattern)** | 11 | 50% | ⏳ Phase 2-3 work |
| **Blocked/Stub (0-1/4 Pattern)** | 6 | 27% | 🟡 Phase 3-4+ |

**Total 5-File Pattern Compliance**: 8/22 (36%) ✅ Good | 6/22 (27%) ⚠️ Partial | 8/22 (36%) ❌ Stub

---

### 🟢 PRODUCTION READY (5 modules)

| Module | Files | Pattern | Status |
|--------|-------|---------|--------|
| **tools** | 6 | 4/4 ✅ | Phase 2 ✅ |
| **teams** | 10 | 4/4 ✅ | Phase 2 ✅ |
| **tasks** | 5 | 4/4 ✅ | Phase 2 ✅ |
| **marketplace** | 9 | 4/4 ✅ | Phase 2 ✅ |
| **a2a_google** | 11 | 4/4 ✅ | Phase 2 ✅ |

**Recommendation**: Deploy immediately in Phase 2

---

### ⏳ PHASE 2 PENDING (11 modules)

**Foundation Layer (Must do first)**:
- **cache** — 3 files, 2/4 pattern | No dependencies
- **roles** — 3 files, 2/4 pattern | No dependencies
- **llm_models** — 1 file, config registry | No dependencies
- **scopes** — 1 file, isolation boundaries | No dependencies

**Core Services (Depend on Foundation)**:
- **agents** — 3 files, 2/4 pattern | Needs: roles, cache | Blockers: Missing enums
- **skills** — 3 files, 2/4 pattern | Depends: cache, roles

**Features (Depend on Core)**:
- **chat** — 1 file, 2/4 pattern | No dependencies
- **tags** — 3 files, 3/4 pattern ✅ | No dependencies
- **triage** — 3 files, 3/4 pattern | No dependencies
- **capabilities** — 2 files, 2/4 pattern | Depends: agents
- **streaming** — 7 files, 1/4 pattern | Needs: Refactoring (2h effort)

---

### 🟡 BLOCKED/STUB (6 modules)

| Module | Phase | Status | Design |
|--------|-------|--------|--------|
| **events** | 3 | core-owned | Async event system in `core/events/` |
| **memory** | 3 | core-owned | Working memory domain; migration to canonical core ownership pending |
| **permissions** | 3 | 0 files | RBAC access control |
| **workspace** | 3 | pending | General session/project directory structure (`core/workspace/`) |
| **a2a_internal** | 4+ | 0 files | Agent-to-agent comms |
| **planer** | 4+ | 0 files | Agent planning AI |

**Status**: Mixed state; ownership note at the top of this file overrides older module-era naming.

---

### CRITICAL PATH ANALYSIS

```
TIER 1: Foundation (Week 1)
├─ cache (no deps)
├─ roles (no deps)
├─ llm_models (no deps)
└─ scopes (no deps)

TIER 2: Core Services (Week 2, depends on Tier 1)
├─ agents (depends: cache, roles)
├─ tools (ready now)
├─ teams (ready now)
└─ skills (depends: cache, roles)

TIER 3: Features (Week 3, depends on Tier 2)
├─ chat
├─ tags
├─ triage
├─ capabilities (depends: agents)
└─ streaming (after refactoring)

TIER 4: Ready Now (no dependencies)
├─ marketplace (core-owned)
└─ a2a_google

TIER 5: Advanced/Stubs (Phase 3-4+)
├─ events (core-owned)
├─ memory (core-owned)
├─ permissions
├─ workspace
├─ a2a_internal
└─ planer
```

---

### BLOCKING DEPENDENCIES

| Blocked | Blocker | Impact |
|---------|---------|--------|
| **agents** | cache, roles | Tier 2 cannot start |
| **skills** | cache, roles | Tier 2 cannot start |
| **capabilities** | agents | Tier 3 blocked |
| **streaming** | needs refactor | Tier 3 delayed 2h |

---

### 5-FILE PATTERN COMPLIANCE

**Excellent (4/4)**: tools, teams, tasks, marketplace, a2a_google (5 modules)

**Good (3/4)**: tags, triage (2 modules)

**Partial (2/4)**: agents, cache, capabilities, chat, roles, skills (6 modules)

**Stub / migration-heavy**: a2a_internal, llm_models, memory, permissions, scopes, streaming, workspace

**Recommendation**: Add missing files to partial modules in Phase 2

---

### session.db SYNCHRONIZATION

✅ **Complete**: All 22 modules inserted into session.db:
- 5 ready modules (status='done')
- 11 pending modules (status='pending')
- 6 blocked modules (status='blocked')
- 1 audit marker (status='done')

**Total**: 23 entries | Ready: 6 | Pending: 11 | Blocked: 6

---

### PHASE 2-3 IMPLEMENTATION ORDER

**Phase 2 Week 1**: cache, roles, llm_models, scopes (Foundation)
**Phase 2 Week 2**: agents, skills, tools, teams (Core)
**Phase 2 Week 3**: chat, tags, triage, capabilities, streaming (Features)
**Phase 2 Week 4**: marketplace, a2a_google (Deploy)

**Phase 3**: events, memory, permissions, workspace (advanced infrastructure; legacy todo ids may still say `working_dir`)

**Phase 4+**: a2a_internal, planer (Specialized systems)

---

### ACTION ITEMS (Phase 2)

| Priority | Task | Effort | Blocker |
|----------|------|--------|---------|
| 1 | Complete cache module | 1h | No |
| 1 | Complete roles module | 1h | No |
| 1 | Create llm_models registry | 1h | No |
| 2 | Add agents enums | 0.5h | agents tier |
| 2 | Connect skills to cache/roles | 1h | agents tier |
| 3 | Streaming refactor + reorganize | 2h | streaming tier |
| 4 | Verify dependencies resolved | 1h | All modules |

---

### Reference

- Complete module status matrix (22 rows × 7 columns)
- Critical path analysis (4 tiers)
- Blocking dependency list
- Implementation order for Phase 2-3

---

---

## 📋 SESSION SUMMARY (2026-05-04 — Archived)

> This summarises the May 3–4 audit session. Current state is in **CURRENT STATUS** at top.

**Phases 0 + 1**: ✅ Complete (22 todos done, committed)  
**session.db**: 542 total — 193 done, 348 pending, 1 blocked  
**Module compliance**: 5/25 fully compliant (`a2a_google`, `marketplace`, `tasks`, `teams`, `tools`)  
**Key decisions made**: Phase 19 module restructuring (rename `planer`→`planner`, `a2a_internal`→`ipc`, remove scopes, absorb strategies→triage); scope hierarchy fully deleted; session files centralized at `~/.css/sessions/`

---

## 🚧 Phase 7 — Feature Completeness

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Todos added**: 19 (cumulative session.db: 542 total — 193 done, 348 pending, 1 blocked)

Deep audit of existing modules vs cybersecurity platform requirements revealed **two categories** of gaps:

1. **Critical stubs** — modules that exist on disk but contain 0 LOC
2. **Missing domain features** — capabilities a cybersec forensics platform needs but has no module for

---

### T7.1 — Critical Stubs (modules that exist but are empty)

| ID | Module | Status | Description |
|----|--------|--------|-------------|
| `feat-chat-endpoints` | `chat/endpoints.py` | ❌ MISSING | No WebSocket or REST endpoint for chat — the chat module has no API surface |
| `feat-memory-impl` | `memory/` | ❌ 0 LOC | Agent context + conversation memory — in-memory ChatSessionManager loses state on restart |
| `feat-working-dir-impl` | `core/workspace/` | ❌ 0 LOC | Agent filesystem workspace — agents have nowhere to write files |
| `feat-planer-impl` | `planer/` | ❌ 0 LOC | Planner orchestrator — the "dev mode" Planner process in system-overview.md has no implementation |
| `feat-strategies-impl` | `strategies/` | ❌ 0 LOC | Response routing strategies — `core/orchestration/response_strategy_router.py` exists (68 LOC) but module is empty stub |

**Priority**: Highest — these block basic functionality.

---

### T7.2 — Auth & User Management (multi-user platform cannot function without these)

| ID | Feature | Notes |
|----|---------|-------|
| `feat-auth-module` | `modules/auth/` | JWT + API key auth. `account.py` entity exists in `core/types/entities/` but no module. FastAPI `Depends()` middleware. |
| `feat-accounts-module` | `core/accounts/` | User profiles, org membership (multi-tenant). Link to roles RBAC. |
| `feat-sessions-persistence` | Persist `ChatSession` | ChatSessionManager is an in-memory `dict` — all history gone on restart. PostgreSQL-backed. |

---

### T7.3 — Cybersec Domain: Incidents & Threats (core platform purpose, zero coverage today)

| ID | Feature | Why Critical |
|----|---------|-------------|
| `feat-incidents-module` | `modules/incidents/` | Incident lifecycle (create/track/close/timeline). A cybersec platform with no incidents module is just a chatbot. |
| `feat-threat-intel-module` | `modules/threat_intel/` | IOC tracking (IP/domain/hash/URL), threat feed pulls (MISP, OTX, VirusTotal). Canonical relational ownership stays here; graph-native entities/relationships later project into `core/rag_graph/`. |
| `feat-mitre-module` | `modules/mitre/` | MITRE ATT&CK framework. Canonical ATT&CK ownership stays here; ATT&CK entities and relationships later project into `core/rag_graph/`. |
| `feat-scan-module` | `modules/scans/` | Vulnerability scan lifecycle: target → orchestrated agent team → findings → incidents. Bridges triage → teams → reports. |

---

### T7.4 — Output & Integrations (sessions produce no deliverables today)

| ID | Feature | Notes |
|----|---------|-------|
| `feat-reports-module` | `modules/reports/` | ~~Jinja2 → Markdown/HTML/PDF~~ **→ superseded by Phase 32 (full design there)** |
| `feat-alerts-module` | `modules/alerts/` | AlertRule + AlertDispatcher (email/Slack/webhook). Triggered by EventStore DomainEvents. |
| `feat-webhooks-module` | `modules/webhooks/` | Outbound webhooks with HMAC-SHA256 signing + retry. SIEM/SOAR integration (Splunk, Elastic, PagerDuty). |
| `feat-scheduler-module` | `modules/scheduler/` | Cron-style scheduling (APScheduler). Use cases: periodic scans, daily threat feed sync, scheduled red-team drills. |

---

### T7.5 — Knowledge & Context (LLM agents are blind without these)

| ID | Feature | Notes |
|----|---------|-------|
| `feat-vector-rag-core` | `core/rag_vector/` + `core/rag_graph/` | Hybrid retrieval foundation split into VectorRAG on PostgreSQL + pgvector and GraphRAG on graph storage, with toggleable retrieval modes (`vector`, `graph`, `hybrid`, `auto`), fused context for agents, and a clean boundary between shared retrieval core vs domain-specific cybersec ingestion. Sources: CVE feeds, PDFs, playbooks, MITRE ATT&CK, threat-intel entities/relationships, and extracted links. |
| `feat-evidence-module` | `modules/evidence/` | Chain-of-custody: Evidence model + EvidenceChain (immutable append via EventStore). Hash-verified, collector-attributed. |
| `feat-audit-compliance-module` | `modules/compliance/` | NIST CSF / SOC2 / ISO27001 / MITRE framework control mapping. % coverage reports. Reads from scans + incidents. |

---

### Implementation Dependencies

```
auth → accounts → sessions-persistence
incidents → threat-intel → mitre → scan
events (p6) → alerts → webhooks
reports → incidents + scans + compliance
rag_vector(core) + rag_graph(core) → memory + agent context assembly
evidence → incidents + EventStore (p6)
```

### Phase 7 Priority Order

1. **Now**: `feat-chat-endpoints`, `feat-memory-impl`, `feat-working-dir-impl` (unblock basic agent sessions)
2. **After Phase 3**: `feat-auth-module`, `feat-accounts-module`, `feat-sessions-persistence`
3. **After Phase 6 (CQRS)**:  `feat-incidents-module`, `feat-threat-intel-module`, `feat-evidence-module`
4. **After incidents**: `feat-reports-module`, `feat-alerts-module`, `feat-webhooks-module`
5. **After Phase 20 hybrid retrieval core**: `feat-vector-rag-core`, `feat-mitre-module`, `feat-audit-compliance-module`
6. **Anytime**: `feat-strategies-impl`, `feat-planer-impl`, `feat-scheduler-module`


---

## 🤖 Phase 8 — AI Execution Layer (Priority: High — AI first)

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Todos added**: 17 (cumulative; session.db: 542 total)  
**Rationale**: Cybersec domain features are downstream. The AI execution layer is the foundation.

### 🚨 Critical Finding: The multi-provider architecture is dead

`streaming/runner.py` → `QueryExecutor` hardcodes:
```python
from claude_agent_sdk import ClaudeSDKClient
```
The 24-provider `ProviderRegistry`, `DynamicCapabilityRegistry`, and `ResponseStrategyRouter` **all exist but are never called**. Every agent uses Claude regardless of config.

---

### T8.1 — Agent Execution Core

| ID | Gap | Finding |
|----|-----|---------|
| `ai-agent-base-protocol` | `agents/base.py` — 0 LOC | No `BaseAgent` Protocol. No `AgentExecutor`. |
| `ai-agent-models` | `agents/models.py` — 0 LOC | `AgentConfig`, `AgentResult`, `AgentTurn` don't exist. |
| `ai-provider-routing` | Claude hardcode | Wire `AgentExecutor` → `DynamicCapabilityRegistry` → `HttpProviderAdapter` |

**Fix pattern**: `AgentExecutor.execute()` → capability check → `HttpProviderAdapter.complete()` → `AgentResult`

---

### T8.2 — Triage: Real LLM Classification

| ID | Gap | Finding |
|----|-----|---------|
| `ai-triage-ollama-wire` | `TriageEngine` — hardcoded 0.85 | `ollama_client` param exists but never called. Needs `POST /api/chat` to Ollama. |
| `ai-triage-strategy-wire` | Strategy router — counts `?` | `qwen_classify_complexity()` is a `# TODO Phase 2` placeholder since Phase 2. Wire to `TriageEngine`. |

---

### T8.3 — Memory & Context Persistence

| ID | Gap | Finding |
|----|-----|---------|
| `ai-memory-context-window` | `memory/` — 0 LOC | No token budget management, no rolling eviction. |
| `ai-memory-session-store` | Sessions lost on restart | `ChatSessionManager` is an `in-memory dict`. Redis + PG persistence needed. |
| `ai-context-fix-antipattern` | Anti-pattern in `context.py` | `@dataclass class ConversationContext(BaseModel)` — documented Phase 3 anti-pattern. → `msgspec.Struct` |

---

### T8.4 — Async Generator Pipeline

| ID | Gap | Finding |
|----|-----|---------|
| `ai-strategies-impl` | `strategies/` — 0 LOC | 4 strategies needed: Direct, Balanced, CostOptimized, LatencyOptimized |
| `ai-pipeline-wire` | No pipeline | `pipe(source \| classify \| route \| execute \| observe)` — Phase 6 P5 shape |

---

### T8.5 — Tool & Skill Execution

| ID | Gap | Finding |
|----|-----|---------|
| `ai-tool-calling-loop` | No call→execute→respond loop | `tools/registry.py` is 475 LOC but no loop that parses `tool_calls` and continues LLM call |
| `ai-skill-base-impl` | `skills/base.py` — 0 LOC | `SkillRegistry` has 181 LOC but no `BaseSkill.execute()` to call |

---

### T8.6 — Agent-to-Agent Communication

| ID | Gap | Finding |
|----|-----|---------|
| `ai-a2a-internal-dispatch` | `a2a_internal/dispatcher.py` — 3 LOC stub | Just re-exports `css.core.redis.dispatcher`. No real dispatch logic. |
| `ai-team-orchestrator-wire` | No sub-agent delegation | `teams/orchestrator.py` not wired to `a2a_internal`. Multi-agent teams don't actually delegate. |

---

### T8.7 — Provider Routing

| ID | Gap | Finding |
|----|-----|---------|
| `ai-capability-routing` | `DynamicCapabilityRegistry` unused | 260 LOC capability discovery, never consulted during execution. |

---

### T8.8 — Token Budget & Rate Limiting

| ID | Gap | Finding |
|----|-----|---------|
| `ai-token-budget` | No budget tracking | `teams/metrics.py` doesn't count tokens or costs |
| `ai-rate-limiting` | No rate limiting | No 429 protection, no per-provider throttling |

---

### Phase 8 Implementation Order

```
1. agents/base.py + agents/models.py      (BaseAgent Protocol + AgentResult)
2. ai-context-fix-antipattern             (fix ConversationContext → msgspec.Struct)
3. ai-provider-routing                    (wire AgentExecutor → ProviderRegistry)
4. ai-triage-ollama-wire                  (real Qwen/Ollama call)
5. ai-memory-context-window               (ContextWindow token budget)
6. ai-memory-session-store                (Redis + PG persistence)
7. ai-tool-calling-loop                   (tool_calls parse → execute → continue)
8. ai-skill-base-impl                     (BaseSkill.execute())
9. ai-strategies-impl                     (4 strategy types)
10. ai-pipeline-wire                      (compose full pipeline)
11. ai-triage-strategy-wire               (connect triage → strategy)
12. ai-capability-routing                 (wire capability check to provider select)
13. ai-a2a-internal-dispatch              (real Redis agent dispatch)
14. ai-team-orchestrator-wire             (multi-agent team delegation)
15. ai-token-budget + ai-rate-limiting    (budget guards)
```

### Dependencies between Phase 8 and Phase 6

Phase 8 **requires** Phase 6 to be partially done first:
- `ai-agent-models` requires Phase 6 P1 (msgspec.Struct) 
- `ai-provider-routing` requires Phase 6 P2 (HttpProviderAdapter YAML providers)
- `ai-pipeline-wire` requires Phase 6 P5 (async generator pipeline shape)
- `ai-a2a-internal-dispatch` requires Phase 6 P3 (CQRS EventStore for DomainEvents)


---

## 🗄️ Phase 9 — ORM / Manager / Registry Unified Pattern

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Todos added**: 8 new | **session.db**: 370 total — 193 done, 176 pending, 1 blocked

---

### The Problem Today

The codebase has **three competing concerns mixed together**:

| Where | What's Wrong |
|-------|-------------|
| `MarketplaceItemRegistry` | Called a Registry but does DB `item.save()` — it's actually a Manager |
| `TagManager` | Called a Manager but manages an `in-memory dict`, ignores Tortoise |
| `ToolRegistry` | 500+ LOC mixing in-memory cache, startup discovery, hardcoded provider data |
| All ORM models | Only `HybridToolDefinition` has `to_schema()`/`from_schema()`. Rest use ad-hoc `dict()`. |
| No Tortoise custom managers | All `.filter()`/`.get_or_none()` scattered across endpoints, registries, scope_utils |
| `BaseRegistry` | Used as DB-CRUD superclass — wrong abstraction |

---

### The Three-Ring Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Ring 1 — Value Types  (msgspec.Struct, frozen, immutable)      │
│  ToolSpec · AgentConfig · ProviderSpec · AgentResult · ...      │
│  Used in: pipeline stages, APIs, business logic, events         │
│  Rule: NO database awareness. Pure Python. 10–40× faster serde. │
└──────────────────────────┬──────────────────────────────────────┘
                 to_domain() │ from_domain()
┌──────────────────────────▼──────────────────────────────────────┐
│  Ring 2 — ORM Models  (Tortoise Model + custom Manager)         │
│  ToolModel · TeamModel · MarketplaceItem · SkillModel · ...     │
│                                                                  │
│  Model is THIN:                                                  │
│    - fields + Meta only                                          │
│    - to_domain() → ToolSpec (output)                            │
│    - from_domain(spec) → ToolModel (classmethod, input)         │
│    - NO business logic inside Model                              │
│                                                                  │
│  Custom Manager (objects = ToolManager()):                       │
│    - async def by_provider(provider: str) → QuerySet            │
│    - async def enabled_for_team(team_id: int) → list[ToolModel] │
│    - async def create_from_domain(spec: ToolSpec) → ToolModel   │
│    - Rule: DB queries ONLY here. No business logic.             │
└──────────────────────────┬──────────────────────────────────────┘
               load at boot │ invalidate after writes
┌──────────────────────────▼──────────────────────────────────────┐
│  Ring 3 — In-Memory Registries  (singleton, startup-loaded)     │
│  ToolRegistry · ProviderRegistry · CapabilityRegistry · ...     │
│                                                                  │
│  Registry is READ-ONLY at runtime:                               │
│    - get(id: str) → T | None                                    │
│    - list(filter) → list[T]                                      │
│    - invalidate(id: str) → removes from cache                   │
│    - reload() → await Manager.all() → rebuild cache             │
│    - Rule: NEVER writes to DB. No async DB calls after startup. │
│    - Rule: Cache invalidated by DomainEvent subscription (P6P3) │
└─────────────────────────────────────────────────────────────────┘
```

---

### Service Functions — the only entry point

```python
# tools/service.py
async def create_tool(spec: ToolSpec, team_id: int) -> ToolSpec:
    """Business logic: validate + persist + invalidate cache."""
    if await ToolModel.objects.exists(name=spec.name, team_id=team_id):
        raise ToolAlreadyExistsError(spec.name)
    model = ToolModel.from_domain(spec)   # Ring 2 in
    await model.save()
    ToolRegistry.get_instance().invalidate(spec.name)  # Ring 3 sync
    return model.to_domain()             # Ring 1 out

# endpoints/tools.py
@router.post("/tools")
async def create_tool_endpoint(req: CreateToolRequest) -> ToolSpec:
    spec = ToolSpec(name=req.name, ...)
    return await create_tool(spec, team_id=req.team_id)  # only calls service
```

Rule: **Endpoints → Service functions → (Manager OR Registry). Never skip a layer.**

---

### Pattern: Custom Tortoise Manager

```python
# tools/user.py
from tortoise import fields, models
from tortoise.manager import Manager

class ToolManager(Manager):
    async def by_provider(self, provider: str):
        return await self.filter(provider=provider, enabled=True)

    async def for_team(self, team_id: int):
        return await self.filter(team_id=team_id, enabled=True)

class ToolModel(models.Model):
    name = fields.CharField(max_length=256, unique=True)
    provider = fields.CharField(max_length=64, db_index=True)
    enabled = fields.BooleanField(default=True)

    objects = ToolManager()          # custom manager replaces default

    def to_domain(self) -> "ToolSpec":
        return ToolSpec(name=self.name, provider=self.provider)

    @classmethod
    def from_domain(cls, spec: "ToolSpec") -> "ToolModel":
        return cls(name=spec.name, provider=spec.provider)

    class Meta:
        table = "tools"
```

---

### Pattern: Clean Registry (Ring 3)

```python
# tools/registry.py
class ToolRegistry:
    _instance: "ToolRegistry | None" = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self._cache: dict[str, ToolSpec] = {}

    @classmethod
    async def create(cls) -> "ToolRegistry":
        """Called ONCE at ASGI startup. Populates from DB."""
        self = cls()
        tools = await ToolModel.objects.filter(enabled=True)
        self._cache = {t.name: t.to_domain() for t in tools}
        return self

    def get(self, name: str) -> ToolSpec | None:
        return self._cache.get(name)

    def invalidate(self, name: str) -> None:
        self._cache.pop(name, None)

    async def reload(self, name: str) -> None:
        model = await ToolModel.objects.get_or_none(name=name)
        if model:
            self._cache[name] = model.to_domain()
```

---

### What Changes per Module

| Module | Action |
|--------|--------|
| `marketplace/registry.py` | Rename → `marketplace/service.py`. Registry becomes thin cache. |
| `tools/registry.py` | Remove hardcoded 500 LOC. Startup-load from DB + YAML provider specs. |
| `tags/manager.py` | Replace in-memory dict with Tortoise custom Manager on `Tag` model. |
| `skills/registry.py` | Extract DB writes to `SkillModel.objects`. Registry = cache only. |
| `core/types/base/base_client.py` | Remove `BaseRegistry` DB-CRUD methods. |
| All ORM models | Add `to_domain()` + `from_domain()`. Add `objects = FooManager()`. |
| All `@dataclass` runtime types | Migrate to `msgspec.Struct` (Phase 6 P1 + Phase 9 T9.1). |

---

### 13 Todos in session.db

| ID | What |
|----|------|
| ~~`orm-value-types-migration`~~ | All runtime `@dataclass` → `msgspec.Struct` |
| ~~`orm-custom-managers`~~ | Add `objects = FooManager()` to every Tortoise model |
| ~~`orm-to-from-domain`~~ | `to_domain()` + `from_domain()` on every model |
| ~~`db-timestamp-mixin-rollout`~~ | Roll out `TimestampMixin` across standard audit-pair ORM models |
| ~~`db-frontmatter-field-semantics`~~ | Split identifier `NameField` from human display-name semantics |
| ~~`db-frontmatter-base-rollout`~~ | Remove `BaseFBSModel`; roll out `BaseFrontmatterMixin` only where semantics fit |
| ~~`db-version-mixin-rollout`~~ | Adopt `VersionMixin` for versioned artifacts with hash provenance |
| ~~`orm-registry-metaclass-fix`~~ | Fix `AsyncSafeSingletonMeta` + `ABC` conflicts before more registry expansion |
| ~~`orm-registry-purge-crud`~~ | Remove DB writes from all registries |
| ~~`orm-registry-invalidation`~~ | Cache invalidation via DomainEvent subscription |
| ~~`orm-service-layer`~~ | `service.py` per module — only entry point for business logic |
| ~~`orm-tag-manager-fix`~~ | `TagManager` → wraps Tortoise, not in-memory dict |
| ~~`orm-base-registry-cleanup`~~ | `BaseRegistry` → pure in-memory `Protocol`, no DB |


---

## 🔌 Phase 10 — Unified Provider SDK Architecture

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Todos added**: 13 new | **session.db**: 383 total — 193 done, 189 pending, 1 blocked  
**Architecture doc**: `.plan/architecture/sdks.md` (fully rewritten this session)

---

### The Four Adapter Types

```
UnifiedLLMClient (umbrella)
├── NativeSDKAdapter    → anthropic SDK (prompt_caching, computer_use, extended_thinking)
│                         openai SDK optional (structured output, Assistants)
├── HttpProviderAdapter → YAML spec + aiohttp
│   ├── openai_compat: true  → 8 providers (groq, together, fireworks, deepinfra, openrouter, deepseek, sambanova, xai)
│   └── proprietary          → 14 providers with schema translators (gemini, cohere, mistral, …)
│                               + ModelNameMapper (model_aliases.yaml per provider)
├── OllamaAdapter       → local HTTP /api/chat + /api/tags + /api/pull (merges 3 existing files)
└── BrowserRelayAdapter → inject prompt into browser LLM UIs via Chrome extension
                          (bypasses API keys — uses user's active session on claude.ai / ChatGPT)
```

All four implement `LLMAdapter` Protocol. `UnifiedLLMClient` is the **only** LLM call entry point.

### Key Decisions

1. **Keep `anthropic` SDK** — prompt_caching, computer_use, extended_thinking are SDK-only features.  
2. **Keep `openai` SDK as optional** — Assistants API, strict structured output.  
3. **All other 22 providers** → HttpProviderAdapter via YAML spec. Zero boilerplate Python.  
4. **Ollama** → OllamaAdapter (custom, uses `/api/chat` not `/v1/chat/completions`). Merges 3 existing files.  
5. **Browser plugin** → `BrowserRelayAdapter` + `/api/plugin/` endpoints. Prompt injection via DOM. Polls Redis for result.

### Builtin Tools Flow

```
ASGI startup
  → for each adapter: adapter.builtin_tools() → ToolRegistry.register(tool)
  → Anthropic: [computer_use, bash_tool, text_editor_20250124]
  → OpenAI:    [code_interpreter, file_search]
  → Others:    [] (function calling only, no provider-level builtins)
```

### 13 Todos (in session.db Phase 10)

| ID | What |
|----|------|
| `sdk-llm-adapter-protocol` | LLMAdapter Protocol definition |
| `sdk-llm-response-types` | LLMResponse + StreamChunk as msgspec.Struct |
| `sdk-native-anthropic-adapter` | AnthropicNativeAdapter |
| `sdk-native-openai-adapter` | OpenAINativeAdapter (optional) |
| `sdk-http-adapter-openai-compat` | HttpProviderAdapter + 8 spec.yaml files |
| `sdk-http-adapter-proprietary` | 14 proprietary translators |
| `sdk-model-name-mapper` | model_aliases.yaml + ModelNameMapper |
| `sdk-ollama-adapter` | OllamaAdapter (merge 3 files) |
| `sdk-browser-relay-adapter` | BrowserRelayAdapter + /api/plugin/ endpoints |
| `sdk-browser-relay-polling` | content.js result polling |
| `sdk-unified-client` | UnifiedLLMClient umbrella |
| `sdk-builtin-tools-registry` | Wire builtin_tools() → ToolRegistry at startup |
| `sdk-replace-queryexecutor` | Remove Claude hardcode from QueryExecutor |


---

## 🧊 Phase 11 — Cross-Provider Prompt Caching

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Todos added**: 10 | **Architecture doc**: `.plan/architecture/sdks.md` (caching section)

---

### The Core Question

> *Can we give every provider something like Anthropic's prompt caching?*

**Yes — but in three distinct tiers.** Not every provider has the same caching API, so
the architecture must be tiered: use native caching where it exists, then fall back to
app-level Redis caching for ALL providers regardless.

---

### Three-Tier Caching Strategy

```
Tier 1 — App-Level Exact Cache (ALL providers)
  Redis:  sha256(provider+model+messages+params) → LLMResponse
  Hit?  → return immediately. Zero API cost. Zero latency.
  Works for: repeated tool calls, dev/test, idempotent agents.

Tier 2 — Native Provider Caching (where supported)
  Anthropic  → automatic top-level cache_control by default; optional explicit breakpoints
                for mixed-cadence prefixes; tracks cache_read_input_tokens and
                cache_creation_input_tokens in usage
  OpenAI     → automatic prefix caching; optionally set prompt_cache_key and
                prompt_cache_retention; tracks cached_tokens in usage response
  DeepSeek   → automatic — tracks prompt_cache_hit_tokens / prompt_cache_miss_tokens
  Gemini     → explicit cachedContent resource: create via REST, reference by name
  Groq       → announced (similar to OpenAI — monitor for GA)
  Others     → fallback to Tier 1 only

Tier 3 — Semantic Cache (future Phase 13+)
  Embedding similarity → find "close enough" prior response
  Not planned yet — Tier 1 + 2 cover the important cases.
```

**Tier 1 is free savings for every provider. Tier 2 multiplies the savings for providers
that support it natively. Both tiers run together.**

---

### Architecture: `PromptCacheManager`

`PromptCacheManager` is injected into `UnifiedLLMClient` as a collaborator. The client
calls `cache_manager.get_or_compute(adapter, messages, model, **kw)` — caching is
completely transparent to all callers.

```python
# core/prompt_cache/manager.py
class PromptCacheManager:
    def __init__(self, redis: Redis, config: CacheConfig):
        self._redis = redis
        self._config = config
        self._injector = CacheBreakpointInjector()  # Anthropic explicit mode only
        self._gemini_cache = GeminiContextCacheClient()

    async def get_or_compute(
        self,
        adapter: LLMAdapter,
        messages: list[dict],
        model: str,
        **kwargs,
    ) -> LLMResponse:
        # --- Tier 1: check Redis exact-match ---
        key = _cache_key(adapter.provider, model, messages, kwargs)
        if (hit := await self._redis.get(key)):
            return LLMResponse(**msgspec.json.decode(hit)) | cache_source="redis"

        # --- Tier 2a: prepare provider-native caching ---
        if adapter.caching_capability == CachingCapability.NATIVE_AUTOMATIC_WITH_EXPLICIT:
            if self._config.prefer_explicit_breakpoints(adapter.provider, model, messages):
                messages, kwargs = self._injector.inject(messages, kwargs)
            else:
                kwargs["cache_control"] = {"type": "ephemeral"}
        elif adapter.caching_capability == CachingCapability.NATIVE_AUTOMATIC:
            kwargs = self._prepare_automatic_cache_kwargs(adapter.provider, kwargs)
        if adapter.caching_capability == CachingCapability.NATIVE_RESOURCE:
            kwargs["cached_content"] = await self._gemini_cache.resolve(messages)

        # --- Compute ---
        response = await adapter.complete(messages, model, **kwargs)
        response.cache_stats = self._native_tracker.extract(adapter.provider, response)

        # --- Tier 1: store in Redis ---
        ttl = self._config.ttl_for(adapter.provider)
        await self._redis.setex(key, ttl, msgspec.json.encode(response))

        return response
```

```python
# CachingCapability on each adapter
class CachingCapability(enum.Enum):
    NONE = "none"  # no native caching
    NATIVE_AUTOMATIC = "native_auto"  # OpenAI, DeepSeek — provider handles prefix caching
    NATIVE_AUTOMATIC_WITH_EXPLICIT = "native_auto_explicit"  # Anthropic — automatic by default, explicit breakpoints available
    NATIVE_RESOURCE = "native_resource"  # Gemini — must create cachedContent object
```

---

### Anthropic: `CacheBreakpointInjector`

Anthropic now supports both automatic and explicit prompt caching. The default harness
path should be automatic top-level `cache_control`, because that is the simplest way to
cache a stable prefix. Use explicit breakpoints only when:

- different prompt sections change at different cadences
- you need multiple cache boundaries
- the 20-block lookback window would make one automatic breakpoint too coarse

Model-specific minimum token thresholds apply, and only 4 breakpoints may exist on a
single request.

```python
# core/prompt_cache/anthropic_injector.py
class CacheBreakpointInjector:
    """
    Adds explicit Anthropic cache_control breakpoints for advanced prompt layouts.
    Strategy:
      - Keep top-level cache_control as the default path
      - Mark the system/tools prefix only when it changes less often than the chat body
      - Mark the last message of the stable prefix when the conversation has a long
        static prefix and a short active suffix
      - Recent 2 messages (active window) → never marked
    """
    def inject(self, messages: list[dict], kwargs: dict) -> tuple[list[dict], dict]:
        # Add block-level cache_control where explicit mode helps more than automatic mode
        ...
```

Default TTL is 5 minutes. Anthropic also supports a 1-hour TTL when the caller opts into
it via `cache_control.ttl`.

---

### Cost Tracking in `LLMResponse`

```python
class CacheStats(msgspec.Struct):
    tier: Literal["none", "redis", "native_auto", "native_auto_explicit", "native_resource"]
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    estimated_savings_usd: float = 0.0
    # ^ Computed from model pricing × token delta

class LLMResponse(msgspec.Struct):
    content: str
    model: str
    provider: str
    usage: TokenUsage
    cache_stats: CacheStats = CacheStats(tier="none")  # new field
    tool_calls: list[ToolCall] = []
    finish_reason: str = "stop"
    raw: bytes | None = None
```

---

### Provider Caching Matrix (updated)

| Provider | Tier 1 Redis | Tier 2 Native | Native Type | Cost Reduction |
|----------|-------------|---------------|-------------|----------------|
| Anthropic | ✅ | ✅ | Automatic top-level + optional explicit breakpoints | Native read/write stats in usage |
| OpenAI | ✅ | ✅ | Automatic prefix + optional cache key / retention hints | Cached tokens reported in usage |
| DeepSeek | ✅ | ✅ | Automatic | Provider-reported cache hit/miss usage |
| Gemini | ✅ | ✅ | Explicit resource | Resource lifecycle + provider billing |
| Groq | ✅ | 🔜 | Auto (announced) | TBD |
| All others | ✅ | ❌ | — | Redis only (dev/test gains) |
| Ollama | ✅ | N/A | Local KV cache | No API cost anyway |
| BrowserRelay | ✅ | ❌ | — | Reduces browser injections |

---

### 10 Todos (Phase 11, session.db)

| ID | Task | What |
|----|------|------|
| `cache-caching-capability-enum` | T11.1 | `CachingCapability` metadata on `LLMAdapter` (including Anthropic auto+explicit support) |
| `cache-response-stats-struct` | T11.1 | Add `CacheStats` to `LLMResponse` |
| `cache-prompt-cache-manager` | T11.1 | `PromptCacheManager` (orchestrates all 3 tiers) |
| `cache-redis-exact-match` | T11.2 | Redis Tier 1 exact-match (all providers) |
| `cache-redis-streaming-buffer` | T11.2 | Buffer stream → store complete response in Redis |
| `cache-anthropic-breakpoint-injector` | T11.3 | `CacheBreakpointInjector` for advanced Anthropic explicit-cache layouts |
| `cache-automatic-native-tracking` | T11.4 | Parse Anthropic/OpenAI/DeepSeek native cache usage fields |
| `cache-gemini-context-cache` | T11.5 | Gemini `cachedContent` create/resolve/reuse |
| `cache-cost-savings-tracker` | T11.6 | Compute `estimated_savings_usd` per response |
| `cache-metrics-openobserve` | T11.6 | Emit `cache.hit`/`miss`/`native` events to OpenObserve |

**Dependencies**: Phase 11 → Phase 10 (requires `LLMAdapter` Protocol + `UnifiedLLMClient`)

---

## 🎛️ Phase 12 — QoL Output Controls Migration

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Source**: `src/legacy/ai_proxy/qol_controls/` (5 files, production-grade)  
**Todos added**: 11 | **session.db**: 393 total → 404 after this phase

---

### What QoL Controls Are

Per-request output behavior directives injected into the system prompt. 8 toggles:

| Toggle | Effect |
|--------|--------|
| `no_thinking` | Suppress reasoning/thinking blocks |
| `no_chat` | Suppress conversational filler |
| `minimal` | One-liners and direct answers only |
| `file_only` | Output ONLY code/files — NOTHING ELSE MAY APPEAR |
| `no_markdown` | Plain text, no Markdown |
| `structured_only` | JSON/YAML/table only, no prose |
| `redact_secrets` | Auto-redact API keys/passwords/tokens |
| `append_audit_trail` | Append `[AUDIT ts=… toggles=<hash>]` at end |

5 builtin presets: `silent`, `code-only`, `structured`, `audit`, `plain-text`.  
3 dangerous combinations blocked at validation time (e.g. `file_only + append_audit_trail`).  
Scope cascade: `session → project → global`.  
Per-agent preset binding. Fragment cache with TTL=300s.  
A2A publisher/subscriber for cross-agent toggle propagation.

---

### Migration Architecture

The legacy system uses JSON files + Pydantic. New architecture:

```
Ring 1: QoLToggle (str Enum) + QoLSettings (msgspec.Struct, immutable value type)
Ring 2: QoLSettingsModel (Tortoise) + QoLSettingsManager (custom manager, per-user scoped)
Ring 3: QoLPresetRegistry (in-memory, startup-loaded builtin presets + user presets)

Injection: QoLInjector (stateless service)
  → inject_into_messages(messages, settings) → list[dict]
  → inject_into_system(system: str, settings) → str
  → fragment cache by frozenset[QoLToggle] (TTL 300s)

Wiring: UnifiedLLMClient.complete() / .stream()
  → BEFORE request: QoLInjector.inject() (using scope-resolved settings)
  → AFTER injection: PromptCacheManager (cache key includes toggle_hash)
  → adapter.complete() / .stream()
```

**Storage**: Pydantic models → msgspec.Struct (Ring 1). JSON files → Tortoise ORM (Ring 2).  
**A2A**: Legacy `from a2a.models import A2AMessage` → `a2a_internal.dispatcher`.  
**Observability**: Legacy `from telemetry import record_event` → OpenObserve via new pipeline.

### Cache Key Change

QoL toggles affect output — same prompt + different toggles = different response.  
`PromptCacheManager` must include `toggle_hash` in the Redis key:

```python
key = sha256(provider + model + json(messages) + json(params) + toggle_hash)
```

`toggle_hash` = `blake2b(sorted(active_toggle_values))` (already implemented in legacy).  
If no toggles active: `toggle_hash = ""` (zero overhead, backward compatible).

---

### 11 Todos (Phase 12, session.db)

| ID | Task | What |
|----|------|------|
| `qol-models-msgspec` | T12.1 | Port QoLToggle + QoLSettings to msgspec.Struct |
| `qol-dangerous-combos-validator` | T12.1 | Port validate_toggle_combo + QoLSecurityError |
| `qol-builtin-presets` | T12.1 | Port BUILTIN_PRESETS (5 presets) |
| `qol-tortoise-model` | T12.2 | QoLSettingsModel (Tortoise) + QoLSettingsManager |
| `qol-preset-registry` | T12.2 | QoLPresetRegistry (Ring 3, in-memory, startup-loaded) |
| `qol-injector-service` | T12.3 | QoLInjector: fragment build + inject_into_messages/system |
| `qol-unified-client-middleware` | T12.3 | Wire QoLInjector into UnifiedLLMClient pre-request step |
| `qol-cache-key-toggle-hash` | T12.4 | Add toggle_hash to PromptCacheManager cache key |
| `qol-a2a-integration` | T12.5 | Port A2A publisher/subscriber to `a2a_internal.dispatcher` |
| `qol-openobserve-metrics` | T12.5 | Port observability to OpenObserve (qol.injection events) |
| `qol-rest-endpoints` | T12.6 | CRUD REST endpoints for toggle/preset/agent-binding management |

**Dependencies**:
- Phase 12 → Phase 10 (`UnifiedLLMClient` must exist for middleware wiring)
- Phase 12 → Phase 11 (`PromptCacheManager` must exist for cache key change)
- `qol-tortoise-model` → Phase 9 ORM pattern (Three-Ring Architecture)

---

## 🔀 Phase 13 — Provider Routing & Resilience

**Session**: 9a5b41c4 | **Added**: 2026-05-04  
**Source**: `src/legacy/ai_proxy/routing/combo.py` + `routing/qwen_triage.py` + `services/`  
**Todos added**: 14 | **Depends on**: Phase 10 (LLMAdapter + UnifiedLLMClient)

---

### What This Phase Covers

The routing and resilience layer that sits **between** `UnifiedLLMClient` and the adapters.
The legacy `combo.py` contains a mature, production-tested implementation of all of this.

```
UnifiedLLMClient.complete(provider, model, messages)
      ↓
ComboRouter.route(combo_id, messages, **kw)
  ├── resolve_targets(combo)           → list[ComboTarget]
  ├── _apply_strategy(targets, strat)  → reordered list
  ├── BudgetGuard.check_budget()       → skip if combo exhausted
  └── For each target (with fallback):
        ├── CircuitBreaker.is_open?    → skip if open
        ├── RateLimiter.wait_and_acquire(provider, tokens)
        ├── adapter.complete(messages)
        ├── CircuitBreaker.record_success/failure
        ├── BudgetGuard.record_cost()
        └── UsageTracker.record()
      ↓
QwenTriageRouter.triage(request)       → selects combo/provider for request
  ├── analyze_complexity()             → TriageMetrics (trivial→critical)
  ├── determine_triage_level()         → tier0–4
  ├── select_provider()                → primary AIProvider
  └── build_fallback_chain()           → cost-ordered fallbacks

TokenCounter.count(messages)           → pre-request token estimate
                                         (drives routing + budget checks)
```

---

### 13 Routing Strategies

| Strategy | Behaviour |
|----------|-----------|
| `PRIORITY` | Ordered list, first success wins |
| `ROUND_ROBIN` | Rotate through targets, session continuity |
| `COST_OPTIMIZED` | Cheapest first (input+output cost) |
| `WEIGHTED` | Probabilistic by weight field |
| `RANDOM` | Shuffle randomly |
| `LEAST_USED` | Fewest past requests first |
| `FILL_FIRST` | Fill one target's quota before next |
| `P2C` | Power of Two Choices — pick 2 random, use least-used |
| `STRICT_RANDOM` | Pure random, no dedup |
| `LKGP` | Last Known Good Provider — pin to last successful target |
| `CONTEXT_OPTIMIZED` | Largest context window first (long conversations) |
| `CONTEXT_RELAY` | Relay full context across accounts for overflow |
| `AUTO` | Delegates to COST_OPTIMIZED |

---

### 10+ Tier Model Routing (ProviderTierList)

Tiers are a **list ordered lowest→highest**. The last entry is ALWAYS S+.
New tiers are inserted between existing ones — S+ stays at the tail forever.
Each tier has: `rank`, `label`, `models`, `cost_class`, `max_request_complexity`, `requires_hardware`.

```python
# core/routing/tiers.py
PROVIDER_TIER_LIST: list[ProviderTier] = [
    ProviderTier(
        rank=0, label="LOCAL_MINIMAL",
        models=["qwen3:0.6b", "llama3.2:1b"],
        cost_usd_per_1m_in=0, cost_usd_per_1m_out=0,
        max_complexity=RequestComplexity.SIMPLE,
        requires_hardware="cpu_only",      # ← your PC
        adapter="ollama",
    ),
    ProviderTier(
        rank=1, label="LOCAL_LIGHT",
        models=["qwen3:1.7b", "llama3.2:3b", "phi3:mini"],
        cost_usd_per_1m_in=0, cost_usd_per_1m_out=0,
        max_complexity=RequestComplexity.MODERATE,
        requires_hardware="4gb_vram",
        adapter="ollama",
    ),
    ProviderTier(
        rank=2, label="LOCAL_STANDARD",
        models=["qwen3:4b", "mistral:7b", "llama3.1:8b"],
        cost_usd_per_1m_in=0, cost_usd_per_1m_out=0,
        max_complexity=RequestComplexity.MODERATE,
        requires_hardware="8gb_vram",
        adapter="ollama",
    ),
    ProviderTier(
        rank=3, label="LOCAL_CAPABLE",
        models=["qwen3:8b", "llama3.1:8b-q8", "deepseek-r1:8b"],
        cost_usd_per_1m_in=0, cost_usd_per_1m_out=0,
        max_complexity=RequestComplexity.COMPLEX,
        requires_hardware="16gb_vram",
        adapter="ollama",
    ),
    ProviderTier(
        rank=4, label="FREE_CLOUD",
        models=["gemini-2.0-flash-lite", "groq/llama3.1-8b", "together/llama-3.1-8b-free"],
        cost_usd_per_1m_in=0, cost_usd_per_1m_out=0,
        max_complexity=RequestComplexity.MODERATE,
        requires_hardware=None,
        adapter="http",
    ),
    ProviderTier(
        rank=5, label="BUDGET_CLOUD",
        models=["gemini-2.0-flash", "deepseek-chat", "grok-3-mini", "mistral/mistral-small"],
        cost_usd_per_1m_in=0.1, cost_usd_per_1m_out=0.4,
        max_complexity=RequestComplexity.COMPLEX,
        requires_hardware=None,
        adapter="http",
    ),
    ProviderTier(
        rank=6, label="STANDARD_CLOUD",
        models=["gpt-4o-mini", "claude-3-haiku-20240307", "gemini-1.5-pro", "mistral/mistral-large"],
        cost_usd_per_1m_in=0.15, cost_usd_per_1m_out=0.6,
        max_complexity=RequestComplexity.COMPLEX,
        requires_hardware=None,
        adapter="http_or_native",
    ),
    ProviderTier(
        rank=7, label="ADVANCED_CLOUD",
        models=["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-2.0-pro", "grok-3"],
        cost_usd_per_1m_in=2.5, cost_usd_per_1m_out=10.0,
        max_complexity=RequestComplexity.CRITICAL,
        requires_hardware=None,
        adapter="http_or_native",
    ),
    ProviderTier(
        rank=8, label="PREMIUM_CLOUD",
        models=["gpt-4.5", "claude-3-7-sonnet-20250219", "gemini-2.5-pro", "o3-mini"],
        cost_usd_per_1m_in=3.0, cost_usd_per_1m_out=15.0,
        max_complexity=RequestComplexity.CRITICAL,
        requires_hardware=None,
        adapter="native",
    ),
    ProviderTier(
        rank=9, label="ELITE_CLOUD",
        models=["claude-opus-4-5", "gpt-5", "o3", "gemini-2.5-ultra"],
        cost_usd_per_1m_in=15.0, cost_usd_per_1m_out=75.0,
        max_complexity=RequestComplexity.CRITICAL,
        requires_hardware=None,
        adapter="native",
    ),
    # ── S+ is ALWAYS LAST. Insert new tiers above, never below. ──────────────
    ProviderTier(
        rank=10, label="S_PLUS",
        models=["claude-opus-4-7", "o3-pro", "gemini-2.5-pro-deep-think"],
        cost_usd_per_1m_in=75.0, cost_usd_per_1m_out=150.0,
        max_complexity=RequestComplexity.CRITICAL,
        requires_hardware=None,
        adapter="native",
        is_frontier=True,   # flag: bleeding edge, may have breaking API changes
    ),
]
```

**Design rules:**
- `PROVIDER_TIER_LIST[-1]` is **always** S+. Never append after it.
- Tiers 0–3 are local-only (Ollama). Tier 0 runs on any CPU.
- `requires_hardware=None` = cloud (no local GPU needed).
- `is_frontier=True` = may have unstable APIs, treat with extra error handling.
- Add future models/tiers by inserting a new `ProviderTier` at the correct rank.
  Renumber ranks by index: `[t.rank for t in PROVIDER_TIER_LIST] == list(range(len(PROVIDER_TIER_LIST)))`.

**Triage routing:**

```
RequestComplexity → minimum tier rank to route to
  TRIVIAL   → 0  (local minimal is fine)
  SIMPLE    → 0  (prefer local, fallback to cloud tier 4 if unavailable)
  MODERATE  → 1  (light local or free cloud)
  COMPLEX   → 5  (budget cloud minimum)
  CRITICAL  → 7  (advanced cloud minimum)
  SECURITY_CRITICAL (level≥9) → 9  (elite or S+)
```

**Budget-aware**: walk tier list from minimum rank upward, skip if `cost × estimated_tokens > budget_remaining`.  
**Hardware-aware**: skip local tiers if `requires_hardware` is not available on host.  
**Fallback**: always try next tier up on failure — S+ is the final fallback.

---

### 14 Todos (Phase 13)

| ID | Task | What |
|----|------|------|
| `routing-combo-target-model` | T13.1 | `ComboTarget` + `ComboConfig` msgspec.Struct |
| `routing-strategy-enum` | T13.1 | `Strategy` enum (13 values) |
| `routing-strategy-resolver` | T13.2 | `_apply_strategy()` — all 13 strategies |
| `routing-circuit-breaker` | T13.3 | `CircuitBreaker` per target (5 failures / 60s reset) |
| `routing-budget-guard` | T13.3 | `BudgetGuard` per-combo spend + enforcement |
| `routing-rate-limiter` | T13.4 | `RateLimiter` token-bucket RPM+TPM, header learning |
| `routing-usage-tracker` | T13.4 | `UsageTracker` per-request + DB persistence |
| `routing-token-counter` | T13.4 | `TokenCounter` pre-request estimate (wraps adapters) |
| `routing-combo-router` | T13.5 | `ComboRouter.route()` — orchestrates all of the above |
| `routing-combo-registry` | T13.5 | `ComboRegistry` (Ring 3) — startup-loaded combos |
| `routing-qwen-triage-router` | T13.6 | `QwenTriageRouter` 5-tier complexity routing |
| `routing-triage-complexity` | T13.6 | `analyze_complexity()` + `RequestComplexity` enum |
| `routing-unified-client-wire` | T13.7 | Wire `ComboRouter` + `QwenTriageRouter` into `UnifiedLLMClient` |
| `routing-rest-endpoints` | T13.8 | `/routing/combos`, `/routing/circuit-breakers`, `/routing/budget` REST API |

**Dependencies**:
- Phase 13 → Phase 10 (`LLMAdapter` Protocol + `UnifiedLLMClient`)
- `routing-token-counter` → `sdk-native-anthropic-adapter` (uses `client.messages.count_tokens()`)
- `routing-usage-tracker` → Phase 9 ORM (persist to Tortoise model)
- `routing-triage-complexity` replaces `ai-triage-strategy-wire` (Phase 8 todo)
- `routing-qwen-triage-router` replaces `ai-triage-ollama-wire` (Phase 8 todo — superseded here)

---

## 🔀 Phase 14 — Event Hooks & Entry/Exit Instrumentation

**Goal**: Every entry and exit point in the system automatically emits `DomainEvent`s. OTEL traces are derived from the event stream. An optional hook compatibility layer allows `@on_event` subscriber patterns.

**Depends on**: Phase 6 T6.3 (`p6-events-domain-event`, `p6-events-otel-bridge`) must be done first.

**Entry points covered**:
- FastAPI HTTP endpoints (all routes via middleware)
- `CommandBus.dispatch()` (all commands)
- `UnifiedLLMClient.complete()` (all LLM calls)
- `Agent.run()` (all agent executions)
- `ToolExecutor.execute()` (all tool calls)

**Exit points covered** (per entry above):
- Normal return → `*.completed` event
- Exception → `*.failed` event with `error` + `type` in payload
- Both carry same `correlation_id` as entry → traces link automatically

---

### T14.1 — `@instrument` Decorator Core

The foundational building block. A single decorator wraps any `async def` (or sync) function and emits three events: `{namespace}.started`, `{namespace}.completed`, `{namespace}.failed`. Everything in T14.2 is just applying this decorator at the right layer.

```python
# core/events/instrument.py
import functools, uuid, asyncio
from .store import event_store  # module-level singleton

def instrument(namespace: str, extract_aggregate_id=None):
    """Emit DomainEvents at entry and exit of any async function.
    
    Usage:
        @instrument("agent.run", extract_aggregate_id=lambda self, *a, **k: self.agent_id)
        async def run(self, task: Task) -> Result: ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            correlation_id = _get_correlation_id()   # from contextvars
            agg_id = extract_aggregate_id(*args, **kwargs) if extract_aggregate_id else namespace
            
            await event_store.append(DomainEvent(
                event_type=f"{namespace}.started",
                aggregate_id=agg_id,
                aggregate_type=namespace,
                payload={"fn": func.__qualname__},
                correlation_id=correlation_id,
            ))
            try:
                result = await func(*args, **kwargs)
                await event_store.append(DomainEvent(
                    event_type=f"{namespace}.completed",
                    aggregate_id=agg_id,
                    aggregate_type=namespace,
                    payload={},
                    correlation_id=correlation_id,
                ))
                return result
            except Exception as exc:
                await event_store.append(DomainEvent(
                    event_type=f"{namespace}.failed",
                    aggregate_id=agg_id,
                    aggregate_type=namespace,
                    payload={"error": str(exc), "exc_type": type(exc).__name__},
                    correlation_id=correlation_id,
                ))
                raise
        return wrapper
    return decorator

# correlation_id lives in a contextvars.ContextVar — propagates through async tasks
_correlation_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

def _get_correlation_id() -> str:
    cid = _correlation_ctx.get()
    if not cid:
        cid = str(uuid.uuid4())
        _correlation_ctx.set(cid)
    return cid
```

**Todos (T14.1)**:
- `events-instrument-decorator` — Implement `@instrument(namespace)` in `core/events/instrument.py` with `ContextVar` correlation propagation (async + sync support)
- `events-event-bus-module` — Wire `EventStore` + `OtelBridge.run()` as module-level singletons in `core/events/__init__.py`; register `OtelBridge.run()` as FastAPI lifespan background task

---

### T14.2 — Entry/Exit Point Wiring

Apply `@instrument` (or equivalent middleware) at all system entry/exit points.

#### FastAPI Middleware

```python
# core/asgi/middleware/event_instrumentation.py
class EventInstrumentationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Extract W3C traceparent or generate new correlation_id
        correlation_id = (
            _extract_traceparent(request.headers.get("traceparent"))
            or request.headers.get("x-correlation-id")
            or str(uuid.uuid4())
        )
        _correlation_ctx.set(correlation_id)
        request.state.correlation_id = correlation_id

        await event_store.append(DomainEvent(
            event_type=EventType.HTTP_REQUEST_STARTED,
            aggregate_id=request.url.path,
            aggregate_type="http.request",
            payload={"method": request.method, "path": request.url.path},
            correlation_id=correlation_id,
        ))
        try:
            response = await call_next(request)
            await event_store.append(DomainEvent(
                event_type=EventType.HTTP_REQUEST_COMPLETED,
                aggregate_id=request.url.path,
                aggregate_type="http.request",
                payload={"status_code": response.status_code},
                correlation_id=correlation_id,
            ))
            response.headers["x-correlation-id"] = correlation_id
            return response
        except Exception as exc:
            await event_store.append(DomainEvent(
                event_type=EventType.HTTP_REQUEST_FAILED, ...
            ))
            raise
```

**Todos (T14.2)**:
- `events-middleware-fastapi` — `EventInstrumentationMiddleware`: `http.request.started` / `http.request.completed` / `http.request.failed`; injects `x-correlation-id` response header; extracts W3C `traceparent`; sets `ContextVar`
- `events-instrument-command-bus` — Apply `@instrument("command.dispatch")` to `CommandBus.dispatch()` in `core/events/commands.py`; payload includes command type name
- `events-instrument-llm-client` — Apply `@instrument("llm.call")` to `UnifiedLLMClient.complete()`; payload includes `model`, `provider`, token counts from `LLMResponse`; dep: Phase 10 `sdk-unified-client`
- `events-instrument-agent` — Apply `@instrument("agent.run")` to `Agent.run()`; payload includes `agent_id`, `task_type`
- `events-instrument-tool` — Apply `@instrument("tool.call")` to `ToolExecutor.execute()`; payload includes `tool_name`

---

### T14.3 — OTEL Context Propagation

Connect `correlation_id` to W3C TraceContext so OtelBridge groups events into proper distributed traces.

```python
# core/events/otel_context.py
from opentelemetry.propagators.textmap import CarrierGetter
from opentelemetry import context, propagate

class TraceContextExtractor:
    """Map incoming W3C traceparent → correlation_id, inject into outgoing requests."""

    @staticmethod
    def extract_from_headers(headers: Mapping[str, str]) -> str:
        """Returns trace_id from W3C traceparent or generates new UUID."""
        ctx = propagate.extract(headers)
        span = trace.get_current_span(ctx)
        if span and span.get_span_context().is_valid:
            return format(span.get_span_context().trace_id, "032x")
        return str(uuid.uuid4())

class OtelSpanInstrumentor:
    """Create a child OTEL span for each @instrument-wrapped call.
    Span attributes: aggregate_id, session_id, agent_id, team_id.
    Span closes on exit event. Duration = entry→exit elapsed time."""
```

**Todos (T14.3)**:
- `events-otel-trace-context` — `TraceContextExtractor` + `ContextVar` → W3C trace propagation; maps `traceparent` trace_id to `correlation_id`; dep: `p6-events-otel-bridge`
- `events-otel-child-spans` — `OtelSpanInstrumentor`: each `@instrument` call creates a child span with `aggregate_id`, `session_id`, `agent_id` OTEL attributes; span closes on completed/failed event; dep: `events-otel-trace-context`
- `events-otel-auto-deps` — Add `opentelemetry-instrumentation-fastapi` + `opentelemetry-instrumentation-aiohttp` to `pyproject.toml`; zero-code HTTP instrumentation layer

---

### T14.4 — Hook Compatibility Layer (optional)

For consumers who prefer `@on_event("llm.call.*")` decorator style over direct Redis Streams consumption. Fire-and-forget, never blocks main flow.

```python
# modules/hooks/registry.py
import fnmatch, asyncio
from collections import defaultdict

class HookRegistry:
    _handlers: dict[str, list[Callable]] = defaultdict(list)

    def register(self, pattern: str, handler: Callable) -> None:
        self._handlers[pattern].append(handler)

    def on_event(self, pattern: str):
        """@on_event("llm.call.*") — subscribes handler to matching events."""
        def decorator(func):
            self.register(pattern, func)
            return func
        return decorator

    async def fire(self, event: DomainEvent) -> None:
        for pattern, handlers in self._handlers.items():
            if fnmatch.fnmatch(event.event_type, pattern):
                for handler in handlers:
                    asyncio.create_task(_safe_call(handler, event))

async def _safe_call(handler, event, timeout: float = 5.0) -> None:
    try:
        await asyncio.wait_for(
            handler(event) if asyncio.iscoroutinefunction(handler) else asyncio.to_thread(handler, event),
            timeout=timeout,
        )
    except Exception:
        pass  # isolated — never propagates to caller

hook_registry = HookRegistry()   # singleton handle
on_event = hook_registry.on      # exported shortcut
```

**Todos (T14.4)**:
- `events-hook-registry` — `HookRegistry` class with glob-pattern matching (`fnmatch`); `register(pattern, handler)` + `run_chain(event_type, payload)`; implemented in `modules/hooks`, consumed via `core/events` compatibility export
- `events-on-event-decorator` — `@on_event("llm.call.*")` decorator shortcut; auto-registers sync and async handlers with `hook_registry`
- `events-hook-executor` — `HookExecutor` / `_safe_call`: fire-and-forget with `asyncio.wait_for(..., timeout=5.0)`; converts sync handlers via `asyncio.to_thread`; catches + logs all errors silently

---

### New EventType Constants (Phase 14)

Add to `EventType` class in `core/events/domain_event.py`:

```python
# HTTP
HTTP_REQUEST_STARTED   = "http.request.started"
HTTP_REQUEST_COMPLETED = "http.request.completed"
HTTP_REQUEST_FAILED    = "http.request.failed"

# Commands
COMMAND_DISPATCHED = "command.dispatched"
COMMAND_HANDLED    = "command.handled"
COMMAND_FAILED     = "command.failed"

# Agents
AGENT_RUN_STARTED   = "agent.run.started"
AGENT_RUN_COMPLETED = "agent.run.completed"
AGENT_RUN_FAILED    = "agent.run.failed"

# Tools
TOOL_CALL_START    = "tool.call.start"
TOOL_CALL_COMPLETE = "tool.call.complete"
TOOL_CALL_ERROR    = "tool.call.error"
```

---

### 13 Todos (Phase 14)

| ID | Task | What |
|----|------|------|
| `events-instrument-decorator` | T14.1 | `@instrument(namespace)` decorator + `ContextVar` correlation propagation |
| `events-event-bus-module` | T14.1 | Wire `EventStore` + `OtelBridge` singletons in `core/events/__init__.py` |
| `events-middleware-fastapi` | T14.2 | `EventInstrumentationMiddleware` for all HTTP entry/exit points |
| `events-instrument-command-bus` | T14.2 | Apply `@instrument` to `CommandBus.dispatch()` |
| `events-instrument-llm-client` | T14.2 | Apply `@instrument` to `UnifiedLLMClient.complete()` (dep: Phase 10) |
| `events-instrument-agent` | T14.2 | Apply `@instrument` to `Agent.run()` |
| `events-instrument-tool` | T14.2 | Apply `@instrument` to `ToolExecutor.execute()` |
| `events-otel-trace-context` | T14.3 | `TraceContextExtractor`: W3C traceparent → `correlation_id` |
| `events-otel-child-spans` | T14.3 | `OtelSpanInstrumentor`: child span per instrumented call |
| `events-otel-auto-deps` | T14.3 | Add OTEL auto-instrumentation packages to `pyproject.toml` |
| `events-hook-registry` | T14.4 | `HookRegistry` with glob-pattern matching |
| `events-on-event-decorator` | T14.4 | `@on_event("pattern.*")` decorator |
| `events-hook-executor` | T14.4 | Fire-and-forget hook runner with timeout + error isolation |

**Dependencies**:
- `events-instrument-decorator` → `p6-events-domain-event`
- `events-instrument-decorator` → `p6-events-otel-bridge`
- `events-event-bus-module` → `p6-events-domain-event`
- `events-middleware-fastapi` → `events-instrument-decorator`
- `events-instrument-command-bus` → `events-instrument-decorator`
- `events-instrument-llm-client` → `events-instrument-decorator`
- `events-instrument-llm-client` → `sdk-unified-client` (Phase 10)
- `events-instrument-agent` → `events-instrument-decorator`
- `events-instrument-tool` → `events-instrument-decorator`
- `events-otel-trace-context` → `p6-events-otel-bridge`
- `events-otel-child-spans` → `events-otel-trace-context`
- `events-otel-auto-deps` → `events-otel-trace-context`
- `events-hook-registry` → `events-instrument-decorator`
- `events-on-event-decorator` → `events-hook-registry`
- `events-hook-executor` → `events-hook-registry`

---

### T14.5 — Interceptor Chain (Mutable Pre/Post Hooks)

**Distinction from T14.4**:
- T14.4 `HookRegistry` = fire-and-forget **observers** — never modify anything, used for telemetry/logging
- T14.5 `InterceptorChain` = **mutating middleware** — can modify inputs before a call, modify outputs after, or block the call entirely

Implementation status (2026-05-09):
- Implemented in `src/css/modules/hooks/interceptors.py`
- `HookContext` is now a mutable `msgspec.Struct`
- `HookBlockedError` blocks execution from pre/post interceptor stages
- `InterceptorRegistry` provides priority-sorted `pre` and `post` chains with glob matching
- Exported shortcuts: `pre_hook`, `post_hook`, `interceptor_registry`
- Wired synchronously into both:
  - `src/css/core/events/emitter.py` (`event.pre/post/past/on_completed/on_failed/all`)
  - `src/css/core/events/instrument.py` (`instrument(...)` context manager)

Implementation guardrail:
- Classes that emit lifecycle/runtime events should inherit `BaseEmitterClass` when practical so namespace qualification and manual event registration are consistent.

**Usage examples**:

```python
from css.core.events import HookBlockedError, HookContext, post_hook, pre_hook

# Validate + clamp tool input before execution
@pre_hook("tool.call.*", priority=10)
async def clamp_tool_timeout(ctx: HookContext) -> HookContext:
    kwargs = ctx.get_kwargs()
    timeout = kwargs.get("timeout")
    if isinstance(timeout, int | float):
        kwargs["timeout"] = min(timeout, 60)
        ctx.set_kwargs(kwargs)
    return ctx

# Block dangerous prompt injection before LLM call
@pre_hook("llm.call", priority=1)  # priority=1 → runs first
async def prompt_safety_check(ctx: HookContext) -> HookContext:
    kwargs = ctx.get_kwargs()
    messages = kwargs.get("messages")
    last_msg = messages[-1].get("content", "") if isinstance(messages, list) and messages else ""
    if "<script>" in last_msg:
        raise HookBlockedError("XSS detected in prompt")
    return ctx

# Redact secrets from LLM output
@post_hook("llm.call", priority=10)
async def redact_llm_output(ctx: HookContext) -> HookContext:
    if ctx.output:
        ctx.output.content = _redact(ctx.output.content)
    return ctx

# Enrich agent output with audit metadata
@post_hook("agent.run.*", priority=50)
async def append_audit_trail(ctx: HookContext) -> HookContext:
    ctx.metadata["audited_at"] = time.time()
    return ctx

# Chain arbitrary pre+post on ANY entry point
@pre_hook("*", priority=100)  # lowest priority — runs last in pre chain
async def global_rate_check(ctx: HookContext) -> HookContext:
    if await rate_limiter.is_exhausted(ctx.metadata.get("user_id")):
        raise HookBlockedError("Rate limit exceeded")
    return ctx
```

**Todos (T14.5)**:
- [x] `events-interceptor-context` — `HookContext` + `HookBlockedError`
- [x] `events-interceptor-registry` — `InterceptorRegistry` with priority + glob
- [x] `events-pre-hook-decorator` — `@pre_hook(pattern, priority=50)` exported from `core/events`
- [x] `events-post-hook-decorator` — `@post_hook(pattern, priority=50)` exported from `core/events`
- [x] `events-instrument-interceptor-wire` — interceptor chain wired into `event.*` + `instrument(...)`

### Updated Todos Table (Phase 14, all tasks)

| ID | Task | What |
|----|------|------|
| `events-instrument-decorator` | T14.1 | `@instrument(namespace)` + ContextVar correlation |
| `events-event-bus-module` | T14.1 | Wire singletons in `__init__.py` + lifespan |
| `events-middleware-fastapi` | T14.2 | `EventInstrumentationMiddleware` |
| `events-instrument-command-bus` | T14.2 | CommandBus wired |
| `events-instrument-llm-client` | T14.2 | UnifiedLLMClient wired (dep: Phase 10) |
| `events-instrument-agent` | T14.2 | Agent.run wired |
| `events-instrument-tool` | T14.2 | ToolExecutor.execute wired |
| `events-otel-trace-context` | T14.3 | W3C traceparent → correlation_id |
| `events-otel-child-spans` | T14.3 | Child OTEL span per call |
| `events-otel-auto-deps` | T14.3 | pyproject.toml OTEL packages |
| `events-hook-registry` | T14.4 | Fire-and-forget observer registry (telemetry only) |
| `events-on-event-decorator` | T14.4 | `@on_event` shortcut |
| `events-hook-executor` | T14.4 | `_safe_call` fire-and-forget runner |
| `events-interceptor-context` | T14.5 | `HookContext` + `HookBlockedError` |
| `events-interceptor-registry` | T14.5 | `InterceptorRegistry` with priority + glob |
| `events-pre-hook-decorator` | T14.5 | `@pre_hook(pattern, priority)` |
| `events-post-hook-decorator` | T14.5 | `@post_hook(pattern, priority)` |
| `events-instrument-interceptor-wire` | T14.5 | Wire interceptor chain into `@instrument` |

---

## 🔀 Phase 15 — Permission System Redesign

**Problem being solved**: The current permission system has three separate concerns tangled together:
1. `@scopes` does scope hierarchy **and** access restriction — these should be separate
2. `@permissions` mixes path permissions (r/w/x) and tool permissions into one blob (`PermissionPolicy`)
3. Path permissions are per-scope-level (abstract), not per actual filesystem path — you cannot express "/etc/passwd READ only" or "/root/ WRITE with sudo"
4. No elevation concept (sudo / root) exists anywhere
5. `has_permission()` returns `True` unconditionally — it's a stub

---

### Module Boundaries After Redesign

**Rule**: Scope ≠ Permission. Scope = *where you are*. Permission = *what you can do*.

```
@scopes          — 2-level config cascade (GLOBAL + SESSION only)
                   ZERO access control logic here
                   provides: ScopeContext (current scope, session_id, parent)

@permissions     — access control only: PathGrant + ToolGrant + PermissionChecker
                   no scope hierarchy, no filesystem path building, no JWT

@workspace       — session/project directory management
                   consumes @permissions PathGrant to enforce what agent can read/write
```

---

### T15.1 — Core Types: PathGrant + ToolGrant

Two orthogonal grant types, both `msgspec.Struct`, both immutable.

```python
# core/permissions/types.py.py

import msgspec
from enum import Flag, auto

class PathOp(Flag):
    """Filesystem operations — can be combined: READ | WRITE."""
    READ    = auto()
    WRITE   = auto()
    EXECUTE = auto()
    ALL     = READ | WRITE | EXECUTE

class PathGrant(msgspec.Struct, frozen=True):
    """Grants specific path operations to a specific agent.
    
    path_pattern uses glob syntax:
      "/etc/**"             — read /etc and all subdirs
      "/home/daen/**"       — full access to home dir
      "/usr/local/bin/nmap" — execute one specific binary
      "/**"                 — root of filesystem (dangerous)
    
    elevated=True means the agent MAY run this op as root/sudo.
    It does NOT mean the agent IS root — it means they CAN request elevation.
    """
    agent_id: str
    path_pattern: str
    ops: frozenset[str]     # {"READ"}, {"WRITE"}, {"READ","WRITE"}, {"EXECUTE"}, etc.
    elevated: bool = False  # True = sudo/root privilege allowed for this path
    scope_id: str | None = None   # restrict to a specific scope_id (None = any scope)
    expires_at: float | None = None  # unix timestamp, None = never expires
    
    def allows(self, op: PathOp) -> bool:
        return op.name in self.ops

class ToolGrant(msgspec.Struct, frozen=True):
    """Grants or explicitly denies a tool pattern to an agent.
    
    tool_pattern uses glob syntax:
      "bash.*"              — all bash tool variants
      "file.read"           — exactly one tool
      "browser.*"           — all browser tools
      "*"                   — all tools (use sparingly)
    
    allowed=True  = agent CAN use matching tools
    allowed=False = explicit DENY — overrides any ALLOW (deny wins)
    """
    agent_id: str
    tool_pattern: str
    allowed: bool = True
    scope_id: str | None = None
    expires_at: float | None = None
```

**Why two separate types (not one PermissionPolicy)**:
- Path grants need glob path matching + elevation flag + per-path granularity
- Tool grants need glob tool-name matching + deny semantics
- Mixing them means you can't have "allow bash.* but deny bash.rm_rf"

**Todos (T15.1)**:
- `perm-path-op-flag` — Define `PathOp(Flag)` enum in `core/permissions/enums.py`. Values: READ, WRITE, EXECUTE, ALL = READ|WRITE|EXECUTE.
- `perm-path-grant-struct` — Define `PathGrant` msgspec.Struct in `core/permissions/types.py`. Fields: agent_id, path_pattern (glob), ops (frozenset[str]), elevated (bool=False), session_id (str|None), expires_at (float|None). Method: `allows(op: PathOp) -> bool`.
- `perm-tool-grant-struct` — Define `ToolGrant` msgspec.Struct in `core/permissions/types.py`. Fields: agent_id, tool_pattern (glob), allowed (bool=True), session_id (str|None), expires_at (float|None). Deny-wins rule documented in docstring.

---

### T15.2 — Grant Storage: Tortoise Model + Redis Cache

```python
# core/permissions/user.py

class PathGrantRecord(Model):
    """Persistent storage for PathGrant. One row per agent+path_pattern."""
    id            = fields.IntField(pk=True)
    agent_id      = fields.CharField(max_length=255)
    path_pattern  = fields.CharField(max_length=1024)
    ops           = fields.JSONField()          # list of "READ", "WRITE", "EXECUTE"
    elevated      = fields.BooleanField(default=False)
    scope_id      = fields.CharField(max_length=255, null=True)
    expires_at    = fields.DatetimeField(null=True)
    created_at    = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = "path_grants"
        indexes = [("agent_id",), ("agent_id", "scope_id")]

class ToolGrantRecord(Model):
    """Persistent storage for ToolGrant."""
    id            = fields.IntField(pk=True)
    agent_id      = fields.CharField(max_length=255)
    tool_pattern  = fields.CharField(max_length=255)
    allowed       = fields.BooleanField(default=True)
    scope_id      = fields.CharField(max_length=255, null=True)
    expires_at    = fields.DatetimeField(null=True)
    created_at    = fields.DatetimeField(auto_now_add=True)
    class Meta:
        table = "tool_grants"
        indexes = [("agent_id",), ("agent_id", "scope_id")]
```

Redis cache key: `perm:agent:{agent_id}` → JSON list of all grants (TTL 60s).
Invalidated on any grant create/delete for that agent.

**Todos (T15.2)**:
- `perm-grant-models` — Create `PathGrantRecord` + `ToolGrantRecord` Tortoise models in `core/permissions/models.py`. Indexes on agent_id and (agent_id, session_id).
- `perm-grant-redis-cache` — `GrantCache` helper in `core/permissions/cache.py`. `load(agent_id) → (list[PathGrant], list[ToolGrant])`. Key: `perm:agent:{agent_id}`, TTL 60s. Invalidate on write.

---

### T15.3 — PermissionChecker: the single `can()` interface

This is the only class other modules should ever import from `@permissions`.

```python
# core/permissions/checker.py

class PermissionChecker:
    """Single entry point for all permission checks.
    
    Inject as dependency. Never instantiate per-request.
    All methods return bool or raise PermissionDenied.
    """

    def __init__(self, cache: GrantCache):
        self._cache = cache

    async def can_path(
        self,
        agent_id: str,
        path: str,           # actual path e.g. "/etc/passwd"
        op: PathOp,
        session_id: str | None = None,
    ) -> bool:
        """True if agent has matching PathGrant for path+op.
        
        Matching rules:
        - path_pattern is a glob: fnmatch("/etc/**", "/etc/passwd") → True
        - session_id=None grants match any session
        - Expired grants are ignored
        - At least one matching grant with op must exist
        """
        grants, _ = await self._cache.load(agent_id)
        now = time.time()
        for g in grants:
            if g.expires_at and g.expires_at < now:
                continue
            if g.session_id and g.session_id != session_id:
                continue
            if fnmatch.fnmatch(path, g.path_pattern) and g.allows(op):
                return True
        return False

    async def can_elevated(self, agent_id: str, path: str, session_id: str | None = None) -> bool:
        """True if agent has a PathGrant with elevated=True for this path."""
        grants, _ = await self._cache.load(agent_id)
        now = time.time()
        for g in grants:
            if g.expires_at and g.expires_at < now: continue
            if g.session_id and g.session_id != session_id: continue
            if fnmatch.fnmatch(path, g.path_pattern) and g.elevated:
                return True
        return False

    async def can_tool(self, agent_id: str, tool_name: str, session_id: str | None = None) -> bool:
        """True if agent may use tool_name.
        
        Deny-wins: if ANY ToolGrant with allowed=False matches → return False.
        Only if no deny matches AND at least one allow matches → return True.
        """
        _, tool_grants = await self._cache.load(agent_id)
        now = time.time()
        allow = False
        for g in tool_grants:
            if g.expires_at and g.expires_at < now: continue
            if g.session_id and g.session_id != session_id: continue
            if fnmatch.fnmatch(tool_name, g.tool_pattern):
                if not g.allowed:
                    return False     # explicit deny — immediately reject
                allow = True
        return allow

    # Raise variants (for use in @pre_hook interceptors and @require_* decorators)
    async def require_path(self, agent_id: str, path: str, op: PathOp, session_id=None):
        if not await self.can_path(agent_id, path, op, session_id):
            raise PermissionDenied(f"{agent_id} cannot {op.name} {path!r}")

    async def require_tool(self, agent_id: str, tool_name: str, session_id=None):
        if not await self.can_tool(agent_id, tool_name, session_id):
            raise PermissionDenied(f"{agent_id} cannot use tool {tool_name!r}")

    async def require_elevated(self, agent_id: str, path: str, session_id=None):
        if not await self.can_elevated(agent_id, path, session_id):
            raise ElevationDenied(f"{agent_id} has no elevated grant for {path!r}")
```

**Key design decisions**:
- `can_tool` with **deny-wins** — explicit `allowed=False` beats any `allowed=True`. This means you can grant `"*"` to an orchestrator and then deny `"bash.rm_rf"` and the deny wins.
- `can_path` with **glob matching** — `/etc/**` matches `/etc/passwd`. Agent's actual filesystem path checked at call time.
- `can_elevated` is a **separate check** — you need both `can_path(..., EXECUTE)` AND `can_elevated(...)` to run something as root. Two gates.

**Todos (T15.3)**:
- `perm-checker-can-path` — `PermissionChecker.can_path()` + `require_path()`. Glob matching via fnmatch, expiry check, session_id filter.
- `perm-checker-can-tool` — `PermissionChecker.can_tool()` + `require_tool()`. Deny-wins logic: explicit `allowed=False` immediately returns False before any allow check.
- `perm-checker-can-elevated` — `PermissionChecker.can_elevated()` + `require_elevated()`. Separate from can_path — must be checked explicitly.
- `perm-checker-exceptions` — `PermissionDenied(agent_id, path_or_tool, op)` and `ElevationDenied(agent_id, path)` in `core/permissions/exceptions.py`. Both subclass a common `AccessDenied` base.

---

### T15.4 — Decorators: `@require_path`, `@require_tool`

```python
# core/permissions/decorators.py

def require_path(path_or_kwarg: str, op: PathOp):
    """@require_path("/etc/**", PathOp.READ)
    or
    @require_path("path", PathOp.WRITE)  # reads 'path' kwarg from function args
    """
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            agent_id = _extract_agent_id(args, kwargs)  # from ScopeContext or agent_id kwarg
            path = kwargs.get(path_or_kwarg, path_or_kwarg)
            await checker.require_path(agent_id, path, op)
            return await fn(*args, **kwargs)
        return wrapper
    return decorator

def require_tool(tool_name: str):
    """@require_tool("bash.execute")"""
    def decorator(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            agent_id = _extract_agent_id(args, kwargs)
            await checker.require_tool(agent_id, tool_name)
            return await fn(*args, **kwargs)
        return wrapper
    return decorator
```

**Todos (T15.4)**:
- `perm-decorator-require-path` — `@require_path(path_or_kwarg, op)` decorator. Extracts agent_id from `scope_context` kwarg or `agent_id` kwarg. Calls `checker.require_path()`.
- `perm-decorator-require-tool` — `@require_tool(tool_name)` decorator. Same agent_id extraction. Calls `checker.require_tool()`.

---

### T15.5 — GrantManager: CRUD + profiles

```python
# core/permissions/manager.py

class GrantManager:
    """CRUD for PathGrant and ToolGrant. Used by REST endpoints and admin commands."""

    async def grant_path(self, agent_id: str, path_pattern: str, ops: set[PathOp], elevated=False, session_id=None, expires_in_seconds=None) -> PathGrant: ...
    async def revoke_path(self, agent_id: str, path_pattern: str) -> None: ...
    async def grant_tool(self, agent_id: str, tool_pattern: str, allowed=True, session_id=None) -> ToolGrant: ...
    async def revoke_tool(self, agent_id: str, tool_pattern: str) -> None: ...
    async def list_grants(self, agent_id: str) -> dict[str, list]: ...
    async def clear_agent(self, agent_id: str) -> None: ...
    
    # Profiles: predefined grant sets for standard roles
    async def apply_profile(self, agent_id: str, profile: GrantProfile) -> None: ...

class GrantProfile:
    """Predefined grant sets. Apply to agent on spawn."""
    WORKER = "worker"           # session workspace only, no elevation
    TEAM_LEADER = "team_leader" # project dir + tool suite, no elevation
    ORCHESTRATOR = "orchestrator"  # full project access + elevated where needed
    PENTESTER = "pentester"     # specific pentest tools + network paths
    SANDBOXED = "sandboxed"     # workspace only, deny all tools except approved set
```

**Todos (T15.5)**:
- `perm-grant-manager` — `GrantManager` class: `grant_path`, `revoke_path`, `grant_tool`, `revoke_tool`, `list_grants`, `clear_agent`. Invalidates Redis cache on every write.
- `perm-grant-profiles` — `GrantProfile` enum + `PROFILE_DEFINITIONS` dict mapping profile → list of PathGrant + ToolGrant. Built-in profiles: WORKER, TEAM_LEADER, ORCHESTRATOR, PENTESTER, SANDBOXED.

---

### T15.6 — Wire into Phase 14 Interceptors

The Phase 14 `@pre_hook` system is the enforcement point. No permission check should live inside business logic — it lives in pre-hooks.

```python
# core/permissions/hooks.py
from css.core.events import pre_hook, HookContext, HookErrorStrategy
from .checker import checker  # module-level singleton

@pre_hook("tool.call.*", priority=5)   # runs early — before tool executes
async def enforce_tool_permission(ctx: HookContext) -> HookContext:
    agent_id = ctx.metadata.get("agent_id")
    tool_name = ctx.namespace.split(".", 2)[-1]  # "tool.call.bash.execute" → "bash.execute"
    if agent_id and not await checker.can_tool(agent_id, tool_name):
        raise HookErrorStrategy(f"Tool denied: {tool_name} for agent {agent_id}")
    return ctx

@pre_hook("agent.run.*", priority=5)
async def enforce_workspace_access(ctx: HookContext) -> HookContext:
    agent_id = ctx.metadata.get("agent_id")
    workspace_root = ctx.input.get("kwargs", {}).get("workspace_root")
    if agent_id and workspace_root:
        if not await checker.can_path(agent_id, str(workspace_root), PathOp.READ):
            raise HookErrorStrategy(f"Path access denied: {workspace_root}")
    return ctx
```

**Todos (T15.6)**:
- `perm-hook-tool-enforcement` — `@pre_hook("tool.call.*", priority=5)` in `core/permissions/hooks.py`. Extracts agent_id from HookContext.metadata. Calls `checker.can_tool()`. Raises HookErrorStrategy on deny. Dep: `events-instrument-decorator` (Phase 14) + `perm-checker-can-tool`.
- `perm-hook-path-enforcement` — `@pre_hook("agent.run.*", priority=5)` for workspace path access checks. Dep: `perm-checker-can-path`.

---

### T15.7 — REST Endpoints

```
GET  /permissions/grants/{agent_id}          — list all grants for an agent
POST /permissions/grants/path                — create PathGrant
POST /permissions/grants/tool                — create ToolGrant
DELETE /permissions/grants/path/{grant_id}   — revoke PathGrant
DELETE /permissions/grants/tool/{grant_id}   — revoke ToolGrant
POST /permissions/check/path                 — dry-run: can agent X read /etc/passwd?
POST /permissions/check/tool                 — dry-run: can agent X use bash.execute?
POST /permissions/profiles/apply             — apply a GrantProfile to an agent
```

**Todos (T15.7)**:
- `perm-rest-endpoints` — FastAPI routes in `core/permissions/endpoints.py`. All 8 routes above. Uses `GrantManager` + `PermissionChecker`. Auth: Orchestrator role required for write endpoints.

---

### Clarified Module Boundaries (Final)

| What | Where | Exports |
|------|-------|---------|
| Scope hierarchy (GLOBAL→SESSION) | `@scopes` | `ScopeContext`, `ScopeManager` |
| Can agent X read path Y? | `@permissions` | `PermissionChecker.can_path()` |
| Can agent X use tool Y? | `@permissions` | `PermissionChecker.can_tool()` |
| Can agent X run as sudo? | `@permissions` | `PermissionChecker.can_elevated()` |
| Manage path/tool grants | `@permissions` | `GrantManager` |
| File lifecycle in workspace | `@workspace` | Workspace layer — consumes PathGrant |
| Enforce at every entry point | `@events` (Phase 14) | `@pre_hook` wired to `PermissionChecker` |

**`@scopes` gets REMOVED of all permission logic.** It only answers: "what is the current namespace context?" It never says "is this allowed."

---

### 17 Todos (Phase 15)

| ID | Task | What |
|----|------|------|
| `perm-path-op-flag` | T15.1 | `PathOp(Flag)`: READ, WRITE, EXECUTE, ALL |
| `perm-path-grant-struct` | T15.1 | `PathGrant` msgspec.Struct with glob path_pattern + elevated |
| `perm-tool-grant-struct` | T15.1 | `ToolGrant` msgspec.Struct with deny-wins `allowed` field |
| `perm-grant-models` | T15.2 | `PathGrantRecord` + `ToolGrantRecord` Tortoise ORM models |
| `perm-grant-redis-cache` | T15.2 | `GrantCache`: load/invalidate per-agent, TTL 60s |
| `perm-checker-can-path` | T15.3 | `can_path()` + `require_path()` with glob + expiry |
| `perm-checker-can-tool` | T15.3 | `can_tool()` + `require_tool()` with deny-wins |
| `perm-checker-can-elevated` | T15.3 | `can_elevated()` + `require_elevated()` separate gate |
| `perm-checker-exceptions` | T15.3 | `PermissionDenied` + `ElevationDenied` + `AccessDenied` base |
| `perm-decorator-require-path` | T15.4 | `@require_path(path_or_kwarg, op)` decorator |
| `perm-decorator-require-tool` | T15.4 | `@require_tool(tool_name)` decorator |
| `perm-grant-manager` | T15.5 | `GrantManager`: full CRUD for path + tool grants |
| `perm-grant-profiles` | T15.5 | `GrantProfile` enum + PROFILE_DEFINITIONS dict |
| `perm-hook-tool-enforcement` | T15.6 | `@pre_hook("tool.call.*")` → enforce tool grants |
| `perm-hook-path-enforcement` | T15.6 | `@pre_hook("agent.run.*")` → enforce path grants |
| `perm-scopes-cleanup` | T15.6 | Remove all permission logic from `@scopes` module. `ScopeContext` becomes pure context carrier (no `has_permission()`, no `has_tool_permission()`). |
| `perm-rest-endpoints` | T15.7 | 8 REST endpoints in `endpoints.py` |

**Dependencies**:
- `perm-path-grant-struct` → `perm-path-op-flag`
- `perm-grant-models` → `perm-path-grant-struct`, `perm-tool-grant-struct`
- `perm-grant-redis-cache` → `perm-grant-models`
- `perm-checker-can-path` → `perm-grant-redis-cache`, `perm-checker-exceptions`
- `perm-checker-can-tool` → `perm-grant-redis-cache`, `perm-checker-exceptions`
- `perm-checker-can-elevated` → `perm-grant-redis-cache`, `perm-checker-exceptions`
- `perm-decorator-require-path` → `perm-checker-can-path`
- `perm-decorator-require-tool` → `perm-checker-can-tool`
- `perm-grant-manager` → `perm-grant-models`, `perm-grant-redis-cache`
- `perm-grant-profiles` → `perm-path-grant-struct`, `perm-tool-grant-struct`
- `perm-hook-tool-enforcement` → `perm-checker-can-tool`, `events-instrument-decorator`
- `perm-hook-path-enforcement` → `perm-checker-can-path`, `events-instrument-decorator`
- `perm-scopes-cleanup` → `perm-checker-can-path` (replacement must exist before removing stubs)
- `perm-rest-endpoints` → `perm-grant-manager`, `perm-checker-can-path`, `perm-checker-can-tool`

---

## 📐 Phase 15 Addendum — Simplify to 2-Level Scope Model (GLOBAL + SESSION)

### Decision: Simplify @scopes to 2-Level Model

**Reason**: Multi-tenant SaaS models (GLOBAL→APP→PROJECT→RUNTIME→SESSION) are unnecessary. This is a cybersec tool. The actual scope model is:

1. **GLOBAL** — system-wide settings (config in `~/.css/`)
2. **SESSION** — per-pentest/threat-hunt working context (config in `~/.css/sessions/session-<sid>/`)

Everything else (APP, PROJECT, RUNTIME) is dead weight.

The simplified model:
- `ScopeLevel` enum: ONLY {GLOBAL, SESSION}
- `SessionContext` — plain struct: session_id, agent_id, project_dir, target
- Config cascade: `~/.css/config.yaml` (GLOBAL) → `~/.css/sessions/{session_id}/config.yaml` (SESSION)
- `core/workspace/` — manages the general session/project directory lifecycle

---

### Replacement: SessionContext

NOT a module. A **core primitive** in `css/core/session.py`. Created once per session start, passed as a dependency everywhere.

```python
# css/core/session.py
import msgspec
from pathlib import Path

class SessionContext(msgspec.Struct, frozen=True):
    """Minimal context for one pentest/threat-hunt session.
    
    Created at session start by the workspace layer.
    Does NOT carry permission logic — that is @permissions.
    Does NOT carry a scope hierarchy — there is none.
    """
    session_id: str                        # UUID, unique per engagement
    agent_id: str                          # which agent owns this context
    project_dir: Path                      # absolute path to session working directory
    target: str | None = None             # optional: "threat-xy", "192.168.1.0/24"
    parent_session_id: str | None = None  # set if this is a sub-agent session
```

Replaces: `ScopeContext` (all 7 fields collapse to these 5).
`session_id` field on `PathGrant`/`ToolGrant` — used by grants to scope to a specific session.

---

### `core/workspace/` — Project Dir + General Layout

`WorkspaceRegistry` is the ONLY place that knows directory layout. Other modules never mkdir themselves.

Legacy Phase 15 todo IDs still use the `working-dir-*` prefix for continuity in `session.db`.

**Directory layout created by the workspace layer:**
```
~/.css/sessions/{session_id}/          ← session root (centralized, NOT /workspace/)
├── plan.md                            ← planner mode only
├── findings/                          ← evidence, screenshots, notes
├── artifacts/                         ← tool output (nmap xml, burp exports)
├── tools/                             ← per-session tool configs
└── agents/
    └── {agent_id}/
        ├── scratch/                   ← agent working space
        └── output/                    ← agent results
```

Three modes:
- **`planner`** — full layout above + starter `plan.md` (session_id, target, created_at, empty Objectives)
- **`search`** — minimal: `findings/` + `artifacts/` only. Used for "hunt threat-xy" tasks
- **`minimal`** — just the session root dir, no sub-structure

Workspace creation ALSO registers the **only automatic PathGrant**:
- `agent_id → ~/.css/sessions/{session_id}/** → READ+WRITE`
- Everything outside this dir: DENIED by default

---

### Least Privilege: Full Flow (copy-pasteable for any LLM implementing this)

Default state for a NEW agent: **zero path access beyond session dir, zero tool access**.

```
STEP 1: WorkspaceRegistry.create_session_workspace(session_id, agent_id, target, mode="planner")
  → creates ~/.css/sessions/{session_id}/ + subdirs based on mode
  → calls grant_manager.grant_path(agent_id, f"{session_dir}/**", {READ,WRITE}, session_id)
  → returns SessionContext(session_id, agent_id, project_dir, target)

STEP 2: Agent starts. Every tool call hits @pre_hook("tool.call.*", priority=5)
  → PermissionChecker.can_tool(agent_id, tool_name) is called
  → Agent has ZERO ToolGrants by default → all tools DENIED

STEP 3: Orchestrator grants tools explicitly before agent can act:
  grant_tool(agent_id, "file.read")
  grant_tool(agent_id, "file.write")
  grant_tool(agent_id, "bash.execute")
  grant_tool(agent_id, "network.scan")
  OR shortcut: apply_profile(agent_id, GrantProfile.PENTESTER)

STEP 4: If agent needs to read outside session_dir (e.g. /etc/hosts):
  grant_path(agent_id, "/etc/hosts", {READ}, session_id=session_id)
  Without this explicit grant: PermissionDenied raised by pre_hook.

STEP 5: If agent needs root/sudo for a path:
  grant_path(agent_id, "/usr/bin/nmap", {EXECUTE}, elevated=True, session_id=session_id)
  Agent must pass BOTH can_path(..., EXECUTE) AND can_elevated(...) checks.
```

---

### @scopes Simplification — Which Files to Touch

2-level scope model requires these updates:

| File | Current State | Fix |
|------|---------------|-----|
| `/enums.py` | ScopeLevel = {GLOBAL, APP, PROJECT, RUNTIME, SESSION} | Keep ONLY {GLOBAL, SESSION}, delete APP/PROJECT/RUNTIME |
| `/context.py` | ScopeContext requires project_id for multi-tenant | Simplify: accept ONLY scope_level in [GLOBAL, SESSION], remove project_id requirement |
| `/manager.py` | Full 5-level hierarchy + path resolution | Simplify for 2-level: no inheritance chain needed |
| `core/permissions/` | Uses `ScopeLevel` + `scope_id` field | Replace ALL `scope_id` → `session_id: str`, remove ScopeLevel dependency |
| `streaming/options_manager.py` | Imports 3-layer config from @scopes | Add local `ConfigLayer(str,Enum)` = {GLOBAL, SESSION} — NOT from @scopes |

Simplification order:
1. Update `/enums.py` — ScopeLevel = {GLOBAL, SESSION} only
2. Update `/context.py` — Simplify validation for 2-level model
3. Update `/manager.py` — Remove inheritance logic
4. Rename `scope_id` → `session_id` in all @permissions types + models
5. Fix `streaming/options_manager.py` with local `ConfigLayer` enum (GLOBAL, SESSION only)
6. Note: Keep `/` directory (GLOBAL scope still exists for config); just simplified to 2 levels

---

### New Todos (Phase 15 Addendum — 9 todos)

These IDs are legacy names. Interpret every `working-dir-*` todo as work on `core/workspace/`.

| ID | Task | Description |
|----|------|-------------|
| `session-context-create` | Create SessionContext | Create `css/core/session.py`. Define `SessionContext(msgspec.Struct, frozen=True)` with fields: session_id:str, agent_id:str, project_dir:Path, target:str\|None=None, parent_session_id:str\|None=None. No logic, just the struct. |
| `working-dir-manager` | WorkspaceRegistry session workspace creation | Create `core/workspace/registry.py`. Async method `create_session_workspace(session_id, agent_id, target, mode)` that: (1) mkdir session_dir, (2) applies the layout fn based on mode, (3) grants `READ+WRITE` for the session tree, (4) returns `SessionContext`. |
| `working-dir-planner-layout` | Planner workspace layout | Create planner layout helper in `core/workspace/layouts.py`. Creates: findings/, artifacts/, tools/, agents/{agent_id}/scratch/, agents/{agent_id}/output/. Writes starter `plan.md`. |
| `working-dir-search-layout` | Search workspace layout | Create search layout helper in `core/workspace/layouts.py`. Creates findings/ and artifacts/ only. No plan.md. |
| `working-dir-agent-subdir` | Per-agent workspace handle | Add helper that provisions `agents/{agent_id}/scratch/` and `agents/{agent_id}/output/` inside the session workspace and returns the agent-scoped handle. |
| `working-dir-cleanup` | Session workspace cleanup | Add workspace cleanup/release flow for a session. If `keep_findings=True`, archive findings before removing the session tree. |
| `perm-rename-scope-to-session` | Rename scope_id to session_id | In core/permissions/ only: rename field `scope_id` → `session_id` on PathGrant, ToolGrant, PathGrantRecord, ToolGrantRecord, and all PermissionChecker method signatures. Update GrantCache key from "perm:agent:{id}" to "perm:agent:{id}" (key unchanged, just field rename). |
| `streaming-decouple-from-scopes` | Remove scopes import from streaming | In `streaming/options_manager.py`: add local `ConfigLayer(str, Enum)` enum at top of file with values GLOBAL="global", SESSION="session". Replace any `ScopeLevel` reference with `ConfigLayer`. No import from @scopes. Remove PROJECT entirely. |
| `scopes-module-simplify` | Simplify @scopes to 2-level | After `perm-rename-scope-to-session` and `streaming-decouple-from-scopes`: (1) update enums.py ScopeLevel to {GLOBAL, SESSION}, (2) simplify context.py validation, (3) simplify manager.py for 2-level model. Keep directory (GLOBAL scope config). |

**Dependencies for new todos:**
- `working-dir-manager` → `session-context-create`, `perm-grant-manager`
- `working-dir-planner-layout` → `working-dir-manager`
- `working-dir-search-layout` → `working-dir-manager`
- `working-dir-agent-subdir` → `working-dir-manager`
- `working-dir-cleanup` → `working-dir-manager`
- `perm-rename-scope-to-session` → `perm-path-grant-struct`, `perm-tool-grant-struct`
- `scopes-module-simplify` → `perm-rename-scope-to-session`, `streaming-decouple-from-scopes`

---

## 🔬 Phase 16 — Provider-Specific Advanced Features (SDK Capability Audit)

**Source**: Deep inspection of `.venv/lib/python3.14/site-packages/` — all installed AI SDKs  
**Updated**: 2026-05-04  
**SDKs inspected**: anthropic 0.84.0 · openai 2.26.0 · groq 1.0.0 · cohere 5.20.7 · mistralai 1.12.4 · together 2.3.0 · fireworks_ai 0.19.20 · ai21 4.3.0 · ollama 0.6.1 · openrouter 0.7.11 · google-generativeai 0.8.6 · claude_agent_sdk 0.1.61 · deepinfra 0.1.0

---

### T16.1 — Extended Thinking / Reasoning Modes

**What was found:**

| Provider | SDK feature | How to enable |
|----------|-------------|---------------|
| **Anthropic** | `ThinkingConfigEnabledParam(type="enabled", budget_tokens=N)` | Pass as `thinking=` in `messages.create()`. Also: `beta_thinking_turns_param` for multi-turn thinking |
| **OpenAI** | `reasoning: Reasoning(effort="low"\|"medium"\|"high", encrypted_content=True)` | Only on o-series (o1/o3/o4) and gpt-5. `encrypted_content` lets reasoning items be passed back for continuity |
| **Anthropic beta** | `BetaThinkingConfigEnabledParam` + `BetaRedactedThinkingBlock` | Thinking can be redacted (content hidden from user) but still counted |

**Design:**
- Add `thinking: ThinkingConfig | None = None` field to `LLMAdapter.complete()` and `LLMAdapter.stream()`  
- `ThinkingConfig(msgspec.Struct)`: `budget_tokens: int | None = None`, `effort: Literal["low","medium","high"] | None = None`  
- Adapter dispatches to provider-specific format: budget_tokens → Anthropic, effort → OpenAI o-series  
- In `@llm_models`: mark models as `supports_thinking=True` in `ModelMetadata`  
- In routing (Phase 13): tier S+ models should default `thinking=ThinkingConfig(budget_tokens=8000)` for complex tasks  
- Expose: `completion(messages, thinking=ThinkingConfig(effort="high"))` in UnifiedLLMClient

**Todos:** `T16.1` (3 todos)

---

### T16.2 — Pre-flight Token Counting

**What was found:**

| Provider | SDK feature |
|----------|-------------|
| **Anthropic** | `messages.count_tokens(model, messages, system, tools)` → `MessageTokensCount(input_tokens=N)`. No API call charge. |
| **OpenAI** | `responses.input_tokens.create(model, input)` → `{input_tokens: N}` |
| **Cohere** | `tokenize(text, model)` + `detokenize(tokens, model)` |
| **Ollama** | Returns `prompt_eval_count` in every response (token count in result) |

**Design:**
- Add `estimate_tokens(messages, model, provider) -> int` to `UnifiedLLMClient`  
- Anthropic: call SDK `count_tokens()` directly (free)  
- OpenAI: call `input_tokens.create()` (may cost)  
- Others: use tiktoken / provider tokenizer heuristics  
- Use in routing (Phase 13) to detect context overflow before routing to tier  
- Use in cache (Phase 11) for L5 cache eligibility check (min 1024 tokens to be worth caching)  
- Surface in `TokenUsage.estimated_input_tokens` field before actual call

**Todos:** `T16.2` (2 todos)

---

### T16.3 — Async Batch APIs

**What was found:**

| Provider | SDK feature |
|----------|-------------|
| **Anthropic** | `messages.batches.create(requests=[MessageCreateParamsNonStreaming...])` → `MessageBatch`. Poll with `batches.retrieve(id)` or stream results with `batches.results(id)` |
| **OpenAI** | `batches.create(input_file_id, endpoint, completion_window)` → `Batch`. Poll `batches.retrieve(id)` |
| **Together** | `batches.py` — similar pattern |

**Design:**
- Add `BatchAdapter` protocol to `LLMAdapter`: `batch_complete(requests) → BatchJob`  
- `BatchJob(msgspec.Struct)`: `batch_id: str`, `provider: str`, `status: Literal["pending","in_progress","done","failed"]`, `created_at: datetime`  
- Use in: scanning hundreds of CVEs in parallel, bulk threat-intel classification, offline eval runs  
- `@tasks` module: `DispatchBatch` command → creates BatchJob, polls with webhook or polling loop  
- Cost: ~50% cheaper than realtime on Anthropic; 50% cheaper on OpenAI  

**Todos:** `T16.3` (3 todos)

---

### T16.4 — Anthropic Native Tool Suite (Beta)

**What was found** (all in `anthropic/types/beta/` and `anthropic/types/`):

| Tool type | Param class | Use case |
|-----------|-------------|----------|
| **Computer use** | `BetaToolComputerUse20251124Param(display_width_px, display_height_px, type="computer_20251124")` | GUI automation, web app testing |
| **Code execution** | `CodeExecutionTool20260120Param` + `BetaCodeExecutionTool20260120Param` | Sandboxed Python/JS execution |
| **Web search** | `WebSearchTool20260209Param(type, max_uses)` | Live OSINT from model |
| **Web fetch** | `WebFetchTool20260209Param(type, allowed_domains)` | Fetch specific URLs |
| **BM25 search** | `ToolSearchToolBm2520251119Param(data_source_id, ...)` | Keyword search over loaded docs |
| **Regex search** | `ToolSearchToolRegex20251119Param(data_source_id, ...)` | Regex search over loaded docs |
| **Bash tool** | `BetaToolBash20250124Param` | Shell execution (with ToolGrant required!) |
| **Text editor** | `BetaToolTextEditor20250728Param` | File editing by model |

**Design:**
- Register all Anthropic native tools in `@tools` registry as `BuiltinTool` variants  
- Wire through `@permissions`: each requires explicit `ToolGrant` — no auto-grants  
- `computer_use`: requires `can_tool("anthropic.computer_use")` + `PathGrant(display screen)`  
- `code_execution`: requires `can_tool("anthropic.code_execution")` + container isolation  
- `web_search` / `web_fetch`: requires `can_tool("anthropic.web_search")` (OSINT sessions: auto-granted)  
- `bash_tool`: requires `can_tool("bash.execute")` (existing ToolGrant)  
- Each maps to a `BuiltinToolGrantProfile` so orchestrator can grant them as a group  
- Event hooks (Phase 14): fire `TOOL_BEFORE` / `TOOL_AFTER` for each execution  

**Todos:** `T16.4` (4 todos)

---

### T16.5 — Context Lifecycle Management

**What was found:**

| Feature | SDK location | Description |
|---------|-------------|-------------|
| **CompactionControl** | `anthropic/lib/tools/_beta_compaction_control.py` | Auto-compress context when `context_token_threshold` is exceeded. Uses a configurable `summary_prompt` to generate a continuation summary. Default threshold: 100,000 tokens |
| **ContextManagementConfig edits** | `anthropic/types/beta/beta_context_management_config_param.py` | Manual edits: `BetaClearToolUses20250919EditParam` (remove old tool calls), `BetaClearThinking20251015EditParam` (remove thinking blocks), `BetaCompact20260112EditParam` (compress) |
| **OpenAI `compact()`** | `openai/resources/responses/responses.py` | Compact a stateful Responses API conversation |
| **Default compaction prompt** | `_beta_compaction_control.py::DEFAULT_SUMMARY_PROMPT` | 5-section continuation summary: Task Overview, Current State, Important Discoveries, Next Steps, Context to Preserve |

**Design:**
- Add `context_mgmt: ContextManagementConfig | None` field to `LLMAdapter`  
- `ContextManagementConfig(msgspec.Struct)`: `auto_compact_at_tokens: int = 100_000`, `clear_thinking_on_compact: bool = True`, `custom_summary_prompt: str | None = None`  
- Anthropic: map to `CompactionControl` + `BetaContextManagementConfigParam`  
- OpenAI Responses API: call `.compact()` when threshold reached  
- Default: auto-compact ON for all sessions > 50K tokens (less than Anthropic default)  
- Hook point: fire `EVENT_CONTEXT_COMPACTED` event when compaction happens → log to OTEL  
- Config in `session metadata.json`: `context_mgmt: {auto_compact_at_tokens: 80000}`  

**Todos:** `T16.5` (2 todos)

---

### T16.6 — OpenAI Stateful Responses API + Background Mode

**What was found:**

```
openai/resources/responses/responses.py:
  .create(background=True)     → response_id for polling
  .retrieve(response_id)       → get status/result
  .cancel(response_id)         → cancel background job
  .delete(response_id)         → cleanup
  .compact(response_id)        → compress conversation
  .connect(response_id)        → WebSocket stream of background job
  input_items.list(response_id) → list conversation turns
  input_tokens.create(...)     → token count estimate
```

**`background=True`** starts an async response job. Poll it later, or stream via WebSocket. Ideal for: full codebase audit, multi-hour analysis, running while user is offline.

**Design:**
- Add `BackgroundJob(msgspec.Struct)` to `@tasks`: `job_id: str`, `provider: str`, `status`, `response_id: str`  
- `DispatchBackground` command: creates a background OpenAI response, stores `response_id` in DB  
- Background poller: AsyncIO task that polls `responses.retrieve(response_id)` every N seconds  
- On completion: fire `EVENT_TASK_COMPLETE` with result  
- Map OpenAI `response_id` ↔ CSS `task_id` in `session.tasks` table  
- Expose in `UnifiedLLMClient.complete_background(...)` → `BackgroundJob`  

**Todos:** `T16.6` (2 todos)

---

### T16.7 — Rerank + Classify Pipeline Stages

**What was found:**

| Provider | Feature | Use in cybersec |
|----------|---------|-----------------|
| **Cohere** | `rerank(query, documents, model="rerank-v3.5")` → `RerankResponse(results=[{index, relevance_score}])` | Sort 50 CVE descriptions by relevance to a specific target system |
| **Cohere** | `classify(inputs, examples)` → `ClassifyResponse(classifications=[{input, prediction, confidence}])` | Auto-classify findings as Critical/High/Medium/Low |
| **Together** | `rerank.create(query, documents, model)` | Alternative reranker |
| **OpenAI** | (built into embeddings + vector stores) | Semantic search |

**Design:**
- Add `RerankAdapter` + `ClassifyAdapter` protocols to `@tools` or new `@retrieval` module  
- Surface in pipeline: after tool results, run `rerank(query=task_objective, documents=findings)` to sort  
- `classify()` useful for: auto-severity on vuln findings, auto-tag tool output  
- Cache rerank scores in @cache (L3 PostgreSQL) keyed by `(query_hash, doc_hashes)`  
- Wire into OTEL: `rerank_latency_ms`, `rerank_provider`, `rerank_top_score`  

**Todos:** `T16.7` (2 todos)

---

### T16.8 — Gemini Persistent Context Caching

**What was found:**

```python
# google/generativeai/caching.py
class CachedContent:
    # Create cached content for repeated use
    # Fields: name, model, display_name, system_instruction,
    #         contents, tools, tool_config, expire_time, ttl, usage_metadata
```

Gemini allows uploading a large document/system prompt once and getting a `CachedContent` name. All subsequent calls reference `cached_content=name` → dramatically cheaper for repeated context.

**Different from our L5 cache**: This is *server-side* caching at Google's infra level, not client-side. The context is stored on Gemini servers with a TTL.

**Design:**
- In `api_services/gemini/`: add `GeminiCacheManager` with `create_cache(contents, ttl) → str` (cached_content name)  
- Store `cached_content_name` in our L5 cache entry under `provider_cache_id`  
- Invalidation: TTL-driven on Gemini side; our L5 cache tracks expiry  
- Use for: large codebase context, shared system prompts across many agents  
- `ContextCacheEntry(msgspec.Struct)`: `provider=Literal["gemini"]`, `provider_cache_id: str`, `expires_at: datetime`, `token_count: int`  

**Todos:** `T16.8` (2 todos)

---

### T16.9 — Anthropic Memory Tool (Custom Backend)

**What was found:**

```python
# anthropic/lib/tools/_beta_builtin_memory_tool.py
class BetaAbstractMemoryTool(BetaBuiltinFunctionTool):
    """Subclass this to create your own memory storage solution."""
    def view(self, command: BetaMemoryTool20250818ViewCommand) -> ...: ...
    def create(self, command: BetaMemoryTool20250818CreateCommand) -> ...: ...
    def insert(self, command: BetaMemoryTool20250818InsertCommand) -> ...: ...
    def str_replace(self, command: BetaMemoryTool20250818StrReplaceCommand) -> ...: ...
    def delete(self, command: BetaMemoryTool20250818DeleteCommand) -> ...: ...
    def rename(self, command: BetaMemoryTool20250818RenameCommand) -> ...: ...
```

This is a **pluggable memory backend** for Claude. The model calls these methods to store/retrieve notes across a session. You implement the storage layer.

**Design:**
- Implement `CSSMemoryTool(BetaAbstractMemoryTool)` in the core-owned memory domain  
- Storage: use `@memory` module's existing store (PostgreSQL or Redis)  
- `view` → `MemoryStore.get_notes(agent_id, session_id)`  
- `create/insert/str_replace/delete` → corresponding MemoryStore mutations  
- Pass `CSSMemoryTool()` in tool list when `session_mode=development` or when agent has `ToolGrant("anthropic.memory_tool")`  
- Bridge to our `@events`: fire `EVENT_MEMORY_WRITTEN` on create/insert  

**Todos:** `T16.9` (2 todos)

---

### T16.10 — Ollama Model Lifecycle Management

**What was found:**

```python
# ollama/_client.py
ollama.pull(model, stream=True)          # Download model (with progress)
ollama.push(model, stream=True)          # Upload to registry
ollama.create(model, modelfile, stream)  # Create from Modelfile
ollama.create_blob(path)                 # Upload binary blob
ollama.list()                            # List installed models
ollama.delete(model)                     # Remove model
ollama.copy(source, dest)                # Duplicate model
ollama.show(model)                       # Model info + Modelfile
ollama.embed(model, input)              # Embeddings
```

**Design:**
- Add `OllamaModelManager` to `core/models/`  
- Methods: `pull(model_name) → AsyncIterator[PullProgress]`, `list() → list[ModelInfo]`, `delete(model_name)`, `is_available(model_name) → bool`  
- Auto-pull on first use: if tier 10 (qwen3-0.6B) not present, auto-pull before routing  
- Progress streaming: emit `EVENT_MODEL_DOWNLOAD_PROGRESS` events (useful for UI)  
- `is_available()` used by router (Phase 13) to skip Ollama tier if model not installed  
- `ModelInfo` cached in @cache L1 (in-memory), refreshed on `list()` call  

**Todos:** `T16.10` (2 todos)

---

### T16.11 — OpenRouter Per-Generation Cost Tracking

**What was found:**

```python
# openrouter/analytics.py
openrouter.analytics.get_user_activity()   # per-day usage stats
# openrouter/credits.py
openrouter.credits.get_credits()           # remaining credits
# openrouter/generations.py
openrouter.generations.get_generation(generation_id)  # per-call cost metadata
# openrouter/providers.py
openrouter.providers.list()                # all available providers + models
```

OpenRouter returns a `generation_id` with each response. Use it to fetch exact cost, latency, provider used.

**Design:**
- In `api_services/openrouter/response.py`: capture `generation_id` from response headers  
- Fire `EVENT_LLM_COMPLETE` with `generation_id` in attributes  
- Background poller: after response, async-fetch `get_generation(id)` → attach cost to OTEL span  
- `OtelBridge`: add `llm.cost_usd`, `llm.actual_provider`, `llm.generation_id` to span attributes  
- In `@cache` (L3): store cost per request for billing aggregation  
- Expose: `GET /api/sessions/{id}/cost` endpoint that sums OTEL cost attributes  

**Todos:** `T16.11` (2 todos)

---

### T16.12 — Mistral OCR + Agents + FIM

**What was found:**

| Feature | Method | Use case |
|---------|--------|----------|
| **OCR** | `mistral.ocr.process(model="mistral-ocr-latest", document=...)` | Parse PDFs/images of security reports, network diagrams, certificates |
| **FIM** | `mistral.fim.complete(prompt, suffix, model="codestral-latest")` | Fill-in-middle code completion for exploit writing/patching |
| **Agents API** | `mistral.agents.create/list/get/update/delete` with versions+aliases | Persistent Mistral agent definitions |
| **Agent handoff** | `AgentHandoffStartedEvent` / `AgentHandoffDoneEvent` | Multi-agent workflows on Mistral platform |

**Design:**
- OCR: add `OcrAdapter` protocol to `@tools`. Mistral implements it. Input: `Path | URL | bytes`. Output: `OcrResult(text, pages, confidence)`  
- FIM: add `fim_complete(prompt, suffix, stop) → str` to `LLMAdapter` protocol. Only implemented by Mistral (Codestral) and Fireworks (similar)  
- Mistral Agents: map to our `@agents` module's agent definitions. Can serialize/restore  

**Todos:** `T16.12` (2 todos)

---

### T16.13 — Groq Audio (Ultra-fast Transcription)

**What was found:**

```
groq/resources/audio/transcriptions.py  → .create(file, model="whisper-large-v3")
groq/resources/audio/translations.py    → .create(file, model, target_language)
groq/resources/audio/speech.py          → .create(model, input, voice)
```

Groq runs Whisper at ~250 tokens/second — fastest available transcription.

**Design:**
- Add `AudioAdapter` protocol: `transcribe(file: Path | bytes, language: str | None) → str`  
- `translate(file, target_language) → str`  
- Groq implements both. OpenAI also supports  
- Use case: transcribe intercepted VoIP, voice commands in red team, security briefings  
- Register as `BuiltinTool("audio.transcribe")` requiring `ToolGrant("audio.transcribe")`  

**Todos:** `T16.13` (1 todo)

---

### T16.14 — Claude Agent SDK Hook Bridge

**What was found** in `claude_agent_sdk/types.py`:

```python
# These are the EXACT same hooks we're designing in Phase 14!
PreToolUseHookInput          # before any tool call → can block/modify
PostToolUseHookInput         # after tool call succeeded
PostToolUseFailureHookInput  # after tool call failed
UserPromptSubmitHookInput    # when user sends message
StopHookInput                # when agent is about to stop
SubagentStartHookInput       # when subagent spawns
SubagentStopHookInput        # when subagent exits
PreCompactHookInput          # before context compaction
NotificationHookInput        # async notification
PermissionRequestHookInput   # permission gate → can return Allow or Deny
```

And session management:
```python
fork_session(session_id)     # branch agent state
delete_session(session_id)
rename_session(session_id)
tag_session(session_id, tags)
list_subagents(session_id)
get_subagent_messages(session_id, subagent_id)
```

**Design:**
- `claude_agent_sdk` hooks are fire-and-modify (interceptors), exactly what our Phase 14 interceptors cover  
- Create `CSSHookBridge` in `core/events/`: maps our `@events` interceptor protocol to `claude_agent_sdk`'s hook format  
- This means when using `claude_agent_sdk` as a backend, hooks registered in our `@events` module automatically wire in  
- `PermissionRequestHookInput` → maps to our `@permissions.can_tool()` check  
- `PreToolUseHookInput` → our `INTERCEPTOR_BEFORE_TOOL` event  
- `PostToolUseHookInput` → our `INTERCEPTOR_AFTER_TOOL` event  
- Session ops (`fork_session`, `tag_session`) → map to `@tasks` `ForkSession` / `TagSession` commands  
- This is NOT re-implementing — it's a bridge so CSS sessions work with claude_agent_sdk sessions  

**Todos:** `T16.14` (2 todos)

---

### T16.15 — xAI Provider Completion

`api_services/xai/service.py` still has two hard TODOs in executable code:

- `_default_base_url()` must resolve from the provider config source of truth instead of returning a stub
- `get_models()` must return concrete `ModelMetadata` so xAI participates in startup seeding and provider discovery like the other OpenAI-compatible adapters

**Todos:** `T16.15` (2 todos)

---

### Phase 16 New Todos Summary

| ID | Task | Description | Deps |
|----|------|-------------|------|
| `thinking-config-struct` | ThinkingConfig struct | Add `ThinkingConfig(msgspec.Struct)` to `core/types/`. Fields: `budget_tokens:int\|None`, `effort:Literal["low","medium","high"]\|None`. |  |
| `thinking-config-adapter` | LLMAdapter thinking support | Add `thinking: ThinkingConfig \| None = None` to `LLMAdapter.complete()` and `LLMAdapter.stream()`. Anthropic adapters map to `ThinkingConfigEnabledParam`. OpenAI adapters map to `Reasoning(effort=...)`. Other adapters ignore. | `thinking-config-struct` |
| `thinking-model-metadata` | Mark models as thinking-capable | In `@llm_models` ModelMetadata: add `supports_thinking: bool = False`, `max_thinking_tokens: int \| None = None`. Mark claude-opus-4/sonnet-4, o1/o3/o4/gpt-5 appropriately. | `thinking-config-adapter` |
| `token-count-method` | UnifiedLLMClient.estimate_tokens() | Add `estimate_tokens(messages, model, provider) → int` to `UnifiedLLMClient`. Anthropic: call `messages.count_tokens()`. OpenAI: call `responses.input_tokens.create()`. Others: character-based heuristic (chars/4). |  |
| `token-count-in-routing` | Use token count in router | In Phase 13 router: call `estimate_tokens()` before routing. If estimate > model.context_window * 0.9: route to model with larger window or trigger compaction. | `token-count-method` |
| `batch-api-protocol` | BatchAdapter protocol | Add `BatchAdapter` protocol to `core/types/`. Methods: `batch_complete(requests: list[CompletionRequest]) → BatchJob`. `BatchJob(msgspec.Struct)`: `batch_id, provider, status, result_url`. |  |
| `batch-api-anthropic` | Anthropic batch implementation | Implement `BatchAdapter` for Anthropic: calls `messages.batches.create()`. Poll `batches.retrieve(id)`. Stream results via `batches.results(id)`. Emit `EVENT_BATCH_COMPLETE`. | `batch-api-protocol` |
| `batch-api-openai` | OpenAI batch implementation | Implement `BatchAdapter` for OpenAI: calls `batches.create()`. Poll `batches.retrieve(id)`. Emit `EVENT_BATCH_COMPLETE`. | `batch-api-protocol` |
| `native-tools-registry` | Anthropic native tools registration | Register Anthropic beta tools in `@tools` registry as `BuiltinTool` variants: `anthropic.computer_use`, `anthropic.code_execution`, `anthropic.web_search`, `anthropic.web_fetch`, `anthropic.bash_tool`, `anthropic.text_editor`. Each requires explicit `ToolGrant`. |  |
| `native-tools-permissions` | ToolGrant profiles for native tools | Add `GrantProfile.OSINT_AGENT` (grants web_search + web_fetch), `GrantProfile.CODE_AGENT` (grants code_execution + bash_tool). Wire into Phase 15 permission system. | `native-tools-registry`, `perm-grant-manager` |
| `native-tools-hooks` | Event hooks for native tool calls | Wire `INTERCEPTOR_BEFORE_TOOL` and `INTERCEPTOR_AFTER_TOOL` events to fire for all Anthropic native tool invocations. | `native-tools-registry` |
| `native-tools-computer-use` | Computer use session isolation | Computer use tool requires isolated display (Xvfb or container). Add `ComputerUseConfig` to session metadata: `display: str`, `width: int`, `height: int`. Guard with separate `ToolGrant("anthropic.computer_use")`. | `native-tools-permissions` |
| `context-mgmt-struct` | ContextManagementConfig struct | Add `ContextManagementConfig(msgspec.Struct)` to `core/types/`. Fields: `auto_compact_at_tokens: int = 100_000`, `clear_thinking_on_compact: bool = True`, `custom_summary_prompt: str \| None = None`. |  |
| `context-mgmt-adapter` | LLMAdapter context management | Add `ctx_mgmt: ContextManagementConfig \| None` to `LLMAdapter`. Anthropic: use `CompactionControl` from `lib/tools/_beta_compaction_control.py`. OpenAI Responses: call `.compact()` when threshold reached. Fire `EVENT_CONTEXT_COMPACTED` on trigger. | `context-mgmt-struct` |
| `background-job-struct` | BackgroundJob struct | Add `BackgroundJob(msgspec.Struct)` to `core/types/`: `job_id, provider, response_id, status, created_at`. Add `DispatchBackground` command to `@tasks`. |  |
| `background-job-openai` | OpenAI background response impl | In `api_services/openai/`: implement `complete_background()` using `responses.create(background=True)`. Store `response_id`. Background poller: `asyncio.create_task` polling `responses.retrieve()`. On done: emit `EVENT_TASK_COMPLETE`. | `background-job-struct` |
| `rerank-adapter` | RerankAdapter protocol | Add `RerankAdapter` protocol to `core/types/`. Method: `rerank(query: str, documents: list[str], model: str) → list[tuple[int, float]]` (index, score). Cohere + Together implement. |  |
| `rerank-cohere` | Cohere rerank implementation | Implement `RerankAdapter` using `cohere.v2.rerank()`. Cache results in @cache L3. Emit `EVENT_RERANK_DONE` with `top_score, latency_ms, provider`. | `rerank-adapter` |
| `gemini-cache-manager` | GeminiCacheManager | Add `GeminiCacheManager` to `api_services/gemini/`. Methods: `create_cache(contents, ttl_seconds) → str`, `get_cache(name) → CachedContent`, `delete_cache(name)`. Store cache names in @cache L3 with TTL. |  |
| `gemini-cache-adapter` | Use Gemini cache in L5 | In `@cache` L5 handler for Gemini: check for existing `CachedContent` before creating new one. Pass `cached_content_name` in model call. Track `provider_cache_id` in `CacheEntry`. | `gemini-cache-manager` |
| `memory-tool-bridge` | CSSMemoryTool implementation | Implement `CSSMemoryTool(BetaAbstractMemoryTool)` in the core-owned memory domain. Bridge view/create/insert/str_replace/delete/rename to `MemoryStore` operations. Fire `EVENT_MEMORY_WRITTEN` on mutations. |  |
| `memory-tool-grant` | Memory tool permission | Add `ToolGrant("anthropic.memory_tool")` to `GrantProfile.DEVELOPMENT_AGENT`. `CSSMemoryTool()` added to tool list only when this grant is present. | `memory-tool-bridge`, `perm-grant-manager` |
| `ollama-model-manager` | OllamaModelManager | Add `OllamaModelManager` to `core/models/`. Methods: `pull(model_name, stream=True)`, `list() → list[ModelInfo]`, `delete(model_name)`, `is_available(model_name) → bool`. Auto-pull S10 model if not installed. Emit `EVENT_MODEL_DOWNLOAD_PROGRESS`. |  |
| `ollama-router-check` | Router skips unavailable Ollama models | In Phase 13 router: before routing to Ollama tier, call `OllamaModelManager.is_available()`. If False: auto-pull (if config allows) or skip to next tier. | `ollama-model-manager` |
| `openrouter-cost-tracking` | OpenRouter generation cost tracking | In `api_services/openrouter/response.py`: capture `X-Generation-ID` response header. After response: async-fetch `generations.get_generation(id)`. Attach `llm.cost_usd`, `llm.actual_provider` to OTEL span via OtelBridge. |  |
| `openrouter-provider-list` | Dynamic OpenRouter provider list | In `api_services/openrouter/`: add `list_providers() → list[ProviderInfo]`. Cache in @cache L2 (Redis, TTL=1h). Use in `@llm_models` to keep OpenRouter model list fresh. | `openrouter-cost-tracking` |
| `mistral-ocr-adapter` | OcrAdapter protocol + Mistral impl | Add `OcrAdapter` protocol to `core/types/`. Method: `ocr(document: Path \| bytes \| str) → OcrResult`. `OcrResult(msgspec.Struct)`: `text: str, pages: list[str], confidence: float \| None`. Implement using `mistral.ocr.process()`. |  |
| `mistral-fim-adapter` | FIM fill-in-middle support | Add `fim_complete(prompt, suffix, stop, model) → str` to `LLMAdapter` (optional method, default raises `NotImplementedError`). Mistral implements via `mistral.fim.complete()`. Mark models as `supports_fim=True` in `ModelMetadata`. | `thinking-config-adapter` |
| `groq-audio-adapter` | AudioAdapter protocol + Groq impl | Add `AudioAdapter` protocol to `core/types/`. Methods: `transcribe(file, language) → str`, `translate(file, target) → str`. Groq implements via `audio.transcriptions.create(model="whisper-large-v3")`. Register as `BuiltinTool("audio.transcribe")` requiring `ToolGrant`. |  |
| `claude-sdk-hook-bridge` | CSSHookBridge for claude_agent_sdk | Add `CSSHookBridge` to `core/events/`. Maps `claude_agent_sdk` hook callbacks to CSS event interceptors: `PreToolUseHookInput` → `INTERCEPTOR_BEFORE_TOOL`, `PermissionRequestHookInput` → `@permissions.can_tool()`, etc. |  |
| `claude-sdk-session-bridge` | Claude SDK session operations | Map `claude_agent_sdk` session ops to CSS session ops: `fork_session()` → `@tasks ForkSession`, `tag_session()` → session metadata update, `list_subagents()` → `@agents list` for session. | `claude-sdk-hook-bridge` |
| `xai-config-base-url-yaml` | Load xAI base URL from provider config | Replace the xAI adapter base-url stub with a lookup from the provider YAML/config source of truth so the service does not drift from registry metadata. |  |
| `xai-get-models-list` | Implement xAI model metadata listing | Replace the xAI `get_models()` stub with concrete `ModelMetadata` generation or fetch logic compatible with startup seeding and provider discovery. | `xai-config-base-url-yaml` |

---

### Phase 16 Implementation Priority

**Implement in order** (each group is independent, order within group is by dependency):

**Group A — Core reasoning/tokens (implement first, foundational):**
1. `thinking-config-struct` → `thinking-config-adapter` → `thinking-model-metadata`
2. `token-count-method` → `token-count-in-routing`
3. `context-mgmt-struct` → `context-mgmt-adapter`

**Group B — Batch + Background (high value, low coupling):**
4. `batch-api-protocol` → `batch-api-anthropic` + `batch-api-openai`
5. `background-job-struct` → `background-job-openai`

**Group C — Native tools (requires Phase 15 permissions done first):**
6. `native-tools-registry` → `native-tools-permissions` → `native-tools-hooks` → `native-tools-computer-use`

**Group D — Semantic pipeline (independent):**
7. `rerank-adapter` → `rerank-cohere`
8. `gemini-cache-manager` → `gemini-cache-adapter`
9. `memory-tool-bridge` → `memory-tool-grant`

**Group E — Model management (independent):**
10. `ollama-model-manager` → `ollama-router-check`
11. `openrouter-cost-tracking` → `openrouter-provider-list`

**Group F — Misc adapters (independent):**
12. `mistral-ocr-adapter`
13. `mistral-fim-adapter`
14. `groq-audio-adapter`

**Group G — SDK bridges (requires Phase 14 done first):**
15. `claude-sdk-hook-bridge` → `claude-sdk-session-bridge`



---

## 🏗️ Phase 17 — Settings & Projects Modules

**Goal**: Two new DB-backed modules — `@settings` (runtime configuration registry connected to the frontend) and `@projects` (project registration + session linking). Together they replace the static `config.py` bootstrap as the live source of truth for all runtime configuration.

**Context**: `config.py` is a flat env-var bootstrap (startup defaults only). `@settings` adds a DB-backed layer on top with registry pattern, scopes, REST API, and frontend integration. `@projects` implements the `ProjectManager` designed in `filesystem-layout.md` — registered references to source dirs, session linking, and project-level config overrides.

---

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  config.py (bootstrap)                                          │
│  → env vars → startup defaults only, never mutated at runtime   │
└────────────────┬────────────────────────────────────────────────┘
                 │ seed on first boot
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  @settings module                                               │
│  ┌─────────────────┐  ┌────────────────┐  ┌──────────────────┐ │
│  │ SettingDef      │  │ SettingsRegist │  │ SettingsManager  │ │
│  │ (key, type,     │  │ -ry            │  │                  │ │
│  │  default,       │  │ register()     │  │ Resolution order:│ │
│  │  sensitive,     │  │ get_def()      │  │  1. env override │ │
│  │  editable,      │  │ list_defs()    │  │  2. DB global    │ │
│  │  requires_restart│  └────────────────┘  │  3. DB project   │ │
│  │  category,scope)│                       │  4. DB session   │ │
│  └─────────────────┘                       │                  │ │
│                                            │ get(key, scope?) │ │
│                                            │ set(key, value)  │ │
│                                            │ reset(key)       │ │
│                                            │ get_all()        │ │
│                                            │ load_template()  │ │
│                                            └──────────────────┘ │
│  DB: settings(key, value_json, scope, scope_id, category)       │
│  Cache: Redis CACHE_CONFIG_TTL=3600                             │
└────────────────┬────────────────────────────────────────────────┘
                 │ project-level overrides
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│  @projects module                                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ ProjectManager                                          │   │
│  │  create(name, source_dir)  → ProjectRecord              │   │
│  │  get(project_id)           → ProjectRecord | None       │   │
│  │  list(active_only)         → list[ProjectRecord]        │   │
│  │  update(project_id, **kw)  → ProjectRecord              │   │
│  │  remove(project_id)        (does NOT touch sessions)    │   │
│  │  find_by_path(source_dir)  → ProjectRecord | None       │   │
│  │  add_session(pid, sid)                                  │   │
│  │  remove_session(pid, sid)                               │   │
│  │  get_sessions(pid)         → list[str]                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│  DB: projects + project_sessions tables                         │
│  FS:  ~/.css/projects/<id>/metadata.json  (sync with DB)        │
└─────────────────────────────────────────────────────────────────┘
                 ▲
     consumed by the workspace layer, Sessions, REST API
```

---

### T17.1 — Settings DB Schema & ORM Model

**Files**: `src/css/core/db/models/settings_model.py` + migration

**Schema**:
```sql
CREATE TABLE settings (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key          TEXT NOT NULL,
    value_json   JSONB NOT NULL,
    scope        TEXT NOT NULL DEFAULT 'global',   -- 'global' | 'project' | 'session'
    scope_id     TEXT,                              -- project_id or session_id; NULL for global
    category     TEXT NOT NULL,                    -- 'system'|'llm'|'cache'|'database'|'security'|'telemetry'|'frontend'|'orchestrator'
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by   TEXT,                             -- agent_id or 'system'
    UNIQUE (key, scope, scope_id)
);
CREATE INDEX ix_settings_category ON settings(category);
CREATE INDEX ix_settings_scope_id ON settings(scope_id) WHERE scope_id IS NOT NULL;
```

**Tortoise ORM model**:
- `SettingRecord` with all fields above
- `to_dict()` helper
- Class method `get_value(key, scope, scope_id)` → Any | None
- Class method `set_value(key, value, scope, scope_id, category, updated_by)` → SettingRecord

**Todos**:
- `settings-db-model` — SettingRecord Tortoise model
- `settings-db-migration` — Alembic/Tortoise migration

---

### T17.2 — SettingDefinition Struct

**Files**: `src/css/core/types/settings.py`

```python
class SettingScope(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"
    SESSION = "session"

class SettingCategory(str, Enum):
    SYSTEM = "system"
    LLM = "llm"
    CACHE = "cache"
    DATABASE = "database"
    SECURITY = "security"
    TELEMETRY = "telemetry"
    FRONTEND = "frontend"
    ORCHESTRATOR = "orchestrator"
    SESSION = "session"

@dataclass
class SettingDefinition:
    key: str                        # e.g. "llm.anthropic.api_key"
    type: type                      # str | int | bool | float | list | dict
    default: Any                    # Value loaded from config.py bootstrap
    description: str
    category: SettingCategory
    scope: SettingScope             # Broadest scope this setting can apply to
    sensitive: bool = False         # True → masked in frontend ("***")
    editable_in_ui: bool = True
    requires_restart: bool = False  # True → warn on update (DB URL, workers)
    validator: Callable | None = None  # Optional validation function
```

**Todos**:
- `settings-definition-struct` — SettingDefinition + SettingScope + SettingCategory in core/types

---

### T17.3 — SettingsRegistry

**Files**: `src/css/core/settings/registry.py`

The registry holds all `SettingDefinition` objects (similar to `ModelRegistry` in `@llm_models`).

```python
class SettingsRegistry:
    def register(definition: SettingDefinition) → None
    def get_definition(key: str) → SettingDefinition | None
    def list_definitions(category: SettingCategory | None = None) → list[SettingDefinition]
    def validate_value(key: str, value: Any) → Any   # runs definition.validator + type check
    def is_sensitive(key: str) → bool
    def requires_restart(key: str) → bool
```

- Built-in `DEFAULT_SETTINGS` list — auto-registered from `config.py` values (see T17.5)
- `SETTINGS_REGISTRY = SettingsRegistry()` module-level singleton

**Todos**:
- `settings-registry-class` — SettingsRegistry class
- `settings-registry-singleton` — Module-level SETTINGS_REGISTRY singleton with DEFAULT_SETTINGS

---

### T17.4 — SettingsManager (Core)

**Files**: `src/css/core/settings/manager.py`

**Resolution order** (highest priority wins):
1. Explicit env override (env var with `CSS_SETTING__<KEY_UPPERCASE>` format)  
2. DB — session-scope setting (scope_id = current session)
3. DB — project-scope setting (scope_id = project_id of current session)
4. DB — global setting
5. `SettingDefinition.default` (from config.py bootstrap)

```python
class SettingsManager:
    # Core read/write
    def get(key: str, scope: SettingScope = GLOBAL, scope_id: str | None = None) → Any
    def set(key: str, value: Any, scope: SettingScope = GLOBAL, scope_id: str | None = None,
            updated_by: str = "system") → None
    def reset(key: str, scope: SettingScope = GLOBAL, scope_id: str | None = None) → None

    # Bulk operations
    def get_all(category: SettingCategory | None = None, scope: SettingScope = GLOBAL,
                scope_id: str | None = None, include_defaults: bool = True) → dict[str, Any]
    def get_category(category: SettingCategory) → dict[str, Any]

    # Bootstrap
    def seed_from_config_py() → None   # Called once on first startup if DB is empty
    def load_template(template_name: str) → None  # Apply a named template profile

    # Export/import
    def export_yaml(category: SettingCategory | None = None) → str
    def import_yaml(content: str, scope: SettingScope = GLOBAL, scope_id: str | None = None) → int
```

**Caching**: Redis layer using `CACHE_CONFIG_TTL = 3600`. Cache key format:
`css:settings:{scope}:{scope_id or "global"}:{key}`

**Todos**:
- `settings-manager-core` — SettingsManager get/set/reset/get_all
- `settings-manager-seed` — seed_from_config_py() bootstrap
- `settings-manager-cache` — Redis cache layer with invalidation
- `settings-manager-templates` — load_template() + export/import YAML

---

### T17.5 — config.py Registration (DEFAULT_SETTINGS list)

**Files**: `src/css/core/settings/defaults.py`

Register every key from `config.py` as a `SettingDefinition`. Example:
```python
DEFAULT_SETTINGS = [
    SettingDefinition(
        key="llm.anthropic.api_key",
        type=str,
        default=ANTHROPIC_API_KEY,   # from config.py
        description="Anthropic API key",
        category=SettingCategory.LLM,
        scope=SettingScope.GLOBAL,
        sensitive=True,
        editable_in_ui=True,
        requires_restart=False,
    ),
    SettingDefinition(
        key="llm.anthropic.default_model",
        type=str,
        default=ANTHROPIC_MODEL,
        description="Default Anthropic model to use",
        category=SettingCategory.LLM,
        scope=SettingScope.PROJECT,   # can be overridden per project
        sensitive=False,
        editable_in_ui=True,
        requires_restart=False,
    ),
    # ... all providers, cache, db, security, orchestrator, frontend settings
]
```

**Coverage** — all config.py sections:
- `system.*` — DEBUG, ENVIRONMENT, LOG_LEVEL, PYTHONUNBUFFERED (requires_restart=True)
- `cache.*` — CACHE_ENABLED, CACHE_BACKENDS, all TTLs, compression, encryption
- `database.postgres.*` — all POSTGRES_DATABASE fields (sensitive=True for password, requires_restart=True for host/port)
- `database.redis.*` — all REDIS_DATABASE fields
- `llm.<provider>.*` — API key (sensitive) + default model + timeout, for all 22 providers
- `orchestrator.*` — heartbeat interval, crash timeout, task timeout, multi-orchestrator
- `session.*` — SESSION_MODE, SESSION_TIMEOUT_MINUTES
- `security.*` — SECRET_KEY, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION_HOURS (all sensitive, requires_restart=True for SECRET_KEY)
- `frontend.*` — FRONTEND_HOST/PORT, REACT_APP_API_URL/WS_URL
- `telemetry.*` — TELEMETRY_ENABLED, AUDIT_LOG_ENABLED, OPEN_OBSERVE connection
- `a2a.*` — CSS_A2A_ENABLED, KB_SIZE, GOOGLE_A2A_ENABLED, server host/port

**Todos**:
- `settings-defaults-all` — Complete DEFAULT_SETTINGS list covering all config.py keys

---

### T17.6 — Setting Templates

**Files**: `src/css/core/settings/profiles/`

> ⚠️ **Dir is `profiles/` not `templates/`** — `templates/` is reserved for the colocated React panel (Phase 18).

YAML profiles that override specific settings for a named mode. Applied with `SettingsManager.load_template("red_team")`.

Templates to create:
- `development.yaml` — debug=true, log_level=DEBUG, LLM using dev-friendly/cheap models
- `red_team.yaml` — session mode=red_team, aggressive timeouts, full tool grants enabled
- `blue_team.yaml` — session mode=blue_team, defensive settings, restricted outbound
- `purple_team.yaml` — session mode=purple_team, hybrid settings
- `minimal.yaml` — minimal mode (local Ollama only, no external API calls, for offline/air-gapped use)

**Todos**:
- `settings-templates` — 5 YAML profile files in `profiles/` + load_template() integration

---

### T17.7 — Settings REST Endpoints

**Files**: `src/css/core/settings/routes.py` (registered with ASGI router)

```
GET    /api/settings/                            → list all (masked if sensitive)
GET    /api/settings/categories/                 → list categories + setting counts
GET    /api/settings/{key}                       → single setting (masked if sensitive)
PUT    /api/settings/{key}                       → update setting (validates type)
POST   /api/settings/{key}/reset                 → reset to default
GET    /api/settings/export/?format=yaml|json    → export full config
POST   /api/settings/import/                     → import from YAML/JSON body
GET    /api/settings/projects/{project_id}/      → get project-level overrides
PUT    /api/settings/projects/{project_id}/{key} → set project-level override
```

**Rules**:
- `sensitive=True` settings: returned as `"***"` in GET, accepted for write, never logged
- `requires_restart=True` settings: write accepted, response includes `{"restart_required": true}`
- Auth required on all endpoints (Phase TBD — connect when auth module exists)

**Todos**:
- `settings-rest-routes` — Full REST router for settings

---

### T17.8 — Projects DB Schema & ORM

**Files**: `src/css/core/db/models/project_model.py` + migration

```sql
CREATE TABLE projects (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name         TEXT NOT NULL,
    source_dir   TEXT NOT NULL,      -- absolute path to project source code
    description  TEXT,
    tags         TEXT[] DEFAULT '{}',
    active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE UNIQUE INDEX ix_projects_source_dir ON projects(source_dir) WHERE active = TRUE;

CREATE TABLE project_sessions (
    project_id   UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    session_id   TEXT NOT NULL,      -- matches ~/.css/sessions/session-<sid>/ dir name
    linked_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (project_id, session_id)
);
CREATE INDEX ix_project_sessions_sid ON project_sessions(session_id);
```

**Tortoise ORM models**: `ProjectRecord`, `ProjectSessionRecord`

**Todos**:
- `projects-db-model` — ProjectRecord + ProjectSessionRecord Tortoise models
- `projects-db-migration` — migration script

---

### T17.9 — ProjectRecord Struct (core/types)

**Files**: `src/css/core/types/projects.py`

```python
@dataclass
class ProjectRecord:
    id: str                     # UUID as string
    name: str
    source_dir: str             # validated: must be absolute path, existence checked
    description: str | None
    tags: list[str]
    active: bool
    created_at: datetime
    updated_at: datetime

    def validate_source_dir(self) → bool:
        """Check that source_dir exists and is accessible."""
        return Path(self.source_dir).is_dir()
```

**Todos**:
- `projects-record-struct` — ProjectRecord dataclass in core/types

---

### T17.10 — ProjectManager (Core)

**Files**: `src/css/modules/projects/manager.py`

```python
class ProjectManager:
    # CRUD
    async def create(name: str, source_dir: str, description: str | None = None,
                     tags: list[str] | None = None) → ProjectRecord
    async def get(project_id: str) → ProjectRecord | None
    async def list(active_only: bool = True) → list[ProjectRecord]
    async def update(project_id: str, **kwargs) → ProjectRecord
    async def remove(project_id: str) → None   # DB delete only, sessions/source untouched

    # Lookup
    async def find_by_path(source_dir: str) → ProjectRecord | None

    # Session linking
    async def add_session(project_id: str, session_id: str) → None
    async def remove_session(project_id: str, session_id: str) → None
    async def get_sessions(project_id: str) → list[str]
    async def get_project_for_session(session_id: str) → ProjectRecord | None

    # Filesystem sync
    def _write_metadata(project: ProjectRecord) → None    # → ~/.css/projects/<id>/metadata.json
    def _delete_metadata(project_id: str) → None         # remove ~/.css/projects/<id>/
    async def sync_filesystem() → None                   # repair FS ↔ DB on startup
```

**FS layout** — written by `_write_metadata()`:
```
~/.css/projects/
└── <project-id>/
    ├── metadata.json   {id, name, source_dir, description, tags, created_at}
    └── config.yaml     (project-level settings overrides — managed by SettingsManager)
```

**Todos**:
- `projects-manager-crud` — CRUD create/get/list/update/remove + find_by_path
- `projects-manager-sessions` — Session linking methods
- `projects-manager-fs-sync` — Filesystem metadata sync on create/remove/startup

---

### T17.11 — Projects REST Endpoints

**Files**: `src/css/modules/projects/routes.py`

```
GET    /api/projects/                         → list all projects
POST   /api/projects/                         → create project (validates source_dir)
GET    /api/projects/{id}/                    → get project details
PUT    /api/projects/{id}/                    → update project
DELETE /api/projects/{id}/                    → remove project (not sessions/source)
GET    /api/projects/{id}/sessions/           → list linked sessions
POST   /api/projects/{id}/sessions/{sid}/     → link session to project
DELETE /api/projects/{id}/sessions/{sid}/     → unlink session
GET    /api/projects/search/?path=<dir>       → find project by source_dir
```

**Todos**:
- `projects-rest-routes` — Full REST router for projects

---

### T17.12 — Workspace Integration

**Files**: update the `core/workspace/` layer used by session creation

When the session workspace is created with `project_id=X`:
1. Auto-calls `ProjectManager.add_session(project_id, session_id)`
2. Stores `project.source_dir` in session metadata (read-only path reference)
3. Auto-applies project-level settings overrides via `SettingsManager.get(..., scope=PROJECT, scope_id=project_id)`

**Todos**:
- `projects-workingdir-integration` — workspace layer auto-links session to project + applies project settings

---

### T17.13 — Event Emission + OTEL

**Files**: update `settings/manager.py` and `projects/manager.py`

After Phase 14 events module is implemented:
- `settings.changed` event — emitted on every `set()` call: `{key, old_value, new_value, scope, updated_by}`
- `project.created` / `project.removed` / `project.session_linked` events
- OTEL spans on DB reads for settings (use `@instrument("settings.get")`)
- Masked values in OTEL (never log sensitive setting values)

**Todos**:
- `settings-event-emission` — Emit settings.changed via EventEmitter (Phase 14 blocker)
- `projects-event-emission` — Emit project lifecycle events (Phase 14 blocker)

---

### Phase 17 Todo Summary

| ID | Task Group | Title | Blocked by |
|----|-----------|-------|-----------|
| `settings-db-model` | T17.1 | SettingRecord Tortoise model | `@core/db` |
| `settings-db-migration` | T17.1 | DB migration | `settings-db-model` |
| `settings-definition-struct` | T17.2 | SettingDefinition + enums | `@core/types` |
| `settings-registry-class` | T17.3 | SettingsRegistry class | `settings-definition-struct` |
| `settings-registry-singleton` | T17.3 | SETTINGS_REGISTRY singleton + DEFAULT_SETTINGS wire-up | `settings-registry-class`, `settings-defaults-all` |
| `settings-manager-core` | T17.4 | SettingsManager get/set/reset/get_all | `settings-db-model`, `settings-registry-class` |
| `settings-manager-seed` | T17.4 | seed_from_config_py() | `settings-manager-core` |
| `settings-manager-cache` | T17.4 | Redis cache layer | `settings-manager-core` |
| `settings-manager-templates` | T17.4 | load_template() + export/import YAML | `settings-manager-core`, `settings-templates` |
| `settings-defaults-all` | T17.5 | Complete DEFAULT_SETTINGS list | `settings-definition-struct` |
| `settings-templates` | T17.6 | 5 YAML template files | `settings-definition-struct` |
| `settings-rest-routes` | T17.7 | Settings REST endpoints | `settings-manager-core` |
| `projects-db-model` | T17.8 | ProjectRecord + ProjectSessionRecord ORM | `@core/db` |
| `projects-db-migration` | T17.8 | DB migration | `projects-db-model` |
| `projects-record-struct` | T17.9 | ProjectRecord dataclass | `@core/types` |
| `projects-manager-crud` | T17.10 | CRUD + find_by_path | `projects-db-model`, `projects-record-struct` |
| `projects-manager-sessions` | T17.10 | Session linking methods | `projects-manager-crud` |
| `projects-manager-fs-sync` | T17.10 | FS metadata sync | `projects-manager-crud` |
| `projects-rest-routes` | T17.11 | Projects REST endpoints | `projects-manager-crud` |
| `projects-workingdir-integration` | T17.12 | workspace auto-link | `projects-manager-sessions`, Phase 15 `working-dir-manager` |
| `settings-event-emission` | T17.13 | settings.changed events | `settings-manager-core`, Phase 14 |
| `projects-event-emission` | T17.13 | project lifecycle events | `projects-manager-crud`, Phase 14 |

**BLOCKED by Phase 14** (events): `settings-event-emission`, `projects-event-emission`
**BLOCKED by Phase 15** (workspace layer): `projects-workingdir-integration`
**All others: no blockers — ready to implement.**

### T17.14 — Startup Seeding (added 2026-05-04)

> Tables that need data pre-populated to be functional. Split into two categories:
> - **init-db** (once on first setup / `manage.py init-db`): static fixtures, default grants, base tags
> - **startup** (every ASGI lifespan start): dynamic data fetched from providers, builtins auto-registered

#### ORM Models needed first

| ID | Title | Blocked by |
|----|-------|-----------|
| `orm-api-service-provider` | Expand `ApiServiceProvider` with full fields (slug, auth_type, is_local, enabled, etc.) | — |
| `orm-llm-model-record` | New `LLMModelRecord` in `core/db/models/llm_models.py` (per-model metadata + costs) | `orm-api-service-provider` |
| `orm-capability-record` | New `ProviderCapabilityRecord` in `core/db/models/capabilities.py` (persisted capability TTL cache) | `orm-llm-model-record` |

#### init-db (static, idempotent, run once)

| ID | Table | What | When |
|----|-------|------|------|
| `seed-providers-fixtures` | `api_service_provider` | All 22 providers from `css/api_services/fixtures/providers.json`. Local providers `enabled=True`, API-key providers `enabled=False` until key set. | `manage.py init-db` |
| `seed-tags-defaults` | `tag` | System tags: severity (critical/high/medium/low/info), category (malware/exploit/recon/...), team (blue/red/purple), source (mitre/nvd/cwe/capec) — must exist before intel seeding | `manage.py init-db` before seed-intel |
| `seed-permissions-defaults` | `permission_grants` | Default role grants: admin=all, orchestrator=read+exec, agent=exec, viewer=read | `manage.py init-db` |

#### startup (dynamic, every ASGI lifespan start)

| ID | Table | What | How |
|----|-------|------|-----|
| `seed-tools-builtin` | `builtin_tool` (or `hybrid_tool`) | `ToolRegistry._load_builtin_tools()` already exists in-memory. Upsert to DB at startup so tools persist + are queryable via REST. | ASGI lifespan |
| `seed-models-startup` | `llm_model_record` | Each provider's `get_models()` → upsert `LLMModelRecord`. Skip if API key missing. Redis cache 24h TTL. | ASGI lifespan |
| `seed-capabilities-startup` | `provider_capability_record` | `DynamicCapabilityRegistry.discover()` already runs in-memory. Persist to DB. Check TTL before re-fetching. | ASGI lifespan |

**Startup order**: providers fixtures (init-db) → tags (init-db) → permissions (init-db) → [ASGI start] → tools builtin → models → capabilities



---

## 🖥️ Phase 18 — Frontend Foundation

**Goal**: Scaffold a running React 19 + TypeScript frontend with dark feature-rich UI, Vite dev server already in Docker, and the **module-colocated panel architecture** — each Python module owns its own React panel alongside its Python code. First three live panels: Settings, Marketplace, Chat.

**Core principle**: Code that belongs together stays together. `src/css/core/settings/templates/` lives next to `settings/manager.py`. The frontend shell discovers panels via a central registry, not file-system scanning.

> **Naming rule**: Module-colocated React panel dirs are called `templates/` (not `frontend/`). Exception: YAML profiles in `@settings` live in `profiles/` to avoid collision.

---

### Architecture Overview

```
src/frontend/                          ← Main Vite app (shell only)
├── package.json                       ← bun + vite + react19 + TS + tailwindv4 + shadcn
├── vite.config.ts                     ← Aliases: @css → ../../css, @ui → ./src/ui
├── tsconfig.json                      ← strict mode
├── index.html
└── src/
    ├── main.tsx                       ← Entry: ReactDOM + RouterProvider + QueryClientProvider
    ├── App.tsx                        ← AppShell layout (sidebar + outlet)
    ├── router.tsx                     ← TanStack Router: all routes
    ├── module-registry.ts             ← Maps module names → lazy-imported panel components
    │
    ├── core/
    │   ├── layout/
    │   │   ├── AppShell.tsx           ← Dark shell: sidebar + topbar + content area
    │   │   ├── Sidebar.tsx            ← Nav items auto-generated from module-registry (REFERENCE: ahs-admin-panel/Sidebar/)
    │   │   ├── TopBar.tsx             ← Breadcrumb + status indicators + connection badge
    │   │   └── PanelContainer.tsx     ← Wrapper with loading skeleton + error boundary
    │   ├── api/
    │   │   ├── client.ts              ← Base fetch wrapper (REST, auto JSON)
    │   │   ├── ws-manager.ts          ← PORT from ahs-admin-panel/useSocket.ts (adapt, not rewrite)
    │   │   └── sse-client.ts          ← SSE reader → returns AsyncIterable<T>
    │   ├── hooks/                     ← PORTED from ahs-admin-panel (see frontend-port-hooks)
    │   │   ├── useWebSocket.ts        ← React hook: subscribe to WS message types
    │   │   ├── useSSE.ts              ← React hook: consume SSE stream as React state
    │   │   ├── useApi.ts              ← TanStack Query wrapper with error toast
    │   │   ├── useStorage.ts          ← PORT: useLocalStorage + useSessionStorage
    │   │   ├── useEventListener.ts    ← PORT: stable ref-based event listener
    │   │   ├── useBreakPoint.ts       ← PORT: xs/sm/md/lg/xl breakpoint detection
    │   │   ├── useClientWidth.ts      ← PORT: ResizeObserver-based element width
    │   │   ├── useDragResizeHeight.ts ← PORT: drag-to-resize height handle
    │   │   ├── useDraggable.ts        ← PORT: grid-snap free-drag with localStorage pos
    │   │   ├── useList.ts             ← PORT: generic list CRUD + reorder
    │   │   ├── useAsync.ts            ← PORT: one-off async state (use TanStack Query for data)
    │   │   └── useIntersectionObserver.ts ← PORT: virtual scroll trigger
    │   ├── charts/                    ← Recharts components (see frontend-live-graphs)
    │   │   ├── TokenUsageChart.tsx    ← AreaChart: input/output tokens over time
    │   │   ├── LatencyChart.tsx       ← LineChart: p50/p95/p99 LLM latency
    │   │   ├── AgentActivityBar.tsx   ← BarChart: calls per model last hour
    │   │   └── EventRateSparkline.tsx ← Tiny sparkline: event rate per 30s
    │   ├── providers/
    │   │   └── SocketProvider.tsx     ← PORT from ahs-admin-panel/SocketProvider.tsx (React Context for wsManager)
    │   └── components/
    │       ├── StatusBadge.tsx
    │       ├── JsonTree.tsx           ← Dark collapsible JSON viewer
    │       ├── CodeBlock.tsx          ← Syntax-highlighted code (shiki)
    │       └── DataTable.tsx          ← shadcn DataTable with sort/filter/pagination
    │
    └── ui/                            ← shadcn/ui components (copy-paste, YOU own them)
        ├── button.tsx
        ├── input.tsx
        ├── card.tsx
        └── ... (added per-need via `bunx shadcn add`)

src/css/modules/<name>/templates/     ← MODULE-COLOCATED panels (named templates/, not frontend/)
    ├── index.tsx                      ← default export: <NamePanel />
    ├── components/                    ← Module-specific sub-components
    ├── hooks.ts                       ← useSettings(), useProjects(), etc.
    └── types.ts                       ← TypeScript types matching Python API schemas
```

---

### Stack Decisions (rationale)

| Choice | Why |
|--------|-----|
| **Vite 6** | Fastest HMR, Bun-native (already in Dockerfile), excellent TS DX |
| **React 19** | You know it; new `use()` hook great for streaming/Suspense |
| **TypeScript strict** | Catches API contract mismatches at compile time |
| **Tailwind CSS v4** | New Oxide engine (CSS-first config), 5× faster than v3, no PostCSS config needed |
| **shadcn/ui** | You own the components (copy-pasted, not installed), dark mode first, Radix primitives, extremely feature-rich and detailed |
| **TanStack Router v1** | Best TypeScript routing — fully type-safe params, loaders, error boundaries per-route |
| **TanStack Query v5** | REST data fetching + cache + background refresh — pairs perfectly with the Settings REST API |
| **Zustand v5** | Tiny. For WebSocket global state (agent status, event stream). No boilerplate |
| **Vite path aliases** | `@css/core/settings/templates` → `../../css/core/settings/templates` — keeps module panels colocated without monorepo complexity |
| **Lucide React** | Icons used by shadcn/ui, consistent dark design |
| **Shiki** | Server-rendered syntax highlighting in CodeBlock (used by Chat + agent output) |

**Not using**: npm (use bun), class-variance-authority only through shadcn, no Redux, no Next.js/Remix (unnecessary complexity), no Webpack.

---

### T18.1 — Vite Project Scaffold

**Files**: `src/frontend/package.json`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.tsx`

Initialize the Vite project via:
```bash
cd /home/daen/Projects/cybersecsuite
bun create vite src/frontend --template react-ts
cd src/frontend
bun add react@19 react-dom@19
bun add -d @types.py/react@19 @types.py/react-dom@19 vite typescript
bun add @tanstack/react-router @tanstack/react-query zustand lucide-react
bun add -d @tanstack/router-devtools @tanstack/query-devtools
```

**`vite.config.ts`** — critical alias setup:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@css': path.resolve(__dirname, '../../css'),   // Module panels live here
      '@ui': path.resolve(__dirname, 'src/ui'),
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/ws':  { target: 'ws://localhost:8000', ws: true },
      '/sse': { target: 'http://localhost:8000', changeOrigin: true },
      '/v1':  { target: 'http://localhost:8000', changeOrigin: true },
    }
  }
})
```

The dev server proxy means the frontend can call `/api/settings/` and it routes to the backend (running locally via `make serve`). No CORS issues in dev. No Docker needed for app code.

**Todos**:
- `frontend-vite-scaffold` — Vite + React 19 + TS project init, package.json, vite.config.ts with aliases + proxy, tsconfig strict

---

### T18.2 — Tailwind v4 + shadcn/ui Setup

**Installation** (Tailwind v4 — CSS-first, no config file needed):
```bash
bun add tailwindcss @tailwindcss/vite
bun add class-variance-authority clsx tailwind-merge
bunx shadcn init   # → configure: dark mode, zinc base color, CSS variables
```

**`src/index.css`** — CSS-first Tailwind v4:
```css
@import "tailwindcss";

@layer base {
  :root {
    --background: 0 0% 3.9%;       /* Near-black base */
    --foreground: 0 0% 98%;
    --card: 0 0% 7%;
    --border: 0 0% 14.9%;
    --primary: 142 70% 45%;        /* Green accent — cybersec aesthetic */
    --destructive: 0 62.8% 30.6%;
    --ring: 142 70% 45%;
  }
}
```

Initial shadcn components to install:
```bash
bunx shadcn add button input card badge separator skeleton toast tabs
bunx shadcn add dialog sheet dropdown-menu tooltip command
bunx shadcn add table scroll-area resizable collapsible
```

**Todos**:
- `frontend-tailwind-shadcn` — Tailwind v4 + shadcn/ui dark theme setup, initial component set, CSS variables for green-on-black cybersec aesthetic

---

### T18.3 — AppShell (Core Layout)

**Files**: `src/frontend/src/core/layout/`

The global shell — renders on every route. No routing logic here, only layout.

```
┌─────────────────────────────────────────────────────────────────┐
│  TopBar: [≡ CSS] [breadcrumb]         [● WS] [● API] [settings] │
├──────────────┬──────────────────────────────────────────────────┤
│  Sidebar     │  <Outlet />  (panel renders here)                │
│              │                                                  │
│  ● Settings  │                                                  │
│  ● Marketplace                                                  │
│  ● Chat      │                                                  │
│  ─────────   │                                                  │
│  ● Projects  │                                                  │
│  ● Agents    │                                                  │
│  ● Events    │                                                  │
│              │                                                  │
└──────────────┴──────────────────────────────────────────────────┘
```

- Sidebar items are driven by `module-registry.ts` — add a panel entry, it appears in nav automatically
- TopBar shows: WebSocket connection badge (green/amber/red), API health badge, breadcrumb
- PanelContainer wraps each panel: Suspense skeleton + ErrorBoundary with retry button
- Collapsible sidebar (icon-only mode at narrow widths)
- All dark: `bg-background`, borders `border-border`, accents `text-primary`

**Todos**:
- `frontend-appshell` — AppShell, Sidebar, TopBar, PanelContainer components. Sidebar items from module-registry. Connection badges.

---

### T18.4 — API Client Layer

**Files**: `src/frontend/src/core/api/`

**REST client** (`client.ts`):
```typescript
// Base typed fetch wrapper
export async function apiGet<T>(path: string): Promise<T>
export async function apiPost<T>(path: string, body: unknown): Promise<T>
export async function apiPut<T>(path: string, body: unknown): Promise<T>
export async function apiDelete(path: string): Promise<void>
// All throw ApiError with {status, message, detail} on non-2xx
```

**WebSocket manager** (`ws-manager.ts`):
```typescript
// Singleton. Connects to /ws on mount. Auto-reconnects with expo backoff.
// Typed message bus — subscribe to event types.py:
wsManager.subscribe('agent.output', (msg: AgentOutputMsg) => void)
wsManager.subscribe('tool.call', (msg: ToolCallMsg) => void)
wsManager.subscribe('settings.changed', (msg: SettingsChangedMsg) => void)
// Exposes: status: 'connected'|'connecting'|'disconnected'|'error'
```

**SSE client** (`sse-client.ts`):
```typescript
// Reusable SSE client for /sse/* and future /v1/* proxy streams
export async function* streamSSE<T>(url: string, body: unknown): AsyncGenerator<T>
// useSSE hook consumes this and updates React state token-by-token
```

**Zustand store** (for WebSocket state — in `src/store.ts`):
```typescript
interface CSSStore {
  wsStatus: WsStatus
  activeAgents: AgentInfo[]
  recentEvents: CSSEvent[]
  // setters
}
```

**Todos**:
- `frontend-api-client` — REST client (typed fetch wrapper), ApiError class, base URL from vite proxy
- `frontend-ws-manager` — WebSocket singleton manager with reconnect, typed message subscribe/unsubscribe
- `frontend-sse-client` — SSE AsyncGenerator + useSSE React hook
- `frontend-zustand-store` — Zustand store for WS state (wsStatus, activeAgents, recentEvents)

---

### T18.5 — Module Panel System

**Files**: `src/frontend/src/module-registry.ts`

The registry is a static list of panel descriptors — each entry maps to a lazy-imported React component. This is the **colocated template system**: the panel component lives next to the Python module.

```typescript
// src/frontend/src/module-registry.ts
import { lazy } from 'react'

export interface ModulePanel {
  id: string            // 'settings' | 'marketplace' | 'chat' | ...
  label: string         // Display name in sidebar
  icon: LucideIcon      // Icon component
  path: string          // Route path: '/settings'
  component: React.LazyExoticComponent<any>  // Lazy-loaded from @css alias
  badge?: () => string  // Optional dynamic badge (e.g. "3 active" for agents)
}

export const MODULE_PANELS: ModulePanel[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: LayoutDashboard,
    path: '/',
    component: lazy(() => import('./pages/LandingDashboard')),
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: Settings,
    path: '/settings',
    // ← This imports from src/css/core/settings/templates/index.tsx
    component: lazy(() => import('@css/core/settings/templates')),
  },
  {
    id: 'marketplace',
    label: 'Marketplace',
    icon: Store,
    path: '/marketplace',
    component: lazy(() => import('@css/core/marketplace/templates')),
  },
  {
    id: 'chat',
    label: 'Chat',
    icon: MessageSquare,
    path: '/chat',
    component: lazy(() => import('@css/modules/chat/templates')),
  },
  // Add new panel here → automatically appears in sidebar + routing
]
```

TanStack Router generates type-safe routes from this registry at startup.

**Adding a new module panel (the full workflow)**:
1. Create `src/css/modules/<name>/templates/index.tsx` — export `default` component
2. Add entry to `MODULE_PANELS` in `module-registry.ts`
3. Done — panel appears in sidebar, route is registered, lazy-loaded on first visit

**Todos**:
- `frontend-module-registry` — ModulePanel type + MODULE_PANELS registry (with `/` dashboard entry) + TanStack Router route generation
- `frontend-panel-colocated-structure` — Scaffold `templates/` stub dirs in settings, marketplace, chat modules (index.tsx + hooks.ts + types.ts)

---

### T18.6 — Settings Panel

**Files**: `src/css/core/settings/templates/`

The first real panel — connects directly to the Phase 17 REST API (`/api/settings/`).

```
┌─────────────────────────────────────────────────────────────────┐
│  Settings                                          [Export YAML] │
│  ─────────────────────────────────────────────────────────────  │
│  🔍 Search settings...                           [Category ▾]   │
│                                                                  │
│  ▼ LLM                                                          │
│    anthropic.api_key          ••••••••••••    [Edit]           │
│    anthropic.default_model    claude-3-5-sonnet  [Edit]        │
│    openai.api_key             ••••••••••••    [Edit]           │
│    ...                                                          │
│                                                                  │
│  ▼ Cache                                                        │
│    cache.enabled              ● true           [Toggle]        │
│    cache.default_ttl          86400            [Edit]          │
│                                                                  │
│  ▼ System                                                       │
│    system.debug               ○ false          [Toggle]        │  
│    system.log_level           INFO             [Select]        │
│    ...                                         ⚠ restart req.  │
└─────────────────────────────────────────────────────────────────┘
```

**Features**:
- Category accordion (collapsed by default, expand per category)
- Search bar filters across all keys + descriptions
- Sensitive values shown as `••••••` with click-to-reveal
- `requires_restart=true` settings show amber ⚠ badge
- Inline edit: click value → inline input → Enter to save (optimistic update via TanStack Query mutation)
- Toast notification on save: "Setting saved" or "Setting saved — restart required"
- Export button → downloads YAML
- Template loader: `[Load Template ▾]` dropdown → applies named template

**Todos**:
- `frontend-settings-panel` — Settings panel with category accordion, search, inline edit, sensitive masking, restart warnings, toast feedback
- `frontend-settings-hooks` — `useSettings()`, `useUpdateSetting()`, `useResetSetting()` TanStack Query hooks for `/api/settings/*`

---

### T18.7 — Marketplace Panel

**Files**: `src/css/core/marketplace/templates/`

Panel for browsing/installing tools from the marketplace.

```
┌─────────────────────────────────────────────────────────────────┐
│  Marketplace                    [🔍 Search] [Category ▾] [Sort] │
│  ─────────────────────────────────────────────────────────────  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │ nmap      │ │ shodan   │ │ burpsuite│ │ metasploit         │
│  │ Tool      │ │ Tool     │ │ Scanner  │ │ Framework│          │
│  │ ★★★★☆   │ │ ★★★★★   │ │ ★★★★☆   │ │ ★★★★★   │          │
│  │[Install] │ │ ✓ Inst. │ │[Install] │ │[Install] │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ─────────────────────────────────────────────────────────────  │
│  Installed (12)                                    [Manage]     │
│  nmap v7.94 ✓  shodan-cli v1.1 ✓  ...                         │
└─────────────────────────────────────────────────────────────────┘
```

**Todos**:
- `frontend-marketplace-panel` — Marketplace panel with tool grid, search/filter, install button, installed tools list
- `frontend-marketplace-hooks` — TanStack Query hooks for marketplace API

---

### T18.8 — Chat Panel

**Files**: `src/css/modules/chat/templates/`

The most complex panel — real-time streaming agent conversation.

```
┌─────────────────────────────────────────────────────────────────┐
│  Chat                [Model: claude-opus-4 ▾] [Session: #abc12] │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  USER ──────────────────────────────────────────────────────── │
│  Scan 192.168.1.0/24 for open ports                            │
│                                                                  │
│  ASSISTANT ─────────────────────────────────────────────────── │
│  Running nmap scan...                                           │
│  ┌ Tool: nmap ─────────────────────────────────────────────┐   │
│  │ $ nmap -sS 192.168.1.0/24 --open                       │   │
│  │ Starting Nmap 7.94...                                   │   │
│  │ Discovered open port 22/tcp on 192.168.1.5             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Found 3 hosts with open services. Summary:                     │
│  - 192.168.1.5: SSH (22), HTTP (80)     [streaming cursor ▌]   │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  [📎] [/commands]  Type a message...          [↑ history] [Send]│
└─────────────────────────────────────────────────────────────────┘
```

**MVP transport**:
- first version should use the existing chat REST + WebSocket session transport
- the hook/state shape should stay transport-agnostic so `/sse/*` or `/v1/*` proxy streaming can be swapped in later

**Features**:
- real-time assistant output over the current chat transport
- Tool call blocks: collapsible, syntax-highlighted input/output
- Model selector dropdown (from `@llm_models` registry via REST)
- Session history sidebar (toggle)
- `/commands` slash command autocomplete
- Markdown rendering with syntax highlighting (shiki)

**Todos**:
- `frontend-chat-panel` — Chat panel with WS-first MVP transport, tool call blocks, markdown rendering, model selector
- `frontend-chat-hooks` — `useChat()` hook managing REST + WebSocket MVP transport, later proxy/SSE-ready

---

### T18.9 — ⏸️ Docker / Nginx / Proxy (deferred — not part of project yet)

Production containerization (Nginx static serving, proxy service wiring, docker-compose cleanup) is out of scope until the frontend and backend are functionally complete. **Run dev with `bun run dev` directly for now.**

---

### T18.10 — Development DX

**Files**: `src/frontend/src/` misc

- TanStack Router devtools (overlay in dev mode — shows route tree, params)
- TanStack Query devtools (overlay — shows cache state, queries, mutations)
- TypeScript path checking: `bun run tsc --noEmit` as pre-commit validation
- Vite build script in package.json:
  ```json
  "scripts": {
    "dev": "vite --host",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "check": "tsc --noEmit"
  }
  ```

**Todos**:
- `frontend-dev-tooling` — TanStack devtools overlays, package.json scripts, tsconfig strict paths

---

### T18.11 — Landing Dashboard Page (`/`)

**Files**: `src/frontend/src/pages/LandingDashboard.tsx`

The root route. A live ops dashboard — dark, information-dense, feature-rich. Layout: responsive 3-column CSS grid (2-col on md, 1-col on sm). All widgets use shadcn Card + Skeleton for loading state.

**Widgets**:
- **SystemHealth** — backend ping status, DB conn, Redis conn, OTEL conn (`GET /api/health`), WS status indicator (from Zustand wsStatus)
- **LiveMetrics** — see T18.12 (Recharts area/line/bar charts, WS-driven)
- **ActiveAgents** — live list of running agents with status badge (WS push via CSS event stream)
- **RecentEvents** — last 20 domain events, auto-scrolling, infinite scroll with `useIntersectionObserver`
- **SessionOverview** — active session count + last 5 sessions with project name (`GET /api/sessions`)
- **ModelUsage** — top 5 models by call count + token spend (`GET /api/llm/stats`)

**Hooks used**:
- `useIntersectionObserver` (ported from ahs-admin-panel) for infinite scroll in RecentEvents
- `useBreakPoint` (ported) for responsive grid
- TanStack Query for REST widgets; Zustand for WS-pushed widgets

**Todos**:
- `frontend-landing-dashboard` — full dashboard page with 6 widgets, responsive grid, Skeleton states

---

### T18.12 — Live Graphs (Recharts + WS data feeds)

**Files**: `src/frontend/src/core/charts/`

```bash
bun add recharts @types.py/recharts
```

All charts: dark zinc palette, `ResponsiveContainer width="100%"`, custom tooltip styling, no mock data — empty Skeleton until first real WS event.

**Charts**:
- `TokenUsageChart.tsx` — AreaChart (x=time last 60min, 1-min buckets, y=tokens; two areas: input(blue) + output(green))
- `LatencyChart.tsx` — LineChart (p50/p95/p99 LLM latency per minute)
- `AgentActivityBar.tsx` — BarChart (agent calls per model last hour)
- `EventRateSparkline.tsx` — Tiny sparkline (no axes), 30s buckets, for use inside dashboard cards

**Data model**: Zustand `metricsSlice` — rolling 60-bucket buffer per metric. `useDashboardMetrics.ts` hook subscribes to WS events of types `llm.call.complete`, `agent.action`, `css.event` and populates the buffer.

**Todos**:
- `frontend-live-graphs` — Recharts install + 4 chart components + metricsSlice + useDashboardMetrics hook

---

### Phase 18 Implementation Order (no blockers — start immediately)

```
T18.1 → T18.2 → T18.3 → T18.4a (port hooks) → T18.4 (api/ws/store)
                ↓
         T18.5 (registry + colocated panel stubs)
                ↓
         T18.7 (marketplace)  ← first live panel, backend already exists
         T18.6 (settings)     ← after Phase 17 settings REST
         T18.8 (chat)         ← WS-first MVP, proxy/SSE later
         T18.10 (DX)          ← alongside active frontend work
         T18.4 SSE client     ← later generic utility for /sse/* and /v1/* streams
                ↓
         T18.11 (landing/dashboard)  ← after sessions/events backend surfaces are ready
                ↓
         T18.12 (live graphs)
```

**Minimum to get something running in the browser**: T18.1 + T18.2 + T18.3 = scaffold + dark shell. Run locally with `bun run dev`. Every task after that adds a live panel.

---

### Phase 18 Todo Summary

| ID | Task | Title | Blocked by |
|----|------|-------|-----------|
| `frontend-vite-scaffold` | T18.1 | Vite + React 19 + TS scaffold, vite.config with aliases+proxy | — |
| `frontend-tailwind-shadcn` | T18.2 | Tailwind v4 + shadcn/ui dark theme + initial components | `frontend-vite-scaffold` |
| `frontend-appshell` | T18.3 | AppShell, Sidebar (ref ahs-admin-panel/Sidebar), TopBar, PanelContainer | `frontend-tailwind-shadcn` |
| `frontend-api-client` | T18.4 | REST client + ApiError | `frontend-vite-scaffold` |
| `frontend-ws-manager` | T18.4 | PORT useSocket.ts from ahs-admin-panel → ws-manager.ts | `frontend-vite-scaffold` |
| `frontend-sse-client` | T18.4 | SSE AsyncGenerator + useSSE hook for later generic `/sse/*` and `/v1/*` streams | `frontend-vite-scaffold` |
| `frontend-zustand-store` | T18.4 | Zustand store for WS state + metricsSlice | `frontend-vite-scaffold` |
| `frontend-port-hooks` | T18.4a | PORT 9 hooks from ahs-admin-panel + SocketProvider | `frontend-vite-scaffold` |
| `frontend-module-registry` | T18.5 | ModulePanel registry (incl `/` dashboard) + TanStack Router routes | `frontend-appshell` |
| `frontend-panel-colocated-structure` | T18.5 | Scaffold `templates/` stubs in settings/marketplace/chat modules | `frontend-module-registry` |
| `frontend-landing-dashboard` | T18.11 | Landing dashboard at `/` with 6 widgets + live graphs | `frontend-appshell`, `frontend-port-hooks`, `frontend-zustand-store`, `sessions-endpoints` |
| `frontend-live-graphs` | T18.12 | Recharts + 4 chart components + metricsSlice + useDashboardMetrics | `frontend-landing-dashboard`, `frontend-ws-manager` |
| `frontend-settings-panel` | T18.6 | Settings panel (accordion, search, inline edit, masking) | `frontend-panel-colocated-structure`, `frontend-settings-hooks`, `settings-rest-routes` |
| `frontend-settings-hooks` | T18.6 | TanStack Query hooks for /api/settings/* | `frontend-api-client`, `settings-rest-routes` |
| `frontend-marketplace-panel` | T18.7 | Marketplace panel (grid, search, install) | `frontend-panel-colocated-structure`, `frontend-marketplace-hooks` |
| `frontend-marketplace-hooks` | T18.7 | TanStack Query hooks for marketplace API | `frontend-api-client` |
| `frontend-chat-panel` | T18.8 | Chat panel (WS-first MVP, tool blocks, markdown, model/session controls) | `frontend-panel-colocated-structure`, `frontend-chat-hooks`, `frontend-port-hooks` |
| `frontend-chat-hooks` | T18.8 | useChat hook (REST + WebSocket MVP, later SSE/proxy-ready) | `frontend-api-client`, `frontend-ws-manager` |
| `frontend-dev-tooling` | T18.10 | Devtools overlays, package.json scripts, tsc check | `frontend-tailwind-shadcn` |

**BLOCKED by Phase 17** (settings REST): `frontend-settings-panel`
**Chat note**: build the first chat panel against the current chat REST + WebSocket backend; Phase 36 proxy/SSE work is an enhancement path, not a blocker for the MVP.
**All others: no blockers — implement in order above.**
**T18.9 (Docker/Nginx/proxy): deferred, not in scope yet.**


---

## 🗂️ Phase 19 — Module Restructuring & Missing Modules

**Goal**: Clean up the 25-module structure — fix typos, remove deprecated code, add missing modules, clarify boundaries. Keeps heavy modularization (LLM-dev-friendly), only acts on confirmed issues.

**Context note**: Docker/frontend location decision for Phase 18 is **deferred** (pending decision — separate conversation).

---

### 19.1 — Frontend Shell Location Decision (PENDING)

Two options for where the Vite shell app lives:

| Option | Path | Pros | Cons |
|--------|------|------|------|
| **A** `src/frontend/` (current plan) | `src/frontend/` | Clean separation — Python tools never see JS; standard Vite project root | Shell is not alongside Python code |
| **B** `core/templates/` | `src/css/core/templates/` | "Everything core in core"; orphaned `node_modules` is already there | Python mypy/linters see JS files; `bun run dev` path is buried; mixing Python pkg with JS project |

> ⚠️ `src/css/core/templates/` currently contains only orphaned `node_modules` (no `package.json`). It was never set up.

**Recommendation**: **Option A** (`src/frontend/`). Module-colocated panels (`templates/`) are the "code alongside Python" story — the shell is just infrastructure. The module-colocated approach is preserved either way.

**Action**: Clean up orphaned `node_modules` in `core/templates/`.

**Todo**: `core-templates-cleanup` — delete `src/css/core/templates/node_modules/`, leave dir for future Jinja2/static HTML templates if needed

---

### 19.2 — Confirmed Renames

| Current | → New | Reason |
|---------|-------|--------|
| `planer/` | `planner/` | Typo. All references throughout codebase must be updated. |
| `a2a_internal/` | `ipc/` | Current name is accurate enough for now, but long-term intent is explicit IPC naming. Keep the future `ipc/` rename separate from the current stabilization pass. |

**Todos**:
- `rename-planer-to-planner` — rename dir + update all imports, plan references, session.db phase refs
- `rename-css-a2a-to-ipc` — rename dir + update all imports, plan references

---

### 19.3 — Confirmed Removal

| Module | Action | Reason |
|--------|--------|--------|
| `scopes/` | **DELETE** | Already marked `⛔ DEPRECATED` in plan.md. The 5-level SaaS scope hierarchy was removed in favour of `core/workspace/` + `permissions`. Todo `scopes-module-remove` already exists in session.db. |

---

### 19.4 — Confirmed Unification

#### `strategies/` → absorb into `triage/`

`strategies/` is a fully empty stub with no `plan.md` and no code. `triage/` already owns the classification → routing pipeline. Execution strategy selection (ReAct, CoT, plan-and-execute, Tree-of-Thought) is a sub-concern of triage output.

**New structure**: `triage/strategies.py` — strategy enum + selector function, called after triage classification. `triage/plan.md` extended to cover both concerns.

**Why not a separate module**: No code exists yet, and "strategy selection" is a 1-file concern that does not justify its own module lifecycle, registry, and plan.md.

**Todos**:
- `merge-strategies-into-triage` — delete `strategies/` dir, create `triage/strategies.py` with `ExecutionStrategy` enum (REACT, COT, PLAN_AND_EXECUTE, TREE_OF_THOUGHT, DIRECT) + `StrategySelector.select(triage_result) → ExecutionStrategy`, update `triage/plan.md`

#### `capabilities/` — keep separate (not absorbed into `llm_models/`)

`capabilities/` has its own `DynamicCapabilityRegistry` and a 4-source discovery pipeline (hardcoded → env → YAML → provider API). This is non-trivial enough to warrant its own module. Keep separate.

---

### 19.5 — Boundary Clarifications (no code changes, plan.md updates only)

| Module | Issue | Clarification |
|--------|-------|--------------|
| `streaming/` | Has `sessions.py` + `session_linking.py` — scope confusion | These are **streaming sessions** (SSE/WS connection state), NOT agent sessions. Rename internally to `StreamingSession` to avoid confusion with the missing `sessions` module (see 19.6). |
| `memory/` | Generic name overlaps with `context` | Memory = task-scoped working state (findings buffer, scratch). It is a core-owned domain, not a long-term business module. NOT session persistence (that's `sessions`). |
| `tasks/` vs `workflows/` | Both are stubs; boundary unclear | `tasks` = single discrete unit of work (atomic). `workflows` = ordered/conditional sequence of tasks (DAG or linear chain). workflows depends on tasks. |
| `roles/` | Has role enums but unclear if RBAC or agent roles | These are **agent roles** (Orchestrator, TeamLeader, Worker, Planner, Triage), NOT user RBAC. Keep name but clarify in plan.md. |

---

### 19.6 — Missing Modules

Three confirmed missing modules with no existing home:

#### `sessions/` — Session Lifecycle Manager ⚠️ HIGH PRIORITY

Referenced in the workspace layer, `agents`, `tasks`, `planner`, `projects` — but no module owns the `Session` entity itself.

**Responsibilities**:
- `Session` ORM model: `id`, `project_id` (nullable), `agent_id`, `mode`, `status`, `started_at`, `ended_at`, `workspace_root`
- `SessionManager.create(agent_id, mode, project_id?)` → `Session`
- `SessionManager.end(session_id)` → cleanup trigger
- `SessionManager.resume(session_id)` → restore state
- `SessionManager.list(project_id?)` → active/recent sessions
- Filesystem: `~/.css/sessions/<session_id>/` (delegated to `core/workspace/`)
- Connects: `projects.project_sessions` junction table, `core/workspace/`

**todos**: `sessions-module-create`

#### `reports/` — Findings Aggregation & Report Generation

No module currently handles security report output. Needed for any real cybersec workflow.

**Responsibilities**:
- Collect findings from agent sessions (tool results, observations)
- Aggregate by severity, type, target
- Generate structured output: JSON summary, Markdown report, HTML report
- Persist to `~/.css/reports/<session_id>/`
- REST endpoint: `GET /api/reports/{session_id}` (download JSON/Markdown/HTML)

**todos**: `reports-module-create`

#### `notifications/` — Alert Dispatch

No notification layer. Security tools need to push alerts without requiring the user to watch a terminal.

**Responsibilities**:
- Dispatch alerts to multiple channels: WebSocket push (frontend dashboard), webhook (HTTP POST to user-configured URL), log file
- `NotificationLevel` enum: DEBUG / INFO / WARNING / ALERT / CRITICAL
- `Notifier.send(level, message, payload?)` — fan-out to all configured channels
- Connects to `events/` (fires on `css.alert.*` events), frontend live dashboard widget

**todos**: `notifications-module-create`

---

### Phase 19 Todo Summary

| ID | Task | Title | Blocked by |
|----|------|-------|-----------|
| `core-templates-cleanup` | T19.0 | Delete orphaned node_modules in core/templates/ | — |
| `rename-planer-to-planner` | T19.2 | Rename planer/ → planner/ + update all imports/refs | — |
| `rename-css-a2a-to-ipc` | T19.2 | Rename `a2a_internal/` → `ipc/` + update all imports/refs | — |
| `merge-strategies-into-triage` | T19.4 | Delete strategies/, create triage/strategies.py, update triage/plan.md | — |
| `sessions-module-create` | T19.6 | New sessions/ module: Session model, SessionManager CRUD, ~/.css/sessions/ | `working-dir-manager` |
| `reports-module-create` | T19.6 | ~~New reports/ module~~ **→ superseded by Phase 32 (full design)** | `sessions-module-create` |
| `notifications-module-create` | T19.6 | New notifications/ module: alert dispatch WS/webhook/log | `events-core-impl` |
| `docker-compose-cleanup` | T19.7 | Remove dashboard+frontend services + dirs + volume | — |
| `docker-dev-workflow-docs` | T19.7 | Document local dev workflow (bun dev + uv run locally) | — |

**scopes-module-remove** already tracked in session.db — no new todo needed.

### T19.7 — Docker Compose Cleanup (added 2026-05-04)

> `cybersec-dashboard` and `cybersec-frontend` are legacy artefacts. Both removed.
> **Docker is infra-only**: postgres, redis, ollama, openobserve.
> Backend (`uv run uvicorn`) and frontend (`bun dev`) run locally — no Docker needed for the application itself.

**Decision**: Docker = infra only. Application runs locally via `make serve` + `bun dev`.

| ID | Description | Blocked by |
|----|-------------|-----------|
| `docker-compose-cleanup` | Remove `cybersec-dashboard` service + ports/volume/depends_on. Remove `cybersec-frontend` stub. Remove `frontend_node_modules` volume. Delete `.docker/dashboard/` and `.docker/frontend/` directories. | — |
| `docker-dev-workflow-docs` | Add dev/prod workflow to `architecture/frontend.md`. Update vite proxy target from `http://cybersec-proxy:8000` → `http://localhost:8000`. | — |

**Dev workflow (confirmed)**:
```bash
# Terminal 1 — infra only
docker compose up cybersec-postgres cybersec-redis cybersec-ollama cybersec-openobserve

# Terminal 2 — backend
make serve   # uv run uvicorn css.core.asgi.app:app --reload --port 8000

# Terminal 3 — frontend (Vite proxies /api/* /ws/* → localhost:8000)
cd src/frontend && bun dev
```

**Prod workflow (TBD — no planned deployment strategy yet)**:
```bash
cd src/frontend && bun run build   # outputs dist/
# app can serve dist/ as StaticFiles, or deploy separately
```


---

## ✅ Rubber-Duck Report Evaluation (2026-05-04, session ffed87aa)

**Status**: EVALUATED | `consolidate-audit-findings` → marked DONE

The three rubber-duck reports (API services, core infrastructure, modules) from 2026-05-03 have been reviewed. All findings remain valid. Consolidation is complete — reports ARE in plan.md (§ AUDIT FINDINGS). The prohibited `audit-results.md` creation was skipped per whitelist rules.

### Evaluation Summary

| Report | Agent | Findings Still Valid? | Action Taken |
|--------|-------|----------------------|--------------|
| API Services (22 providers) | rubber-duck-1 | ✅ Yes — 12 ready, 10 research needed | Phase 6 T6.2 YAML specs cover Phase 2 order |
| Core Infrastructure (4 components) | rubber-duck-2 | ✅ Yes — ASGI/DB solid, OTEL stub | Phase 4 types reorganization + Phase 6 OTEL bridge |
| Modules (22 modules) | rubber-duck-3 | ✅ Yes — 5/22 ready, 11 pending, 6 stub | Phase 3–8 implementation tiers confirmed |

### New Gaps Identified vs Reports

Since the rubber-duck reports (2026-05-03), Phase 8 audit revealed additional critical gaps:
- `streaming/runner.py` hardcodes Claude — multi-provider routing dead (todos: `ai-provider-routing`)
- `agents/base.py`, `agents/models.py` — 0 LOC (todos: `ai-agent-base-protocol`, `ai-agent-models`)
- `core/triage/` ConfidenceScore hardcoded 0.85 (todo: `ai-triage-ollama-wire`)

These are captured in Phase 8 todos. All rubber-duck report findings are actionable and tracked.

---

## 🚧 Phase 19 — Module Restructuring + Sessions (Expanded)

> Sessions lifecycle and mode-driven layout added to Phase 19 (session ffed87aa)

### T19.6 — New Modules (expanded)

| ID | Task | Description | Depends On |
|----|------|-------------|-----------|
| `sessions-lifecycle` | SessionManager lifecycle + state machine | create/resume/end + active/paused/ended/errored states | — |
| `sessions-mode-layout` | Mode-driven working dir layout | planner (full) / search (findings+artifacts) / minimal (root) | `sessions-lifecycle` |
| `sessions-persistence` | Persist SessionContext to PostgreSQL | SessionRecord ORM: session_id, mode, agent_id, project_dir, status | `sessions-lifecycle` |
| `sessions-endpoints` | FastAPI CRUD for sessions | POST/GET/PATCH /sessions routes, auto-discovered | `sessions-persistence` |
| `sessions-module-create` | Full 5-file sessions/ module | Integrates lifecycle + mode layout + persistence | all above |
| `reports-module-create` | reports/ module | **→ superseded by Phase 32** | `sessions-module-create` |
| `notifications-module-create` | notifications/ module | Alert dispatch: WS push, webhook, log | `events-core-impl` |

---

## 🚧 Phase 20 — Persistent Memory Layer

**Session**: ffed87aa | **Added**: 2026-05-04  
**Todos added**: 12 | **Rationale**: Memory must survive model + provider swaps. In-memory dict → Redis (hot) + PostgreSQL (cold).

### Design

```
User Message → AgentExecutor
    → MemoryManager.retrieve(session_id, token_budget) 
    → ContextAssembler.assemble(entries, provider_id)  ← provider-agnostic
    → LLM call (any provider)
    → MemoryManager.store(MemoryEntry)
    → [async] hot→cold promotion if threshold exceeded
```

**Key invariant**: `MemoryEntry` contains no provider-specific fields. `ContextAssembler` handles format conversion. A session started on Anthropic/Claude can resume on OpenAI/GPT-4o with full context.

### T20.1 — Memory Protocol
- `mem-protocol-struct` — MemoryEntry msgspec.Struct (content, role, session_id, provider_id, model_id, timestamp, token_count, tags)
- `mem-protocol-interface` — MemoryStore Protocol (store/retrieve/evict/clear)

### T20.2 — Hot Tier (Redis)
- `mem-redis-adapter` — RedisMemoryAdapter: sliding window, TTL, msgspec.json serialization
- `mem-redis-token-budget` — Token budget enforcement: trim oldest entries when window full

### T20.3 — Cold Tier (PostgreSQL)
- `mem-pg-model` — ConversationTurn Tortoise ORM model + tsvector FTS index
- `mem-pg-adapter` — PostgresMemoryAdapter: bulk flush + FTS search

### T20.4 — Memory Manager
- `mem-manager` — MemoryManager: warm-up on resume, flush on end, hot→cold promotion
- `mem-context-assembler` — ContextAssembler: MemoryEntry → OpenAI/Anthropic/Gemini message format
- `mem-provider-survival` — E2E test: Anthropic → OpenAI mid-session, all context preserved

### T20.5 — Integration
- `mem-session-wire` — Wire into SessionManager lifecycle hooks
- `mem-agent-wire` — Wire into AgentExecutor pre/post turn
- `mem-module-files` — core-owned memory package surface (types, enums, exceptions, models, endpoints)

---

## 🚧 Phase 21 — Qwen3-0.6B Triage Intelligence

**Session**: ffed87aa | **Added**: 2026-05-04  
**Todos added**: 14 | **Rationale**: Cheap local 0.6B model handles 12 meta-cognitive tasks, saving expensive model calls.  
**Prerequisite**: `ai-triage-ollama-wire` (Phase 8) — must connect Ollama before any Phase 21 features work.

### Feature Overview

| # | ID | Feature | Exotic Factor |
|---|----|---------|--------------|
| 1 | `triage-micro-router` | Micro-Router 2.0 — 4-6 dynamic tags per message in <3s | ★★★★ |
| 2 | `triage-confidence-scorer` | Confidence Scorer — 0-100 per agent response | ★★★★ |
| 3 | `triage-echo-detector` | Echo Detector — detect repeated ideas (n-gram + semantic) | ★★★★ |
| 4 | `triage-intent-drift` | Intent Drift Watchdog — cosine-distance drift alert | ★★★★★ |
| 5 | `triage-tone-adapter` | Tone Adapter — rewrite output to match user tone | ★★★★ |
| 6 | `triage-micro-voter` | Parallel Micro-Voter — 3-5 instances, majority vote, <1s | ★★★★★ |
| 7 | `triage-token-budget-analyst` | Token Budget Analyst — pre-flight cost + cheaper suggestion | ★★★ |
| 8 | `triage-memory-tagger` | Memory Tagger — 7-10 retrieval tags per memory entry | ★★★★ |
| 9 | `triage-paradox-spotter` | Paradox Spotter — detect contradictory instructions | ★★★★ |
| 10 | `triage-fallback-whisperer` | Fallback Whisperer — instant local answer on big model fail | ★★★★★ |
| 11 | `triage-paraphrase-suggester` | Paraphrase Suggester — 2-3 alternatives on echo detection | ★★★★ |
| 12 | `triage-pre-filter` | Pre-Filter — route trivial to 0.6B, escalate complex | ★★★★★ |
| 13 | `triage-graph-rag-entity-projection` | Graph Projection Hook — emit stable entities, ATT&CK hints, and relationships into graph ingest | ★★★★ |

### T21.1 — Micro-Router
- `triage-micro-router` — MessageTagger: async tag() → 4-6 labels in <3s via Qwen3-0.6B

### T21.2 — Quality Gates
- `triage-confidence-scorer` — 0-100 score attached to AgentResult
- `triage-echo-detector` — n-gram + semantic similarity, fires EchoDomainEvent
- `triage-paradox-spotter` — detect contradictory instructions in context

### T21.3 — Conversation Health
- `triage-intent-drift` — embed original goal, alert on cosine drift > threshold
- `triage-tone-adapter` — detect tone → rewrite output (formal/casual/urgent/frustrated/curious)

### T21.4 — Redundancy & Fallback
- `triage-micro-voter` — asyncio.gather() 3-5 Qwen3 instances → majority vote
- `triage-fallback-whisperer` — local Qwen3 response on main model timeout/error

### T21.5 — Cost & Budget
- `triage-token-budget-analyst` — tiktoken estimate + PROVIDER_TIER_LIST cheaper alternatives
- `triage-pre-filter` — integrates with QwenTriageRouter (Phase 13) for TRIVIAL/SIMPLE bypass

### T21.6 — Memory & Context
- `triage-memory-tagger` — 7-10 semantic tags per MemoryEntry (feeds Phase 20 retrieval)
- `triage-paraphrase-suggester` — triggered by EchoDetector, 2-3 diverse rephrasings

### T21.7 — Integration
- `triage-intelligence-wire` — orchestrate all sub-systems in triage/engine.py TriageEngine
- `triage-graph-rag-entity-projection` — emit only stable extracted entities, ATT&CK candidate mappings, confidence-scored links, and provenance into the GraphRAG ingest queue; do not project ephemeral routing state or write directly to Neo4j
- `triage-module-plan-update` — update `src/css/modules/triage/triage.md`

### Dependencies
```
Phase 8: ai-triage-ollama-wire ← all Phase 21 features
Phase 13: routing-qwen-triage-router ← budget analyst + pre-filter
Phase 20: mem-protocol-struct ← memory-tagger
Phase 21: echo-detector ← paraphrase-suggester
Phase 21: triage-intelligence-wire ← micro-router + pre-filter + fallback-whisperer
Phase 21: triage-graph-rag-entity-projection ← triage-intelligence-wire + graph-rag-backend
```

---

## 🚧 Phase 22 — MCP Protocol Layer

**Purpose**: Dedicated `mcps/` module for MCP server management — connecting to any MCP-compatible server, discovering tools, and executing calls. Supports **PYTHON_DIRECT** (in-process bypass, zero HTTP), **STDIO** (subprocess), **SSE**, and **StreamableHTTP** transports.

**Split from tools/**: `@tools` = LLM provider builtin tools. `@mcps` = MCP server connections. MCP tools bridge into ToolRegistry via `McpToolBridge`.

**Key design**: `PYTHON_DIRECT` transport uses `fastmcp.Client(FastMCP_instance)` — passes a FastMCP server object directly, no subprocess, no HTTP, no JSON serialization overhead.

### T22.0 — Documentation
- `mcp-module-plan` — done: `src/css/modules/mcps/mcps.md` now documents the MCP runtime layer, server-scoped IDs, and runtime/tool/marketplace boundaries
- `mcp-tools-plan-update` — done: `src/css/modules/tools/tools.md` now reflects the MCP bridge boundary and current registry reality
- `mcp-rules-update` — done: `mcps` is already present in `rules.md` module inventory

### T22.1 — Foundation Types
- `mcp-enums` — McpTransportType (PYTHON_DIRECT/STDIO/SSE/STREAMABLE_HTTP) + McpServerStatus
- `mcp-exceptions` — McpConnectionError, McpCallError, McpNotFoundError, McpProtocolError
- `mcp-types-struct` — McpServerConfig + McpToolDef + McpCallResult (msgspec.Struct)

### T22.2 — Client
- `mcp-client` — McpClient wrapping fastmcp.Client (all 3 transports, same async API)
- `mcp-python-direct` — PYTHON_DIRECT: `importlib` → FastMCP instance → `Client(instance)` (in-process)

### T22.3 — Registry + Bridge
- `mcp-server-registry` — finish the existing `mcps/registry.py` as `McpRuntimeRegistry` (server config, connect/disconnect, restore/load, tool routing)
- `mcp-tool-bridge` — `McpToolBridge`: register server-scoped MCP tools into `ToolRegistry` as `ToolType.MCP`

### T22.4 — Persistence
- `mcp-models` — Tortoise ORM McpServerConfigRecord (persisted server configs)

### T22.5 — API
- `mcp-endpoints` — FastAPI /api/mcps/* (server CRUD + /tools list + /call proxy)

### T22.6 — Integration
- `mcp-startup-wire` — ASGI startup: load_from_db() + auto_connect + bridge sync
- `mcp-builtin-servers` — register built-in PYTHON_DIRECT servers (cssmcp cybersec)

### Dependencies
```
Phase 9: orm-registry-metaclass-fix ← mcp-server-registry, mcp-tool-bridge, mcp-startup-wire
Phase 3: mod-tools registry ← mcp-tool-bridge
Phase 6: p6-pipeline-asgi ← mcp-startup-wire, mcp-endpoints
mcp-enums + mcp-exceptions + mcp-types-struct ← mcp-client ← mcp-server-registry ← mcp-tool-bridge, mcp-endpoints, mcp-startup-wire
```

---

## 🚧 Phase 23 — Prompt Registry

**Purpose**: Prompts as first-class entities — reusable, versioned, tagged text templates with variable substitution. Separate from MCP. Integrated with the marketplace (`MarketplaceItemType.prompt` already exists).

**Key design**: Pure-Python renderer (no Jinja2), `{{var}}` substitution, `{{> partial_id}}` includes (one level). All types are msgspec.Struct (frozen).

### T23.0 — Documentation
- `prompt-module-plan` — prompts/plan.md (DONE this session)
- `prompt-rules-update` — add prompts to rules.md modules table

### T23.1 — Foundation
- `prompt-enums` — PromptCategory (SYSTEM/USER/FEW_SHOT/CHAIN/PERSONA/INSTRUCTION) + PromptStatus + PromptVariableType
- `prompt-exceptions` — PromptNotFoundError, PromptRenderError, PromptValidationError
- `prompt-types-struct` — PromptVariable + PromptDefinition + PromptRenderResult (msgspec.Struct)

### T23.2 — Engine
- `prompt-renderer` — PromptRenderer: regex-based `{{var}}` + `{{> partial}}` (no Jinja2)
- `prompt-registry` — PromptRegistry singleton: CRUD + render + versioned lookup + search

### T23.3 — Persistence
- `prompt-models` — Tortoise ORM PromptDefinitionRecord (prompt_id+version unique)

### T23.4 — API
- `prompt-endpoints` — FastAPI /api/prompts/* (CRUD + /render + /search + /versions)

### T23.5 — Integration
- `prompt-marketplace-wire` — MarketplaceItemType.prompt install/uninstall ↔ PromptRegistry

### Dependencies
```
prompt-enums + prompt-exceptions + prompt-types-struct ← prompt-renderer ← prompt-registry ← prompt-endpoints, prompt-marketplace-wire
prompt-types-struct + prompt-enums ← prompt-models ← prompt-endpoints
```

---

## 🚧 Phase 24 — Git Tracking & Worktree Isolation

**Core idea**: Every session directory is a git repo. Every agent turn generates a commit. Multiple agents in one session each get their own git worktree + branch — merged at session end.

**Why this is best practice** (confirmed 2024–2025): git worktrees are what Claude Code, Cursor 2.0, Codex CLI all use for parallel agent isolation. "One agent, one branch, one worktree" is the industry standard.

### Are there better methods?

Short answer: **No single better method — but a 3-layer stack is better than worktrees alone:**

| Layer | What it tracks | Technology |
|-------|---------------|------------|
| **L1 — Git commits** | File changes per agent turn | `GitTracker` + worktrees (Phase 24) |
| **L2 — Domain events** | What happened at the model level | CQRS Event Store (Phase 6 P3 — already planned) |
| **L3 — Session turns** | Agent reasoning + conversation | `SessionManager` (Phase 19 — already planned) |

Each layer answers a different audit question. Git alone can't tell you WHY. Event store alone can't diff files. Session turns alone can't replay filesystem state.

**Alternatives evaluated:**
- Full repo clones per agent → slow, redundant; only for deep runtime isolation
- Containers per agent → better runtime isolation but heavy; overkill for Python tool
- Filesystem snapshots (btrfs/zfs) → platform-specific, no history
- Stash-based → serial only, not parallel
- **Verdict**: git worktrees + event store + session turns = best stack

**Legacy note**: `scope.py` already had `worktree_path` field (computed: `/var/css/{runtime_id}/worktree-{session_id}`). This concept is migrated to `core/workspace/` in Phase 24.

### T24.0 — Documentation
- `git-tracking-docs` — update workspace design docs with the git/worktree lifecycle
- `git-rules-update` — add git principles + branch convention to memory.md

### T24.1 — Tracking
- `git-session-init` — init git repo when the session workspace is created
- `git-tracker` — GitTracker: `git add -A && git commit` after each agent turn (fire-and-forget)
- `git-tracker-hook` — wire GitTracker into AgentExecutor via Phase 14 @post_hook

### T24.2 — Worktrees
- `git-worktree-manager` — WorktreeManager: create/delete/list per-agent worktrees + branches
- `git-worktree-sessionmgr` — wire into SessionManager (Phase 19) add_agent/remove_agent lifecycle

### T24.3 — Merge
- `git-merge-manager` — SessionMergeManager: SQUASH/REBASE/OURS/MANUAL strategies; called on session end

### T24.4 — Migration
- `git-scope-migration` — remove worktree_path from deprecated scope.py, adopt `core/workspace/` convention

### Branch Convention
```
agent/{session_id[:8]}/{agent_id}
# e.g. agent/abc12345/recon-agent-1
```

### Dependencies
```
Phase 15: working-dir-manager ← git-session-init ← git-tracker ← git-tracker-hook
Phase 15: working-dir-manager ← git-worktree-manager ← git-merge-manager ← git-worktree-sessionmgr
Phase 19: session-manager-create ← git-worktree-sessionmgr
Phase 15: scopes-module-remove ← git-scope-migration
```

---

## 🚧 Phase 25 — Integration Hardening

**Goal**: Close all inter-module connection gaps found during the connection audit (2026-05-04).

---

### Gap Inventory

| ID | Location | Gap | Severity |
|----|----------|-----|----------|
| A | `css.core.session` | File missing — `SessionContext` referenced by agents, planer, workspace, scopes | CRITICAL (tracked Phase 15 as `session-context-create`) |
| B | `core/db/models/` | ORM models missing: `ProjectRecord`, `McpServerConfigRecord`, `PromptDefinitionRecord` | HIGH |
| C | `core/types/projects.py` | File missing — projects/plan.md references it | HIGH |
| D | `core/types/context.py` | `@dataclass + BaseModel` anti-pattern on 4 classes | HIGH (BLOCKED) |
| E | `` | 5-level ScopeLevel hierarchy (GLOBAL→APP→PROJECT→RUNTIME→SESSION) | RESOLVED (simplified to 2-level: GLOBAL + SESSION) |
| F | `agents/agents.md` | Integration table: stale `project_dir` + missing `prompts` row | MEDIUM |
| G | `events/events.md` | Planned events list missing `project.*`, `settings.changed`, `mcp.call.*` | MEDIUM |
| H | 8 module markdown files | `*(fill in module-specific relationships)*` placeholder tables | MEDIUM |
| I | chat, triage | Integration prose exists, but the module-level boundaries are still not formalized into concise matrices. `llm_proxy` and `workflows` are already covered. | MEDIUM |
| J | cache | Referenced by nobody in integration tables despite being needed by 4+ modules | MEDIUM |

---

### T25.docs — Documentation & Wiring

- `gap-agents-plan-stale` — fix agents/plan.md: rename `project_dir` → `session_dir`, add `prompts` row
- `gap-events-missing-ns` — add `project.*`, `settings.changed`, `mcp.call.*` to events/plan.md planned events
- `gap-integration-placeholders` — fill integration tables for 8 placeholder modules (cache, tags, skills, memory, roles, `a2a_google`, `a2a_internal`, capabilities)
- `gap-triage-integration` — rewrite triage/plan.md integration prose into a concise module-level matrix
- `gap-chat-integration` — rewrite chat/plan.md integration prose into a formal matrix aligned with the WS-first MVP
- `gap-cache-wiring` — add `@cache` row to all consuming module integration tables

### T25.db — Missing ORM Models (routed to module phases)
- `gap-core-types-projects` (Phase 17) — create `core/types/projects.py`
- `gap-orm-projects-models` (Phase 17) — create `ProjectRecord + ProjectSessionRecord` in `core/db/models/projects.py`
- `gap-orm-mcps-models` (Phase 22) — create `McpServerConfigRecord` in `core/db/models/mcps.py`
- `gap-orm-prompts-models` (Phase 23) — create `PromptDefinitionRecord` in `core/db/models/prompts.py`

### Blocked (RESOLVED or dropped)
- Gap E — simplified to 2-level model (Phase 15 Addendum)

### Dependencies
```
naming-clarity-docs → gap-agents-plan-stale
gap-integration-placeholders → gap-cache-wiring
gap-triage-integration → gap-cache-wiring
gap-core-types-projects → gap-orm-projects-models
```

---

## 📐 ORM Naming & Migration Rules (2026-05-04)

> Added to `rules.md` — summarised here for visibility

- **No `Record` suffix**: `LLMModel` not `LLMModelRecord`, `ChatMessage` not `ChatMessageRecord`
- **No Aerich migrations during dev**: `manage.py init-db` = `generate_schemas(safe=False)` + seed fixtures (drop + reseed)
- Migrate to Aerich only after all phases are locked

---

## 🗄️ Database Engineer Audit (2026-05-04)

> Agent: db-engineer | Scope: full DB layer audit — all ORM models, schema design, OpenObserve, seeding, indexes, pooling

---

### Summary

- **16 ORM models** exist across core and modules; **5 are stubs or duplicates** that must be resolved before Phase 17 lands
- **Tortoise is never initialised in ASGI lifespan** — `app.py` calls `close_connections()` on shutdown but never `Tortoise.init()` on startup; the app runs against no DB
- **3 pairs of duplicate enums** (`Severity`/`SeverityLevel`, `Confidence`/`ConfidenceLevel`, `ForensicIOCStatus`/`IOCStatus`) pollute `enums.py`; `ToolType` is an empty enum that will crash on first use
- **OpenObserve is configured but completely unwired** — no client, no stream writes, no flush queue; `AUDIT_LOG_ENABLED` and `TELEMETRY_ENABLED` flags control nothing
- **Seeding plan is well-documented** in plan.md but has zero implementation — `init-db` only calls `generate_schemas()` with no seed logic and startup seeds are absent from lifespan

---

### 🔢 Critical Issues — Execution Order

Fix in this exact order (each unblocks the next):

| # | Todo ID | What | Why first |
|---|---------|------|-----------|
| 1 | `db-dedupe-enums` | Delete `SeverityLevel`, `ConfidenceLevel`, `ForensicIOCStatus`; fix `ToolType` | Enums are imported by models — fix before touching any model |
| 2 | `db-delete-team-stub` | Delete `modules/teams/models.py` (conflicting stub) | Prevents table collision before schema generation |
| 3 | `db-delete-orchestrator-dup` | Delete `modules/teams/orchestrator.py` (duplicate `OrchestratorPoolEntry`) | Same — remove before generate_schemas |
| 4 | `db-fix-pk-permissions` | `PermissionGrant` + `RolePermissionCache` → `BigIntField` PK | Must be correct before any schema drop+reseed |
| 5 | `db-fix-marketplace-item-pk` | `MarketplaceItem.id` → `BigIntField`; add `slug` field | Same |
| 6 | `db-fix-fk-labels-scope` | Fix `SessionScope` FK labels to `css.ProjectScope` / `css.SessionScope` | FK resolution needed for `generate_schemas` to pass |
| 7 | `db-fix-charfield-enums` | All other raw `CharField` status fields → `CharEnumField` | Bulk cleanup |
| 8 | `db-fix-index-tuple-syntax` | All tuple-syntax indexes → `models.Index(fields=[...])` | Must be correct before generate_schemas |
| 9 | `db-asgi-tortoise-init` | Wire `Tortoise.init()` + `generate_schemas()` into ASGI lifespan | **Unblocks everything** — app can now actually use the DB |

After these 10: app boots with a working schema. Then tackle high-priority todos (TaskAssignment updated_at, CacheEntry expires_at, SoftDeleteMixin, ApiServiceProvider expansion).

---

### Critical Issues (fix before Phase 17 lands)

**1. Tortoise never initialised at ASGI startup**
- File: `src/css/core/asgi/app.py` — `lifespan()` only closes connections on shutdown, never calls `Tortoise.init()` or `generate_schemas()` at startup
- Fix: Add `await init_tortoise_db(POSTGRES_DATABASE)` inside the lifespan enter block; optionally call `await Tortoise.generate_schemas(safe=True)` in dev mode; use Aerich in production

**2. `PermissionGrant` and `RolePermissionCache` use `IntField` PK — violates core rule**
- File: `src/css/core/permissions/models.py` lines 10, 43
- Fix: `id = fields.BigIntField(primary_key=True)` on both models

**3. `ScopeSession.id` is a `CharField` PK — non-sequential, not auto-incrementing**
- File: `src/css/core/permissions/models.py` line 27
- Fix: `id = fields.BigIntField(primary_key=True)`; rename current id field to `session_key = fields.CharField(max_length=255, unique=True, db_index=True)`

**4. `MarketplaceItem.id` is a `CharField` PK — violates BigIntField rule**
- File: `src/css/core/db/models/marketplace.py` line 28
- Fix: `id = fields.BigIntField(primary_key=True)`; keep the slug in a separate `slug = fields.CharField(max_length=255, unique=True)` field

**5. `SessionScope` FK references use wrong app label `"models.Project"` / `"models.Session"`**
- File: `src/css/core/db/models/scope.py` lines 66-69
- Tortoise uses app-qualified labels like `"css.ProjectScope"` (matching the key in `build_tortoise_modules()`). `"models.Project"` will resolve to nothing, silently breaking all FK lookups.
- Fix: Change to `"css.ProjectScope"` and `"css.SessionScope"` (verify against actual Tortoise app-name key produced by `build_tortoise_modules()`)

**6. `ScopedEntry.scope_level` is a raw `CharField` — must use `CharEnumField(ScopeLevel)`**
- File: `src/css/core/db/models/scope.py` line 146
- Fix: `scope_level = fields.CharEnumField(ScopeLevel, default=ScopeLevel.SESSION, db_index=True)`

**7. `ToolType` enum is completely empty — will raise `ValueError` on first `CharEnumField` use**
- File: `src/css/core/db/enums.py` line 324
- Fix: Either populate with `BUILTIN = "builtin"`, `MCP = "mcp"`, `HYBRID = "hybrid"`, `EXTERNAL = "external"` or delete until the model field that references it is created

**8. `Team.status` and `OrchestratorInstance.status` use raw `CharField` — should use `CharEnumField`**
- Files: `src/css/core/db/models/team.py` line 31; `src/css/core/db/models/orchestrator.py` line 9
- Fix: Create `TeamStatus(str, Enum)` and `OrchestratorStatus(str, Enum)` in `enums.py`; replace field definitions

**9. `HybridToolDefinition.composition_strategy` uses deprecated `choices=` kwarg — violates CharEnumField rule**
- File: `src/css/modules/tools/models.py` lines 22-29
- Fix: Create `CompositionStrategy(str, Enum)` in tools enums; use `CharEnumField(CompositionStrategy)`

**10. `TeamModel` in `modules/teams/models.py` is a conflicting stub (table `teams_integration`) that partially overlaps with `Team` in `core/db/models/team.py` (table `teams`)**
- File: `src/css/modules/teams/models.py` — entire file
- Fix: Delete `modules/teams/models.py`. If the teams module needs ORM, import from `css.core.db.models.team`. The `teams_integration` table will be created in addition to `teams`, creating orphaned tables.

**11. `OrchestratorPoolEntry` in `modules/teams/orchestrator.py` duplicates `OrchestratorInstance` in `core/db/models/orchestrator.py` with conflicting schemas**
- `OrchestratorInstance.orchestrator_id` = `CharField(128)` (string ID); `OrchestratorPoolEntry.orchestrator_id` = `BigIntField` (int FK) — incompatible
- Both have `related_name="orchestrators"` / `"orchestrator_instances"` on `Team` — will cause related_name collision
- Fix: Choose one canonical model. Recommend: keep `OrchestratorInstance` in `core/db/`; delete `modules/teams/orchestrator.py`

**12. Three duplicate enum pairs in `enums.py` — cause confusion and import drift**
- `Severity` ↔ `SeverityLevel` (identical values, lines 51–64)
- `Confidence` ↔ `ConfidenceLevel` (identical values, lines 67–78)
- `IOCStatus` ↔ `ForensicIOCStatus` (overlapping values, lines 90–103)
- Fix: Keep `Severity`, `Confidence`, `IOCStatus`; delete `SeverityLevel`, `ConfidenceLevel`, `ForensicIOCStatus`; update all import sites

---

### High Priority (Phase 17–19 window)

**1. `TaskAssignment` missing `updated_at` — no way to track status transitions over time**
- File: `src/css/core/db/models/quotas.py`
- Fix: Add `updated_at = fields.DatetimeField(auto_now=True)`

**2. `TeamQuota.daily_reset_at` uses `auto_now_add=True` — reset timestamp should be writable**
- The field is auto-stamped on creation; it should be updated when the daily quota resets, not frozen at row creation time
- Fix: Change to `daily_reset_at = fields.DatetimeField(null=True)` and set/update it in the quota reset service logic

**3. Index tuple syntax used instead of `models.Index()` — silently ignored by some Tortoise versions**
- Files: `cache/models.py` line 27 (`indexes = [("namespace", "key")]`); `tools/models.py` line 96; `marketplace/models.py` lines 47, 67
- Fix: Replace all tuple-syntax index entries with `models.Index(fields=["namespace", "key"])` etc.

**4. `CacheEntryModel` stores `ttl_seconds` but no `expires_at` — TTL queries require full table scan**
- Filtering expired entries requires `WHERE created_at + (ttl_seconds * interval '1 second') < now()` — unindexable
- Fix: Add `expires_at = fields.DatetimeField(null=True, db_index=True)` computed at write time; create partial index `CREATE INDEX ON cache_entry (expires_at) WHERE expires_at IS NOT NULL`

**5. `ApplicationScope` is defined but not exported from `core/db/models/__init__.py`**
- File: `src/css/core/db/models/__init__.py`
- Fix: Add `ApplicationScope` to imports and `__all__`

**6. `ApiServiceProvider` is a stub with only an `id` field — seeding will fail**
- File: `src/css/api_services/models.py`
- This blocks `seed-providers-fixtures` and `seed-models-startup` todos
- Fix: see "Missing ORM Models" section below for full recommended schema

**7. `PermissionGrant.scope_level` and `PermissionGrant.role` are raw `CharField` — no validation**
- File: `src/css/core/permissions/models.py`
- Fix: `scope_level = fields.CharEnumField(ScopeLevel)`; create `RoleEnum` in `enums.py` or use `permissions/enums.py`

**8. `ScopeSession` and `RolePermissionCache` have no indexes on `expires_at` — expiry cleanup is full-scan**
- Fix: Add `db_index=True` to `expires_at` on both models; add partial index `CREATE INDEX ON scope_sessions (expires_at) WHERE expires_at IS NOT NULL`

**9. No `SoftDeleteMixin` abstract class — soft delete pattern duplicated across 4+ models**
- `ProjectScope`, `ApplicationScope`, `SessionScope`, `ScopedEntry` all repeat `is_active + deleted_at`
- Fix: Create `class SoftDeleteMixin(Model)` in `core/db/models/mixins.py` with `is_active`, `deleted_at`, and a `soft_delete()` async method; make the above models inherit from it

**10. `init-db` CLI command creates schemas only — no seed execution**
- File: `src/css/manager.py` lines 83–92
- Fix: After `generate_schemas()`, call seed functions in order: `seed_providers()` → `seed_default_tags()` → `seed_permission_grants()`

---

### ORM Meta Completeness Gaps

| Model | Missing `table` | Missing `table_description` | Missing `ordering` | Missing/broken `indexes` | PK not BigIntField | Raw CharField for enum | Missing `unique_together` |
|---|---|---|---|---|---|---|---|
| `ProjectScope` | ✓ | ✓ (plural only) | ✗ | duplicate: `name` indexed twice | ✓ | — | — |
| `ApplicationScope` | ✓ | ✓ (singular only) | ✗ | `unique_together=["name"]` + field `unique=True` — double constraint | ✓ | — | `name` redundant |
| `SessionScope` | ✓ | ✓ (both) | ✗ | wrong app label in FK; missing `(mode, is_active)` | ✓ | — | — |
| `ScopedEntry` | abstract | — | — | missing `(project_id, scope_level)`, `(session_id, runtime_id)` | — | `scope_level` is raw CharField | — |
| `Team` | ✓ | ✓ | ✓ | ✓ | ✓ | `status` raw CharField | ✓ |
| `TaskAssignment` | ✓ | ✗ | ✗ | missing `(status, assigned_at)` | ✓ | `status`, `priority` raw CharField | — |
| `TaskResult` | ✓ | ✗ | ✗ | — | ✓ | — | — |
| `TeamQuota` | ✓ | ✗ | ✗ | — | ✓ | — | — |
| `OrchestratorInstance` | ✓ | ✗ | ✗ | missing `(status, heartbeat_at)` | ✓ | `status` raw CharField | — |
| `HybridToolDefinition` | ✓ | ✗ | ✓ | missing `(enabled,)`, uses `choices=` | ✓ | `composition_strategy` CharField+choices | — |
| `HybridToolDefinitionTag` | ✓ | ✓ | ✗ | tuple syntax (broken) | ✓ | — | ✓ |
| `CacheEntryModel` | ✓ | ✓ | ✗ | tuple syntax (broken); missing `expires_at` | ✓ | — | — |
| `CacheStatsModel` | ✓ | ✓ | ✗ | no indexes | ✓ | — | — |
| `PermissionGrant` | ✓ | ✗ | ✗ | no explicit indexes (only unique_together) | **IntField** ✗ | `role`, `scope_level` raw CharField | ✓ |
| `ScopeSession` | ✓ | ✗ | ✗ | no indexes | **CharField PK** ✗ | `scope_level`, `role` raw CharField | — |
| `RolePermissionCache` | ✓ | ✗ | ✗ | no indexes | **IntField** ✗ | `scope_level` raw CharField | — |
| `Tag` | ✓ | ✓ (both) | ✓ | — | ✓ | — | `(name)` — slug is unique but name is not |
| `MarketplaceMeta` | ✓ | ✓ (both) | ✓ | missing `(status, update_available)` | ✓ | — | — |
| `MarketplaceItem` | ✓ | ✓ (both) | ✓ | tuple syntax (broken) | **CharField PK** ✗ | — | ✓ |
| `MarketplaceItemTag` | ✓ | ✓ | ✗ | tuple syntax (broken) | ✓ | — | ✓ |
| `ApiServiceProvider` | ✓ | ✗ | ✗ | no indexes | ✓ | — | — |
| `OrchestratorPoolEntry` | ✓ | ✗ | ✗ | — | ✓ | `status` raw CharField | — |
| `TeamModel` (stub) | `teams_integration` ✗ conflicts | ✗ | ✗ | none | ✓ | — | — |

---

### Missing ORM Models (schema recommendations)

**`ApiServiceProvider`** — `src/css/api_services/models.py` (replace stub)
```
table: api_service_provider
purpose: Registry of all 22 LLM API providers + local Ollama
key fields:
  id: BigIntField PK
  slug: CharField(64, unique, db_index)          -- "openai", "anthropic", "ollama"
  display_name: CharField(128)
  is_local: BooleanField(default=False)           -- True for Ollama
  enabled: BooleanField(default=False, db_index)  -- True when API key configured
  base_url: CharField(512, null=True)
  auth_type: CharEnumField(AuthType)              -- api_key, oauth2, none
  supports_streaming: BooleanField(default=True)
  supports_tools: BooleanField(default=False)
  default_model: CharField(128, null=True)
  extra_config: JSONField(default=dict)           -- provider-specific params
  created_at: DatetimeField(auto_now_add)
  updated_at: DatetimeField(auto_now)
indexes: (enabled,), (is_local, enabled), (slug,)
```

**`LLMModelRecord`** — `src/css/core/db/models/llm_models.py` (new file, blocks seed-models-startup)
```
table: llm_model_record
purpose: Per-provider model metadata, costs, capabilities — refreshed at startup
key fields:
  id: BigIntField PK
  provider: ForeignKeyField(ApiServiceProvider, on_delete=CASCADE, db_index)
  model_id: CharField(256, db_index)             -- "claude-3-opus-20240229"
  display_name: CharField(256)
  family: CharEnumField(ModelFamily)
  status: CharEnumField(ModelStatus, default=ACTIVE, db_index)
  tier: CharEnumField(ModelTier, default=STANDARD, db_index)
  context_window: IntField(default=4096)
  max_output_tokens: IntField(default=4096)
  input_cost_per_1k: DecimalField(max_digits=10, decimal_places=6, null=True)
  output_cost_per_1k: DecimalField(max_digits=10, decimal_places=6, null=True)
  supports_streaming: BooleanField(default=True)
  supports_tools: BooleanField(default=False)
  supports_vision: BooleanField(default=False)
  capabilities_json: JSONField(default=list)     -- serialised ModelCapability list
  fetched_at: DatetimeField(null=True)           -- when provider API last returned it
  created_at: DatetimeField(auto_now_add)
  updated_at: DatetimeField(auto_now)
unique_together: [(provider, model_id)]
indexes: (provider_id, status), (status, tier), (provider_id, fetched_at)
```

**`ProviderCapabilityRecord`** — `src/css/core/db/models/capabilities.py` (new file)
```
table: provider_capability_record
purpose: Persisted TTL cache of DynamicCapabilityRegistry results — survives restarts
key fields:
  id: BigIntField PK
  provider: ForeignKeyField(ApiServiceProvider, on_delete=CASCADE, db_index)
  capability_key: CharField(128, db_index)       -- e.g. "tool_use", "vision", "json_mode"
  supported: BooleanField(default=False)
  confidence: FloatField(default=1.0)
  extra_data: JSONField(default=dict)
  checked_at: DatetimeField(db_index)
  expires_at: DatetimeField(db_index)            -- TTL enforcement
  created_at: DatetimeField(auto_now_add)
unique_together: [(provider, capability_key)]
indexes: (expires_at,), partial: (expires_at) WHERE expires_at > now()
```

**`ChatSessionRecord`** — `src/css/modules/chat/models.py` (add alongside dataclasses)
```
table: chat_session
purpose: Persisted chat sessions for history, search, and cross-restart continuity
key fields:
  id: BigIntField PK
  session_uuid: CharField(128, unique, db_index) -- matches ChatSession.session_id
  project: ForeignKeyField(ProjectScope, null=True, on_delete=SET_NULL, db_index)
  title: CharField(512, default="")
  status: CharEnumField(ChatStatus, default=ACTIVE, db_index)
  model_id: CharField(256, null=True, db_index)
  provider_slug: CharField(64, null=True, db_index)
  system_prompt: TextField(default="")
  message_count: IntField(default=0)
  total_tokens: IntField(default=0)
  extra_meta: JSONField(default=dict)
  is_active: BooleanField(default=True, db_index)
  deleted_at: DatetimeField(null=True)
  created_at: DatetimeField(auto_now_add)
  updated_at: DatetimeField(auto_now)
indexes: (project_id, status), (status, updated_at), (model_id, provider_slug)
```

**`ChatMessageRecord`** — `src/css/modules/chat/models.py` (add alongside dataclasses)
```
table: chat_message
purpose: Individual message persistence — enables history recall and token accounting
key fields:
  id: BigIntField PK
  chat_session: ForeignKeyField(ChatSessionRecord, on_delete=CASCADE, db_index)
  role: CharEnumField(ChatRole, db_index)
  message_type: CharEnumField(ChatMessageType)
  content: TextField
  tokens: IntField(default=0)
  extra_meta: JSONField(default=dict)
  created_at: DatetimeField(auto_now_add, db_index)  -- for chronological ordering
ordering: ["created_at"]
indexes: (chat_session_id, role), (chat_session_id, created_at)
```

**`SkillRecord`** — `src/css/modules/skills/models.py` (add alongside dataclasses)
```
table: skill_record
purpose: Persisted skill registry — survives restarts, enables admin management
key fields:
  id: BigIntField PK
  skill_id: CharField(256, unique, db_index)
  name: CharField(256, db_index)
  description: TextField
  category: CharEnumField(SkillCategory, db_index)
  status: CharEnumField(SkillStatus, default=ACTIVE, db_index)
  version: CharField(32, default="1.0.0")
  author: CharField(256, default="")
  parameters_json: JSONField(default=list)       -- serialised SkillParameter list
  dependencies_json: JSONField(default=list)     -- other skill_id strings
  extra_meta: JSONField(default=dict)
  is_builtin: BooleanField(default=False, db_index)
  created_at: DatetimeField(auto_now_add)
  updated_at: DatetimeField(auto_now)
indexes: (category, status), (is_builtin, status)
```

**`SettingRecord`** — `src/css/core/settings/models.py` (Phase 17 T17.1)
```
table: setting_record
purpose: Persisted application settings with scope and validation
key fields:
  id: BigIntField PK
  key: CharField(256, unique, db_index)           -- e.g. "llm.default_model"
  value_json: JSONField                           -- typed value blob
  scope_level: CharEnumField(ScopeLevel, default=GLOBAL, db_index)
  scope_id: CharField(255, default="", db_index) -- project/session id for scoped settings
  is_secret: BooleanField(default=False)
  source: CharField(64, default="user")          -- "user", "config_py", "env", "template"
  created_at: DatetimeField(auto_now_add)
  updated_at: DatetimeField(auto_now)
unique_together: [(key, scope_level, scope_id)]
indexes: (scope_level, scope_id), (source,)
```

**`ProjectRecord`** — `src/css/core/db/models/projects.py` (Phase 17 T17.8)
```
table: project_record
purpose: User-visible project container (distinct from ProjectScope which is scope anchor)
key fields:
  id: BigIntField PK
  slug: CharField(128, unique, db_index)
  name: CharField(256, db_index)
  description: TextField(default="")
  path: CharField(1024, default="")              -- filesystem path
  owner: CharField(256, default="")
  mode: CharEnumField(RedBlueMode, default=BLUE, db_index)
  is_active: BooleanField(default=True, db_index)
  deleted_at: DatetimeField(null=True)
  extra_meta: JSONField(default=dict)
  created_at: DatetimeField(auto_now_add)
  updated_at: DatetimeField(auto_now)
indexes: (is_active, deleted_at), (mode, is_active)
```

**`MemoryEntry`** — core-owned memory model surface in `src/css/core/memory/models.py` (Phase 20 — stub recommended now)
```
table: memory_entry
purpose: Provider-agnostic persistent memory entries for cross-session context recall
key fields:
  id: BigIntField PK
  entry_uuid: CharField(128, unique, db_index)
  session_id: CharField(128, db_index)
  project: ForeignKeyField(ProjectScope, null=True, on_delete=SET_NULL, db_index)
  role: CharEnumField(ChatRole, db_index)         -- user / assistant / system
  content: TextField
  provider_slug: CharField(64, default="", db_index)
  model_id: CharField(256, default="", db_index)
  token_count: IntField(default=0)
  tags: JSONField(default=list)                  -- 7-10 semantic tags per entry
  embedding_id: CharField(256, null=True)        -- future vector store ref
  created_at: DatetimeField(auto_now_add, db_index)
ordering: ["-created_at"]
indexes: (session_id, created_at), (project_id, session_id), (role, session_id)
-- BRIN index candidate: CREATE INDEX ON memory_entry USING BRIN (created_at)
```

---

### OpenObserve Stream Recommendations

OpenObserve is configured in `config.py` (`OPEN_OBSERVE` dict, `ZO_ROOT_USER_*` vars) but **zero client code exists** in `src/css/`. The following work is needed:

**Required client infrastructure** (before any stream can be used):
1. Create `src/css/core/observability/oo_client.py` — thin async HTTP wrapper around OO's `/api/default/<stream>/_json` bulk ingest endpoint
2. Create `src/css/core/observability/queue.py` — in-process `asyncio.Queue` with a background flush task (batch size 100, flush interval 5 s, flush on shutdown)
3. Wire the queue into ASGI lifespan: start flush task on startup, drain on shutdown

**Recommended streams:**

| Stream | Retention | Partition Key | Key Fields | Source |
|---|---|---|---|---|
| `audit_logs` | 365 days | `_timestamp` (BRIN) | action, resource_type, resource_id, actor, scope_level, severity, session_id | every write/delete in ORM services |
| `api_usage_log` | 90 days | `_timestamp` (BRIN) | provider_slug, model_id, input_tokens, output_tokens, cost_usd, status, session_id | LLM proxy after every API call |
| `llm_calls` | 90 days | `_timestamp` (BRIN) | provider_slug, model_id, latency_ms, prompt_tokens, completion_tokens, error, session_id | LLM proxy on completion |
| `agent_runs` | 60 days | `_timestamp` (BRIN) | agent_id, team_id, session_id, task_id, status, duration_ms, tool_calls_count | orchestrator after task completion |
| `chat_turns` | 30 days | `_timestamp` (BRIN) | chat_session_id, role, model_id, tokens, latency_ms | chat module after each turn |
| `events_stream` | 30 days | `_timestamp` (BRIN) | event_type, topic, payload_size, session_id | domain events bus |
| `intel_update_log` | 180 days | `_timestamp` (BRIN) | feed_name, iocs_added, iocs_removed, status | intel update jobs |
| `tool_executions` | 30 days | `_timestamp` (BRIN) | tool_name, tool_type, success, duration_ms, session_id | tool executor |

**What stays in PostgreSQL (not OO):**
- All relational entities: teams, orchestrators, tasks, sessions, permissions, settings, marketplace items
- `MemoryEntry` — structured recall, needs FK joins and rich querying
- `CacheEntryModel` — needs TTL-based point lookups by key
- Any entity with UPDATE/DELETE semantics (OO is append-only)

**TTL strategy per stream:**
- Use OO's `data_stream_settings` API (`max_query_range` + retention policies)
- Define via `PUT /api/default/_stream_settings` at ASGI startup if not already set
- Recommended TTL: audit=365d, intel=180d, api_usage+llm_calls=90d, agent_runs=60d, chat_turns+events+tools=30d

---

### Index Audit

| Model / Table | Missing Indexes | Redundant / Broken |
|---|---|---|
| `permission_grants` | `(role, scope_level)` for role-based lookup; `(expires_at)` if/when added | Only `unique_together` — no separate read indexes |
| `scope_sessions` | `(scope_level, role)`, `(expires_at)` — needed for cleanup jobs | None |
| `role_permission_cache` | `(role, scope_level)`, `(expires_at)` — cache invalidation | None |
| `orchestrator_instances` | `(heartbeat_at)` — stale orchestrator detection; `(created_at)` | None |
| `task_assignments` | `(status, assigned_at)` — time-bucketed status queries; `(completed_at)` | None |
| `cache_entry` | `(expires_at)` where not null — expiry sweep; `(namespace, key, expires_at)` composite | Tuple syntax `[("namespace", "key")]` silently broken |
| `hybrid_tool` | `(enabled,)` — startup tool registry load | None |
| `marketplace_meta` | `(status, update_available)` — update check queries | None |
| `marketplace_item` | FK index on `kind+status` broken (tuple syntax) | `unique_together=(kind, name)` + separate `(kind, status)` index — tuple syntax broken |
| `llm_model_record` (planned) | `(provider_id, status)`, `(status, tier)`, `(fetched_at)` | — |
| `memory_entry` (planned) | BRIN on `created_at`; `(session_id, created_at)` | — |
| `audit_logs` (OO stream) | BRIN on `_timestamp`; regular on `actor`, `action`, `session_id` | — |

**PostgreSQL-specific index recommendations:**
```sql
-- Partial index for non-deleted active records (covers most WHERE clauses)
CREATE INDEX CONCURRENTLY idx_projects_active ON projects (name) WHERE is_active AND deleted_at IS NULL;
CREATE INDEX CONCURRENTLY idx_sessions_active ON sessions (project_id, created_at) WHERE is_active AND deleted_at IS NULL;

-- Partial index for cache expiry sweep (background job)
CREATE INDEX CONCURRENTLY idx_cache_entry_expires ON cache_entry (expires_at) WHERE expires_at IS NOT NULL;

-- BRIN index for time-series tables (very fast inserts, minimal size)
-- (apply once memory_entry and audit log tables reach 100k+ rows)
CREATE INDEX CONCURRENTLY idx_memory_entry_time ON memory_entry USING BRIN (created_at);
CREATE INDEX CONCURRENTLY idx_task_assignment_time ON task_assignments USING BRIN (assigned_at);

-- pg_trgm for free-text search (install extension first)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX CONCURRENTLY idx_marketplace_item_desc_trgm ON marketplace_item USING GIN (description gin_trgm_ops);
CREATE INDEX CONCURRENTLY idx_hybrid_tool_desc_trgm ON hybrid_tool USING GIN (description gin_trgm_ops);
```

---

### Seeding Architecture Review

**Current state**: `init-db` calls `generate_schemas()` only. No seed functions exist anywhere. All 8 seed todos are pending.

**Recommended execution order:**

```
manage.py init-db (run once per environment)
│
├─ 1. generate_schemas(safe=True)           -- creates all tables
├─ 2. seed_providers_fixtures()             -- inserts 22 ApiServiceProvider rows (slug, display_name, is_local, enabled=False)
├─ 3. seed_default_tags()                   -- system tags: severity levels, categories, team modes, sources
└─ 4. seed_permission_grants()             -- admin/orchestrator/agent/viewer default grants

ASGI lifespan startup (every process start)
│
├─ 5. Tortoise.init() + generate_schemas(safe=True)
├─ 6. seed_builtin_tools()                 -- upsert HybridToolDefinition for all builtins
├─ 7. seed_provider_models()               -- foreach provider: call get_models() → upsert LLMModelRecord (skip if no API key)
└─ 8. seed_capabilities()                  -- DynamicCapabilityRegistry.run() → upsert ProviderCapabilityRecord
```

**Idempotency requirements for each seed:**

| Seed | Upsert key | Safe repeat strategy |
|---|---|---|
| `seed_providers_fixtures` | `slug` | `get_or_create(slug=...)` — never overwrite `enabled` field |
| `seed_default_tags` | `slug` | `update_or_create(slug=..., defaults={name, color, description})` |
| `seed_permission_grants` | `(role, scope_level, scope_id)` | `get_or_create(role=..., scope_level=..., scope_id="*")` |
| `seed_builtin_tools` | `name` | `update_or_create(name=..., defaults={...})` — updates definition if changed |
| `seed_provider_models` | `(provider_id, model_id)` | `update_or_create(...)` — always refresh cost/status |
| `seed_capabilities` | `(provider_id, capability_key)` | `update_or_create(...)` — update `checked_at`, `expires_at` |

**Missing from seed plan:**
- `MarketplaceMeta` singleton row (registry metadata)
- Default `SettingRecord` rows once Phase 17 lands
- Default `ProjectRecord` ("default" project) for sessions that don't belong to an explicit project

---

### Connection + Pooling Audit

**Issues found in `src/css/config.py`:**

1. **Two sources of truth for pool size** — `POSTGRES_DATABASE['min_size']=5, max_size=20` AND `DB_POOL_MIN_SIZE=5, DB_POOL_MAX_SIZE=20` env vars. Only the dict is used in `build_tortoise_db_url()` (which ignores `min_size`/`max_size` entirely — they're asyncpg connect args, not URL params).
   - Fix: Pass pool params via Tortoise's `credentials` dict, not the URL. In `manager.py` `init_tortoise_db()`, use `"connections": {"default": {"engine": "tortoise.backends.asyncpg", "credentials": {..., "minsize": 5, "maxsize": 20, "max_queries": 50000, "max_inactive_connection_lifetime": 300}}}` 

2. **No `command_timeout`** — asyncpg default is unlimited. A stuck query will hold a pool connection forever.
   - Fix: Add `"command_timeout": 30` to credentials dict

3. **`max_cacheable_statement_size: 15000` is half the asyncpg default (32768)** — reduces prepared statement cache effectiveness for complex queries.
   - Fix: Either remove (use asyncpg default of 32768) or increase to 32768

4. **`generate_schemas(safe=True)` used as migration strategy** — this is DDL-only, no rollbacks, no version tracking. Safe for dev but must be replaced with Aerich before Phase 17 data migrations.
   - Fix: Add Aerich to dev dependencies; run `aerich init` and `aerich init-db` before Phase 17; keep `generate_schemas` only for test fixtures

5. **Unix socket path hardcoded as `/var/run/postgresql`** in `build_tortoise_db_url()` — not portable to Docker environments where socket path may differ.
   - Fix: Make socket path configurable via `POSTGRES_UNIX_SOCKET` env var

---

### Future-Proofing Recommendations

1. **Partition `task_assignments` by `assigned_at` range once row count > 1M** — use PostgreSQL declarative partitioning by month: `PARTITION BY RANGE (assigned_at)`. Tortoise doesn't manage partitions; add as raw SQL in a migration.

2. **Partition `memory_entry` (Phase 20) by `created_at` from day one** — with 22 providers and frequent usage, memory entries will grow quickly. Design the table as range-partitioned from the start.

3. **Materialized view for team quota summary** — `current_concurrent_tasks` and `daily_tasks_count` in `TeamQuota` are mutable counters updated on every task state change; at scale these become hot rows. Replace with a materialized view `team_quota_summary` refreshed every 60 seconds: `SELECT team_id, COUNT(*) FILTER (WHERE status='running') AS concurrent, ...`

4. **JSONB operators on `task_payload`** — queries like "find all tasks with `task_payload->>'agent_id' = X`" will need a GIN index: `CREATE INDEX ON task_assignments USING GIN (task_payload jsonb_path_ops)`. Document which top-level keys are queryable.

5. **`cache_entry` table will become a hot write table** — at 4 workers × 100 concurrent tasks each caching LLM responses, peak insert rate could hit thousands/sec. Consider: (a) Redis-only for hot cache, (b) Postgres only for cold/archived cache, (c) TTL-based partitioning by `expires_at` month.

6. **`RolePermissionCache` in Postgres is a poor fit** — permission caches belong in Redis with a short TTL (60–300 s). The Postgres table will be hit on every request and is a potential bottleneck. Recommend: delete this ORM model, use Redis via the `@cache` module with `namespace="permission_cache"` and a 300 s TTL.

7. **`pg_trgm` extension for marketplace/tool search** — users will search by description and name. Without pg_trgm, all text searches are full-table scans. Install the extension and add GIN trigram indexes (see Index Audit section).

8. **Consider BRIN indexes on all `created_at` columns in append-heavy tables** (task_assignments, audit traces, memory entries) — BRIN is 10–100× smaller than B-tree for monotonically increasing timestamps and has near-zero insert overhead.

9. **Add `CHECK` constraints for enum-ish CharField columns** until they're migrated to `CharEnumField` — e.g., `ALTER TABLE teams ADD CONSTRAINT teams_status_check CHECK (status IN ('pending', 'active', 'paused', 'completed'))`. This catches application bugs before data corruption.

10. **Plan for schema versioning** — before Phase 17 adds `SettingRecord` and `ProjectRecord`, set up Aerich (`aerich init -t css.manager.TORTOISE_ORM`), generate baseline migration 0001, and enforce "no raw `generate_schemas()` in production" in CI.

---

### Quick Wins (< 30 min each)

- **Fix `PermissionGrant` + `RolePermissionCache` PK** — 2-line change per model, prevents silent BigInt overflow on busy systems
- **Fix all tuple-style index definitions** — 4 files, global replace `[("a", "b")]` → `[models.Index(fields=["a", "b"])]`; 10 min total
- **Delete `modules/teams/models.py`** (stub with conflicting table name) — 30 seconds; prevents phantom `teams_integration` table from being created
- **Add `ApplicationScope` to `core/db/models/__init__.py` exports** — 2-line change
- **Delete `SeverityLevel`, `ConfidenceLevel`, `ForensicIOCStatus` from `enums.py`** — removes 15 lines of dead enum definitions; grep import sites first
- **Add `updated_at = fields.DatetimeField(auto_now=True)` to `TaskAssignment`** — 1-line change, critical for audit trail
- **Fix `TeamQuota.daily_reset_at`** from `auto_now_add=True` to `null=True` — prevents frozen reset timestamps
- **Wire `Tortoise.init()` into ASGI lifespan** — without this the entire app runs DB-less; ~10 lines in `app.py`
- **Add `expires_at` to `CacheEntryModel`** — 1-line field addition; enables `WHERE expires_at < now()` expiry sweep with an index
- **Add `command_timeout: 30` to asyncpg credentials** — prevents pool starvation from hung queries


---

## 🚧 Phase 20 — Persistent Memory Layer (Expanded)

> **Updated**: 2026-05-04 — added Canvas, Vault, semantic search, and compression tiers.
> Original 12 todos (T20.1–T20.5) unchanged. New tasks added as T20.6–T20.8.

### T20.6 — Canvas (Agent Working Scratchpad)

Canvas = structured mutable workspace per session. Agent writes intermediate findings, hypotheses, scratch notes. Survives turn boundaries but scoped to one session. Backed by Redis (hot) with PostgreSQL flush.

Existing stubs: `memory/canvas/generator.py`, `memory/canvas/canvas_validate.py`

- `mem-canvas-model` — `CanvasBlock` msgspec.Struct: block_id, type (text/code/table/finding), content, created_at, updated_at, author_agent
- `mem-canvas-manager` — CanvasManager: create/read/update/delete blocks, render to markdown, flush to DB on session end
- `mem-canvas-orm` — `Canvas` + `CanvasBlock` Tortoise ORM models, `canvas_blocks` table with session FK
- `mem-canvas-wire` — wire into AgentExecutor: inject CanvasManager into agent context; blocks visible to all agents in same session

### T20.7 — Vault (Persistent Cross-Session Knowledge)

Vault = long-lived, cross-session, cross-provider knowledge base. Facts, patterns, findings that outlive individual sessions. Backed exclusively by PostgreSQL. Optionally: Obsidian markdown on disk (existing vault manager handles this).

Existing stubs: `memory/vault/manager.py` (Obsidian scaffold), `memory/vault/hot_cache.py`

- `mem-vault-orm` — `VaultEntry` Tortoise ORM model: entry_id, project_id (FK, nullable), title, content, tags (JSONB), source_session, confidence, embedding (pgvector), created_at
- `mem-vault-backend` — VaultBackend: store/retrieve/search by tag + semantic (pgvector cosine), cross-session visibility
- `mem-vault-wire` — wire into MemoryManager as 3rd tier: hot (Redis) → cold (PG ConversationTurn) → vault (PG VaultEntry)
- `mem-vault-obsidian-bridge` — bridge VaultEntry ↔ existing VaultManager Obsidian files: bidirectional sync on session end

### T20.8 — Semantic Search & Compression

- `mem-pgvector-setup` — enable `pgvector` extension; add `embedding vector(1536)` to `ConversationTurn` and `VaultEntry`; wrap embedding generation behind `EmbeddingProvider` Protocol (OpenAI text-embedding-3-small or local nomic-embed-text via Ollama)
- `mem-compression` — EpisodicCompressor: when cold tier > N turns, summarise oldest K turns into a single `MemoryEntry(type=SUMMARY)` using cheapest available LLM; store summary, discard originals. Keeps context window lean across long sessions.
- `mem-memory-tagger-hook` — hook point for Phase 21 `triage-memory-tagger`: after every store(), call MemoryTagger.tag(entry) async (fire-and-forget), update entry tags in place

### T20.9 — Hybrid Retrieval Core (VectorRAG + GraphRAG)

- `rag-core-ownership` — promote the shared `rag_vector` runtime into `src/css/core/rag_vector/` as the vector retrieval + hybrid orchestration package; domain ingestion stays out of this layer
- `rag-cache-layer` — retrieval cache layer via `core/cache`: embeddings, vector hits, graph traversals, fused results, route hints, TTL policy, and ingest/update invalidation
- `graph-rag-core-ownership` — create `src/css/core/rag_graph/` as the dedicated GraphRAG subsystem with package surface, types, ingest/query boundaries, and local plan doc
- `rag-vector-backend` — VectorRagBackend in `core/rag_vector/`: PostgreSQL + pgvector for document/chunk storage, embedding lookup, filters, similarity search, and normalized results
- `graph-rag-backend` — GraphRagBackend in `core/rag_graph/`: Neo4j-backed entity/relationship ingest plus neighbor/path/community retrieval with provenance-preserving materialization
- `rag-query-modes` — `RetrievalMode` selection with manual `vector` / `graph` / `hybrid` toggles plus an initial `auto` routing policy and a later hook for Phase 21 triage
- `rag-fusion-layer` — merge, rerank, deduplicate, and preserve provenance across `rag_vector` + `rag_graph` results into one normalized retrieval payload
- `rag-context-wire` — wire hybrid retrieval into `ContextAssembler`, memory-backed context assembly, and agent execution so callers receive retrieval evidence before model invocation

**Routing note**: `auto` mode should work with a simple routing policy first. Later, Phase 21 intelligence/triage can participate in backend choice for complex requests.

### Dependencies (Phase 20 expanded)
```
mem-protocol-struct → mem-canvas-model, mem-vault-orm, mem-pgvector-setup
mem-pg-model → mem-canvas-orm, mem-vault-orm
mem-canvas-manager → mem-canvas-orm
mem-vault-backend → mem-vault-orm
mem-pgvector-setup → mem-compression, mem-vault-backend, rag-vector-backend
mem-manager → mem-canvas-wire, mem-vault-wire
rag-core-ownership → rag-cache-layer, rag-vector-backend
rag-core-ownership → graph-rag-core-ownership
rag-cache-layer → rag-vector-backend, graph-rag-backend
graph-rag-core-ownership → graph-rag-backend
rag-vector-backend + graph-rag-backend → rag-query-modes → rag-fusion-layer
mem-context-assembler + mem-agent-wire + rag-fusion-layer → rag-context-wire
rag-context-wire → Phase 29 domain-rag-ingestion
Phase 21: triage-memory-tagger → mem-memory-tagger-hook
Phase 21: intelligence/triage may later inform `AUTO` retrieval-mode choice
```

---

## 🚧 Phase 26 — Human Approval Workflows

**Session**: ffed87aa | **Added**: 2026-05-04  
**Rationale**: High-risk agentic actions (tool calls, file writes, network ops) must pause and surface to a human for approve/reject before proceeding. Critical for red-team and production deployment.

### Design

```
AgentExecutor.run_tool(tool, args)
    → ApprovalGate.check(tool, args, session, permissions)
        → policy match? → REQUIRED / ALLOWED / DENIED
        REQUIRED:
            → ApprovalRequest.create(status=PENDING, timeout=300s)
            → EVENT approval.requested (→ WebSocket push to frontend)
            → await ApprovalChannel.wait(request_id, timeout)
                  ← POST /approvals/{id}/approve|reject from user
            → APPROVED  → continue tool execution
            → REJECTED  → raise ApprovalDeniedError
            → TIMEOUT   → apply policy.timeout_action (auto-reject / auto-approve / escalate)
```

### T26.1 — Approval Protocol

- `approval-protocol` — `ApprovalRequest` msgspec.Struct: id (UUID), session_id, agent_id, action_type, action_payload, status (PENDING/APPROVED/REJECTED/EXPIRED), created_at, decided_at, decided_by, timeout_seconds, reason
- `approval-policy` — `ApprovalPolicy` dataclass: scope (global/project/session), action_patterns (glob), roles_exempt, timeout_action (REJECT|APPROVE|ESCALATE), timeout_seconds

### T26.2 — ORM Models

- `approval-orm` — `ApprovalRequest` Tortoise ORM model: table `approval_requests`, BigIntField PK, session FK, status CharEnumField(ApprovalStatus), action_type CharField(128), action_payload JSONB, decided_by CharField(nullable), expires_at DatetimeField indexed
- `approval-policy-orm` — `ApprovalPolicy` Tortoise ORM model: table `approval_policies`, scope CharEnumField(ScopeLevel), action_pattern CharField(256), roles_exempt JSONB, timeout_seconds IntField, seed defaults at init-db

### T26.3 — Approval Gate

- `approval-gate` — ApprovalGate service: `check(action_type, payload, context)` → resolves policy, returns `ApprovalDecision(gate=REQUIRED|ALLOWED|DENIED, policy_id)`
- `approval-channel` — ApprovalChannel: asyncio.Event per pending request_id; `wait(id, timeout)` suspends coroutine; WebSocket message from frontend resolves it
- `approval-timeout-handler` — background task sweeping `expires_at < now()` pending requests; applies `timeout_action`

### T26.4 — API Endpoints

- `approval-endpoints` — FastAPI router `/approvals/`:
  - `GET /approvals/pending?session_id=` — list pending requests visible to current user
  - `GET /approvals/{id}` — get single request with payload
  - `POST /approvals/{id}/approve` — sets APPROVED, resolves channel event, logs audit
  - `POST /approvals/{id}/reject` — sets REJECTED + reason, resolves channel event
  - `GET /approvals/history?session_id=&limit=` — paginated decision history

### T26.5 — WebSocket Push

- `approval-ws-push` — on `approval.requested` event → push `{type: "approval_required", request: {...}}` over session WebSocket; on resolution → push `{type: "approval_resolved", ...}`. Frontend shows inline approval card.

### T26.6 — Integration

- `approval-agentexecutor-wire` — wire ApprovalGate.check() into AgentExecutor before every `run_tool()` call; raise `ApprovalDeniedError` on rejection; handle `ApprovalRequiredError` suspension
- `approval-permissions-wire` — extend PermissionGrant: add `requires_approval: bool` column; ApprovalGate reads this as part of policy resolution
- `approval-events` — define `approval.requested`, `approval.approved`, `approval.rejected`, `approval.expired` event namespaces in events module
- `approval-module-files` — create `modules/approvals/` with full 5-file pattern; register in Tortoise app modules

### T26.7 — Audit

- `approval-audit-stream` — every APPROVE/REJECT/EXPIRE decision → emit to OpenObserve `approvals_log` stream: request_id, agent_id, action_type, decision, decided_by, latency_seconds
- `approval-seed-policies` — `init-db` seeds default policies: all file-write tools REQUIRED, all network tools REQUIRED in red-mode, all read-only tools ALLOWED

### Dependencies
```
Phase 14: events module → approval-events
Phase 15: permissions → approval-permissions-wire
Phase 20: mem-session-wire → approval-agentexecutor-wire (need session context)
Phase 26: approval-orm → approval-gate
Phase 26: approval-gate → approval-channel → approval-agentexecutor-wire
Phase 26: approval-endpoints → approval-ws-push
Phase 26: approval-audit-stream → db-oo-stream-definitions (Phase 27 OO work)
```

---

## 🚧 Phase 27 — Graph Visualization Engine

**Session**: ffed87aa | **Added**: 2026-05-04  
**Rationale**: Two independent graph tracks that share the same rendering pipeline:
1. **Telemetry graphs** — OpenObserve time-series → charts (token costs, latency, error rates)
2. **Workflow graphs** — Agent DAGs, session flows, tool call trees, multi-agent orchestration (live + historical)

### Design

```
                     ┌─────────────────────────────┐
Telemetry track:     │  OpenObserve streams         │
                     │  → GraphDataService.query()   │
                     │  → TimeSeriesGraph{nodes,data}│
                     └──────────┬──────────────────┘
                                │ JSON (nodes + edges + series)
Workflow track:      ┌──────────▼──────────────────┐
                     │  PostgreSQL (sessions,        │
                     │  task_assignments, events)    │
                     │  → WorkflowGraphBuilder       │
                     │  → DAGGraph{nodes, edges}     │
                     └──────────┬──────────────────┘
                                │
                     ┌──────────▼──────────────────┐
                     │  WebSocket / SSE             │ ← live updates
                     │  GET /graphs/{type}/{id}     │ ← snapshot
                     └──────────┬──────────────────┘
                                │
                     ┌──────────▼──────────────────┐  Frontend
                     │  React Flow (DAG/workflow)   │
                     │  Recharts (telemetry series) │
                     └─────────────────────────────┘
```

### T27.1 — Graph Protocol

- `graph-protocol` — `GraphNode` + `GraphEdge` + `GraphSnapshot` msgspec.Structs: provider-agnostic, serialisable to JSON; node types: agent, tool, session, decision, approval, llm_call
- `graph-types` — GraphType enum: `WORKFLOW_DAG`, `SESSION_FLOW`, `TOOL_CALL_TREE`, `AGENT_DEPENDENCY`, `TELEMETRY_COST`, `TELEMETRY_LATENCY`, `TELEMETRY_ERRORS`, `APPROVAL_FLOW`

### T27.2 — Workflow Graph Builder (PostgreSQL-backed)

- `graph-workflow-builder` — WorkflowGraphBuilder: reads TaskAssignment + OrchestratorInstance + sessions tables → builds DAGGraph. Nodes = agents/tools, edges = calls/dependencies, weights = latency/token count
- `graph-session-flow` — SessionFlowBuilder: per-session turn-by-turn graph: user→agent→tool→result→agent chain. Reads from MemoryManager cold tier (ConversationTurn) + task_assignments
- `graph-approval-flow` — ApprovalFlowBuilder: overlay approval gate nodes on workflow DAG (gate → pending → approved/rejected)
- `graph-snapshot-orm` — `GraphSnapshot` Tortoise ORM model: snapshot_id, graph_type, ref_id (session/project), data JSONB, created_at. Table `graph_snapshots`. Used for history playback.

### T27.3 — Telemetry Graph Service (OpenObserve-backed)

- `graph-telemetry-service` — GraphTelemetryService: queries OO streams (`llm_calls`, `api_usage_log`, `approvals_log`) via OO SQL API → transforms to time-series format
- `graph-cost-chart` — CostChart: per-provider, per-model, per-session token cost over time → `{provider, model, tokens, cost_usd, timestamp}` series
- `graph-latency-chart` — LatencyChart: p50/p95/p99 latency by model and tool type over time
- `graph-error-chart` — ErrorRateChart: error counts by provider + error type (timeout, rate_limit, auth_fail, context_overflow)

### T27.4 — Real-time Streaming

- `graph-ws-stream` — GraphStream WebSocket endpoint: `WS /ws/graphs/{graph_type}/{ref_id}` — subscribes to live graph diffs; on new TaskAssignment/event → recompute delta → push `{type: "graph_patch", nodes_added, edges_added, nodes_updated}` 
- `graph-sse-endpoint` — SSE fallback: `GET /graphs/stream/{type}/{id}` for clients without WebSocket support

### T27.5 — REST API

- `graph-endpoints` — FastAPI router `/graphs/`:
  - `GET /graphs/workflow/{session_id}` — full session workflow DAG snapshot
  - `GET /graphs/telemetry/{type}?window=1h|24h|7d&project_id=` — telemetry chart data
  - `GET /graphs/snapshots/{ref_id}` — list historical snapshots
  - `POST /graphs/snapshots` — manually save current state as named snapshot

### T27.6 — Frontend Rendering

- `graph-react-flow` — WorkflowGraph React component using React Flow: renders agent DAGs with live patch subscription. Nodes coloured by type (agent=blue, tool=green, approval=orange, error=red).
- `graph-recharts` — TelemetryDashboard React component: cost/latency/error charts using recharts. Shared time axis, period selector (1h/24h/7d).
- `graph-approval-overlay` — ApprovalOverlay component: renders pending approval gates on workflow graph with approve/reject buttons inline (connects to Phase 26 approval WebSocket).

### T27.7 — Integration

- `graph-events-wire` — subscribe to `task.assigned`, `tool.called`, `tool.completed`, `approval.requested`, `approval.resolved`, `llm.response` events → feed WorkflowGraphBuilder live diffs
- `graph-openobserve-wire` — GraphTelemetryService uses OO client from `db-oo-client-implementation`
- `graph-module-files` — create `modules/graphs/` with full 5-file pattern; register router

### Dependencies
```
Phase 14: events module → graph-events-wire
Phase 26: approval-events → graph-approval-flow, graph-approval-overlay
Phase 27: graph-protocol → graph-workflow-builder, graph-telemetry-service
Phase 27: graph-workflow-builder → graph-session-flow, graph-approval-flow
Phase 27: graph-snapshot-orm → graph-endpoints (history)
Phase 27: graph-ws-stream → graph-react-flow (live updates)
db-oo-client-implementation → graph-telemetry-service
db-oo-stream-definitions → graph-telemetry-service
```

---

---

## 🔍 Feature Gap Analysis (2026-05-04)

> Full overview audit — what exists in plan vs what a production cybersec AI platform needs.

---

### ✅ Well-Covered (phases + todos + design)

| Area | Phase(s) |
|------|---------|
| Multi-orchestrator teamscope | 0–1 |
| SDK provider architecture (22 providers) | 2, 10, 16 |
| Persistent memory (hot/cold/vault/canvas) | 20 |
| MCP protocol | 22 |
| Prompt registry | 23 |
| Git worktree isolation | 24 |
| Triage intelligence (Qwen3-0.6B) | 21 |
| Approval workflows | 26 |
| Graph visualization | 27 |
| Permissions + RBAC | 15 |
| Event hooks + OTEL | 14 |
| Provider routing + resilience | 13 |
| Settings + Projects | 17 |
| Frontend foundation | 18 |

---

### 🔴 Critical Gaps (blocking basic usability)

**G1 — No Auth Module** (Phase 7 todo, no dedicated phase, no design)
- Zero JWT/session auth anywhere. Every API endpoint is currently open.
- `feat-auth-module` todo exists but has no T-tasks, no ORM model design, no middleware design.
- **Missing**: `modules/auth/` — JWT issue/verify, API key hash storage, `Depends(get_current_user)` FastAPI dependency, refresh token rotation.
- Blocks: `feat-accounts-module`, every endpoint that should be protected (approvals, settings, sessions, tasks, permissions).

**G2 — No User/Account Model** (Phase 7 todo only)
- Platform is multi-agent but there's no concept of _who is using it_.
- **Missing**: `core/accounts/` — `User` ORM model (id, email, hashed_password, api_key_hash, roles, is_active), `AccountManager`, registration + invite flow.
- Blocks: audit trail (`decided_by` in approvals), multi-user project isolation, permission grants scoped to users.

**G3 — WebSocket lifecycle unspecified**
- `frontend-ws-manager` todo (Phase 18) covers reconnect, but no server-side WS session management documented.
- **Missing**: WS heartbeat/ping-pong (keepalive), graceful reconnect with session resume (re-join same stream), per-session WS broadcast group, max connections per session limit.
- Affects: chat, graph live stream, approval push, notification push.

---

### 🟠 High-Priority Gaps (cybersec platform purpose)

**G4 — Cybersec Domain Modules have no phase** (19 todos in Phase 7, no T-tasks, no design)

All of these are single-line todos with no implementation plan:

| Module | Missing | Why critical |
|--------|---------|-------------|
| `incidents` | ORM, lifecycle, REST, severity → notifications | Core purpose of the platform |
| `threat_intel` | IOC model, feed pull (MISP/OTX/VT), enrichment | Threat hunting without IOCs is useless |
| `mitre` | ATT&CK matrix import, tactic→technique mapping, incident tagging | Forensic narrative requires this |
| `scans` | Scan lifecycle, target→team→findings pipeline | Bridges agents to deliverables |
| `evidence` | Chain-of-custody, hash verification, collector attribution | Legal admissibility |
| `knowledge` | RAG pipeline, pgvector, CVE/PDF/playbook ingestion | LLM agents are blind without RAG |
| `compliance` | NIST/SOC2/ISO27001 control mapping, coverage % | Compliance reports are primary deliverable |
| `reports` | Jinja2 → MD/HTML/PDF, ExecutiveSummary, TechnicalFindings | Sessions produce nothing exportable today |

→ Needs **Phase 28 — Cybersec Domain Layer** with full T-tasks for each module.

**G5 — Workflow Engine is empty** (`modules/workflows/plan.md` = "TODO: Everything")
- Multi-agent pipeline orchestration — defining a DAG of steps, retries, conditional branches — has zero implementation plan.
- **Missing design**: `WorkflowDefinition` (steps, edges, conditions), `WorkflowRunner` (async DAG executor), `WorkflowState` persistence, suspend/resume, timeout per-step, failure handling.
- Different from `teams/` (runtime agents) — this is the _definition layer_ of "how should agents collaborate".
- → Needs dedicated **Phase 29 — Workflow Engine**.

**G6 — IPC / Agent-to-Agent protocol has no phase**
- Phase 19 plans `a2a_internal` → `ipc` but still gives no design for what IPC actually does.
- `a2a_internal/dispatcher.py` = 3 LOC re-export stub. No actual dispatch logic.
- **Missing**: in-process message bus (asyncio queues), cross-process via Redis pub/sub, message schema (`IPCMessage` msgspec.Struct), agent address book (who is reachable), broadcast vs unicast.
- → Belongs in **Phase 29 — Workflow Engine** (IPC is the communication layer for workflow steps).

**G7 — Planner module has no design** (`planer/` = empty, Phase 19 only renames it)
- Phase 15 Addendum references a `planner` mode with full working dir layout. But the actual Planner logic — decompose goal → subgoals → assign to agents — has no design.
- **Missing**: `PlannerAgent` class, goal decomposition prompt chain, subgoal → task assignment, progress tracking (which subgoals done), re-planning on failure.
- → Belongs in **Phase 29 — Workflow Engine**.

---

### 🟡 Medium Gaps (production-readiness)

**G8 — API key / secrets management for 22 providers**
- Provider API keys are in `.env` / `config.py` at startup. No way to:
  - Add/rotate a key without restart
  - Scope a key to a project/user
  - Track which key was used for which call (for billing separation)
- `settings` module (Phase 17) covers config overrides, but API keys are secrets — they need different storage (encrypted at rest, never logged, audit trail on access).
- **Missing**: `modules/secrets/` or extend `settings` with a `SettingType.SECRET` variant that encrypts value at rest (using `cryptography.fernet` or PG pgcrypto) and redacts from logs/API responses.

**G9 — Rate limiting has no dedicated implementation**
- `ai-rate-limiting` is a single todo. `routing-rate-limiter` (Phase 13) covers per-provider RPM/TPM token-bucket.
- **Missing**: per-user rate limiting at the API layer (FastAPI middleware), per-project quota enforcement (link to `TeamQuota`), 429 response with `Retry-After` header, burst allowance.

**G10 — Task queue mechanism undefined**
- `TaskAssignment` ORM exists. But _how does a task get picked up_ by an orchestrator?
- No queue implementation: no Redis list pop, no asyncio.Queue, no APScheduler integration.
- `feat-scheduler-module` (Phase 7) is a single todo with no design.
- **Missing**: `TaskQueue` abstraction — push/pop with priority, worker pull loop in orchestrator, dead-letter queue for failed tasks (max_retries exceeded → DLQ), visibility timeout (task "locked" while processing).

**G11 — Configuration persistence gap**
- `settings` module (Phase 17) designs `SettingRecord` ORM. But `config.py` currently causes import-time side effects (mkdir on CACHE_DIR/LOG_DIR at module load). No bridge between the two.
- **Missing**: bootstrap migration — on first startup, seed `SettingRecord` table from env vars; on subsequent startups, `SettingRegistry` overrides env-defaults from DB. Prevents config.py creep.

**G12 — LLM proxy module missing**
- This is now promoted into **Phase 36 — Local Proxy & Transport Surfaces**.
- `modules/llm_proxy` is planned as an **in-process local facade**, not a separate service.
- Remaining work is implementation, not architecture ownership: `/v1/*` compatibility breadth, routing bridge, streaming normalization, and local trust boundary.

**G13 — Streaming multi-provider gap**
- `streaming/runner.py` hardcodes Claude (tracked as `ai-provider-routing` in Phase 8).
- Phase 36 now adds an explicit transport split (`/ws/*`, `/sse/*`, `/v1/*`) plus streaming normalization work, but provider delta compatibility and cancellation behavior still need implementation.

---

### 🔵 Low / Future Gaps

**G14 — No deployment strategy**
- Docker is infra-only (decided). But: how is the app deployed in production? No Dockerfile for the ASGI app, no `gunicorn` config, no nginx reverse proxy plan, no SSL termination, no environment promotion (dev → staging → prod).
- "Prod workflow" in Phase 19 section says "TBD".

**G15 — OpenAPI schema / developer docs absent**
- FastAPI auto-generates OpenAPI. But no customisation: no tags, no security scheme definition, no response model annotations on most routes. The generated schema is unusable.
- **Missing**: consistent use of `response_model=`, `tags=`, `summary=`, `security=` across all routers.

**G16 — Plugin/marketplace install-on-runtime undefined**
- `marketplace/` handles metadata and discovery. But "install" = what exactly? Copy files to `installed-plugins/`? Validate sha512? Reload module loader?
- No plan for hot-reload of marketplace items without restart.

**G17 — Multi-tenancy isolation**
- Multiple users can log in (once auth exists). But project/session data isolation at DB level is not designed: all users see all projects. No row-level security (PG RLS) plan, no `user_id` FK on projects/sessions.

**G18 — Alerting / notifications has no implementation design**
- `notifications-module-create` (Phase 19) is 1 todo. `feat-alerts-module`, `feat-webhooks-module` (Phase 7) are 2 todos. Combined: 3 todos, no T-tasks, no ORM, no schema.
- For a security platform this is critical: on high-severity incident → push to Slack/PagerDuty.

---

### 📋 Missing Phases Summary

| New Phase | Contents | Dependencies |
|-----------|---------|-------------|
| **Phase 28 — Auth & Accounts** | `modules/auth/` (JWT, API keys), `core/accounts/` (User ORM, profiles), row-level project isolation | Phase 15 (permissions), Phase 17 (settings/projects) |
| **Phase 29 — Cybersec Domain Layer** | incidents, threat_intel, mitre, scans, evidence, compliance, reports, cybersec retrieval ingestion on top of `core/rag_vector/` + `core/rag_graph/`, including MITRE/threat-intel graph projections | Phase 20 (hybrid retrieval core), Phase 28 (auth), Phase 14 (events) |
| **Phase 30 — Workflow Engine + IPC** | `modules/workflows/` DAG engine, `modules/ipc/` (A2A messaging), `modules/planner/` (goal decomposition) | Phase 20 (memory), Phase 26 (approvals), Phase 14 (events) |
| **Phase 31 — Production Readiness** | Secrets management, rate limiting, task queue, deployment Dockerfile, OpenAPI polish, alerting/webhooks, multi-tenancy RLS | Phase 28 (auth), Phase 26 (approvals), Phase 27 (graphs) |

---

---

## Phase 32 — Reports Module

**Status**: Planned | **Sort order**: 32
**Supersedes**: `feat-reports-module` (Phase 7), `reports-module-create` (Phase 19), `domain-reports` (Phase 29 placeholder)

> After red/blue/purple team sessions, scan runs, or incident investigations, there is currently no way to produce a deliverable. Phase 32 builds the full reports pipeline: data collection → template rendering → multi-format export → artifact storage → REST delivery.

---

### ORM Models (`modules/reports/models.py`)

```python
class ReportType(str, Enum):
    EXECUTIVE_SUMMARY    = "executive_summary"
    TECHNICAL_FINDINGS   = "technical_findings"
    INCIDENT_TIMELINE    = "incident_timeline"
    COMPLIANCE_MAPPING   = "compliance_mapping"
    VULNERABILITY_SUMMARY = "vulnerability_summary"
    THREAT_INTEL_BRIEF   = "threat_intel_brief"

class ReportFormat(str, Enum):
    MARKDOWN = "markdown"
    HTML     = "html"
    PDF      = "pdf"
    JSON     = "json"

class ReportStatus(str, Enum):
    PENDING    = "pending"
    GENERATING = "generating"
    READY      = "ready"
    FAILED     = "failed"

class Report(Model):
    id            = BigIntField(primary_key=True)
    title         = CharField(max_length=255)
    report_type   = CharEnumField(ReportType)
    status        = CharEnumField(ReportStatus, default=ReportStatus.PENDING)
    generated_by  = ForeignKeyField("css.User", null=True, on_delete="SET NULL")
    project       = ForeignKeyField("css.Project", null=True, on_delete="SET NULL")
    source_refs   = JSONField(default=dict)  # {"incident_ids":[…], "scan_ids":[…]}
    error_message = TextField(null=True)
    created_at    = DatetimeField(auto_now_add=True)
    updated_at    = DatetimeField(auto_now=True)
    class Meta:
        table = "reports"
        indexes = [Index(fields=["project", "created_at"]), Index(fields=["status"])]

class ReportArtifact(Model):
    id          = BigIntField(primary_key=True)
    report      = ForeignKeyField(Report, related_name="artifacts", on_delete="CASCADE")
    format      = CharEnumField(ReportFormat)
    content     = TextField()                 # Markdown or HTML (not PDF)
    file_path   = CharField(max_length=512, null=True)  # PDF path on disk
    size_bytes  = BigIntField(default=0)
    sha256      = CharField(max_length=64, null=True)
    created_at  = DatetimeField(auto_now_add=True)
    class Meta:
        table = "report_artifacts"
        indexes = [Index(fields=["report", "format"])]

class ReportTemplate(Model):
    id           = BigIntField(primary_key=True)
    name         = CharField(max_length=128, unique=True)
    report_type  = CharEnumField(ReportType)
    template_md  = TextField()      # Jinja2 Markdown template
    variables    = JSONField(default=dict)   # expected context keys + descriptions
    is_default   = BooleanField(default=False)
    created_at   = DatetimeField(auto_now_add=True)
    class Meta:
        table = "report_templates"
```

---

### Service Layer

**`ReportBuilder`** (`services/builder.py`)
- `async build(report: Report) → ReportContext` — queries incidents/scans/compliance for `source_refs`, aggregates findings, returns typed context dict for the template.
- Context keys: `project_name`, `generated_at`, `executive_summary`, `findings: list[Finding]`, `incident_timeline: list[IncidentEvent]`, `compliance_controls: list[ControlResult]`, `scan_results: list[ScanFinding]`

**`ReportRenderer`** (`services/renderer.py`)
- `render_markdown(template: ReportTemplate, ctx: ReportContext) → str` — Jinja2 render
- `render_html(md: str) → str` — markdown → HTML via `mistune` (already a dep candidate)
- Both return strings stored in `ReportArtifact.content`

**`ReportExporter`** (`services/exporter.py`)
- `export_pdf(html: str, report_id: int) → Path` — weasyprint HTML → PDF, saves to `ARTIFACTS_DIR/reports/{report_id}.pdf`, stores path + sha256 in `ReportArtifact`
- `export_json(report: Report, ctx: ReportContext) → str` — serialize context to JSON artifact

---

### Async Generation Flow

```
POST /api/reports/           → create Report(status=PENDING), enqueue background task, return 202 + {id}
BackgroundTask.generate(id)  → Report(status=GENERATING)
                             → ReportBuilder.build() → ReportRenderer.render_markdown/html()
                             → ReportExporter.export_pdf() if PDF requested
                             → ReportArtifact saved → Report(status=READY)
                             → fire event report.generation.complete
                             → WS push to subscribed frontend clients

On error:                    → Report(status=FAILED, error_message=...) + fire report.generation.failed
```

---

### REST Endpoints (`routers/reports.py`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/reports/` | Trigger generation. Body: `{report_type, project_id, source_refs, formats[]}`. Returns 202. |
| `GET` | `/api/reports/` | List reports (filter: project, type, status). Paginated. |
| `GET` | `/api/reports/{id}` | Report metadata + status + artifact list |
| `GET` | `/api/reports/{id}/download` | `?format=pdf\|html\|md\|json` — stream artifact |
| `DELETE` | `/api/reports/{id}` | Soft-delete report + artifacts |
| `GET` | `/api/report-templates/` | List available templates |
| `POST` | `/api/report-templates/` | Create custom template |

---

### Builtin Templates (seed on `init-db`)

1. **Executive Summary** — Risk score gauge, top-5 findings table, action items section. Target: CISOs.
2. **Technical Findings** — Per-finding: title, severity badge, CVE/CWE refs, PoC steps, remediation. Target: engineers.
3. **Incident Timeline** — Chronological event table with actor, action, affected asset, detection source. Target: IR team.
4. **Compliance Mapping** — Per-framework (NIST CSF / SOC2 / ISO27001) control list with pass/fail/partial + coverage %. Target: auditors.
5. **Vulnerability Summary** — Scan aggregation: severity distribution donut, top-25 CVEs, affected hosts. Target: red/blue team leads.

---

### Hook Events

```python
"report.generation.started"  # payload: {report_id, report_type, project_id}
"report.generation.complete" # payload: {report_id, formats_ready, artifact_ids}
"report.generation.failed"   # payload: {report_id, error}
"report.deleted"             # payload: {report_id}
```

---

### Frontend (`src/frontend/`)

- `ReportsPanel` — list view with status badges + download buttons
- `GenerateReportModal` — select type, project, source refs (incident IDs, scan IDs), format checkboxes
- `ReportViewer` — inline HTML render inside modal/drawer (no separate page)
- `TemplateEditor` — Monaco editor for custom Jinja2 templates

---

### Task Breakdown — Phase 32

| ID | T# | What | Deps |
|----|-----|------|------|
| `reports-enums` | T32.1 | `ReportType`, `ReportFormat`, `ReportStatus` enums in `core/db/enums.py` | `db-dedupe-enums` |
| `reports-orm` | T32.2 | `Report`, `ReportArtifact`, `ReportTemplate` ORM models; `init-db` registers them | `reports-enums`, `db-asgi-tortoise-init` |
| `reports-builder` | T32.3 | `ReportBuilder.build()` — query incidents/scans/compliance, return `ReportContext` | `reports-orm`, `domain-incidents`, `domain-scans`, `domain-compliance` |
| `reports-renderer` | T32.4 | `ReportRenderer` — Jinja2 MD render + mistune HTML conversion | `reports-builder` |
| `reports-pdf-export` | T32.5 | `ReportExporter.export_pdf()` — weasyprint HTML→PDF, sha256, artifact record | `reports-renderer` |
| `reports-json-export` | T32.6 | `ReportExporter.export_json()` — serialize `ReportContext` to JSON artifact | `reports-renderer` |
| `reports-builtin-templates` | T32.7 | Seed 5 builtin templates on `init-db` (`management/seed_reports.py`) | `reports-orm` |
| `reports-endpoints` | T32.8 | REST router: POST trigger, GET list, GET detail, GET download, DELETE | `reports-renderer`, `reports-pdf-export` |
| `reports-background-task` | T32.9 | `BackgroundTask` wrapper: PENDING→GENERATING→READY/FAILED + event fire | `reports-endpoints`, `prod-task-queue` |
| `reports-events` | T32.10 | Hook events: `report.generation.*` + `report.deleted` | `reports-background-task`, `events-core-impl` |
| `reports-frontend` | T32.11 | `ReportsPanel`, `GenerateReportModal`, `ReportViewer`, `TemplateEditor` | `reports-endpoints` |

---

## 🚧 Phase 36 — Local Proxy & Transport Surfaces

**Rationale**: The platform already assumes `/api/*`, `/ws/*`, SSE token streams, and an eventual `/v1/*` proxy facade, but the current ASGI runtime still treats routing as one flat HTTP router tree. This phase prepares `core/asgi/` and `modules/llm_proxy/` for a single-process, local-only transport architecture.

### Transport Topology

```text
localhost:8000
├── /api/*          platform REST + CRUD
├── /ws/*           browser/session realtime channels
├── /sse/*          one-way stream endpoints
├── /v1/*           local-compatible LLM proxy facade
├── /.well-known/*  discovery surfaces
└── /health         process health
```

Rules:
- compose stays infra-only
- `llm_proxy` is in-process, not a compose service
- host-local operation stays the default assumption
- transport policy must work for HTTP, WebSocket, SSE, and proxy streaming explicitly

### Starlette Position

FastAPI remains the right tool for typed API surfaces and OpenAPI, but the root transport shell should use **Starlette-style composition**:
- mounted sub-apps or transport-specific router trees
- raw ASGI middleware where HTTP-only middleware is insufficient
- WebSocket lifecycle management
- `StreamingResponse`-based SSE output where needed

This is not a rewrite to pure Starlette. It is a transport-boundary design choice.

### Task Breakdown — Phase 36

| ID | T# | What | Deps |
|----|-----|------|------|
| `asgi-transport-topology` | T36.1 | Document and lock route families (`/api`, `/ws`, `/sse`, `/v1`, root/discovery) plus loader expectations in `core/asgi/` | — |
| `asgi-mounted-surfaces` | T36.1 | Refactor the root ASGI runtime toward dedicated transport-aware mounted surfaces or router trees inside one local process | `asgi-transport-topology` |
| `asgi-transport-policy` | T36.2 | Unify auth, rate-limit, telemetry, heartbeat, cancellation, and backpressure policy across HTTP/WS/SSE/proxy | `asgi-mounted-surfaces` |
| `proxy-module-plan` | T36.3 | Create `modules/llm_proxy/llm_proxy.md` with purpose, integration matrix, and local-only scope | `asgi-transport-topology` |
| `proxy-openai-surface` | T36.3 | Minimal `/v1/models` + `/v1/chat/completions` compatibility facade for local clients like Claude Code and other tooling | `proxy-module-plan`, `sdk-unified-client` |
| `proxy-routing-bridge` | T36.4 | Translate proxy requests into `UnifiedLLMClient`, prompt cache, routing, and optional memory/retrieval context assembly | `proxy-openai-surface`, `routing-unified-client-wire`, `rag-context-wire` |
| `proxy-streaming-normalization` | T36.4 | Normalize provider streaming deltas into one SSE-compatible outward shape with cancellation and usage trailers | `proxy-openai-surface`, `cache-redis-streaming-buffer` |
| `proxy-local-trust-boundary` | T36.5 | Localhost-first bind policy, optional local bearer token, per-project routing overrides, and proxied-call audit trail | `proxy-module-plan`, `asgi-transport-policy` |


---

## 🚨 Phase 37 — SIEM/EDR Integration

**Rationale**: CyberSecSuite needs native SIEM/EDR integration to compete with Vigil and CyberStrikeAI. Leverages existing stack: OpenObserve (time-series), PostgreSQL (relational), Neo4j (graph).

### Data Store Allocation

| Data Store | Purpose |
|------------|---------|
| **OpenObserve (5080)** | High-volume EDR telemetry, metrics (alert counts, MTTR), SOC dashboards, traces via OTel Bridge |
| **PostgreSQL + Tortoise** | \`siem_alerts\`, \`edr_detections\`, \`incidents\` tables with JSONB payloads, alert state tracking, structured queries |
| **Neo4j (7474/7687)** | Entity graph (IP→Host→Process→File), attack path analysis, MITRE ATT&CK technique mapping via relationships |

### Architecture Flow

```
External SIEM/EDR (Splunk, CrowdStrike, SentinelOne)
        ↓ (MCP Phase 22 clients)
Ingest Service → Normalize to SecurityEvent (msgspec.Struct)
        ↓
┌───────┴───────┬──────────────┬─────────────┐
▼               ▼              ▼             ▼
PostgreSQL    OpenObserve    Neo4j    EventStore
(alerts/      (telemetry/    (attack    (.append →
 incidents)    metrics/       paths/    Redis Streams
               dashboards)   MITRE)    → AI Analyzer)
```

### Task Breakdown — Phase 37

| ID | T# | What | Deps |
|----|-----|------|------|
| \`siem-types\` | T37.1 | SecurityEvent contract + SIEM event namespaces | — |
| \`siem-module\` | T37.2 | `modules/siem/` package: ORM, API, enums, exceptions, exports | `siem-types` |
| \`siem-ingest\` | T37.3 | MCP-based SIEM/EDR ingest normalization service | `siem-types`, `mcp-tool-bridge`, `mcp-startup-wire` |
| \`siem-models\` | T37.4 | OpenObserve-first storage pipeline + Postgres + GraphRAG fan-out | `siem-types`, `siem-module`, `db-oo-client-implementation`, `db-oo-stream-definitions`, `graph-rag-backend` |
| \`siem-analyzer\` | T37.5 | Correlate OO telemetry with GraphRAG + VectorRAG for remediation context | `siem-ingest`, `siem-models`, `events-event-bus-module`, `rag-vector-backend`, `graph-rag-backend`, `rag-context-wire` |
| \`siem-response\` | T37.6 | Workflow-backed response actions with approval gating | `siem-analyzer`, `workflow-runner`, `approval-gate`, `approval-agentexecutor-wire`, `mcp-tool-bridge`, `mcp-startup-wire` |

### Implementation Details

**T37.1** — \`core/siem/types.py\`:
\`\`\`python
class SecurityEvent(msgspec.Struct, frozen=True):
    source: str              # "splunk", "crowdstrike", "sentinelone"
    severity: str            # "critical", "high", "medium", "low"
    timestamp: float
    source_ip: str | None
    host_id: str | None
    process_id: str | None
    mitre_technique: str | None
    raw_data: dict
    payload: dict
\`\`\`

Extend \`EventType\` in \`core/events/domain_event.py\`:
- \`SIEM_ALERT_CREATED\`, \`EDR_DETECTION_NEW\`, \`INCIDENT_CREATED\`

**T37.2** — \`modules/siem/\` (5-file pattern):
- \`models.py\`: \`SiemAlert\`, \`EdrDetection\`, \`Incident\` (inherit BaseModel)
- \`endpoints.py\`: FastAPI routes \`/api/siem/alerts\`, \`/incidents\`, \`/graph/attack-path\`
- \`types.py\`, \`enums.py\`, \`exceptions.py\`, \`__init__.py\`

**T37.3** — \`core/siem/ingest.py\`:
- \`SiemIngestService\` using \`McpToolBridge\` (Phase 22)
- Normalize external alerts to \`SecurityEvent\`
- Preserve source server/tool provenance and prepare the event for OpenObserve-first fan-out

**T37.4** — Storage:
- OpenObserve first: raw telemetry, dashboards, operational search, and audit visibility
- PostgreSQL: curated \`siem_alerts\` / \`incidents\` application records with indexes on timestamp, severity, status, mitre_technique
- Neo4j / GraphRAG: project entities as nodes (IP, Host, Process, File, Technique) with relationships

**T37.5** — \`core/siem/analyzer.py\`:
- \`SiemAnalyzerAgent\` subscribes to Redis Streams \`css:events\`
- Correlates OpenObserve telemetry with GraphRAG + VectorRAG
- Uses LLM (existing provider-agnostic client) to generate remediation steps

**T37.6** — \`core/siem/response.py\`:
- \`SiemResponseManager\` using Phase 30 Workflow Engine + Phase 26 Human Approval
- Actions: isolate endpoint, block IP, kill process
- Wire to \`modules/siem/endpoints.py\`

### Integration Points

- Extends \`EventType\` in \`core/events/domain_event.py\`
- EventStore.append() / SIEM fan-out → OpenObserve + PostgreSQL + GraphRAG
- Reuses the Phase 35 OpenObserve client + stream definitions as the primary telemetry path
- Reuses \`McpToolBridge\` (Phase 22) for external SIEM/EDR connections and response actions
- Uses Phase 30 Workflow Engine for response playbooks
- Uses Phase 26 Human Approval Workflows for actions

### Success Criteria

- [x] 6 todos added to session.db
- [ ] \`core/siem/types.py\` with SecurityEvent struct
- [ ] \`modules/siem/\` with 5-file pattern
- [ ] Ingest from at least 1 SIEM + 1 EDR via MCP
- [ ] PostgreSQL models with indexes
- [ ] Neo4j graph projections working
- [ ] AI analyzer correlating events
- [ ] Response playbooks with human approval

---

## 🚧 Phase 38 — IDE PyCharm Integration

**Rationale**: Connect CyberSecSuite with PyCharm IDE tooling. The project already has full PyCharm capabilities documented in `pycharm_tools.md` (file ops, search, code analysis, run configs, DB queries, refactoring), but there's no module wrapping these into the app's standard module pattern.

### Architecture

```
modules/ide_pycharm/
├── __init__.py        # Public API exports via __all__
├── types.py           # FileLocation, RunConfiguration, SearchQuery, IDEOperationResult, etc.
├── enums.py           # IDEToolCategory, SearchMode, OperationStatus, IDEConnectionState
├── exceptions.py      # IDEError, IDEConnectionError, IDEOperationError, IDETimeoutError
├── client.py          # PyCharmToolClient — typed async methods per tool category
├── database.py        # DatabaseClient — IDE DB connection operations
├── endpoints.py       # /api/ide/* FastAPI routes
└── ide_pycharm.md     # Module planning document
```

### Task Breakdown — Phase 38

| ID | T# | What | Deps |
|----|-----|------|------|
| `idepycharm-foundation` | T38.1 | Module scaffold: types.py, enums.py, exceptions.py, __init__.py | — |
| `idepycharm-client` | T38.2 | PyCharmToolClient with stubs for all tool categories | `idepycharm-foundation` |
| `idepycharm-endpoints` | T38.3 | FastAPI endpoints at /api/ide/* | `idepycharm-client` |
| `idepycharm-database` | T38.4 | DatabaseClient for IDE DB operations | `idepycharm-foundation` |
| `idepycharm-agent-wiring` | T38.5 | Agent tool registration + ASGI lifespan wiring | `idepycharm-client`, `idepycharm-endpoints`, `idepycharm-database` |

### Implementation Details

**T38.1** — Foundation:
- `types.py`: 14 msgspec.Struct types — FileLocation, RunConfiguration, SearchQuery, SearchMatch, IDEOperationResult[T], CodeAnalysisProblem, DBConnection, DBSchema, DBObject, QueryResult, TablePreview, SymbolInfo, ProjectInfo
- `enums.py`: IDEToolCategory (FILE/SEARCH/CODE_ANALYSIS/RUN/REFACTOR/DATABASE/PROJECT), SearchMode (TEXT/REGEX/SYMBOL/GLOB/FILENAME), OperationStatus (SUCCESS/ERROR/TIMEOUT/NOT_AVAILABLE), IDEConnectionState, RefactorKind
- `exceptions.py`: IDEError → IDEConnectionError, IDEOperationError, IDETimeoutError, IDENotAvailableError

**T38.2** — `client.py`:
- `PyCharmToolClient` with typed async methods:
  - File: read_file, get_file_text, create_file, replace_text, reformat_file, open_file
  - Search: search_text, search_regex, search_symbol, find_files_by_glob, find_files_by_name
  - Code Analysis: get_file_problems, get_symbol_info, build_project
  - Run: list_run_configurations, execute_run_configuration
  - Refactor: rename_symbol
  - Project: get_project_info, list_directory_tree

**T38.3** — `endpoints.py`:
- FastAPI APIRouter at `/api/ide/` with routes for status, file ops, search, analysis, run, refactor, project info, database
- Uses `init_clients()` for dependency injection

**T38.4** — `database.py`:
- `DatabaseClient` with methods: list_connections, list_schemas, list_schema_objects, get_object_description, execute_query, preview_table, test_connection

**T38.5** — Wiring:
- ASGI lifespan calls `init_clients()`
- Optionally register IDE tools in ToolRegistry for agent use

### Integration Points

| Component | Direction | Relationship |
|-----------|-----------|--------------|
| `css.modules.tools` | → registers | IDE tools become agent-callable tools in ToolRegistry |
| `css.core.asgi` | → started by | ASGI lifespan calls `init_clients()` |
| `css.modules.agents` | → consumed by | Agents use IDE tools for code operations |

### Success Criteria

- [x] 5 todos added to session.db
- [x] `modules/ide_pycharm/` with foundation files
- [x] PyCharmToolClient with typed method stubs
- [x] FastAPI endpoints at /api/ide/*
- [ ] DatabaseClient wired into endpoints
- [ ] ASGI lifespan integration
- [ ] Agent-callable IDE tools registered
