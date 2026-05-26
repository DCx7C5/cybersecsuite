# Development Rules

**Status**: 📋 Active Convention | **Updated**: 2026-05-08

---

## 🚀 FIRST: WHERE DO I START?

If you are an AI agent starting a new session, do this **in order**:

```bash
# 1. Go to project root
cd /home/daen/Projects/cybersecsuite

# 2. Check what is in progress (finish these first)
sqlite3 .plan/session.db "SELECT id, title FROM todos WHERE status = 'in_progress';"

# 3. Find the next ready todo with no blocked dependencies (ALWAYS sorted by phase order)
sqlite3 .plan/session.db "
SELECT t.id, t.title, t.phase, t.task
FROM todos t
WHERE t.status = 'pending'
AND NOT EXISTS (
  SELECT 1 FROM todo_deps td
  JOIN todos dep ON td.depends_on = dep.id
  WHERE td.todo_id = t.id AND dep.status != 'done'
)
ORDER BY t.sort_order, t.task, t.id LIMIT 5;"

# 4. Read the full spec for the todo you'll work on
sqlite3 .plan/session.db "SELECT description FROM todos WHERE id = 'CHOSEN-ID';"

# 5. Read the local planning markdown for the area you're working in
cat src/css/modules/<module_name>/<module_name>.md 2>/dev/null || \
cat src/css/core/<area>/settings.md 2>/dev/null || \
cat src/css/api_services/api_services.md
```

---

# CRITICAL MOST IMPORTANT RULES NEVER FORGET:

## Environment
- **ABSOLUTE: your new workingdir is `.plan/`. `~/.{claude,copilot}` are all obsolete.**
- **ABSOLUTE: you track TODOs, TASKs & PHASEs in `.plan/session.db`** 
- **ABSOLUTE: use `.venv/bin/` or source `.venv/bin/activate`**
- **ABSOLUTE: start app with `python manage.py ...`**
- **ABSOLUTE: use docker compose to manage databases**
- **ABSOLUTE: use `scripts/codebase_dependency_analyzer.py` as often as possible. Pipe into `| jq ''`**
- **ABSOLUTE: rule violations are fixed on the fly, or if implications are too heavy, a TODO in session.db is created.**

## Session & Project Planning
- **ABSOLUTE: Git track everything. use worktrees for parallel working subagents if possible**
- **ABSOLUTE: `.plan/plan.md` is the session workspace plan, and [.plan/session.db](session.db) is the only progress tracker** — use `plan.md` for high-level session planning only, and record every todo status change in `session.db`, not only in markdown
- **ABSOLUTE: local planning Markdown exists across `src/css/` and must stay synchronized with `session.db` during work** — read the nearest file first (`<module>.md` in modules, nearest `plan.md` elsewhere) so each area document reflects current todos and milestones
- **ABSOLUTE: there is no backwards compatibility requirement** — if your changes make code deprecated, delete the deprecated code directly
- **ABSOLUTE: use lazy imports only when clearly justified, and preserve existing directory, file, and content patterns when adding or changing code**

## Code & Execution
- **ABSOLUTE: never add `Co-authored-by:` to any new commit** — historical commits contain it; do not amend history to remove it, but all future commits must omit it entirely
- **ABSOLUTE: `@dataclass` is legacy, and `@dataclass + ABC` is forbidden** — when you touch one, migrate it toward `msgspec.Struct`, and fix mixed patterns immediately
- **ABSOLUTE: keep chat responses bare and under 500 words unless impossible**
- **ABSOLUTE: explicitly announce every TODO, TASK, or PHASE completion, give every tool execution a clear headline, and always end with a normal summary**
- **ABSOLUTE: always prefer async Python whenever possible**
- **ABSOLUTE: avoid `Any` and never use typing comments** — prefer exact `TypedDict`s over `Any`, and never write `# type: ...`
- **ABSOLUTE: use the required stack choices** — `bun`, not `npm`; `aiohttp`, not `httpx`
- **ABSOLUTE: we never use the python `global` variable. if we find it in existing code we create a TODO for it**
- **ABSOLUTE: never use `from __future__ import annotations`, it's an already built-in feature in newer Python versions**
- **ABSOLUTE: never use bare `Exception`** — create custom exceptions with help from `src/core/exceptions.py`
- **ABSOLUTE: use Singleton metaclass patterns from `src/core/types/meta.py`** — no end-of-file instantiation
- **ABSOLUTE: event-emitting classes should use `src/css/core/types/base_emitter.py::BaseEmitterClass` whenever practical** — keep namespaces and manual event registration consistent
- **ABSOLUTE: hook ownership is split and must stay split** — observer hooks live in `src/css/modules/hooks/registry.py` (`@on_event`), mutating/blocking hooks live in `src/css/modules/hooks/interceptors.py` (`@pre_hook` / `@post_hook`)
- **ABSOLUTE: use explicit imports `from X import Y` where applicable, and do not create `"Expected type XY, got None instead"` warnings**

## Architecture & Structure
- **ABSOLUTE: deletion of a module or whole directory is never a solution to a problem**
- **ABSOLUTE: planning hierarchy is always PHASE > TASK > TODO** — every new TODO must belong to exactly one TASK and exactly one PHASE
- **ABSOLUTE: [.plan/](../.plan) is the working directory, and [.venv/bin/](../.venv/bin) is the Python entry point**
- **ABSOLUTE: follow existing directory, documentation, and code patterns, and use [.plan/architecture/*.md](architecture) plus the nearest local planning markdown as the architecture source of truth**
- **ABSOLUTE: use `src/css/core/settings/config.py` `MODULES` list (line 17) as the canonical module import-order reference** — for ordering disputes, doc updates, or loader-order decisions, this list wins.

## Workflow & Tooling
- **ABSOLUTE: read and follow [.plan/development-workflow.md](development-workflow.md) for every applicable task**
- **ABSOLUTE: in PLAN MODE, keep `.plan/plan.md`, relevant `.plan/architecture/*.md`, and local planning Markdown synchronized with [.plan/session.db](session.db) while working**
- **ABSOLUTE: update `memory.md` and `checkpoints.md` at the end of every PHASE** — not after every task and not only at end-of-session
- **ABSOLUTE: exception for `memory.md`** — refresh it immediately after major architecture, source-of-truth, or tracker-structure changes that would otherwise mislead the next session
- **ABSOLUTE: never hallucinate; if unsure, ask the user before proceeding**
- **ABSOLUTE: make multiple logical and atomic commits**

# CRITICAL RULES ABOVE: APPLY AND CONFIRM EVERY SINGLE ONE AFTER YOU HAVE COMPLETELY READ THIS FILE

**Then follow**: `.plan/development-workflow.md` — WORKFLOW 1 for todos, WORKFLOW 2 for tasks, WORKFLOW 3 for phases.


## ✅ FILE ORGANIZATION: PROJECT vs LOCAL

### `.plan/` Directory WHITELIST (7 files ONLY)

| File                         | Purpose                                               |
|------------------------------|-------------------------------------------------------|
| **plan.md**                  | Project session workspace plan (high-level overview)  |
| **architecture/*.md**        | System design decisions                               |
| **memory.md**                | Compressed context from previous sessions             |
| **development-workflow.md**  | Development process and git strategy                  |
| **rules.md**                 | Development rules (THIS FILE)                         |
| **checkpoints.md**           | Phase summaries and completion records                |
| **session.db**               | Todo tracker (SQLite) — ALWAYS KEEP IN SYNC!!!        |

**❌ FORBIDDEN in `.plan/`**: Other .md files, subdirectories except `architecture/`, staging files, temporary docs
**CONSOLIDATE**: If you need new content, merge into one of the 7 whitelisted files above.

### LOCAL Planning Markdown Files (Throughout `src/css/`)

**✅ REQUIRED**: Local planning markdown is mandatory throughout `src/css/`:
- `src/css/plan.md` — CSS root planning
- `src/css/core/core.md` — core infrastructure planning
- `src/css/core/*/*.md` — each subdirectory (asgi, db, redis, otel, types, orchestration, etc.)
- `src/css/modules/modules.md` — modules index
- `src/css/modules/*/<module>.md` — each module (agents, permissions, skills, tools, chat, etc.)
- `src/css/api_services/api_services.md` — provider planning

**These are NOT part of `.plan/` whitelist.** They are organizational files within the codebase structure. Each local planning markdown file:
- Reflects todos/milestones relevant to that directory
- Must be kept synchronized with files in `.plan/`, very important is `.plan/session.db` while working there
- Should be updated DURING work, not at end-of-session
- Is committed to git (part of codebase structure, not project planning)

---

## 📊 Tech Stack Rules

| Area                   | Decision                                                                                                      |
|------------------------|---------------------------------------------------------------------------------------------------------------|
| **Python**             | 3.14+ (async-first, no sync wrappers except CLI)                                                              |
| **Package Manager**    | `uv` (Python), `bun` (Node/JS)                                                                                |
| **ORM**                | Tortoise ORM (PostgreSQL) + asyncpg (async driver)                                                            |
| **Database**           | PostgreSQL (primary OLTP)                                                                                     |
| **Cache**              | Redis (rate limiter, token cache)                                                                             |
| **Observability**      | OpenObserve (time-series: telemetry, audit, API usage, LLM calls)                                             |
| **Frontend**           | React 19.2+, TypeScript,                                                                                      |
| **API**                | FastAPI (async), Pydantic v2                                                                                  |
| **Testing**            | pytest (unit/integration), only after phase complete                                                          |
| **Containerization**   | Docker Compose infra services: PostgreSQL, Redis, OpenObserve, Neo4j. App/frontend/Ollama run outside Docker. |
| **Async HTTP library** | `aiohttp`, never `httpx`                                                                                      |
| **Vector RAG**         | Database: postgres via docker compose                                                                         |
| **Graph RAG**          | Database: neo4j via docker compose service cybersec-neo4j                                                     |


### Running the App

```bash
# Start infra (postgres, redis, openobserve, neo4j) — Docker-only
docker-compose up -d

# Start ASGI app directly (NOT in Docker)
cd /home/daen/Projects/cybersecsuite
source .venv/bin/activate
CACHE_DIR=/tmp/css-cache LOG_DIR=/tmp/css-logs python manage.py serve --reload
# → uvicorn css.core.asgi.app:app --reload on port 8000

# Frontend (dev, NOT in Docker)
cd src/frontend && bun run dev
```

### Service Ports
| Port  | Service                  | Notes                                                                                                              |
|-------|--------------------------|--------------------------------------------------------------------------------------------------------------------|
| 8000  | Backend ASGI             | `manage.py serve` (direct)                                                                                         |
| 5432  | PostgreSQL               | Docker: `cybersec-postgres`                                                                                        |
| 6379  | Redis                    | Docker: `cybersec-redis`                                                                                           |
| 11434 | Ollama (local LLM)       | **Native process** — `OllamaProcessManager` starts `ollama serve` via asyncio subprocess (not Docker). Linux-only. |
| 5080  | OpenObserve (metrics/UI) | Docker: `cybersec-openobserve`                                                                                     |

> **Docker is infra-only** — `cybersec-dashboard`, `cybersec-frontend`, `cybersec-proxy`, `cybersec-ollama` are removed/legacy. The ASGI app and frontend run directly via `manage.py` + `bun`. Ollama runs natively via `OllamaProcessManager` (see `core/ollama/`).

### llama-cpp-python (CUDA — Pascal/GTX 10xx series, sm_61)

llama-cpp-python requires a manual build step for CUDA support. Run this **once** after `uv sync`:

```bash
uv pip install llama-cpp-python --reinstall --no-cache-dir --force-reinstall
```

> ⚠️ `sm_61` = Pascal architecture (GTX 1060/1070/1080 etc.). Do NOT change this for other GPU generations.

### manage.py Commands
```bash
python manage.py serve [--reload] [--port 8000]   # start ASGI
python manage.py init-db                           # drop + generate_schemas(safe=False) + seed
python manage.py shell                             # async REPL
```

---

## 🏗️ Project Structure (Django-style)

```
src/css/
├── core/              # Shared infrastructure
├── api_services/      # External providers (24+)
├── modules/           # Business logic
├── manager.py         # CLI entry
└── config.py          # Configuration (SOURCE OF TRUTH)
```

---

## 📁 Module Pattern (5 Optional Files for Organization)

```
modules/<name>/
├── __init__.py           # Package marker
├── models.py             # Tortoise ORM (auto-discovered IF present, optional)
├── endpoints.py          # FastAPI routes (auto-discovered IF present, optional)
├── types.py              # Dataclasses, types (organizational structure only, manually imported)
├── enums.py              # Enumerations (organizational structure only, manually imported)
├── exceptions.py         # Custom exceptions (organizational structure only, manually imported)
├── <name>.md             # Required module planning/ownership document
|-- other files 
└── __init__.py
```

### Module-Specific Structural Rules

- Every directory under `src/css/modules/` must contain `<module>.md` with the same basename as the module directory.
- Every Tortoise ORM table model in `src/css/modules/*/models.py` must inherit `css.core.db.models.base.BaseModel`, never raw `tortoise.Model`.
- If a module defines `Enum` classes, they belong in `enums.py`, not in `models.py`, `endpoints.py`, or ad-hoc utility files.

### Current Modules

The live module inventory changes faster than this rules file. Use `src/css/modules/` and
`src/css/modules/modules.md` as the canonical directory index.

Current module directories include:
`a2a_google`, `a2a_internal`, `agents`, `alerts`, `approvals`, `chat`, `compliance`,
`evidence`, `graphs`, `hooks`, `incidents`, `jetbrains`, `llm_proxy`, `local_assist`,
`mcps`, `mitre`, `planner-dev`, `projects`, `prompts`, `reports`, `scans`,
`scheduler`, `sessions`, `siem`, `skills`, `strategies`, `tags`, `tasks`, `teams`,
`threat_intel`, `tools`, `triage`, `webhooks`, and `workflows`.

**Binding ownership overrides**:
- `accounts`, `events`, `marketplace`, `memory`, `rag_vector`, and `rag_graph` belong in `src/css/core/`.
- Those core-owned areas must not have competing legacy module directories under `src/css/modules/`.
- `working_dir` is retired terminology. No implemented replacement package is confirmed; read the sessions, projects, and permissions owner docs before introducing a session-output manager.

**Moved to `core/` (infrastructure, not business logic)**:
- `accounts` → `core/accounts/`
- `cache` → `core/cache/` (KV cache: L1 memory, L2 Redis, L3 PostgreSQL)
- `events` → `core/events/`
- `marketplace` → `core/marketplace/`
- `memory` → `core/memory/` (legacy module package removed)
- `rag_vector` and `rag_graph` → currently `core/rag_vector/` and `core/rag_graph/`; a future move under `core/memory/` requires source/import/API migration
- `working_dir` → unresolved session-output boundary; the historical `core/workspace/` proposal is not implemented

**Loader.py auto-discovers**:
- `endpoints.py` — FastAPI routers (if present, module is skipped silently if missing)
- `models.py` — Tortoise ORM models (if present, module is skipped silently if missing)

**NOT auto-discovered** (manual import required):
- `types.py`, `enums.py`, `exceptions.py` — These provide structure/organization only. Import explicitly where needed.

---

## 🔧 Config as Source of Truth

```
config.py (CONFIG_SPEC: all vars, types, defaults)
    ↓ generates
.env.example (reference)
    ↓ user creates
.env (deployment)
    ↓ runtime
config.py loads from .env (overrides defaults)
```

**Rule**: New config → edit config.py only. Regenerate .env.example from CONFIG_SPEC.

---

## 📦 API Services (24 Providers)

Provider implementations in `api_services/`:

| Provider    | Type      | Status             |
|-------------|-----------|--------------------|
| ai21        | Cloud API | ⏳ Pending refactor |
| anthropic   | Cloud API | ⏳ Pending refactor |
| cerebras    | Cloud API | ⏳ Pending refactor |
| cloudflare  | Cloud API | ⏳ Pending refactor |
| cohere      | Cloud API | ⏳ Pending refactor |
| deepinfra   | Cloud API | ⏳ Pending refactor |
| deepseek    | Cloud API | ⏳ Pending refactor |
| fireworks   | Cloud API | ⏳ Pending refactor |
| gemini      | Cloud API | ⏳ Pending refactor |
| github      | Cloud API | ⏳ Pending refactor |
| groq        | Cloud API | ⏳ Pending refactor |
| huggingface | Cloud API | ⏳ Pending refactor |
| lambda_api  | Cloud API | ⏳ Pending refactor |
| mistral     | Cloud API | ⏳ Pending refactor |
| nscale      | Cloud API | ⏳ Pending refactor |
| nvidia      | Cloud API | ⏳ Pending refactor |
| ollama      | Local     | ⏳ Pending refactor |
| openai      | Cloud API | ⏳ Pending refactor |
| opencode    | Cloud API | ⏳ Pending refactor |
| openrouter  | Cloud API | ⏳ Pending refactor |
| perplexity  | Cloud API | ⏳ Pending refactor |
| sambanova   | Cloud API | ⏳ Pending refactor |
| together    | Cloud API | ⏳ Pending refactor |
| xai         | Cloud API | ⏳ Pending refactor |

**Pattern**: Each provider should follow a **consistent file structure**. The 5-file baseline (models, endpoints, types, enums, exceptions) is a guideline, not a rigid rule. Use more files if needed for functionality; use fewer if not all file types are needed (e.g., a provider without database models skips models.py, or without enums skips enums.py). The key is **consistent naming and patterns** across providers when files DO exist.

---

## 🧬 ABC & @dataclass Consistency

**❌ WRONG** — mixing on the same class:
```python
@dataclass
class Base(ABC):  # Contradictory — use one or the other
    pass

@dataclass
class Ctx(BaseModel):  # Also wrong — @dataclass + Pydantic together
    pass
```

**✅ RIGHT** (pick one per class):
```python
# Abstract contract → Protocol (Phase 6 P1 direction) or plain ABC
class Base(ABC):
    @abstractmethod
    def method(self): ...

# Value / data container → msgspec.Struct (preferred)

class SessionContext(msgspec.Struct, frozen=True):   # Phase 6 P1 target for all value types.py
    session_id: str
```

**Migration rule (Phase 6 P1)**: *When you touch a `@dataclass` value type, convert it to `msgspec.Struct`.* Don't mass-migrate — only on touch.

**Status**: `base_entity.py`, `base_header.py`, `base_client.py` still mix both → tracked in Phase 4 refactor todos. `core/types/context.py` uses `@dataclass + BaseModel` → tracked as `gap-context-antipattern` (Phase 15).

---

## 🔑 Pattern Consistency

### Module Organization
- ✅ **Consistent file structure** (baseline: models.py, endpoints.py, types.py, enums.py, exceptions.py — flexible based on module needs)
- ✅ Loader auto-discovers: endpoints.py + models.py only (if present, both optional)
- ✅ Types/enums/exceptions: manually imported (organizational structure only)
- **Current**: 2/19 modules (11%)

### Core Organization
- ✅ Each subdir follows consistent file/function/class/variable naming patterns
- ✅ Entities moved: core/types/entities/ → modules/*/types.py
- **Current**: 1/8 subdirs (13%)

### Entity Consolidation
```
Account    → core/accounts/types.py
Agent      → modules/agents/types.py
Role       → core/permissions/types.py
Skill      → modules/skills/types.py
Tool       → modules/tools/types.py
```

---

## 🧪 Testing Strategy

**❌ WRONG**: Test during phase (import errors, missing files)  
**✅ RIGHT**: Test only AFTER phase complete

**Process**:
1. Complete phase (all files created)
2. Validate imports (no circular deps)
3. Loader discovers all modules
4. Run pytest
5. Commit with checklist

---

## 💾 Git Commits

**Format**:
```
[TASK-X] Feature: Description
```

**Rules**:
- ✅ Atomic commits per module/subdir
- ✅ Validate before commit:
  - All necessary files present with consistent naming
  - No import errors
  - Loader discovers all
  - Todos updated
  - Validation checklist passed

---

## 📝 Scope Hierarchy

**Location** (filesystem):
- `~/.css/` — Global
- `$(pwd)/` — Project
- `$(pwd)/.css/sessions/session-<sid>/` — Session

**Orchestration** (runtime):
- Dev: 3 orchestrators (Planner, Normal, Background)
- Others: 2 orchestrators

---

## 📋 When to Update .plan/ Files

| Change          | File                              | Action                |
|-----------------|-----------------------------------|-----------------------|
| New feature     | plan.md + local markdown + session.db | Add + create todo |
| Phase milestone | plan.md                           | Update CURRENT STATUS |
| System design   | architecture.md                   | Add decision          |
| Process change  | development-workflow.md           | Update section        |
| New rule        | rules.md                          | Add section           |
| Progress        | session.db                        | Update todo status    |
| Phase summary   | checkpoints.md + memory.md        | Add entry + refresh counts |

---

## 🗄️ ORM Naming & Schema Rules

| Rule                                 | Detail                                                                                                                                                                                                                                                                                                     |
|--------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **No `Record` suffix**               | Model class is `LLMModel`, not `LLMModelRecord`. Table name is `llm_models`. Only suffix allowed is a domain noun (e.g., `ProviderCapability`, `ChatMessage`).                                                                                                                                             |
| **No migrations during dev**         | While phases are in progress we drop + reseed. `manage.py init-db` calls `generate_schemas(safe=False)` in dev, then runs all seed fixtures. Only consider Aerich migration tooling after all phases are locked.                                                                                           |
| **BaseModel required**               | Every Tortoise ORM entity inherits `css.core.db.models.base.BaseModel`. The default primary key comes from `BaseModel.id`, not from repeating raw `fields.BigIntField(primary_key=True)` in each model.                                                                                                    |
| **PrimaryKeyField default PK**       | `BaseModel.id` uses `PrimaryKeyField()` from `css.core.db.fields`. Override `id` only when a documented domain requirement truly needs a non-default primary key.                                                                                                                                          |
| **CharEnumField for enums**          | All enum-valued columns use `CharEnumField(MyEnum)`, never raw `CharField` with manual choices.                                                                                                                                                                                                            |
| **Semantic field helpers required**  | When field meaning matches an existing helper, use `css.core.db.fields`: `NameField`, `DescriptionField`, `VersionField`, `SlugField`, `UrlField`, `PathField`, `SHA512SumField`, `IPv4Field`, `IPv6Field`, `QualityScoreField`, `CostField`. Use raw Tortoise fields only when no helper fits the domain. |
| **Full Meta class**                  | Every model needs: `table`, `table_description`, `ordering`, `indexes` (as `models.Index(fields=[...])`), `unique_together` where applicable.                                                                                                                                                              |
| **Index syntax**                     | Always `models.Index(fields=["a", "b"])` — never tuple syntax `("a", "b")` (silently ignored).                                                                                                                                                                                                             |
| **auto_now timestamps**              | `created_at = fields.DatetimeField(auto_now_add=True)`, `updated_at = fields.DatetimeField(auto_now=True)` on every mutable model.                                                                                                                                                                         |
| **Soft delete pattern**              | `is_active = BooleanField(default=True, db_index=True)` + `deleted_at = DatetimeField(null=True)`. Use `SoftDeleteMixin` once created.                                                                                                                                                                     |
| **null=True only if truly nullable** | Don't use `null=True` as a default. Required fields must be non-null with a sensible default.                                                                                                                                                                                                              |
| **No duplicate enum names**          | One canonical enum per concept. Keep `Severity`, `Confidence`, `IOCStatus` — delete `SeverityLevel`, `ConfidenceLevel`, `ForensicIOCStatus`.                                                                                                                                                               |

---

## 🚫 Anti-Patterns (NEVER)

| Anti-Pattern                           | Fix                                                                                                         |
|----------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Create .md outside whitelist           | Consolidate to 7 files                                                                                      |
| Manual .env.example edits              | Regenerate from CONFIG_SPEC                                                                                 |
| Mix ABC + @dataclass on same class     | Use ABC alone OR @dataclass alone OR msgspec.Struct                                                         |
| @dataclass + BaseModel(Pydantic)       | Replace with msgspec.Struct (see gap-context-antipattern)                                                   |
| Test during phase                      | Test only after phase complete                                                                              |
| Cross-module imports (non-core)        | Import only from core                                                                                       |
| Hardcoded manager.py defaults          | Use CONFIG object                                                                                           |
| Inconsistent file/naming structure     | Follow patterns established in other modules for same domain                                                |
| Skip commit validation                 | Run validation checklist                                                                                    |
| `Record` suffix on ORM models          | Use domain noun only: `LLMModel`, `ChatMessage`, `ProviderCapability`                                       |
| Aerich migrations during dev           | Drop + reseed via `manage.py init-db` until all phases locked                                               |
| Tuple-syntax indexes in Meta           | Use `models.Index(fields=["a","b"])` — tuple syntax silently ignored                                        |
| `class X(Model)` for ORM entities      | Use `class X(BaseModel)` from `css.core.db.models.base`                                                     |
| Raw semantic fields when helper exists | Use `css.core.db.fields` helper classes for URLs, paths, versions, costs, scores, slugs, checksums, and IPs |


---


### Tortoise ORM Best Practices

| #  | Best Practice                                          | Why It Matters                          |
|----|--------------------------------------------------------|-----------------------------------------|
| 1  | Use `BigIntField(pk=True)` or custom `PrimaryKeyField` | Better than `IntField` for large tables |
| 2  | Always use **async** methods (`await`)                 | Tortoise is async-native                |
| 3  | Use **Aerich** for all migrations                      | Official and reliable migration tool    |
| 4  | Use `tortoise.contrib.pydantic` for FastAPI            | Clean Pydantic schemas from models      |
| 5  | Add indexes on frequently filtered fields              | Greatly improves query performance      |
| 6  | Use `atomic()` for transactions                        | Ensures data consistency                |
| 7  | Use `prefetch_related()` to avoid N+1 queries          | Critical for performance                |
| 8  | Keep models focused (no business logic)                | Better separation of concerns           |
| 9  | Use `JSONField` for flexible data                      | Good for metadata, params, etc.         |
| 10 | Close connections properly in tests                    | Prevents connection leaks               |

### Tortoise ORM Anti-Patterns (Avoid These)

| #  | Anti-Pattern                                      | Problem                              |
|----|---------------------------------------------------|--------------------------------------|
| 1  | Using sync code inside async functions            | Blocks the event loop                |
| 2  | Forgetting `prefetch_related()`                   | Causes N+1 query problem (very slow) |
| 3  | Putting business logic inside models              | Hard to test and maintain            |
| 4  | Not using Aerich for schema changes               | Manual SQL is error-prone            |
| 5  | Overusing `raw()` SQL queries                     | Loses ORM benefits and safety        |
| 6  | Creating too many connections without pooling     | Performance and resource issues      |
| 7  | Using `IntField(pk=True)` on high-volume tables   | Risk of running out of IDs           |
| 8  | Ignoring `Meta` class options (indexes, ordering) | Missed optimization opportunities    |
| 9  | Mixing sync and async Tortoise code               | Causes runtime errors                |
| 10 | Not handling database connection errors           | Poor error handling and crashes      |

---

## 1. Core Type Mappings (Legacy → Modern)

| Legacy (Avoid)                     | Modern (Python 3.14+)                        | Notes                              |
|------------------------------------|----------------------------------------------|------------------------------------|
| `typing.List[int]`                 | `list[int]`                                  | Use built-in                       |
| `typing.Dict[str, float]`          | `dict[str, float]`                           | Use built-in                       |
| `typing.Tuple[int, str]`           | `tuple[int, str]`                            | Use built-in                       |
| `typing.Set[str]`                  | `set[str]`                                   | Use built-in                       |
| `typing.FrozenSet[int]`            | `frozenset[int]`                             | Use built-in                       |
| `typing.Optional[str]`             | `str \| None`                                | Preferred                          |
| `typing.Union[int, str]`           | `int \| str`                                 | Preferred                          |
| `typing.Iterable[str]`             | `collections.abc.Iterable[str]`              | Abstract types                     |
| `typing.Mapping[str, int]`         | `collections.abc.Mapping[str, int]`          | Abstract types                     |
| `typing.Callable[[int], str]`      | `Callable[[int], str]` (from `typing`)       | See Callable table below           |

---

## 2. When to Import from `typing` (Still Recommended)

| Construct                   | Use Case                                      | Recommended Import                          |
|-----------------------------|-----------------------------------------------|---------------------------------------------|
| `Callable`                  | Functions, decorators, higher-order functions | `from typing import Callable`               |
| `ParamSpec` + `Concatenate` | Advanced decorators & wrappers                | `from typing import ParamSpec, Concatenate` |
| `TypedDict`                 | Structured dictionaries with known keys       | `from typing import TypedDict`              |
| `Protocol`                  | Structural interfaces / duck typing           | `from typing import Protocol`               |
| `Literal`                   | Specific allowed literal values               | `from typing import Literal`                |
| `Self`                      | Methods returning the current class instance  | `from typing import Self`                   |
| `TypeIs` / `TypeGuard`      | Custom type narrowing                         | `from typing import TypeIs, TypeGuard`      |
| `Annotated`                 | Attach metadata (validation, docs, etc.)      | `from typing import Annotated`              |
| `TypeVar` / `TypeVarTuple`  | Generic classes & functions                   | `from typing import TypeVar, TypeVarTuple`  |
| `Any`, `Never`, `NoReturn`  | Escape hatch, never-return functions          | `from typing import Any, Never, NoReturn`   |
| `LiteralString`             | Compile-time literal strings (security)       | `from typing import LiteralString`          |

---

## 3. `Callable` Patterns (Most Common Advanced Use)

| Pattern                              | Example                                                              | When to Use                  |
|--------------------------------------|----------------------------------------------------------------------|------------------------------|
| Simple function                      | `Callable[[int, str], bool]`                                         | Basic cases                  |
| Any arguments, specific return       | `Callable[..., str]`                                                 | Rare                         |
| Preserve signature (decorator)       | `Callable[P, R]` + `ParamSpec("P")`                                  | **Recommended**              |
| Add prefix argument                  | `Callable[Concatenate[str, P], R]`                                   | Wrappers                     |
| Method decorator                     | `Callable[Concatenate[Self, P], R]`                                  | Class methods                |
| Async callable                       | `Callable[P, Coroutine[Any, Any, R]]`                                | Async wrappers               |

**Best Practice**: Always import `Callable`, `ParamSpec`, and `Concatenate` from `typing` for anything beyond the simplest signatures.

---

## 4. Deprecated / Avoid in Python 3.14+

| Avoid                                     | Reason                                        | Replacement                                   |
|-------------------------------------------|-----------------------------------------------|-----------------------------------------------|
| `from typing import List, Dict, Tuple...` | Deprecated since 3.9, warnings starting 3.14+ | Built-ins                                     |
| `from __future__ import annotations`      | Mostly unnecessary (PEP 649 lazy evaluation)  | Remove                                        |
| `typing.ByteString`                       | Poorly defined, scheduled for removal in 3.17 | `collections.abc.Buffer` or explicit union    |
| Old `NamedTuple("Name", x=int)` syntax    | Deprecated since 3.13                         | Class-based or functional with list of tuples |
| `typing.no_type_check_decorator`          | Never supported by any major type checker     | Remove                                        |
| Direct access to `__annotations__`        | Fragile with lazy evaluation (PEP 649)        | `from annotationlib import get_annotations`   |

---

## Quick Decision Guide

**Use built-ins / `collections.abc` for:**
- Lists, dicts, sets, tuples
- Abstract collections (`Iterable`, `Mapping`, `Sequence`, etc.)

**Use `typing` for:**
- `Callable` (especially with `ParamSpec`)
- `TypedDict`, `Protocol`, `Literal`, `Self`, `TypeIs`
- Advanced generics (`TypeVar`, `Annotated`, etc.)

**Never use in new code (Python 3.14+):**
- `typing.List`, `Dict`, `Tuple`, `Optional`, `Union`
- `from __future__ import annotations`

---
