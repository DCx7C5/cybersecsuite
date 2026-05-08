# Planning Memory & Session State

**Last Updated**: 2026-05-08T16:56:43+02:00 | **Session**: Planning workflow phase-sync rules update

⚠️ **CRITICAL**: `.plan/` is the working directory. NEVER use `~/.copilot/` as working dir.  
⚠️ **CRITICAL**: session.db MUST use PHASE > TASK > TODO hierarchy (see rules.md).  
⚠️ **Remember**: `src/css/` uses local planning Markdown everywhere — core areas use `plan.md`, modules use same-name docs like `agents/agents.md`. Read the nearest one FIRST and update it DURING work (not end-of-session).  
⚠️ **Architecture**: `accounts`, `events`, `marketplace`, and `memory` are core-owned. `working_dir` is legacy terminology; use `core/workspace/`.  
⚠️ **STARTUP**: `CACHE_DIR=/tmp/css-cache LOG_DIR=/tmp/css-logs python manage.py serve --reload` (Docker = infra-only: postgres/redis/openobserve). Ollama: native `ollama serve` via `core/ollama/OllamaProcessManager`. Frontend: `cd src/frontend && bun run dev`.

---

## 📊 session.db State (2026-05-08)

**Total**: 783 todos | **Done**: 393 | **Pending**: 384 | **Blocked**: 6

**Last Verified**: 2026-05-08 (matches session.db exactly)

| Phase                                        | Todos | Done | Pending | Blocked |
|----------------------------------------------|-------|------|---------|---------|
| Phase 0 — TeamScope Foundation               | 12    | 12   | 0       | 0       |
| Phase 1 — Multi-Orchestrator Core            | 16    | 16   | 0       | 0       |
| Phase 2 — SDK Architecture                   | 64    | 64   | 0       | 0       |
| Phase 3 — Module Consistency                 | 151   | 149  | 0       | 2       |
| Phase 4 — Core Consistency + Types           | 24    | 22   | 0       | 2       |
| Phase 5 — Integration & Testing              | 32    | 32   | 0       | 0       |
| Phase 6 — Architecture Overhaul              | 37    | 37   | 0       | 0       |
| Phase 9 — ORM/Manager/Registry               | 27    | 16   | 11      | 0       |
| Phase 28 — Auth & Accounts                   | 6     | 1    | 5       | 0       |
| Phase 34 — Dependency Map                    | 19    | 1    | 18      | 0       |

**DB note**: `sort_order INTEGER` column — use `ORDER BY sort_order` not `ORDER BY phase` (alphabetical breaks ordering).

---

## 🔑 Recent Phase Key Points

### ✅ Phase N0 — Python 3.14 Typing Normalization (Completed 2026-05-07)

- Removed forbidden typing patterns in active code scope.
- `src/css + tests` now have:
  - `from __future__ import annotations` = 0
  - legacy typing imports (`List/Dict/Optional/...`) = 0
  - `typing.List/Dict/Optional/...` = 0
- Added guardrail command: `make lint-typing-rules` (scoped to `src/css` + `tests`).

### ✅/⛔ Phase N1 — dataclass → msgspec.Struct (2026-05-07)

- Migrated `@dataclass` usage in active scope:
  - `src/css/core/**` → done
  - `src/css/modules/**` → done
- Guardrail extended to block dataclass reintroduction in active scope.
- `src/css + tests` current state:
  - dataclass decorators = 0
  - dataclass imports (`dataclass`/`field`) = 0
- **User directive applied**: `src/legacy/**` is out of scope until explicitly requested.
  - `phase-n1-migrate-legacy` set to `blocked` accordingly.

### ✅ Phase 4 Entity Migrations (Completed 2026-05-05)

Session completed 7 Phase 4 entity migration todos:
- `phase4-verify-imports`: Core module imports verified (css.core.types, css.core.db, css.core.events, css.modules.roles all functional)
- `types-option-c-accounts`: Account entity moved to `src/css/core/accounts/types.py`
- `types-option-c-agents`: Agent entity moved to `src/css/modules/agents/types.py`
- `types-option-c-permissions`: Role entity added to `src/css/core/permissions/types.py` with built-in singletons (ORCHESTRATOR, TEAM_MODE, WORKER)
- `types-option-c-skills`: Skill entity moved to `src/css/modules/skills/types.py`
- `types-option-c-tools`: Tool entity moved to `src/css/modules/tools/types.py` + 5 helper classes (ToolParameter, ToolReturnType, ToolSchema, HybridToolSchema, ManagedTool)
- `types-option-c-reimport`: Updated `src/css/core/types/__init__.py` to import entities from new module locations

**QA Verification**: ✅ PASS
- All 5 new entity files in correct locations with proper Python syntax
- All module __init__.py files export entities via __all__
- Import chain verified: css.core.types → css.modules.*.types (no circular imports)
- Base classes (BaseAgent, BaseRole, BaseSkill, BaseTool) remain in core/types/entities/ as expected
- Old entity files still preserved for Phase 4 cleanup (types-option-c-cleanup todo)
- All changes passed ruff linting

**Files Modified**:
- src/css/core/types/__init__.py (updated imports)
- src/css/core/accounts/__init__.py (new)
- src/css/modules/agents/__init__.py (updated)
- src/css/core/permissions/__init__.py (updated)
- src/css/modules/skills/__init__.py (new)
- src/css/modules/tools/__init__.py (updated)

**Session Progress**:
- Started: 235/768 todos (Phase 3: 125/147, Phase 4: 0/23)
- Completed: 242/768 todos (+7 entity migration todos, now Phase 4: 7/24)

### ✅ DB Critical Startup Chain (Completed 2026-05-04)

`app.py` lifespan now initializes Tortoise on startup and closes connections on shutdown.  
Completed TODOs: `db-dedupe-enums`, `db-fix-tooltype-enum-empty`, `db-delete-team-stub`, `db-delete-orchestrator-dup`, `db-fix-pk-permissions`, `db-fix-marketplace-item-pk`, `db-fix-fk-labels-scope`, `db-fix-scope-level-charenum`, `db-fix-charfield-enums`, `db-fix-index-tuple-syntax`, `db-asgi-tortoise-init`.

### Phase 32 — Reports Module (2026-05-04, NEWLY ADDED)
- **Supersedes** 3 duplicate report todos from Phase 7/19/29 (marked blocked)
- **ORM**: `Report`, `ReportArtifact`, `ReportTemplate` — 3 models
- **Services**: `ReportBuilder` (data collection) → `ReportRenderer` (Jinja2→MD→HTML) → `ReportExporter` (weasyprint PDF + JSON)
- **5 builtin templates** seeded on `init-db`: ExecutiveSummary, TechnicalFindings, IncidentTimeline, ComplianceMapping (NIST/SOC2/ISO27001), VulnerabilitySummary
- **Async generation**: POST /api/reports/ → 202 + BackgroundTask PENDING→GENERATING→READY/FAILED
- **Hook events**: `report.generation.started/complete/failed` + WS push
- **Frontend**: ReportsPanel, GenerateReportModal, ReportViewer, TemplateEditor (Monaco)
- **Deps**: gates on `domain-incidents`, `domain-scans`, `domain-compliance`, `prod-task-queue`

### Phase 25 — Integration Hardening (2026-05-04, NEWLY ADDED)
- **10 inter-module connection gaps** found in full audit (Gaps A–J)
- **Gap A** (CRITICAL): `css.core.session` missing — already tracked as `session-context-create` in Phase 15
- **Gap B** (HIGH): ORM models missing — ProjectRecord, McpServerConfigRecord, PromptDefinitionRecord
- **Gap C** (HIGH): `core/types/projects.py` missing — projects/plan.md references it
- **Gap D** (BLOCKED): `context.py` uses `@dataclass + BaseModel` anti-pattern on 4 classes
- **Gap E** (BLOCKED): `ScopeLevel` defined independently in 3 places (core/db, scopes, permissions)
- **Gap H/I**: 8 modules have placeholder integration tables; triage/llm_proxy/chat/workflows have NO section
- **Gap J**: `@cache` not referenced in any consuming module's integration table
- **Two todos BLOCKED** (`gap-scopelevel-deduplicate`, `gap-context-antipattern`) pending user decision

### Phase 24 — Git Tracking & Worktree Isolation
- **Every session dir is a git repo** — `git-session-init` runs when the workspace layer creates the session root
- **Auto-commit per turn** — `GitTracker.commit_turn()` fires as @post_hook priority=100 (non-blocking, fire-and-forget)
- **One agent = one worktree = one branch** — `WorktreeManager.create()` on SessionManager.add_agent()
- **Branch convention**: `agent/{session_id[:8]}/{agent_id}`
- **Merge at session end**: MergeStrategy SQUASH (default) / REBASE / OURS / MANUAL
- **3-layer audit**: L1 git (files) + L2 Phase 6 P3 events (domain) + L3 Phase 19 turns (reasoning)
- **Migration**: legacy `scope.py` had `worktree_path` → moves to the workspace-layer worktree manager
- **Gates**: depends on Phase 15 (working-dir-manager) + Phase 19 (session-manager-create)

### Phase 23 — Prompt Registry
- Prompts = first-class versioned entities. **Not MCP.** Platform's own template library.
- `MarketplaceItemType.prompt` already existed — wired in `prompt-marketplace-wire`
- Template syntax: `{{variable}}` + `{{> partial_id}}` includes (one level, no Jinja2)
- All types: msgspec.Struct (frozen). PromptCategory: SYSTEM/USER/FEW_SHOT/CHAIN/PERSONA/INSTRUCTION
- Versioning: prompt_id + version unique key. `registry.get("id")` returns latest.

### Phase 22 — MCP Protocol Layer
- `@mcps` ≠ `@tools`. tools/ = LLM provider builtin tools. mcps/ = MCP server connections.
- **PYTHON_DIRECT**: `Client(FastMCP_instance)` — in-process, zero HTTP. `module_path="pkg:factory"` format.
- fastmcp v3.1.0 already in pyproject.toml. `fastmcp.Client` unified across all transports.
- `McpToolBridge` pushes MCP tools into ToolRegistry as `ToolType.MCP`, `provider="mcp:{server_id}"`.

### Phase 33 — Ollama Native (2026-05-04, NEWLY ADDED)
- **Docker removed**: `cybersec-ollama` container deleted from docker-compose.yml
- `core/ollama/` manages native process: `installer.py` (Linux-only, Arch/Debian, prints dev model hints), `process.py` (asyncio subprocess), `client.py` (ollama.AsyncClient wrapper)
- **One client only** — `ollama.AsyncClient`. Ollama handles CUDA natively. No `llama_client.py`.
- **No preloader** — models are dev recommendations, pulled manually. `installer.py` prints the hint:
    `ollama pull qwen3:0.6b` / `phi4-mini:3.8b-q4_K_M` / `qwen3:4b-q4_K_M`
- `llama-cpp-python` = optional dep, NOT wired into `core/ollama/`. Separate CUDA sm_61 install.
- Dependency chain: `ollama-install-checker` → `ollama-process-manager` → `ollama-lifespan-wire` → `ollama-docker-remove`

### Phase 21 — Intelligence Layer (renamed from Triage, 2026-05-04)
- **Renamed**: `core/triage/` → `modules/intelligence/`, Phase 21 renamed "Local Intelligence Layer"
- Todo: `triage-rename-module` (Phase 19)
- Scope broadened: quality gates, conversation health, cost budget, memory tagging, tone adaptation — all local AI assistance (not just routing/classification)
- Uses `core/ollama/client.py` (native process), preloaded models via `core/ollama/preloader.py`

### Phase 20 — Persistent Memory Layer
- `MemoryEntry` (msgspec.Struct, frozen): provider-agnostic — survives model/provider swap.
- Hot tier: Redis sliding window + token budget. Cold tier: PostgreSQL + tsvector FTS.
- `ContextAssembler`: MemoryEntry list → provider-specific message format.
- Integration: SessionManager.create/resume/end + AgentExecutor pre/post turn.

---

## 🚀 Phase 6 — 5 Approved Architecture Proposals

All 5 approved. Tasks under `Phase 6 — Architecture Overhaul` in session.db.

| Proposal                                 | Core idea                                                                                                  | Key tasks              |
|------------------------------------------|------------------------------------------------------------------------------------------------------------|------------------------|
| P1 — Protocol-first + msgspec            | Drop ABC/dataclass mixing. Protocol for contracts, msgspec.Struct for values. 10-40× faster serialization. | `p6-msgspec-*` (5)     |
| P2 — 24 YAML specs + 1 adapter           | Replace 24 provider classes (~4800 LOC) with YAML + 1 HttpProviderAdapter (~150 LOC)                       | `p6-yaml-*` (5)        |
| P3 — CQRS + Event Store                  | Every mutation = immutable DomainEvent in PostgreSQL. Forensic replay built-in.                            | `p6-events-*` (5)      |
| P4 — importlib.metadata entry_points     | Replace pkgutil with Python plugin system. Loader → 20 lines.                                              | `p6-entrypoints-*` (4) |
| P5 — Composable async generator pipeline | `pipe(source, classify, route, execute, observe)` — each stage one `async def __aiter__`                   | `p6-pipeline-*` (6)    |

---

## 🩺 Anti-Patterns (avoid repeating)

1. `agents/base.py`, `skills/base.py` → ✅ DELETED (0 LOC, no refs)
2. `__all__` in wrong files — must be in `__init__.py` only
3. **`@dataclass + ABC` on same class** = forbidden. **`@dataclass + BaseModel(Pydantic)` on same class** = forbidden. Pure `@dataclass` alone (no ABC) = acceptable for value types / frontmatter structs, but migrate to `msgspec.Struct` on touch (Phase 6 P1). `context.py` fix tracked as `gap-context-antipattern`.
4. `aiohttp` not `httpx`, `uv` not `pip`, `bun` not `npm`
5. Do not import from `~~scopes~~` — DEPRECATED, pending deletion (Phase 15)
6. **`project_dir` ≠ `session_dir`** — `SessionContext.session_dir` is the scratch space (`~/.css/sessions/{id}/`). `project.source_dir` is the target/codebase (read-only). `project_id` is an optional FK. They are siblings, not parent/child. Never nest sessions inside projects on disk.

---

## ⚠️ Structural Debt (open)

- **`core/caching/` renamed → `core/prompt_cache/`**: Clearer name. Two-tier only (Redis + Anthropic `cache_control`). Gemini `NATIVE_RESOURCE` deferred — complex separate billing model. Tracked: `cache-gemini-context-cache` blocked.
- **`core/retry/` renamed → `core/resilience/`**: Already has `detection.py`, `orchestrator.py`, `config.py` — broader than retry alone.
- **`working_dir` module deleted → `core/workspace/` pending**: `WorkspaceRegistry` tracks N `WorkspaceDirHandle` entries per entity. Default `~/.css/sessions/<sid>/` + optional project dir, both WRITE. List expandable. Todos rewritten under Phase 15.
- **`modules/cache/` → `core/cache/` pending**: L4 SQLite removed. 3-layer (L1 memory, L2 redis.asyncio, L3 PostgreSQL). `cache-move-to-core` todo gates L4-removal + redis.asyncio migration. All tracked in Phase 3.
- **`core/triage/` → `modules/intelligence/` pending**: Rename tracked as `triage-rename-module` (Phase 19). Phase 21 broadened to full local AI assistance.
- Tool Registry partially implemented (provider normalization + execution path still pending) — Phase 3
- Permissions not implemented — Phase 15
- Events module missing (0/5 files) — Phase 6 P3
- 5-file pattern: only 3/48 components compliant — Phase 3/4
- 13 pre-existing test collection errors (bare `db`/`api_services`/`ai_proxy` imports) — Phase 6 P4

---

## 📚 Key Planning Documents

- `.plan/plan.md` — phases overview + Phase 6 proposals
- `.plan/session.db` — **783 todos**, PHASE > TASK > TODO hierarchy (35 phases + unassigned)
- `.plan/rules.md` — absolute dev rules (21 modules, ready-query, stack rules)
- `.plan/checkpoints.md` — session history (012 checkpoints)
- `src/css/modules/*/<module>.md` — module source-of-truth (23 module directories)
- `src/css/api_services/*/plan.md` — provider source-of-truth (24 files)
