# @loader — Auto-Discovery for Modules & Models

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/core/loader.py` (~150+ lines)

**Responsibility**: Auto-discover module routers, ORM models, FastAPI integration.

---

## Overview

The loader auto-discovers:
1. **Module routers** — Each `modules/<app>/endpoints.py` exposes `router` or `root_router`
2. **ORM models** — Each `modules/<app>/models.py`, `api_services/<app>/models.py`, `core/db/models/`
3. **Tortoise ORM config** — Builds connection URL from environment

---

## Module Router Discovery

### Convention

Each module **optionally** exposes:

- **`router: APIRouter`** (required) — App-scoped routes (e.g., `/api/marketplace/*`)
- **`root_router: APIRouter`** (optional) — Root-level routes (e.g., `/.well-known/*`)

**File**: `src/css/core/marketplace/endpoints.py`

```python
from fastapi import APIRouter

router = APIRouter(prefix="/marketplace", tags=["marketplace"])

@router.get("/status")
async def get_status():
    return {"status": "ok"}

@router.post("/install")
async def install_item(item_id: str):
    # installation logic
    pass
```

### Discovery Function

```python
def iter_app_routers() -> Iterator[AppRouters]:
    """Yield AppRouters for every sub-package of modules that has endpoints.py.
    
    Yields:
        AppRouters namedtuple with (app_name, router, root_router)
    
    Silently ignores modules with no endpoints.py.
    Raises errors from modules that DO exist (broken endpoints surface immediately).
    """
    # 1. Iterate all modules in css.modules
    # 2. For each, try import css.modules.<app>.endpoints
    # 3. Extract router + root_router attributes
    # 4. Yield AppRouters(app_name, router, root_router)
```

### Router Mounting

**File**: `src/css/core/asgi/router.py`

```python
def mount_app_routers(app: FastAPI):
    """Mount all discovered app routers to the FastAPI instance."""
    from css.core.loader import iter_app_routers
    
    for app_routers in iter_app_routers():
        # Mount app-scoped router
        if app_routers.router:
            app.include_router(
                app_routers.router,
                prefix=f"/api/{app_routers.app_name}"
            )
        
        # Mount root router (e.g., /.well-known/*)
        if app_routers.root_router:
            app.include_router(app_routers.root_router)
```

**Result**:

```
Module: marketplace → /api/marketplace/status, /api/marketplace/install
Module: chat → /api/chat/send, /api/chat/history
Module: capabilities → /api/capabilities/list
```

---

## ORM Model Discovery

### Convention

Models are discovered from:
- `css.core.db.models` (core models)
- `css.modules.<app>.models` (for each module)
- `css.api_services.<app>.models` (for each API service)

**File**: `src/css/core/db/models/marketplace.py`

```python
from tortoise import Model, fields

class MarketplaceItem(Model):
    """Marketplace package."""
    
    id = fields.BigIntField(primary_key=True)
    slug = fields.CharField(max_length=255, unique=True, db_index=True)
    name = fields.CharField(max_length=255)
    # ... other fields
    
    class Meta:
        table = "marketplace_item"
```

### Discovery Function

```python
def discover_tortoise_models() -> list[ModelModule]:
    """Auto-discover all Tortoise ORM models.
    
    Returns:
        List of ModelModule namedtuples with (module_name, model_path)
    """
    models = []
    
    # Core models (always included)
    models.append(ModelModule("core.db", "css.core.db.models"))
    
    # Module models
    for module_name in discover_modules():
        models.append(ModelModule(
            module_name,
            f"css.modules.{module_name}.models"
        ))
    
    # API service models
    for service_name in discover_api_services():
        models.append(ModelModule(
            service_name,
            f"css.api_services.{service_name}.models"
        ))
    
    return models
```

---

## Tortoise ORM Configuration

### URL Building

```python
def build_tortoise_db_url(db_config: dict) -> str:
    """Build Tortoise ORM-compatible asyncpg connection string.
    
    Supports both TCP (host:port) and Unix socket modes.
    
    Args:
        db_config: Database config dict
    
    Returns:
        Tortoise connection URL like "asyncpg://user:pass@host:port/dbname"
    """
    host = db_config.get("host")
    port = db_config.get("port")
    user = db_config.get("user", "cybersec")
    password = db_config.get("password", "change_me")
    database = db_config.get("database", "cybersec_forensics")
    
    if host:
        # TCP mode
        port_val = port or 5432
        return f"asyncpg://{user}:{password}@{host}:{port_val}/{database}"
    else:
        # Unix socket mode
        return f"asyncpg://{user}:{password}@/{database}?host=/var/run/postgresql"
```

### Tortoise Config Dict

```python
# Generated by loader, used in app.py lifespan
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "cybersec-postgres",
                "port": 5432,
                "user": "cybersec",
                "password": "<from env>",
                "database": "cybersec",
            }
        }
    },
    "apps": {
        "models": {
            "models": [
                "css.core.db.models",
                "css.modules.marketplace.models",
                "css.modules.chat.models",
                # ... auto-discovered models
            ],
            "default_connection": "default",
        }
    }
}
```

---

## Integration in App Startup

**File**: `src/css/core/asgi/app.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    
    # 1. Build Tortoise config (auto-discovers models)
    tortoise_config = build_tortoise_config()
    
    # 2. Initialize Tortoise ORM
    await Tortoise.init(config=tortoise_config)
    await Tortoise.generate_schemas()
    
    # 3. Mount module routers (auto-discovers endpoints)
    mount_app_routers(app)
    
    yield
    
    # Shutdown
    await Tortoise.close_connections()
```

---

## Error Handling

**Convention**: 
- Modules with **no** `endpoints.py` → silently ignored
- Modules with `endpoints.py` but **broken imports** → error raised (fail fast)

```python
try:
    module = importlib.import_module(f"css.modules.{module_name}.endpoints")
    router = getattr(module, "router", None)
except ImportError as e:
    if "No module named" in str(e):
        pass  # No endpoints.py, skip
    else:
        log.error(f"Failed to import {module_name}.endpoints: {e}")
        raise  # Broken endpoints, fail startup
```

---

## Key Data Structures

```python
class AppRouters(NamedTuple):
    """Discovered routers from a module."""
    app_name: str
    router: APIRouter | None
    root_router: APIRouter | None

class ModelModule(NamedTuple):
    """Discovered ORM model module."""
    module_name: str
    model_path: str  # Python dot path for Tortoise config
```

---

## Integration Points

- **@asgi**: Calls `mount_app_routers()` to register module endpoints
- **@db**: Builds Tortoise ORM config with discovered models
- **All modules**: Auto-mounted if they expose `router` or `root_router`
- **All models**: Auto-discovered and registered with Tortoise

---

**Status**: 🟢 Implemented | **Priority**: 🔴 High | **Last Updated**: 2026-05-03


# @logger — Unified Logging System

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/core/logger.py` (71 lines)

**Responsibility**: Centralized logger factory, lazy root initialization, dual output (file + stdout), cached instances.

---

## Overview

Every module initializes its logger from the core factory:

```python
from css.core.logger import getLogger

logger = getLogger(__name__)  # Lazy initialization on first call
```

**Result**: Logger instances named `css.modules.cache`, `css.modules.chat`, etc.

---

## Implementation Details

**Key feature**: Root logger only initialized on **first `getLogger()` call**

```python
# src/css/core/logger.py (actual implementation)

import logging
import logging.handlers
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASGI_LOG = PROJECT_ROOT / "asgi.log"

_log_level = logging.INFO
_loggers: dict[str, logging.Logger] = {}

def _ensure_root() -> logging.Logger:
    """Lazily configure root logger (runs once on first getLogger call)."""
    global _loggers
    if "cybersecsuite" in _loggers:
        return _loggers["cybersecsuite"]
    
    root = logging.getLogger("cybersecsuite")
    root.setLevel(_log_level)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    # File handler (rotating)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=ASGI_LOG,
        maxBytes=1024 * 1024,    # 1MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
    _loggers["cybersecsuite"] = root
    
    return root

def getLogger(name: str) -> logging.Logger:
    """Get a logger instance, cached for reuse.
    
    Args:
        name: Logger name (typically __name__ from calling module)
    
    Returns:
        Configured logger instance
    
    Example:
        from css.core.logger import getLogger
        logger = getLogger(__name__)  # 'css.modules.cache'
        logger.info("Cache hit: key123")
    """
    if name in _loggers:
        return _loggers[name]
    
    _ensure_root()
    logger = logging.getLogger(name)
    logger.setLevel(_log_level)
    _loggers[name] = logger
    return logger
```
---

## Log Levels & Examples

| Level | Example |
|-------|---------|
| `DEBUG` | `logger.debug(f"Cache L1 miss, checking L2")` |
| `INFO` | `logger.info(f"Marketplace seeded: 36 agents")` |
| `WARNING` | `logger.warning(f"Redis timeout, falling back")` |
| `ERROR` | `logger.error(f"Checksum mismatch: {item_id}")` |
| `CRITICAL` | `logger.critical(f"Database unreachable")` |

---

## Output Destinations

### 1. **File Logging**

- **Location**: `src/css/asgi.log` (in project root)
- **Rotating**: 1MB per file, keep 5 backups (5MB total)
- **Format**: ISO timestamp + logger name + level + message

### 2. **Console Logging**

- **Destination**: stdout (captured by Docker daemon)
- **View with**: `docker logs cybersec-proxy`
- **Same format** as file handler

---

## Module Logger Pattern

Every module's `__init__.py` follows this pattern:

```python
"""Module docstring."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)  # Becomes 'css.modules.{module_name}'

from .models import ...
from .exceptions import ...

__all__ = [...]
```

---

## Caching Mechanism

Module loggers are cached in `_loggers` dict:

```python
_loggers = {
    "cybersecsuite": <root logger>,
    "css.modules.marketplace": <marketplace logger>,
    "css.modules.chat": <chat logger>,
    # ... all other module loggers
}
```

Subsequent calls to `getLogger(name)` return cached instance (no re-initialization).

---

# core/prompt_cache/ — LLM Prompt Caching (Phase 11, renamed from caching/)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos added here must be synced with `.plan/session.db`.

**Location**: `src/css/core/prompt_cache/`  
**Status**: 🔴 Pending

### Overview

Two-tier prompt cache managed by `PromptCacheManager`. Gemini `NATIVE_RESOURCE` deferred.

```
Tier 1: Redis exact-match (all providers)
Tier 2: Native provider caching — Anthropic only (Phase 11)
```

### Files
```
core/prompt_cache/
├── __init__.py
├── manager.py              — PromptCacheManager (Tier 1 + Tier 2 orchestration)
└── anthropic_injector.py   — CacheBreakpointInjector (cache_control breakpoints)
```

> Gemini `cachedContent` → deferred to future phase. Add `gemini_cache.py` only when needed.

### Key todos (session.db)
| Todo ID | Description |
|---------|-------------|
| `cache-caching-capability-enum` | CachingCapability enum on LLMAdapter |
| `cache-prompt-cache-manager` | PromptCacheManager class |
| `cache-redis-exact-match` | Tier 1 Redis exact-match |
| `cache-anthropic-breakpoint-injector` | CacheBreakpointInjector |

---

# core/cache/ — KV Caching Layer (moved from modules/cache/)

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos added here must be synced with `.plan/session.db`.

**Todo**: `cache-move-to-core` (Phase 3) — move `modules/cache/` to `core/cache/`.

**Location**: `src/css/core/cache/`  
**Status**: 🔴 Pending (`cache-move-to-core` not yet started)

### Overview

3-layer KV cache (L4 SQLite removed — PostgreSQL + Redis are the stack):

```
L1: MemoryCache    — in-process dict, TTL eviction
L2: RedisCache     — redis.asyncio.from_url (migrated from deprecated aioredis.create_redis_pool)
L3: PostgreSQL     — CacheEntry ORM model (persistent, auditable)
```

### Files (target layout)
```
core/cache/
├── __init__.py
├── base.py          — CacheBackend protocol, UnifiedCache orchestrator
├── models.py        — CacheEntry, CacheStats (Tortoise ORM)
├── exceptions.py    — CacheError, CacheMiss, CacheWriteError
└── plan.md          — (this section, will become standalone file)
```

### Key todos (session.db)
| Todo ID | Description |
|---------|-------------|
| `cache-move-to-core` | Move module, update all imports, fix L2 redis.asyncio |
| `cache-remove-l4-sqlite` | Delete L4 SqliteCache class |
| `cache-fix-l2-redis-client` | Migrate from `aioredis.create_redis_pool` → `redis.asyncio.from_url` |

---

# core/workspace/ — Multi-Workspace Registry

**Todo**: `working-dir-manager` updated (Phase 15)  
**Location**: `src/css/core/workspace/`  
**Status**: 🔴 Pending

### Concept

An entity (session or agent) owns a `WorkspaceRegistry` containing N `WorkspaceDirHandle` entries.

```
workspaces[0]  = DEFAULT  ~/.css/sessions/<sid>/        READ+WRITE  (always present)
workspaces[1]  = PROJECT  /home/user/my-project/        READ+WRITE  (optional, default)
workspaces[N]  = EXTRA    /any/path/in/the/system       configurable (expandable at runtime)
```

- `workspaces.default` → always `workspaces[0]`
- `WorkspaceRegistry.add(path, permissions=READ|WRITE)` → new `WorkspaceDirHandle`
- `WorkspaceDirHandle` enforces its `PermissionSet` on all path operations
- Both default + project dir have WRITE by default

### Files (target layout)
```
core/workspace/
├── __init__.py
├── registry.py      — WorkspaceRegistry (add, remove, get_default, list_all)
├── handle.py        — WorkspaceDirHandle + PermissionSet enum
├── layouts.py       — planner_layout(), search_layout() helpers
└── plan.md
```

---

# core/ollama/ — Native Ollama Process Manager

**Todos**: Phase 33 (`ollama-install-checker`, `ollama-process-manager`, `ollama-model-preloader`, `ollama-lifespan-wire`, `ollama-docker-remove`, `ollama-llama-cpp-dep`)  
**Location**: `src/css/core/ollama/`  
**Status**: 🔴 Pending

### Components

```
core/ollama/
├── __init__.py
├── installer.py     — OllamaInstallChecker (Linux-only, Arch/Debian)
│                      also prints dev hint: which models to pull manually
│                        ollama pull qwen3:0.6b
│                        ollama pull phi4-mini:3.8b-q4_K_M
│                        ollama pull qwen3:4b-q4_K_M
├── process.py       — OllamaProcessManager (asyncio.create_subprocess_exec)
├── client.py        — thin wrapper → ollama.AsyncClient
└── plan.md
```

> **One client only**: `ollama.AsyncClient`. Ollama handles CUDA natively via GGML.
> `llama-cpp-python` is an optional dep for in-process GGUF loading — **not** wired into
> `core/ollama/`. Install only if needed separately (see CUDA install command in sdks.md).
> No auto-preloader: models are dev recommendations, pulled manually before dev sessions.

### llama-cpp-python CUDA (Pascal GTX 10xx, sm_61)
Run ONCE after `uv sync` IF needed for direct GGUF loading (NOT required for Ollama):
```bash
CMAKE_ARGS="-DGGML_CUDA=on -DCMAKE_CUDA_ARCHITECTURES=61" \
FORCE_CMAKE=1 \
uv pip install llama-cpp-python --reinstall --no-cache-dir --force-reinstall
```



> **BIDIRECTIONAL SYNC REQUIRED**: This file and `.plan/session.db` must always be in sync.
>
> - When adding/completing a TODO: update `status` in `.plan/session.db`
> - When updating session.db: reflect changes back to this checklist
> - **PHASE > TASK > TODO is ABSOLUTE** — every TODO belongs to exactly one TASK in one PHASE
> - See `.plan/rules.md` CRITICAL section for full rules
>
> **Pattern rules enforced here**:
> - `__all__` lives ONLY in `__init__.py` (never in types.py, enums.py, endpoints.py)
> - Never mix `@dataclass` with `ABC` on the same class
> - Use `msgspec.Struct` for value types, `Protocol` for structural contracts (Phase 6)
> - HTTP clients: always `aiohttp`, never `httpx`
> - Package manager: always `uv`/`bun`, never `pip`/`npm`
