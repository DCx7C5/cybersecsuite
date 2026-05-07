## 🗂️ FILESYSTEM LAYOUT

> **Design principle**: Everything lives under `~/.css/`. No `.css/` folders scattered inside project source trees.
> Sessions, agents, teams, plans — all centralized. Projects are registered by reference to their source directory.

---

### Global (~/.css/)

```
~/.css/
├── config.yaml              # Global user config
├── credentials/             # API keys (per-provider files)
│   ├── anthropic.key
│   ├── openai.key
│   └── groq.key
├── cache/                   # Global cache
│   ├── embeddings/
│   └── models/
├── logs/                    # Global logs
│   └── app.log
│
├── projects/                # ProjectManager registry
│   ├── projects.json        # List of registered projects: {id, name, path, created_at}
│   └── <project-id>/        # Per-project metadata (NOT source code)
│       ├── metadata.json    # {id, name, source_dir, created_at}
│       └── config.yaml      # Project-level config overrides (overrides global)
│
└── sessions/                # ALL sessions live here, regardless of project
    ├── session-<sid>/
    ├── session-<sid>/
    └── session-<sid>/
```

---

### ProjectManager

Projects are NOT directories that contain a `.css/` folder. Projects are **registered references** to a source directory.

```
# Register an existing project directory
ProjectManager.create(name="my-webapp", source_dir="/home/user/projects/my-webapp")
→ creates ~/.css/projects/<generated-id>/metadata.json
   {id, name, source_dir: "/home/user/projects/my-webapp", created_at}

# List all registered projects
ProjectManager.list() → list of {id, name, source_dir}

# Add session to project
ProjectManager.add_session(project_id, session_id)
→ stored in ~/.css/projects/<project-id>/metadata.json

# Remove project (does NOT delete source dir or its sessions)
ProjectManager.remove(project_id)
→ deletes ~/.css/projects/<project-id>/

# CRUD summary: create / list / get / update / remove
```

Sessions are linked to a project via `project_id` field in session metadata. A session without a `project_id` is a standalone session (e.g. a quick threat-hunt).

---

### Session (~/.css/sessions/session-\<sid\>/)

All sessions live here. Source code is accessed via the `project.source_dir` path — never copied into the session dir.

```
~/.css/sessions/session-<sid>/
├── metadata.json            # {id, mode, project_id|null, created_at, agent_id, target}
├── config.yaml              # Session config (run_mode, model tier, etc.)
│
├── plan/                    # Planner mode output only (mode=development)
│   ├── decisions/
│   ├── analysis/
│   ├── proposals.md
│   └── logs/
│
├── teams/                   # Team subdivisions
│   ├── team-<name>/
│   │   ├── config.yaml
│   │   ├── queue.db         # SQLite task queue (team-local)
│   │   ├── orchestrators/   # Per-orchestrator state files
│   │   │   ├── orch-1.json
│   │   │   └── orch-2.json
│   │   ├── results/
│   │   └── logs/
│   └── team-<name>/
│       └── [same structure]
│
├── orchestrators/           # Standalone orchestrators (no teams)
├── tasks/                   # Task definitions & status
│   ├── task-001.json
│   └── task-002.json
├── findings/                # Evidence, screenshots, notes (cybersec sessions)
├── artifacts/               # Tool output (nmap xml, burp exports, etc.)
├── results/                 # Aggregated results
│   └── results.json
└── logs/
    └── app.log
```

**Session modes** (`metadata.json` → `mode` field):
- `development` — planner + main orchestrator + triage. Reads project source_dir. Writes to session dir.
- `red_team` — attack context. Full access to project source_dir + system paths (per PathGrant).
- `blue_team` — defense context. Same access model as red_team.
- `purple_team` — two orchestrators sharing results via IPC.
- `search` — lightweight threat-hunt. findings/ + artifacts/ only, no plan.

### Project Source Files

```markdown
src/css/
├── api_services/
│   ├── <provider>/
│   │   ├── __init__.py
│   │   ├── spec.yaml          # ProviderSpec declaration (model aliases, endpoints, auth)
│   │   ├── adapter.py         # Optional provider-specific adapter glue
│   │   ├── client.py
│   │   ├── response.py
│   │   └── exceptions.py
│   └── ...
├── core/
│   ├── asgi/            # ASGI app, lifespan, router
│   ├── cache/           # ← KV cache infrastructure (L1 memory, L2 Redis, L3 PostgreSQL)
│   │   ├── base.py      #   CacheBackend ABC, L1MemoryCache, L2RedisCache, L3PostgresCache
│   │   ├── models.py    #   CacheEntry (dataclass) + CacheEntryModel (Tortoise ORM)
│   │   ├── exceptions.py
│   │   └── __init__.py
│   ├── prompt_cache/    # ← LLM prompt caching (Phase 11) — provider-native cache injection
│   │   ├── manager.py   #   PromptCacheManager (Redis exact-match + adapter-native)
│   │   ├── anthropic_injector.py  # CacheBreakpointInjector (cache_control breakpoints)
│   │   └── __init__.py
│   ├── db/              # Tortoise ORM config, base models
│   ├── ollama/          # ← Native Ollama process management (Phase 33)
│   │   ├── installer.py #   OllamaInstallChecker (Linux/Arch/Debian) — documents dev models
│   │   ├── process.py   #   OllamaProcessManager (asyncio subprocess)
│   │   ├── client.py    #   thin wrapper around ollama.AsyncClient
│   │   └── __init__.py
│   ├── orchestration/
│   ├── otel/
│   ├── redis/
│   ├── resilience/      # ← retry/backoff/detection (renamed from retry/)
│   │   ├── config.py
│   │   ├── detection.py
│   │   ├── orchestrator.py
│   │   ├── retry_wrapper.py
│   │   └── __init__.py
│   ├── types/
│   ├── workspace/       # ← Multi-workspace registry (Phase 15, replaces working_dir module)
│   │   ├── registry.py  #   WorkspaceRegistry — tracks N dirs per entity, expandable at runtime
│   │   ├── layouts.py   #   planner_layout(), search_layout()
│   │   ├── handle.py    #   WorkspaceDirHandle — enforces permissions per path
│   │   └── __init__.py
│   ├── loader.py
│   ├── logger.py
│   └── plan.md
└── modules/
    └── <module>/        # 20 business-logic modules (see rules.md)
        ├── __init__.py
        ├── models.py
        ├── endpoints.py
        ├── types.py
        ├── enums.py
        ├── exceptions.py
        └── other files

```


---

## Phase 6 Alignment (2026-05-07)

### API service provider declaration pattern

`api_services` should standardize around declarative provider metadata:

1. `spec.yaml` is the source of truth for provider capabilities and model mapping.
2. `HttpProviderAdapter` consumes `ProviderSpec` and normalizes request/response behavior.
3. Service startup composes providers from `entry_points` + YAML spec loading.
