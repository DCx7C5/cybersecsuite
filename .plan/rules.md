# Development Rules

**Status**: 📋 Active Convention | **Updated**: 2026-05-04

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

# 5. Read the local plan.md for the module you're working in
cat src/css/modules/<module_name>/plan.md
```


---

## CRITICAL MOST IMPORTANT RULES NEVER FORGET

### Session & Project Planning
- **ABSOLUTE: `.plan/plan.md` is the session workspace plan** — high-level project overview for THIS session's work (planning ONLY, not progress logs)
- **ABSOLUTE: track all progress in [.plan/session.db](session.db) ONLY** — every todo status change goes here, never in markdown
- **ABSOLUTE: local `plan.md` files exist throughout the codebase** — `src/css/plan.md`, `src/css/core/plan.md`, `src/css/modules/*/plan.md`, `src/css/api_services/plan.md`, `src/css/core/*/plan.md`, etc.
- **ABSOLUTE: keep EVERY local plan.md synchronized with [.plan/session.db](session.db) while working in that directory** — each plan.md reflects todos/milestones relevant to that module/subdirectory
- **ABSOLUTE: when working in a module (e.g., `src/css/modules/permissions/`), READ that module's local `plan.md` FIRST** — understand what's planned, in-progress, and completed for that area
- **ABSOLUTE: update local plan.md DURING work (not end-of-session)** — keep it fresh as todos move through pending → in_progress → done

### Code & Execution
- **ABSOLUTE: never add `Co-authored-by:` to any new commit** — historical commits contain it; do not amend history to remove it, but all future commits must omit it entirely
- **ABSOLUTE: keep thinking chat to bare essentials only** — No reasoning bloat, no hidden verbosity
- **ABSOLUTE: keep every chat response under 500 words unless impossible**
- **ABSOLUTE: explicitly announce whenever a TODO, TASK, or PHASE is completed**
- **ABSOLUTE: every tool execution must have a clear headline**
- **ABSOLUTE: always end with a normal summary**
- **ABSOLUTE: always prefer async Python whenever possible**
- **ABSOLUTE: for frontend work, always use `bun`, never `npm`, unless impossible**
- **ABSOLUTE: always use `aiohttp`, never `httpx`**
- **ABSOLUTE: never use `from __future__ import annotations`, it's an already built-in feature in newer Python versions**
- **ABSOLUTE: never use `Exception` only, create custom exception with help of base exceptions in `src/core/exceptions.py`**

### Architecture & Structure
- **ABSOLUTE: deletion of a module or whole directory is never a solution to a problem**
- **ABSOLUTE: in planning mode, always structure work as PHASE > TASK > TODO**
- **ABSOLUTE: every new TODO must belong to exactly one TASK and one PHASE**
- **ABSOLUTE: [.plan/](../.plan) is the working directory** — never treat `~/.copilot/` or `~/.claude` as the working directory
- **ABSOLUTE: use the project virtualenv at [.venv/bin/](../.venv/bin) whenever Python execution is needed**
- **ABSOLUTE: follow all existing directory, documentation, and code patterns for consistency**
- **ABSOLUTE: use [.plan/architecture/*.md](architecture) & nearest `plan.md` as the source of truth for general architecture**

### Workflow & Tooling
- **ABSOLUTE: read and follow [.plan/development-workflow.md](development-workflow.md) for every applicable task**
- **ABSOLUTE: in PLAN MODE, update every `.md` under `.plan/` and keep all of them synchronized with [.plan/session.db](session.db)**
- **ABSOLUTE: keep also `memory.md` and `checkpoints.md` in sync with [.plan/session.db](session.db)** — but only at end-of-session, not during work
- **ABSOLUTE: never hallucinate; if unsure, ask the user before proceeding**

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

**❌ FORBIDDEN in `.plan/`**: Other .md files, subdirectories, staging files, temporary docs
**CONSOLIDATE**: If you need new content, merge into one of the 7 whitelisted files above.

### LOCAL `plan.md` Files (Throughout `src/css/`)

**✅ REQUIRED**: Every directory in the `src/css/` tree has its own `plan.md`:
- `src/css/plan.md` — CSS root planning
- `src/css/core/plan.md` — core infrastructure planning
- `src/css/core/*/plan.md` — each subdirectory (asgi, db, redis, otel, types, orchestration, etc.)
- `src/css/modules/*/plan.md` — each module (agents, permissions, skills, tools, chat, etc.)
- `src/css/api_services/plan.md` — api_services planning

**These are NOT part of `.plan/` whitelist.** They are organizational files within the codebase structure. Each local `plan.md`:
- Reflects todos/milestones relevant to that directory
- Must be kept synchronized with files in `.plan/`, very important is `.plan/session.db` while working there
- Should be updated DURING work, not at end-of-session
- Is committed to git (part of codebase structure, not project planning)

---

## 📊 Tech Stack Rules

| Area                 | Decision                                                                             |
|----------------------|--------------------------------------------------------------------------------------|
| **Python**           | 3.14+ (async-first, no sync wrappers except CLI)                                     |
| **Package Manager**  | `uv` (Python), `bun` (Node/JS)                                                       |
| **ORM**              | Tortoise ORM (PostgreSQL) + asyncpg (async driver)                                   |
| **Database**         | PostgreSQL (primary OLTP)                                                            |
| **Cache**            | Redis (rate limiter, token cache)                                                    |
| **Observability**    | OpenObserve (time-series: telemetry, audit, API usage, LLM calls)                    |
| **Frontend**         | React 19.2+, TypeScript                                                              |
| **API**              | FastAPI (async), Pydantic v2                                                         |
| **Testing**          | pytest (unit/integration), only after phase complete                                 |
| **Containerization** | Docker Compose (6 services: ASGI, Dashboard, PostgreSQL, Redis, Ollama, OpenObserve) |

### Running the App

```bash
# Start infra (postgres, redis, ollama, openobserve) — Docker-only
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
| Port  | Service                  | Notes                        |
|-------|--------------------------|------------------------------|
| 8000  | Backend ASGI             | `manage.py serve` (direct)   |
| 5432  | PostgreSQL               | Docker: `cybersec-postgres`  |
| 6379  | Redis                    | Docker: `cybersec-redis`     |
| 11434 | Ollama (local LLM)       | **Native process** — `OllamaProcessManager` starts `ollama serve` via asyncio subprocess (not Docker). Linux-only. |
| 5080  | OpenObserve (metrics/UI) | Docker: `cybersec-openobserve` |

> **Docker is infra-only** — `cybersec-dashboard`, `cybersec-frontend`, `cybersec-proxy`, `cybersec-ollama` are removed/legacy. The ASGI app and frontend run directly via `manage.py` + `bun`. Ollama runs natively via `OllamaProcessManager` (see `core/ollama/`).

### llama-cpp-python (CUDA — Pascal/GTX 10xx series, sm_61)

llama-cpp-python requires a manual build step for CUDA support. Run this **once** after `uv sync`:

```bash
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=61" \
FORCE_CMAKE=1 \
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
|-- other files 
└── __init__.py
```

### Current Modules (20 total)

| Module        | Purpose                                       |
|---------------|-----------------------------------------------|
| agents        | Agent orchestration & execution               |
| capabilities  | Capability definitions & registry             |
| chat          | Chat session management                       |
| events        | Event bus & streaming                         |
| google_a2a    | Google Auth2App integration                   |
| intelligence  | Local AI assistance — Qwen3/Phi4/llama.cpp routing, quality gates, cost budget, conversation health (renamed from `triage`) |
| llm_models    | LLM model registry & metadata                 |
| llm_proxy     | LLM provider abstraction layer                | ⚠️ Directory does NOT exist — Phase 12 target |
| marketplace   | Marketplace (plugins, integrations)           |
| mcps          | MCP server management (register/connect/call) — PYTHON_DIRECT bypass, STDIO, SSE, HTTP transports |
| memory        | Memory & context management                   |
| permissions   | Role-based access control                     |
| prompts       | Prompt registry, template engine, variable substitution — reusable versioned prompt definitions |
| roles         | Role definitions & assignment                 |
| ~~scopes~~    | ⚠️ DEPRECATED — deletion target (Phase 15, todo: scopes-module-remove). Do NOT import. |
| skills        | Skill definitions & execution                 |
| streaming     | Streaming & SSE support                       |
| tags          | Tag management & categorization               |
| teams         | Team management & isolation                   |
| tools         | Tool registry & execution (LLM provider builtins; MCP tools bridged in via mcps/) |

**Moved to `core/` (infrastructure, not business logic)**:
- `cache` → `core/cache/` (KV cache: L1 memory, L2 Redis, L3 PostgreSQL)
- `working_dir` → `core/workspace/` (multi-workspace registry with per-entity expandable dir list)

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

# Value / data container → @dataclass (acceptable) or msgspec.Struct (preferred)
@dataclass
class SkillDefinition:     # pure data — no ABC, fine as-is until Phase 6 P1 migration
    field: str

class SessionContext(msgspec.Struct, frozen=True):   # Phase 6 P1 target for all value types
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
Account    → modules/accounts/types.py
Agent      → modules/agents/types.py
Role       → modules/permissions/types.py
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
| New feature     | features_overview.md + session.db | Add + create todo     |
| Phase milestone | plan.md                           | Update CURRENT STATUS |
| System design   | architecture.md                   | Add decision          |
| Process change  | development-workflow.md           | Update section        |
| New rule        | rules.md                          | Add section           |
| Progress        | session.db                        | Update todo status    |
| Phase summary   | checkpoints.md                    | Add entry             |

---

## 🗄️ ORM Naming & Schema Rules

| Rule | Detail |
|------|--------|
| **No `Record` suffix** | Model class is `LLMModel`, not `LLMModelRecord`. Table name is `llm_models`. Only suffix allowed is a domain noun (e.g., `ProviderCapability`, `ChatMessage`). |
| **No migrations during dev** | While phases are in progress we drop + reseed. `manage.py init-db` calls `generate_schemas(safe=False)` in dev, then runs all seed fixtures. Only consider Aerich migration tooling after all phases are locked. |
| **BigIntField PK always** | `id = fields.BigIntField(primary_key=True)` on every model. No `IntField`, no `CharField` PK. |
| **CharEnumField for enums** | All enum-valued columns use `CharEnumField(MyEnum)`, never raw `CharField` with manual choices. |
| **Full Meta class** | Every model needs: `table`, `table_description`, `ordering`, `indexes` (as `models.Index(fields=[...])`), `unique_together` where applicable. |
| **Index syntax** | Always `models.Index(fields=["a", "b"])` — never tuple syntax `("a", "b")` (silently ignored). |
| **auto_now timestamps** | `created_at = fields.DatetimeField(auto_now_add=True)`, `updated_at = fields.DatetimeField(auto_now=True)` on every mutable model. |
| **Soft delete pattern** | `is_active = BooleanField(default=True, db_index=True)` + `deleted_at = DatetimeField(null=True)`. Use `SoftDeleteMixin` once created. |
| **null=True only if truly nullable** | Don't use `null=True` as a default. Required fields must be non-null with a sensible default. |
| **No duplicate enum names** | One canonical enum per concept. Keep `Severity`, `Confidence`, `IOCStatus` — delete `SeverityLevel`, `ConfidenceLevel`, `ForensicIOCStatus`. |

---

## 🚫 Anti-Patterns (NEVER)

| Anti-Pattern                    | Fix                                   |
|---------------------------------|---------------------------------------|
| Create .md outside whitelist    | Consolidate to 7 files                |
| Manual .env.example edits       | Regenerate from CONFIG_SPEC           |
| Mix ABC + @dataclass on same class  | Use ABC alone OR @dataclass alone OR msgspec.Struct |
| @dataclass + BaseModel(Pydantic)    | Replace with msgspec.Struct (see gap-context-antipattern) |
| Test during phase               | Test only after phase complete        |
| Cross-module imports (non-core) | Import only from core                 |
| Hardcoded manager.py defaults   | Use CONFIG object                     |
| Inconsistent file/naming structure | Follow patterns established in other modules for same domain |
| Skip commit validation          | Run validation checklist              |
| `Record` suffix on ORM models   | Use domain noun only: `LLMModel`, `ChatMessage`, `ProviderCapability` |
| Aerich migrations during dev    | Drop + reseed via `manage.py init-db` until all phases locked |
| Tuple-syntax indexes in Meta    | Use `models.Index(fields=["a","b"])` — tuple syntax silently ignored |
