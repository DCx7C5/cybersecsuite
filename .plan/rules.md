# Development Rules

**Status**: 📋 Active Convention | **Updated**: 2026-05-03

---

## CRITICAL MOST IMPORTANT RULES TO STICK TO
- **no Co-authored-by: Copilot**
- **minimize your thinking chat to only essentials**
- **minimize your chat to only essentials**
- keep normal summaries in the end
- `.plan/` is now your working directory. Not `~/.copilot/` or `~/.claude` anymore. Or whatever else it was.
- no hallucinations, ask the user if unsure
- read the different workflows in [development-workflow.md](development-workflow.md)
- you have access to `.venv/bin/` here in the cybersecsuite Project
- don't ask dumb questions like should I mark task as complete or todo as complete. just run the necessary workflow.
- **you follow existing directory, documentary and code patterns for consistency**
- **WHEN WORKING IN PLAN MODE ALWAYS UPDATE EVERY .md UNDER `.plan/` and keep in sync with `.plan/session.db`!**
- **YOU HAVE OVERVIEW OF ARCHITECTURE for everything in `src/css/core/` -> `.plan/core/*.md`**
- **YOU HAVE OVERVIEW OF ARCHITECTURE for everything in `src/css/modules/` -> `.plan/modules/*.md`**
- **YOU HAVE OVERVIEW OF ARCHITECTURE for everything in `src/css/api_services/` -> `.plan/api_services/*.md`**
- **GENERAL ARCHITECTURE IN `.plan/architecture/*.md`**
- **TELL WHEN A SESSION IS ABOUT TO END OR A NEW ONE TO START**
- you are aware of analogy between `.plan/{core,modules,api_services}/` and `src/css/{core,modules,api_servies}`}`

# CRITICAL RULES ABOVE: VERIFY AND CONFIRM EVERY SINGLE ONE AFTER YOU HAVE COMPLETELY READ THIS FILE

## ✅ .plan/ WHITELIST (8 Files Only)

| File                         | Purpose                                               |
|------------------------------|-------------------------------------------------------|
| **plan.md**                  | Project overview, milestones, timeline                |
| **architecture/*.md**        | System design                                         |
| **api_services/*.md**        | Corresponding plan to src/css/api_services/<provider> |
| **modules/*.md**             | Corresponding plan to src/css/modules/<module>        |
| **core/*.md**                | Corresponding plan to src/css/core/<module>           |
| **memory.md**                | Highly compressed previous session context            |
| **development-workflow.md**  | Development process, git strategy                     |
| **rules.md**                 | THIS FILE — development rules                         |
| **checkpoints.md**           | Phase summaries, history                              |
| **archtiecture/frontend.md** | Frontend architecture, UI/UX patterns                 |
| **session.db**               | Todo tracker (SQLite)    ALWAYS KEEP IN SYNC!!!!!     |

**❌ FORBIDDEN**: Other .md files, subdirectories, staging files. if rule is broken, files content must be moved into white listed files and file deleted
**CONSOLIDATE**: If you need a new file, merge content into one of the 8 above.

---

## 📊 Tech Stack Rules

| Area | Decision |
|------|----------|
| **Python** | 3.14+ (async-first, no sync wrappers except CLI) |
| **Package Manager** | `uv` (Python), `bun` (Node/JS) |
| **ORM** | Tortoise ORM (PostgreSQL) + asyncpg (async driver) |
| **Database** | PostgreSQL (primary OLTP) |
| **Cache** | Redis (rate limiter, token cache) |
| **Observability** | OpenObserve (time-series: telemetry, audit, API usage, LLM calls) |
| **Frontend** | React 19.2+, TypeScript |
| **API** | FastAPI (async), Pydantic v2 |
| **Testing** | pytest (unit/integration), only after phase complete |
| **Containerization** | Docker Compose (6 services: ASGI, Dashboard, PostgreSQL, Redis, Ollama, OpenObserve) |

### Service Ports (docker-compose)
| Port | Service | Container |
|------|---------|-----------|
| 8765 | Backend ASGI (direct) | cybersec-proxy |
| 8000 | Dashboard HTTP | cybersec-dashboard |
| 8443 | Dashboard TLS | cybersec-dashboard |
| 5432 | PostgreSQL (Unix socket) | cybersec-postgres |
| 6379 | Redis | cybersec-redis |
| 11434 | Ollama (local LLM) | cybersec-ollama |
| 5080 | OpenObserve (metrics/UI) | cybersec-openobserve |

### ⚠️ Frontend Changes Require Service Restart
After editing React/TypeScript frontend code in `src/frontend/`:
```bash
docker-compose restart cybersec-dashboard
# or full restart
docker-compose down && docker-compose up -d
```
**Reason**: Dashboard container rebuilds on code changes, but not automatically detected

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

### Current Modules (19 total)

| Module | Purpose |
|--------|---------|
| agents | Agent orchestration & execution |
| cache | Caching layer (Redis, local) |
| capabilities | Capability definitions & registry |
| chat | Chat session management |
| events | Event bus & streaming |
| google_a2a | Google Auth2App integration |
| llm_models | LLM model registry & metadata |
| llm_proxy | LLM provider abstraction layer |
| marketplace | Marketplace (plugins, integrations) |
| memory | Memory & context management |
| permissions | Role-based access control |
| roles | Role definitions & assignment |
| scopes | Scope hierarchy (Project, App, Session, Team) |
| skills | Skill definitions & execution |
| streaming | Streaming & SSE support |
| tags | Tag management & categorization |
| teams | Team management & isolation |
| tools | Tool registry & execution |
| working_dir | Working directory & file management |

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

| Provider | Type | Status |
|----------|------|--------|
| ai21 | Cloud API | ⏳ Pending refactor |
| anthropic | Cloud API | ⏳ Pending refactor |
| cerebras | Cloud API | ⏳ Pending refactor |
| cloudflare | Cloud API | ⏳ Pending refactor |
| cohere | Cloud API | ⏳ Pending refactor |
| deepinfra | Cloud API | ⏳ Pending refactor |
| deepseek | Cloud API | ⏳ Pending refactor |
| fireworks | Cloud API | ⏳ Pending refactor |
| gemini | Cloud API | ⏳ Pending refactor |
| github | Cloud API | ⏳ Pending refactor |
| groq | Cloud API | ⏳ Pending refactor |
| huggingface | Cloud API | ⏳ Pending refactor |
| lambda_api | Cloud API | ⏳ Pending refactor |
| mistral | Cloud API | ⏳ Pending refactor |
| nscale | Cloud API | ⏳ Pending refactor |
| nvidia | Cloud API | ⏳ Pending refactor |
| ollama | Local | ⏳ Pending refactor |
| openai | Cloud API | ⏳ Pending refactor |
| opencode | Cloud API | ⏳ Pending refactor |
| openrouter | Cloud API | ⏳ Pending refactor |
| perplexity | Cloud API | ⏳ Pending refactor |
| sambanova | Cloud API | ⏳ Pending refactor |
| together | Cloud API | ⏳ Pending refactor |
| xai | Cloud API | ⏳ Pending refactor |

**Pattern**: Each provider should follow 5-file structure (models, endpoints, types, enums, exceptions)

---

## 🧬 ABC & @dataclass Consistency

**❌ WRONG**:
```python
@dataclass
class Base(ABC):  # Contradictory
    pass
```

**✅ RIGHT** (pick one):
```python
# Pure abstract
class Base(ABC):
    @abstractmethod
    def method(self): ...

# Pure concrete
@dataclass
class Base:
    field: str
```

**Status**: `base_entity.py`, `base_header.py`, `base_client.py` mix both → **refactor needed**

---

## 🔑 Pattern Consistency

### Module Organization
- ✅ 5-file pattern for structure (models, endpoints, types, enums, exceptions)
- ✅ Loader auto-discovers: endpoints.py + models.py only (if present, both optional)
- ✅ Types/enums/exceptions: manually imported (organizational structure only)
- **Current**: 2/19 modules (11%)

### Core Organization
- ✅ Each subdir follows 5-file pattern for consistency
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
[TRACK-X] Feature: Description
```

**Rules**:
- ✅ Atomic commits per module/subdir
- ✅ Validate before commit:
  - All 5-file pattern files present
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

| Change | File | Action |
|--------|------|--------|
| New feature | features_overview.md + session.db | Add + create todo |
| Phase milestone | plan.md | Update CURRENT STATUS |
| System design | architecture.md | Add decision |
| Process change | development-workflow.md | Update section |
| New rule | rules.md | Add section |
| Progress | session.db | Update todo status |
| Phase summary | checkpoints.md | Add entry |

---

## 🚫 Anti-Patterns (NEVER)

| Anti-Pattern | Fix |
|--------------|-----|
| Create .md outside whitelist | Consolidate to 7 files |
| Manual .env.example edits | Regenerate from CONFIG_SPEC |
| Mix ABC + @dataclass | Choose pure abstract OR pure concrete |
| Test during phase | Test only after phase complete |
| Cross-module imports (non-core) | Import only from core |
| Hardcoded manager.py defaults | Use CONFIG object |
| Missing 5-file pattern | Ensure all 5 files |
| Skip commit validation | Run validation checklist |
