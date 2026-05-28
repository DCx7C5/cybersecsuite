# Checkpoints — Phase Summaries

## How To Read This File

This file is an append-only historical record of completed phase work and
planning intake. It is not the current implementation queue.

- Query `.plan/session.db` for live todo state and descriptions.
- Read the nearest `src/css/**/*.md` file for the executable local contract.
- Read `.plan/architecture/feature-overview.md` for the verified source
  inventory.
- Counts, paths, status words, and type names inside older checkpoints record
  what was stated at that point in time. They do not override current rules or
  current source ownership.

### Current Reconciliation Note (2026-05-26)

- Active memory ownership is `src/css/core/memory/`,
  `src/css/core/rag_vector/`, and `src/css/core/rag_graph/`; the retired
  parallel memory branch must not be recreated.
- Triage ownership is `src/css/modules/triage/`; response strategy ownership
  is `src/css/modules/strategies/`. Redundant root `core/intelligence.py` and
  `core/routing.py` facades were removed.
- Value objects implemented or revised now must follow the current
  `msgspec.Struct` rule, even where older checkpoint prose records historical
  `dataclass` work.
- Session/output-directory ownership is still unresolved. Historical
  `working_dir` or proposed `core/workspace` references require an explicit
  ownership decision before implementation.
- Current tracker snapshot: `927` todos, `485` done, `436` pending,
  `6` blocked, `0` in progress.
- Phase 41 preparation is complete (`12/12` remediation todos done). The
  completed `db40-lane-marketplace` row is not an active continuation point;
  any implementation resumption must use live dependency and owner-doc checks.

---

## Checkpoint 000: Phase 0 — TeamScope Foundation ✅

**Date**: 2026-05-03  
**Duration**: 1 day (planned 10 days; accelerated with TODO loop)  
**Status**: COMPLETE

### Summary
Built TeamScope foundation: team isolation layer with orchestrator pool, task assignments, resource quotas, and lifecycle state machine.

### Tasks Completed
- Task 0-1: Team database schema + dataclass models
- Task 0-2: Team lifecycle + quota enforcement
- Task 0-3: Orchestrator pool + endpoints
- Task 0-4: Results isolation + metrics

### Todos Completed (12)
1. teamscope-1-schema: Team ORM model
2. teamscope-2-models: Team/TeamScope dataclasses
3. teamscope-3-isolation: TaskAssignment + TeamQuota models
4. teamscope-4-orchestrator-pool: OrchestratorPoolEntry
5. teamscope-5-endpoint-crud: CRUD endpoints
6. teamscope-6-lifecycle: State machine
7. teamscope-7-pause-resume: Pause/resume mechanism
8. teamscope-8-results-isolation: Results aggregation
9. teamscope-9-priority-scheduling: Priority scheduler
10. teamscope-10-metrics: Metrics tracking
11. teamscope-11-isolation-testing: Test suite
12. teamscope-12-integration: Models integration

### Files Created
- `src/css/core/db/models/team.py` (Team ORM model)
- `src/css/core/db/models/quotas.py` (TaskAssignment, TeamQuota)
- `src/css/modules/teams/enums.py` (TeamStatus, OrchestratorMode)
- `src/css/modules/teams/types.py` (TeamScope, Team dataclasses)
- `src/css/modules/teams/endpoints.py` (CRUD endpoints)
- `src/css/modules/teams/lifecycle.py` (State machine)
- `src/css/modules/teams/pause_resume.py` (Pause/resume)
- `src/css/modules/teams/orchestrator.py` (Orchestrator pool)
- `src/css/modules/teams/results.py` (Results isolation)
- `src/css/modules/teams/priority_scheduler.py` (Priority scheduler)
- `src/css/modules/teams/metrics.py` (Metrics)
- `src/css/modules/teams/models.py` (Integration)
- `tests/modules/teams/test_isolation.py` (Isolation tests)

### Key Decisions
1. **5-file pattern**: Teams module follows strict pattern (enums, types, endpoints, models, orchestrator, etc)
2. **Immutable scope**: TeamScope snapshot for operation context; mutable Team entity for state changes
3. **Quota enforcement**: TaskAssignment + TeamQuota models separate concerns (assignment vs resource limits)
4. **Lifecycle state machine**: pending → active → paused ↔ active → completed

### Blockers Resolved
- None encountered during Phase 0

### Lessons Learned
1. TODO loop strategy (12 stubs in parallel) worked well for rapid scaffolding
2. 5-file pattern must be enforced early (teams module needed restructuring to avoid duplication in core)
3. Lifecycle state machine benefits from separate validation methods (can_activate, can_pause, etc)

### Architecture Updates
- Added Team ORM model to core/db/models with FK to SessionScope
- Extended teams module with full scaffolding (7 new files)
- Clarified immutable/mutable entity pattern (TeamScope vs Team)

### Next Phase
Phase 1: Multi-Orchestrator Core (14 days)
- Orchestrator lifecycle management (spawn, kill, heartbeat)
- Pull-based task queue implementation
- Crash detection & auto-recovery
- Health monitoring & result aggregation

---

## Checkpoint 001: Phase 1 — Multi-Orchestrator Core ✅

**Date**: 2026-05-03  
**Duration**: Accelerated (1 phase-cycle)  
**Status**: COMPLETE

### Summary
Built multi-orchestrator coordination layer: orchestrator lifecycle management, pull-based task queue, heartbeat monitoring, crash detection & recovery, health metrics, load balancing, and atomic result merging.

### Todos Completed (10)
1. orchestrator-1-schema: OrchestratorInstance ORM model
2. orchestrator-2-models: Orchestrator dataclass entity
3. orchestrator-3-endpoints: CRUD endpoints (spawn, get, kill)
4. orchestrator-4-task-queue: Pull-based task distribution
5. orchestrator-5-heartbeat: Heartbeat monitoring
6. orchestrator-6-crash-recovery: Crash detection & recovery
7. orchestrator-7-health-monitoring: Health metrics collection
8. orchestrator-8-load-balancing: Load balancing strategy
9. orchestrator-9-result-merging: Atomic result merging
10. orchestrator-10-tests: Test suite

### Files Created
- `src/css/core/db/models/orchestrator.py` (OrchestratorInstance ORM)
- `src/css/core/base/entities/orchestrator.py` (Orchestrator dataclass)
- `src/css/modules/orchestration/` (9 new files)

### Key Decisions
1. **Pull-based architecture**: Orchestrators pull tasks from queue (not push) for better resilience
2. **Separate heartbeat**: Dedicated mechanism for liveness detection
3. **Atomic recovery**: Crash detection triggers automatic recovery
4. **Multi-strategy load balancing**: Support multiple approaches

### Architecture Updates
- Added OrchestratorInstance ORM model to core/db/models
- Created orchestration module with 9 components
- Orchestrator entity pattern (immutable/mutable separation)

### Next Phase
Phase 2: Config Integration & SDK Architecture (12 days)

---

## Checkpoint 002: Phase 2 — SDK Pattern & Response ✅

**Date**: 2026-05-03  
**Duration**: Accelerated (1 phase-cycle)  
**Status**: COMPLETE

### Summary
Phase 2 completed: SDK Pattern & Response, UniversalLLMClient registry + lazy-load router, Orchestration Roles module, Modules auto-discovery.

### Todos Completed (16)
1. sdk-universal-client
2. sdk-registry
3. sdk-roles-module
4. sdk-auto-discovery
5. sdk-responses-layer
6. sdk-async-wrappers
7. sdk-streaming-support
8. sdk-error-handling
9. sdk-tools-registry
10. sdk-integration-test
(16 total per plan.md)

### Files Created/Modified
- `src/css/modules/roles/role_types.py` (140 lines)
- `src/css/core/base/universal_client.py` (220 lines)
- `src/css/modules/roles/__init__.py` (updated)
- `src/css/core/base/api_services.py` (updated)
- `src/css/modules/__init__.py` (updated, auto-discovery)

### Key Decisions
1. UniversalLLMClient = Registry + lazy-load pattern
2. Orchestration Roles defined in modules/roles/
3. Module auto-discovery via importlib

### Next Phase
Phase 3: Module Consistency

---

## Checkpoint 003A: Full-System Audit Complete (2026-05-03)

**Status**: 🎯 COMPLETE | **Duration**: ~1 hour

**Three Parallel Rubber-Duck Agents**:
- Agent 1: 22/22 API providers audited (12 ready, 10 TBD)
- Agent 2: 4/4 core components audited (3 ready, 1 stub)
- Agent 3: 22/22 modules audited (5 ready, 11 pending, 6 blocked)

**Coverage**: 48/48 plan.md files analyzed & synced with session.db

**Key Results**:
- 41 entries in session.db (23 modules + 8 core + 10 phase markers)
- 4 central audit documents (48 KB)
- Phase 2 implementation tiers determined (4 tiers)
- Critical path clear (no blockers)
- 5 modules ready for immediate deployment

**Next**: Phase 2 Foundation Tier Implementation

Historical note: the former `session-checkpoint.md` reference is retired.
Current navigation is `.plan/plan.md`; current status is in
`.plan/session.db`; current context is in `.plan/memory.md`.


---

## Checkpoint 003B: Architecture Proposals + Plan Restructure (2026-05-04, session 9a5b41c4)

**Status**: 🎯 PLANNING COMPLETE

### Work Done

**Deep Codebase Inspection**:
- Read all 22 architecture docs + 48 plan.md files + source listings
- Identified 5 types.py/base.py antipatterns across codebase
- Read all 31 files in core/base/ directory

**5 Anti-Patterns Documented (Phase 3/4)**:
1. Empty base.py: `agents/base.py`, `skills/base.py` → delete
2. `__all__` in 20+ wrong files → move to `__init__.py` only
3. `@dataclass + ABC` in `base_entity.py`, `base_header.py` → remove @dataclass
4. base.py size violations: tools (9 LOC merge), cache (293 LOC split)
5. core/base/ soup: 9 orphans, 1 god file (280 LOC/11 classes) → full reorganisation

**5 Architecture Proposals Approved (Phase 6)**:
1. **Protocol-first + msgspec.Struct** — Kill ABC/dataclass mixing; 10-40× faster serialization
2. **24 YAML specs + 1 HttpProviderAdapter** — Replace ~4800 LOC boilerplate with declarative YAML
3. **CQRS + Append-only Event Store** — Forensic replay; events module becomes the domain heart
4. **importlib.metadata entry_points** — 20-line loader; marketplace = `uv add`; fixes 33 test failures
5. **Composable async generator pipeline** — `pipe(classify, route, execute, observe)` replaces Queue+polling

**session.db Restructured**:
- Added `phase` and `task` columns to todos table (PHASE > TASK > TODO now enforced)
- Populated all 288 existing todos with PHASE > TASK assignments
- Inserted 25 new Phase 6 todos
- Total: 313 todos (191 done, 121 pending, 1 blocked)

**Key Decisions**:
1. Old "Phase 6: Integration & Polish" → renumbered to Phase 7
2. session.db schema extended: phase + task columns mandatory going forward
3. msgspec over Pydantic for domain value objects; Pydantic stays for API schemas only
4. YAML-first provider architecture — no new provider Python classes ever

See: `plan.md` for Phase 6 section | `memory.md` for full state | `session.db` for all todos

---

## Checkpoint 004: Rubber-Duck Evaluation + Phases 20–21 (2026-05-04, session ffed87aa)

**Status**: 🎯 PLANNING COMPLETE

### Work Done

**Rubber-Duck Report Evaluation**:
- Evaluated all three 2026-05-03 rubber-duck reports (API services, core infra, modules)
- All findings confirmed valid — no stale data
- `consolidate-audit-findings` marked DONE (reports already in plan.md, audit-results.md skipped per whitelist)
- Phase 8 gaps (Claude hardcode, empty agents/) noted as post-audit additions not covered by duck reports

**Phase 19 Expanded**:
- Added 4 new todos: `sessions-lifecycle`, `sessions-mode-layout`, `sessions-persistence`, `sessions-endpoints`
- SessionManager planning gained full lifecycle (create/resume/end) + state
  machine + mode-driven layout.
- Historical dependency: Phase 15 directory setup was described as
  `WorkingDirManager`. Current ownership is unresolved and must be confirmed
  before implementation.

**Phase 20 — Persistent Memory Layer** (12 todos):
- MemoryEntry msgspec.Struct (provider-agnostic, frozen)
- Redis hot tier (sliding window + token budget)
- PostgreSQL cold tier (Tortoise ORM + tsvector FTS)
- ContextAssembler: converts entries → any provider message format
- Memory survives model + provider change (key design invariant)
- Session lifecycle hooks + AgentExecutor turn hooks

**Phase 21 — Qwen3-0.6B Triage Intelligence** (14 todos):
- 12 micro-features: Micro-Router, Confidence Scorer, Echo Detector, Intent Drift, Tone Adapter,
  Parallel Micro-Voter, Token Budget Analyst, Memory Tagger, Paradox Spotter, Fallback Whisperer,
  Paraphrase Suggester, Pre-Filter
- All gate on `ai-triage-ollama-wire` (Phase 8)
- PreFilter + FallbackWhisperer are highest value (cost savings + resilience)
- Originally proposed below `core/triage/`; current canonical owner is
  `src/css/modules/triage/`, orchestrated by `TriageEngine`.

**session.db**: 572 total (194 done, 377 pending, 1 blocked) | +30 todos this session

---

## Checkpoint 005 — DB Fixes + Test Improvements (session ffed87aa-p2, 2026-05-04)

### Rubber-Duck Audit Fixes Applied

**CRITICAL fixes (session.db)**:
- C1: Fixed 40 todos with broken phase names (`'15'`, `'18'`, `'19'`, `'''19'''` → full phase names)
- C2: Deleted 2 orphaned `todo_deps` rows (scope-teamscope-workdir, events-core-impl); added real dep `notifications-module-create → audit-hp-events`
- H3: Added 6 Phase 10 gate deps on Phase 6 YAML todos (prevents Phase 10 starting before Phase 6)
- New `sort_order` INTEGER column — `ORDER BY sort_order` now respects intended phase sequence

**Plan/rules fixes**:
- H1: Removed `rubber-duck-sync-plan.md` ghost reference from plan.md whitelist table + stale "See:" link
- H2: `scopes` marked ⚠️ DEPRECATED in rules.md modules table
- H4: rules.md "8 above" → "7 above" (whitelist count)
- rules.md ready-query updated to `ORDER BY t.sort_order, t.task, t.id`

**Code fixes**:
- `legacy/hooks/events.py`: Added `HookContext` re-export (was documented, not implemented)
- `legacy/hooks/recovery_hooks.py`: `from hooks.events` → `from .events` (relative import)
- `legacy/hooks/__init__.py`: Import `HookContext` from `css.core.base.hook_events`
- `tests/unit/test_recovery_hooks.py` + `test_streaming_hooks.py` + `test_registry_instrumentation_integration.py`: Fixed stale `css.core.registries.hooks` → `legacy.registries.hooks`
- Deleted `agents/base.py`, `skills/base.py` (both 0 LOC, no references)

**Test improvements**:
- `pytest.ini`: Added ignore for `tests/scope/`, `tests/features/test_dashboard_routing.py`, and 3 legacy unit test files
- Baseline improved: 178 ✅ / 71 ❌ / 80 ⏭️ (was 106 / 67 / 79)
- 13 remaining collection errors are pre-existing (bare `db`, `api_services`, `ai_proxy` imports) — tracked in Phase 6

**session.db**: 572 total (194 done, 377 pending, 1 blocked) | no new todos added

---

## Checkpoint 006 — Phase 22 MCP Protocol Layer Planned (2026-05-04)

**Trigger**: Resumed mid-planning after compaction; wrote full Phase 22 design

### session.db Changes
- **14 new todos** inserted for Phase 22 — MCP Protocol Layer (sort_order=22)
- **17 new todo_deps** inserted for Phase 22 dependency chain
- Total: ~586 todos

### Files Modified
- `src/css/modules/mcps/mcps.md` (formerly referenced as `plan.md`):
  complete design for transports, client, registry, bridge, types, API, and examples.
- `src/css/modules/tools/tools.md` (formerly referenced as `plan.md`):
  removed MCP server ownership and documented the `ToolType.MCP` bridge.
- `.plan/rules.md`: 19 → 20 modules; mcps added to table; tools note updated
- `.plan/plan.md`: Phase 22 added to phases table + full Phase 22 section appended
- `.plan/memory.md`: Phase 22 key points section; session.db state updated; prev session block renamed

### Key Decisions

**mcps/ vs tools/ split:**
- `@tools` = LLM provider builtin tools only (code_interpreter, computer_use, etc.)
- `@mcps` = MCP server management (any MCP-compatible server: local, remote, in-process)
- Bridge: McpToolBridge pushes MCP tools into ToolRegistry as ToolType.MCP

**Transport hierarchy:**
1. `PYTHON_DIRECT` — `Client(FastMCP_instance)` — in-process, zero HTTP, trusted servers only
2. `STDIO` — subprocess JSON-RPC — most external MCPs
3. `SSE` — HTTP+SSE — legacy MCP transport
4. `STREAMABLE_HTTP` — MCP 2025-03 spec — modern remote

**fastmcp v3.1.0** already in pyproject.toml — no new deps needed

**Phase 22 readiness gates:**
- Needs: Phase 3 tools module (ToolRegistry) + Phase 6 ASGI pipeline
- Ready to implement as standalone files; startup wire waits for Phase 6

### Status
- Phase 22 todos: 14 pending (all 14 new)
- `mcps/mcps.md`: ✅ Written
- `tools/tools.md`: ✅ Updated
- rules.md: ✅ 20 modules
- plan.md: ✅ Phase 22 added
- memory.md: ✅ Synced

---

## Checkpoint 007 — Phase 23 Prompt Registry (2026-05-04)

**Trigger**: User added `prompts/` as own module category (not MCP)

### Context
- MarketplaceItemType.prompt already existed in marketplace/enums.py
- No prompt infrastructure existed anywhere else
- Created standalone module: prompts as first-class versioned entities

### session.db Changes
- 10 new todos inserted for Phase 23 — Prompt Registry (sort_order=23)
- 11 dependency edges inserted
- Total: ~596 todos

### Files Created/Modified
- `src/css/modules/prompts/__init__.py`: Scaffolded (1 line)
- `src/css/modules/prompts/prompts.md` (formerly referenced as `plan.md`):
  full design for categories, types, renderer rules, and registry API.
- `.plan/rules.md`: 20 → 21 modules; prompts added alphabetically
- `.plan/plan.md`: Phase 23 row + Phase 23 section appended
- `.plan/memory.md`: Phase 23 key points; state updated

### Key Design Decisions
- No Jinja2 — pure Python regex renderer ({{var}} + {{> partial}})
- msgspec.Struct frozen for all value types
- PromptDefinition versioned by prompt_id + version (unique together in DB)
- Marketplace integration: MarketplaceItemType.prompt items install/uninstall → PromptRegistry
- "latest" version alias for registry.get()

---

## Checkpoint 008 — Inter-Module Connection Audit (2026-05-04T21:11)

**Session**: ffed87aa | **Phase Added**: Phase 25 — Integration Hardening

### Work Done
- Full cross-module integration audit: read all 25+ module plan.md files, all integration tables
- Confirmed 10 distinct gaps (A–J) ranging from CRITICAL to MEDIUM severity
- Added 14 new todos to session.db (622 total, 425 pending, 3 blocked)
- Appended Phase 25 — Integration Hardening to plan.md
- Updated plan.md header (status, todos count, audit date)

### Gaps Found

| Gap | Where | What |
|-----|-------|------|
| A (CRITICAL) | `css.core.session` | File doesn't exist; `session-context-create` already tracked in Phase 15 |
| B (HIGH) | `core/db/models/` | ORM models missing: ProjectRecord, McpServerConfigRecord, PromptDefinitionRecord |
| C (HIGH) | `core/base/projects.py` | Missing — `projects/projects.md` requires it |
| D (HIGH, BLOCKED) | `core/base/context.py` | `@dataclass + BaseModel` anti-pattern on 4 classes |
| E (HIGH, BLOCKED) | `permissions.ScopeLevel` | 3 independent definitions of same enum |
| F (MEDIUM) | `agents/agents.md` | Stale `project_dir`, missing `prompts` row |
| G (MEDIUM) | `events/events.md` | Missing project.*, settings.changed, mcp.call.* event namespaces |
| H (MEDIUM) | 8 modules | Placeholder integration tables not filled |
| I (MEDIUM) | triage, llm_proxy, chat, workflows | NO integration section at all |
| J (MEDIUM) | `cache` | Not referenced anywhere despite 4+ consumers |

### Two BLOCKED Todos Need User Decision
1. **`gap-scopelevel-deduplicate`**: 3 independent `ScopeLevel` enums. Proposed: `core/db/enums` = source of truth; permissions re-exports from there; scopes deleted (Phase 15).
2. **`gap-context-antipattern`**: `context.py` uses `@dataclass + BaseModel` on 4 classes (anti-pattern #3). Proposed: replace all 4 with `msgspec.Struct`. Currently only re-exported from `core/base/__init__.py` — not yet used by any module.

### Key Technical Findings
- `ScopeLevel` exists in: `core/db/enums.py` AND `/enums.py` AND `core/permissions/enums.py`
- `streaming/options_manager.py` already uses local `Scope = Literal[...]` — NOT importing deprecated scopes module (that todo is already done)
- `ConversationContext` / `ModelContext` / `ExecutionContext` in context.py are not imported by any module — safe to replace
- Phase 19 sessions module is still fully missing — it's the upstream gate for Phase 24 worktrees

---

## Checkpoint 009 — Phase 4 Entity Migrations + QA Review (2026-05-05T06:48)

**Session**: Current | **Phase Progress**: Phase 3 (85%), Phase 4 (29%)

### Work Done

**7 Phase 4 Entity Migration Todos Completed**:
1. `phase4-verify-imports` — Core module imports verified (css.core.base, css.core.db, css.core.events, css.modules.roles)
2. `types-option-c-accounts` — Account entity moved to `src/css/core/accounts/types.py`
3. `types-option-c-agents` — Agent entity moved to `src/css/modules/agents/types.py`
4. `types-option-c-permissions` — Role entity added to `src/css/core/permissions/types.py` with built-in singletons
5. `types-option-c-skills` — Skill entity moved to `src/css/modules/skills/types.py`
6. `types-option-c-tools` — Tool entity moved to `src/css/modules/tools/types.py` + 5 helper classes
7. `types-option-c-reimport` — Updated `src/css/core/base/__init__.py` to import entities from new module locations

**Comprehensive QA Review Performed**:
- ✅ All 5 new entity files in correct locations with valid Python syntax
- ✅ All module __init__.py files export entities via __all__
- ✅ Import chain verified working: css.core.base → css.modules.*.types (no circular imports)
- ✅ Base classes (BaseAgent, BaseRole, BaseSkill, BaseTool) remain in core/base/entities/ as designed
- ✅ Old entity files preserved in original locations (for types-option-c-cleanup todo later)
- ✅ All changes passed ruff linting checks
- ✅ Documentation complete with proper docstrings

### Files Modified (7 total)
- `src/css/core/base/__init__.py` (updated imports from new module locations)
- `src/css/core/accounts/__init__.py` (new)
- `src/css/core/accounts/types.py` (new)
- `src/css/modules/agents/__init__.py` (new)
- `src/css/modules/agents/types.py` (new)
- `src/css/core/permissions/__init__.py` (updated)
- `src/css/core/permissions/types.py` (updated)
- `src/css/modules/skills/__init__.py` (new)
- `src/css/modules/skills/types.py` (new)
- `src/css/modules/tools/__init__.py` (updated)
- `src/css/modules/tools/types.py` (updated)

### session.db Changes
- **+7 todos completed**: All in Phase 4 — Core Consistency + Types
- **+0 new dependencies**: No new blockers introduced
- Total: 768 todos (242 done, 522 pending, 0 blocked)
- Phase 3 progress: 125/147 (85%)
- Phase 4 progress: 7/24 (29%)

### Key Architecture Decisions
1. **Account entity**: 8 fields (vault_key, provider_id, label, auth_method, active, etc) + 3 properties (is_active, needs_test, mark_tested)
2. **Agent entity**: 3 fields (header, skill_tags, claude_metadata) + properties (is_default, base_url, client())
3. **Role entity**: Built-in singletons (ORCHESTRATOR, TEAM_MODE, WORKER) + REGISTRY dict + get() factory
4. **Skill entity**: 4 fields (status, install_path, installed_at) + 3 properties (is_installed, has_update, is_deprecated)
5. **Tool entity**: Main class + 5 helper classes (ToolParameter, ToolReturnType, ToolSchema, HybridToolSchema, ManagedTool)
6. **Import pattern**: Entities now import from css.core.base.base and css.core.base.headers (no circular deps)

### Verification Checklist (ALL PASS ✅)
1. ✅ File structure verification
2. ✅ Module exports verification  
3. ✅ Import chain verification
4. ✅ Python syntax validation
5. ✅ Original files preservation
6. ✅ Entity class completeness
7. ✅ Circular import check
8. ✅ Imports in entity files
9. ✅ Documentation quality
10. ✅ Consistency checks

### Status
- **Phase 4 Progress**: 7/24 todos done (29%) — Entity migration phase progressing
- **Next**: Continue with phase4-linting-cycle2, types-option-c-cleanup, and config strategy todos
- **No blockers**: All Phase 4 migrations successful, ready for cleanup and next phase

---

## Checkpoint 010 — Session.db Sync & Plan File Update (2026-05-07)

**Status**: 🎯 SYNC COMPLETE

### Work Done
- Synced `.plan/memory.md` with current session.db state (772 total todos, 297 done, 467 pending, 7 blocked)
- Updated all per-phase todo counts in memory.md to match latest session.db query
- Added unassigned todo row (4 pending) to memory.md phase table
- Updated memory.md last updated timestamp to 2026-05-07

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 772   |
| Done         | 297   |
| Pending      | 467   |
| Blocked      | 7     |

### Key Phase Progress Updates
| Phase                | Done (Old) | Done (New) | Pending (Old) | Pending (New) | Blocked (New) |
|----------------------|-------------|-------------|----------------|----------------|----------------|
| Phase 3 — Module Consistency | 125 | 140 | 22 | 5 | 2 |
| Phase 4 — Core Consistency + Types | 7 | 21 | 16 | 1 | 2 |
| Phase 5 — Integration & Testing | 2 | 16 | 30 | 16 | 0 |
| Phase 6 — Architecture Overhaul | 2 | 5 | 34 | 30 | 0 |
| Phase 8 — AI Execution Layer | 0 | 8 | 17 | 9 | 0 |
| Phase 28 — Auth & Accounts | 0 | 1 | 6 | 5 | 0 |

### Files Modified
- `.plan/memory.md`: Updated session state, phase table, timestamps
- `.plan/checkpoints.md`: Added this checkpoint entry

### Next Steps
- Continue Phase 3/4 completion (highest done counts)
- Resolve 7 blocked todos (Phase 3: 2, Phase4:2, Phase7:1, Phase11:1, Phase19:1)
- Sync local plan.md files in src/css/ modules with updated session.db state

---

## Checkpoint 011 — Python 3.14 + msgspec Normalization (2026-05-07T17:14)

**Status**: 🎯 COMPLETE (active scope) | ⛔ legacy deferred by user directive

### Work Done
- Completed pre-phase typing normalization for active scope (`src/css` + `tests`):
  - Removed `from __future__ import annotations`
  - Removed legacy typing imports (`List/Dict/Tuple/Set/FrozenSet/Optional/Union`)
  - Removed `typing.List/Dict/...` usage
- Migrated all active-scope `@dataclass` models to `msgspec.Struct`.
- Added/updated guardrail command in `Makefile`:
  - `make lint-typing-rules`
  - Enforces typing + dataclass bans in `src/css` and `tests`.

### Verification Snapshot
- `src/css + tests`:
  - dataclass decorators: **0**
  - dataclass imports (`dataclass`/`field`): **0**
  - forbidden typing patterns: **0**
- `make lint-typing-rules`: ✅ pass

### Scope Decision
- Per user instruction: **`src/legacy/**` is out of scope** until explicitly requested.
- Reverted legacy edits from this pass.
- SQL todo `phase-n1-migrate-legacy` marked `blocked` with explicit reason.

### SQL Todo State (phase-n1)
- done: `phase-n1-dataclass-baseline`, `phase-n1-migrate-core`, `phase-n1-migrate-modules`, `phase-n1-compat-fixes`, `phase-n1-guardrail`, `phase-n1-validation`
- blocked: `phase-n1-migrate-legacy`

---

## Checkpoint 012 — Marketplace Architecture Alignment + Planning Sync (2026-05-07T19:46)

**Status**: 🎯 COMPLETE

### Work Done
- Enforced core architecture rules in implementation:
  - `core/` subdirs use enums from `src/css/core/enums.py`
  - ORM models moved to `src/css/core/db/models/<subdir>.py` (marketplace moved to `core/db/models/marketplace.py`)
- Updated marketplace imports across runtime code to the new canonical locations.
- Removed `src/css/core/marketplace/enums.py` and reverted loader model discovery to `core/db/models/*.py` only.

### Planning Docs Synced
- Updated stale marketplace path references across planning docs:
  - `src/css/core/marketplace/*` as canonical runtime location
  - `src/css/core/db/models/marketplace.py` as canonical ORM location
  - `@css/core/marketplace/templates` as canonical template location
- Updated `.plan/plan.md` and `.plan/memory.md` headline todo counts to current session.db values.

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 780   |
| Done         | 323   |
| Pending      | 449   |
| Blocked      | 7     |

---

## Checkpoint 013 — plan.md Cleanup (2026-05-09)

**Status**: 🧹 HOUSEKEEPING COMPLETE

### Work Done
- Removed 4 deprecated/completed sections from `.plan/plan.md`:
  1. **BLOCKER #3: App Initialization Fails → RESOLVED** — all fixes applied, app starts successfully
  2. **✅ RESOLVED table** — historical audit-blocker tracking, no longer relevant
  3. **✅ FACT-CHECKED + sub-sections** — 2026-05-05 audit results archived
  4. **🔍 AUDIT FINDINGS (Archived)** — 2026-05-03 audit snapshot
- Moved preserved content to this checkpoint entry for historical reference

### Historical Reference (preserved from removed sections)

**BLOCKER #3 Resolution** (2026-05-04):
- Fixed: deprecated `src/core/a2a` module removal, circular import in accounts/types.py, circular import in scopes/context.py, marketplace config exports
- 4 root causes fixed across commits 158da6bf, b3c13e01, 12808bde
- Verified: all critical imports work, app init passes

**System Fact-Check** (2026-05-05):
- 92-94% confidence that all 284 "done" todos were actually complete
- 30-todo random sample: 97% pass rate
- Zero problematic circular imports found across 22 modules

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 832   |
| Done         | 447   |
| Pending      | 379   |
| Blocked      | 6     |

**Next**: Phase 12 — QoL Output Controls Migration (starting `qol-models-msgspec`)

---

## Checkpoint 014 — Phase 18 Frontend + Marketplace Initial Slice (2026-05-09T16:28+0200)

**Status**: 🟢 PARTIAL PHASE EXECUTION COMPLETE

### Work Done
- Completed the first executable frontend tranche in `Phase 18 — Frontend Foundation`:
  - `frontend-vite-scaffold`
  - `frontend-tailwind-shadcn`
  - `frontend-appshell`
  - `frontend-api-client`
  - `frontend-module-registry`
  - `frontend-panel-colocated-structure`
  - `frontend-marketplace-hooks`
  - `frontend-marketplace-panel`
- Wired a functional marketplace UI path:
  - UI implementation: `src/frontend/src/panels/marketplace/*`
  - Colocated module bridge: `src/css/core/marketplace/templates/{index,hooks,types}.ts*`
- Added Vite proxy route for `/marketplace` to match live backend route ownership (`core/marketplace/endpoints.py` uses `/marketplace/*` prefix).

### Dependency Analyzer Sync
- Ran `scripts/codebase_dependency_analyzer.py` on:
  - `src/css/core/marketplace/`
  - `src/css/core/settings/`
  - `src/css/modules/chat/`
  - `src/frontend/`
- Result highlights:
  - No cross-module import violations in analyzed Python areas.
  - Marketplace/settings/chat markdown references detected and updated where stale.
  - Frontend path currently yields `0` analyzer Python files (expected; TS/TSX surface).

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 832   |
| Done         | 464   |
| Pending      | 362   |
| Blocked      | 6     |

---

## Checkpoint 016 — Three-Agent Audit Todo Intake (2026-05-09T16:59+0200)

**Status**: 🟡 TRACKER EXPANSION COMPLETE

### Work Done
- Processed three audit result streams and converted findings into explicit `session.db` todos.
- Added **Phase 39 — Audit Remediation (A1/A2/A3)** with **18 pending todos** split across:
  - `T39.1 Agent 1 — Architecture & Runtime Gaps` (EventStore durability, OTEL runtime wiring, permissions enforcement, workspace baseline, P4 entry_points gap, stale scope refs)
  - `T39.2 Agent 2 — Plan & Tracker Integrity` (phase table sync, phase naming normalization, Phase 22 reconciliation, unassigned rehome, stale blocked cleanup, feature inventory sync)
  - `T39.3 Agent 3 — Code Quality & Rules Compliance` (`__future__` removal, legacy typing import cleanup, `__all__` policy, bare exception replacement, `Any` reduction, CharEnumField migration)
- Added dependency chains inside each task so execution order is explicit.
- Corrected phase-number collision by assigning these new remediation todos to **Phase 39** (existing Phase 38 is IDE PyCharm).

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 850   |
| Done         | 464   |
| Pending      | 380   |
| Blocked      | 6     |

---

## Checkpoint 017 — DB Consolidation Todo Intake (2026-05-09T17:53+0200)

**Status**: 🟡 PLAN INTAKE COMPLETE

### Work Done
- Added **Phase 40 — DB Model Consolidation & Rich Schemas** with **29 new todos** from current DB/model planning directives.
- Structured into five tasks:
  - `T40.1 Model Canonicalization & Ownership` (12 todos)
  - `T40.2 Menu + Tree Modeling` (6 todos)
  - `T40.3 Tagging Architecture + Meta Standards` (5 todos)
  - `T40.4 Fields + BaseModel + Mixins Enrichment` (4 todos)
  - `T40.5 Runtime Module Home Reassignment` (2 todos)
- Captured concrete requested fix tracks:
  - memory model move cutover and stale import cleanup
  - marketplace model duplication reconciliation
  - tasks-vs-quotas model cutover
  - `MenuItem.menu_id` sidebar/menu partitioning
  - `BaseTreeModel` adoption inventory
  - tag architecture standardization (`*Tag` singular naming/meta pattern)
  - provider model rename cutover, user-vs-account boundary
  - historical planning todo for `intelligence.py` and `pipeline.py` homes;
    current reconciliation removed the root intelligence/routing facades,
    retains shared `core/pipeline.py`, and assigns triage/strategy behavior to
    their module owners.
- Adjusted phase ordering:
  - Phase 39 sort order normalized to follow Phase 38
  - Phase 40 assigned the next sort slot

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 879   |
| Done         | 464   |
| Pending      | 409   |
| Blocked      | 6     |

---

## Checkpoint 018 — Phase 40 Parallel Lane Preparation (2026-05-09T17:53+0200)

**Status**: 🟢 PARALLEL TRACKER PREP COMPLETE

### Work Done
- Prepared `session.db` for parallel execution of Phase 40 by adding `T40.0 Parallel Lanes` with 6 lane bootstrap todos.
- Lanes are disjoint by ownership/write scope:
  - Lane A: memory model canonicalization
  - Lane B: marketplace model consolidation
  - Lane C: tasks/provider/user ownership cutover
  - Lane D: menu/tree modeling
  - Lane E: tagging standards
  - Lane F: fields/mixins/docs/runtime-home planning
- Added dependency bindings from existing Phase 40 todos to their lane bootstrap todo so each worker can claim one lane safely.
- Re-prioritized Phase 40 sort order to be ready before older backlog phases for this session.

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 885   |
| Done         | 464   |
| Pending      | 415   |
| Blocked      | 6     |

### Next Step
- Continue remaining Phase 18 todos (`frontend-ws-manager`, `frontend-zustand-store`, `frontend-port-hooks`, settings/chat panels, dev tooling, dashboard/graphs).

---

## Checkpoint 015 — Phase 18 Realtime Graph Planning Sync (recorded out of order; 2026-05-09T16:41+0200)

**Status**: 🟡 PLAN UPDATE APPLIED

### Work Done
- Synced Phase 18 chart direction to the latest frontend guidance:
  - Replaced `Recharts` plan language with **Apache ECharts** for dashboard charts.
  - Added **Web Worker data-processing pipeline** to T18.12 for high-frequency feeds (batching, downsampling, stats).
  - Added Comlink-first worker API note with raw `postMessage` fallback.
- Updated `session.db` todo details for:
  - `frontend-live-graphs` (title + full description now ECharts + worker-oriented)
  - `frontend-landing-dashboard` (explicit dependency on worker-processed LiveMetrics surface)
  - `graph-recharts` legacy ID (title/description updated to ECharts + worker policy)
- Captured a carry-over chat-history note in Phase 19:
  - Keep module-colocated `templates/` contract (`src/css/core/marketplace/templates/`) unless explicitly overridden.

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 832   |
| Done         | 464   |
| Pending      | 362   |
| Blocked      | 6     |

---

## Checkpoint 019 — Directive Sync: Unassigned Rehome + Phase 40/18 Expansion (2026-05-09T18:41+0200)

**Status**: 🟢 TRACKER/DOC SYNC COMPLETE

### Work Done
- Rehomed all legacy `unassigned` todos into explicit phase/task ownership:
  - A2A repairs → `Phase 3`
  - framework hardening legacy rows → `Phase 25`
  - MCP stabilization legacy rows → `Phase 22`
  - memory backlog rows → `Phase 20`
  - marketplace core-ownership migration row → `Phase 19`
- Completed `audit38-unassigned-rehome` after pending unassigned rows were fully reassigned.
- Added `audit39-module-import-order-canonical` to enforce canonical ordering reference:
  - `src/css/core/settings/config.py` `MODULES` list (line 17) is now the import-order source of truth.
- Expanded Phase 40 with `db40-direct-schema-policy`:
  - current tranche uses direct schema/table edits only (no migration scripts; Aerich deferred).
- Refined Phase 40 descriptions to encode latest directives:
  - duplicate model strategy = keep higher-quality canonical file + merge missing features
  - identity/account boundary = `user` internal identity, `provider/accounts` external provider-account graph
  - `provider 1..N accounts`, `user 1..N accounts`
  - BaseTreeModel prioritization for menu/url/path/breadcrumb navigation surfaces
  - tags remain classification-first, not navigation structure
- Added new Phase 18 task bucket:
  - `T18.13 Navigation UX + shadcn-admin Reuse` with 5 todos for sidebar/settings/topnav + marketplace UX refinement.

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 892   |
| Done         | 465   |
| Pending      | 421   |
| Blocked      | 6     |

### Next Step
- Execute Phase 40 lanes with canonicalization first (`db40-marketplace-*`, `db40-memory-*`, `db40-user-vs-account-boundary`) and parallelize with new Phase 18 `T18.13` UI work.

---

## Checkpoint 020 — Frontend/Settings/MCP/XYFlow Directive Intake (2026-05-09T20:05+0200)

**Status**: 🟢 TRACKER + PLAN SYNC COMPLETE

### Work Done
- Added new **Phase 18 parallel worker lanes** (`T18.0 Parallel Lanes`) for:
  - theme/layout
  - settings/config integration
  - navigation shell
  - marketplace UX
  - MCP GUI
  - XYFlow integration
- Added frontend directives as explicit todos:
  - early theming pass before feature-heavy implementation
  - stronger shadcn-admin layout/component reuse
  - marketplace sidebar children navigation
  - removal of marketplace side tabs
  - redesigned installed+catalog marketplace display
  - MCP server lifecycle hooks/panel in GUI
  - `@xyflow/react` integration + first topology view
- Added `Phase 17` config convergence task set (`T17.14 Config Consolidation`) to migrate:
  - `src/css/core/config.py`
  - `src/css/core/settings/config.py`
  into a single core/settings-owned config surface.
- Added `Phase 22` lifecycle control-plane todos for MCP backend:
  - `mcp-server-lifecycle-api`
  - `mcp-server-lifecycle-runtime-wire`
- Added `db40-menu-marketplace-children-contract` to ensure seeded/stable Marketplace child items (`agents`, `skills`, `mcps`, `workflows`, `templates`, `prompts`, `teams`).
- Added `graph-xyflow-adoption-plan` in Phase 27 for long-term graph-engine alignment.

### session.db Current State
| Metric       | Count |
|--------------|-------|
| Total Todos  | 913   |
| Done         | 465   |
| Pending      | 442   |
| Blocked      | 6     |

### Next Step
- Start parallel execution by claiming one lane from `T18.0` and one from `T40.0`, with settings/config and menu/sidebar prerequisites first.

---

## Checkpoint 021 — Documentation Contract Sanitization + Tracker Description Audit (2026-05-25)

**Status**: DOCUMENTATION/TRACKER CONTRACT SYNC COMPLETE
**Scope**: Information quality and ownership reconciliation only; no todo
status changes were made in this checkpoint.

### Work Done

- Clarified that this file is historical evidence; live execution begins with
  `.plan/session.db` and the nearest `src/css/**/*.md` owner document.
- Corrected obsolete live-looking document references and recorded the
  canonical memory, triage, strategies, and removed-facade outcomes.
- Audited all tracker descriptions and filled every missing description,
  including the underdefined Phase 20 memory backlog.
- Corrected active descriptions that would have directed implementation into
  removed or obsolete locations:
  - memory work -> `src/css/core/memory/`
  - triage behavior -> `src/css/modules/triage/`
  - response strategies -> `src/css/modules/strategies/`
  - provider routing/resilience -> `src/css/core/resilience/routing/`
  - event ownership -> `src/css/core/events/`
  - permissions ownership -> `src/css/core/permissions/`
- Rewrote legacy `dataclass` implementation instructions to require frozen
  `msgspec.Struct` value types where active work remains.
- Gated all pending session-output/workspace instructions: no model may create
  `core/workspace` or revive `working_dir` until ownership is explicitly
  selected.

### Local Document Audit

- Added implementation/validation contracts to short active owner documents
  for accounts, alerts, evidence, incidents, scans, webhooks, compliance,
  scheduler, threat intelligence, MITRE, strategies, menu, redis, workflows,
  browser relay, and marketplace frontend integration.
- Filled placeholder integration matrices in the skills, teams, cache, roles,
  capabilities, and tags owner documents.
- Declared the local document sufficiency standard in `src/css/plan.md`.
  Provider-specific directories remain intentionally covered by the central
  `src/css/api_services/api_services.md` specification; helper subdirectories
  inherit parent core ownership unless assigned independent work.

### Verification Snapshot

| Metric | Result |
|--------|--------|
| Tracker todos | `914` |
| Blank descriptions | `0` |
| Active descriptions shorter than 80 characters | `0` |
| Active minimum description length | `85` characters |
| Status snapshot | `467 done / 440 pending / 6 blocked / 1 in progress` |
| Current in-progress todo | `db40-lane-marketplace` |
| SQLite integrity check | `ok` |

### Open Ownership Decision

Session/output-directory ownership remains deliberately unresolved. The user
previously indicated that `core/workspace` may be obsolete. Before Phase 15
or Phase 24 filesystem/git lifecycle work begins, choose the canonical owner
or explicitly retire those tasks; the tracker now prevents accidental
implementation of the obsolete proposal.

---

## Checkpoint 022 — _GetCoreSchemaHandler Production-Ready Protocol Upgrade (2026-05-27)

**Status**: 🟢 COMMITTED

### Work Done

- Upgraded the inline `_GetCoreSchemaHandler` Protocol in
  `core/base/base_endpoint.py` from a minimal 6-line stub to a
  production-ready version:
  - Added full docstrings matching pydantic's original `GetCoreSchemaHandler`
    documentation for each method (`__call__`, `generate_schema`,
    `resolve_ref_schema`) and the `field_name` property.
  - Added the `_get_types_namespace` method (internal pydantic interface
    used during type resolution for serializer annotations), typed as
    `tuple[dict[str, object], ...]`.
  - Removed the redundant `-> dict[str, object]` return annotation on
    `__get_pydantic_core_schema__` — the type checker now infers
    `PlainValidatorFunctionSchema` from the method body, avoiding both
    `Any` and module-level pydantic imports.
- Updated `.plan/memory.md` and `.plan/plan.md` to reflect the upgrade.
- Comitted as `a42f7944 [protocol-prod-ready]`.

### Design Invariants

- No pydantic import at module level (only inlined `from pydantic_core import
  core_schema` inside the method body, matching FastAPI's transitive
  dependency).
- No `Any` (rule 67), no quoted annotations (rule 68).
- Protocol uses `type` instead of `Any` for `source_type` parameters (more
  precise, structurally compatible with pydantic's `Any` through contravariance).

### session.db Current State (unchanged from prior checkpoint)

| Metric       | Count |
|--------------|-------|
| Total Todos  | 1083  |
| Done         | 601   |
| Pending      | 474   |
| Blocked      | 8     |
