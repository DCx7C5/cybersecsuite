# CyberSecSuite: Implementation Plan

**Main Workdir**: `/home/daen/Projects/cybersecsuite/.plan/`  
**Status**: 🎯 Ready for Phase 0 Execution  
**Updated**: 2026-05-03  
**Timeline**: 84 days (7 phases, ~12 weeks)

---

## 📚 START HERE: Guide to the 8 Files

Only 8 files allowed in `.plan/` (see rules.md § FILE OWNERSHIP):

| File | What | Read First? |
|------|------|-----------|
| **plan.md** | Timeline, milestones, phases (you are here) | ✅ YES |
| **features_overview.md** | What we're building (6 features) | ✅ YES |
| **development-workflow.md** | How we work (TODO/TASK/PHASE workflows) | ✅ YES |
| **architecture.md** | System design (scope hierarchy, database) | If deep dive needed |
| **rules.md** | Development rules (tech stack, patterns) | When implementing |
| **frontend.md** | Frontend architecture & UI/UX patterns | When building UI |
| **checkpoints.md** | Phase summaries & decisions made | After each phase |
| **session.db** | Todo tracker (133 todos, 36 tasks, 7 phases) | For task assignment |

---

## 📊 CURRENT STATUS

**Project**: Multi-Orchestrator + TeamScope + Config Integration + SDK Architecture + Consistency Patterns  
**Phases**: 7 sequential (Phase 0-6)  
**Tasks**: 36 total (4-7 per phase)  
**Todos**: 135 total (125 pending, 10 done)  
**Next Action**: Fix blocking issues → Start Phase 0 (TeamScope Foundation)

### ⚠️ CRITICAL BLOCKING ISSUES (Must fix before Phase 0)

1. **ABC + @dataclass violations** (5 files)
   - `core/types/base/base_entity.py:16`
   - `core/types/base/base_header.py:7`
   - `modules/marketplace/base.py:11, 35, 62`
   - **Impact**: Violates Python type system and ORM constraints
   - **Fix**: Refactor to use only @dataclass OR ABC (not both)

2. **Hardcoded config defaults** (manager.py)
   - Lines 58-60: db-user, db-password, db-name hardcoded
   - Line 97: log-level hardcoded
   - **Impact**: Config not centralized (violates rules.md § CONFIG PATTERN)
   - **Fix**: Use config.py constants instead

3. **Cross-module import violation** (streaming→agents)
   - `modules/streaming/runner.py` imports from `modules/agents`
   - **Impact**: Creates circular dependency risk
   - **Fix**: Move client_pool to core/orchestration

4. **Dangling references to forbidden files** ✅ FIXED
   - ~~development-workflow.md lines 184, 270-272~~
   - Updated to reference only allowed files

5. **Module count inconsistencies** ✅ FIXED
   - ~~plan.md, development-workflow.md, features_overview.md~~
   - Updated 15 → 19 modules across all references

---

## 🔍 AUDIT FINDINGS (2026-05-03)

### Planning Gaps Discovered

**Feature 1: Multi-Orchestrator** — 0/10 todos
- ❌ Database schema for orchestrator_instances table
- ❌ Orchestrator lifecycle management (spawn, kill, heartbeat)
- ❌ Pull-based task queue implementation
- ❌ Crash detection & auto-recovery
- ❌ CLI commands (spawn, list, health, shutdown)
- ❌ REST endpoints (GET/POST/DELETE orchestrators)
- ❌ Health monitoring (heartbeat polling, timeout detection)
- ❌ Idempotency key logic for result merging
- ❌ Atomic result aggregation
- ❌ Test suite validation
- **Status**: COMPLETELY MISSING from session.db

**Feature 2: TeamScope** — 0/12 todos
- ❌ Teams table schema + indexes
- ❌ Orchestrator_instances extended with team_id FK
- ❌ Task_assignments with team isolation
- ❌ Sessions table extended (orchestrator_mode, max_teams, team_count, enable_team_isolation)
- ❌ CLI commands (create, list, status, pause, resume, complete, metrics)
- ❌ REST endpoints (POST/GET/PATCH/DELETE teams, team metrics)
- ❌ Team lifecycle state machine
- ❌ Resource quota enforcement
- ❌ Priority scheduling logic
- ❌ Isolation testing & validation
- ❌ Team pause/resume mechanism
- ❌ Team results aggregation
- **Status**: COMPLETELY MISSING from session.db

**Feature 3: Config Integration** — 6/8 todos (25%)
- ✅ Phase 4.5 tracked (6 todos in session.db)
- ❌ Phases 1-3 missing (CONFIG_SPEC design, dataclass implementation)
- **Status**: INCOMPLETE - high-level planning missing

**Feature 4: SDK Architecture** — ~12/15 todos (80%)
- ✅ response.py pattern partially tracked
- ✅ 4 custom SDKs partially tracked
- ❌ UniversalLLMClient router planning missing
- ❌ Provider-specific refactoring fragmented
- **Status**: FRAGMENTED - needs consolidation

**Feature 5: Module Consistency** — 7/42 todos (17%)
- ✅ google_a2a module partially done
- ✅ marketplace module partially done
- ❌ 17 remaining modules need full 5-file pattern
- ❌ Loader enhancement for auto-discovery
- **Status**: SEVERELY INCOMPLETE

**Feature 6: Core Consistency** — 0/30+ todos (0%)
- ❌ 8 core subdirectories need 5-file pattern
- ❌ 28+ file creation todos missing
- ❌ loader.py enhancement for core/*/models.py discovery
- ❌ Validation & testing todos missing
- **Status**: COMPLETELY MISSING from session.db

### Module Pattern Compliance

Only **2/19 modules** fully compliant with 5-file pattern:
- ✅ google_a2a
- ✅ marketplace
- ❌ 10 modules are empty stubs (no files at all)
- ❌ 7 modules partially implemented

### Todos Created ✅ (22 new items)

**Successfully added to session.db**:
- ✅ 10 Multi-Orchestrator todos (orchestrator-1-schema through orchestrator-10-tests)
- ✅ 12 TeamScope todos (teamscope-1-schema through teamscope-12-integration)
- Dependencies linked sequentially for proper task flow

**session.db Status**:
- Total todos: 135 (10 done, 125 pending)
- Orchestrator Feature: 0/10 done
- TeamScope Feature: 0/12 done

---

### Current State
```
ProjectScope
    ↓
ApplicationScope
    ↓
SessionScope
    ↓
Orchestrator (1, serial)
    ↓
Agents (sequential)
```

### Target State (After Phase 1)
```
ProjectScope
    ↓
ApplicationScope
    ↓
SessionScope
    ↓
TeamScope (NEW) ← Multiple teams per session
    ├─ Orchestrator Pool (NEW) ← Multiple orchestrators per team
    │   ├─ Agent 1 (parallel)
    │   ├─ Agent 2 (parallel)
    │   └─ Agent N (parallel)
    └─ [Additional teams...]
```

---

## 📋 PHASES & MILESTONES

| Phase | Title | Duration | Tasks | Status |
|-------|-------|----------|-------|--------|
| 0 | TeamScope Foundation | 10d | 4 | 🟡 Pending |
| 1 | Multi-Orchestrator Core | 14d | 5 | 🟡 Pending |
| 2 | SDK Pattern & Response | 12d | 5 | 🟡 Pending |
| 3 | Module Consistency | 14d | 6 | 🟡 Pending |
| 4 | Core Consistency | 12d | 7 | 🟡 Pending |
| 5 | Config Integration | 8d | 4 | 🟡 Pending |
| 6 | Integration & Polish | 14d | 5 | 🟡 Pending |
| **TOTAL** | — | **84d** | **36** | — |

### Phase 0: TeamScope Foundation (10 days)

✅ **What**: Add TeamScope model, team management, extend SessionScope with team support  
📦 **Deliverables**: TeamScope database model, Team entity dataclass, 4 API endpoints, scope hierarchy extension  
🎯 **Success**: TeamScope fully integrated, teams can be created/listed/updated/deleted  

**4 Tasks**:
1. TeamScope Model Creation (models.py + Tortoise ORM) — 2 days
2. Team Entity & Database (Team dataclass, DB schema, isolation) — 2 days
3. Scope Hierarchy Extension (add TeamScope to scope.py) — 3 days
4. TeamScope API Endpoints (REST + CLI) — 3 days

🔗 **See**: features_overview.md § FEATURE 2: TeamScope

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

🔗 **See**: features_overview.md § FEATURE 1: Multi-Orchestrator

---

### Phase 2: SDK Pattern & Response (12 days)

✅ **What**: Unified LLM client routable to 24+ providers  
📦 **Deliverables**: response.py per provider, 4 custom SDKs, UniversalLLMClient  
🎯 **Success**: All 24 providers callable through unified interface  

**5 Tasks**:
1. Unified Response Layer (CSSResponse dataclass, streaming) — 3 days
2. Async SDK Wrappers (Anthropic, OpenAI, Google, etc.) — 4 days
3. Streaming Support (SSE, chunked responses) — 2 days
4. Error Handling & Retry (exponential backoff, rate limits) — 2 days
5. SDK Tools Registry (discovery, capability matrix) — 3 days

🔗 **See**: features_overview.md § FEATURE 4: SDK Architecture

---

### Phase 3: Module Consistency (14 days)

✅ **What**: Enforce 5-file pattern on all 19 modules  
📦 **Deliverables**: 95 new files (models.py, endpoints.py, types.py, enums.py, exceptions.py per module)  
🎯 **Success**: All 19 modules fully compliant with pattern  

**6 Tasks**:
1. Modules: models.py Pattern — 2 days
2. Modules: endpoints.py Pattern — 2 days
3. Modules: types.py Pattern (entity consolidation) — 3 days
4. Modules: enums.py Pattern — 1 day
5. Modules: exceptions.py Pattern — 1 day
6. Module Loader Validation — 2 days

🔗 **See**: features_overview.md § FEATURE 5: Module Consistency

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

🔗 **See**: features_overview.md § FEATURE 6: Core Consistency

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

🔗 **See**: features_overview.md § FEATURE 3: Config Integration

---

### Phase 6: Integration & Polish (14 days)

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

## 🎯 FEATURES (See features_overview.md for Details)

1. **Multi-Orchestrator** — Parallel execution with task queue
2. **TeamScope** — Team isolation & resource quotas
3. **Config Integration** — CONFIG_SPEC pattern, centralized config
4. **SDK Architecture** — Unified routing to 24+ LLM providers
5. **Module Consistency** — 5-file pattern for all modules
6. **Core Consistency** — 5-file pattern for all core subdirs

---

## 🚀 NEXT STEPS

### PRE-PHASE-0: Fix Blocking Issues (Priority: CRITICAL)

1. **Fix ABC + @dataclass Violations** (3 files)
   - `core/types/base/base_entity.py:16` — Remove @dataclass, use ABC only
   - `core/types/base/base_header.py:7` — Remove @dataclass, use ABC only
   - `modules/marketplace/base.py:11, 35, 62` — Fix 3 violation instances
   - Impact: BLOCKING (violates Python type system)
   - Effort: 2-4 hours

2. **Fix Hardcoded Config Defaults** (manager.py)
   - Lines 58-60: Replace hardcoded db-user, db-password, db-name with config.py constants
   - Line 97: Replace hardcoded log-level with config.py constant
   - Impact: BLOCKING (violates rules.md § CONFIG PATTERN)
   - Effort: 1-2 hours

3. **Fix Cross-Module Import** (streaming/runner.py)
   - Move client_pool from modules/agents to core/orchestration
   - Update import in streaming/runner.py
   - Impact: HIGH (circular dependency risk)
   - Effort: 2-3 hours

**Timeline**: 5-9 hours total (~1 day)

### AFTER BLOCKING FIXES: Execute Phase 0

4. ✅ **Read features_overview.md** — Understand what we're building
5. ✅ **Read development-workflow.md** — Understand how to work
6. ✅ **Check session.db** — See Phase 0 tasks and todos
7. ⏳ **Start Phase 0** — Create TeamScope model (Task 0-1)

```sql
-- Quick check of Phase 0 todos:
SELECT * FROM todos WHERE id LIKE 'teamscope-%' ORDER BY id;

-- Check blocking issues:
SELECT * FROM todos WHERE id IN (
  'blocker-2-startup', 'blocker-3-circular', 'blocker-4-mappers'
) ORDER BY id;
```

---

## 📈 PROGRESS TRACKING

Use SQL queries to track progress:

```sql
-- Current phase status
SELECT p.id, p.title, COUNT(t.id) as tasks, 
  SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as tasks_done
FROM phases p LEFT JOIN tasks t ON p.id = t.phase_id
GROUP BY p.id ORDER BY p.id;

-- Ready tasks (all todos done)
SELECT t.* FROM tasks t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todos td WHERE td.task_id = t.id AND td.status != 'done'
);
```

---

**Last Updated**: 2026-05-03  
**Next Review**: After Phase 0 completion
