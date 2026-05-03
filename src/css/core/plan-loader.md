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

**File**: `src/css/modules/marketplace/endpoints.py`

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

**File**: `src/css/modules/marketplace/models.py`

```python
from tortoise import Model, fields

class MarketplaceItem(Model):
    """Marketplace package."""
    
    id = fields.CharField(max_length=255, pk=True)
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
