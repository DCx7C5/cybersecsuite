# @marketplace — Remote Package Manager & Installation

⚠️ **CRITICAL SESSION.DB SYNC REQUIREMENT**: All todos, tasks, or implementation changes added to this plan must be synchronized with `.plan/session.db`. When you add/modify/remove TODOs in this file, update session.db accordingly. This file and session.db are **bidirectional sources-of-truth** for implementation tracking.

---

**Location**: `src/css/modules/marketplace/`

**Responsibility**: Install agents, skills, workflows, prompts, templates, and MCPs from remote GitHub index. Provide update detection and package management UI.

---

## Current State

🟡 **Partial** (seeder exists, installer skeleton, no update detection)

**Files**:
- `seeder.py` — Fetches index.json from GitHub, verifies SHA512, seeds DB
- `installer.py` — Skeleton for package installation
- `models.py` — ORM models (MarketplaceMeta, MarketplaceItem)
- `endpoints.py` — Basic REST routes
- `enums.py` — Package types (agent, skill, mcp, template, workflow, prompt)
- `exceptions.py` — Custom exceptions
- `base.py`, `registry.py`, `types.py` — Supporting code

---

## Purpose

- **Remote Installation**: Download & install 36+ agents, 60+ skills, workflows, prompts, templates, MCPs from `ai-marketplace` GitHub repo
- **Update Detection**: Track SHA512 hash of remote index.json → notify frontend when updates available
- **Package Management**: Install, uninstall, list, filter packages by type
- **Multi-Type Support**: Handle 6 different package types with appropriate installation paths
- **Background Sync**: Check for updates every 1 hour (configurable)

---

## Index Structure

Remote index at: `https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json`

```json
{
  "version": "0.1.0",
  "updated": "2026-05-02T12:55:07.083375",
  "agents": [
    {
      "name": "agent-factory",
      "description": "Universal agent factory...",
      "file": "agents/AGENT_FACTORY.md",
      "sha512": "abc123..."
    },
    ...
  ],
  "skills": [...],
  "workflows": [...],
  "prompts": [...],
  "templates": [...],
  "mcps": [...]
}
```

**Hash Verification File**: `index.json.sha512` (single SHA512 hex string)

---

## Installation Paths

| Type      | Path                                  | Format  |
|-----------|---------------------------------------|---------|
| agents    | `~/.css/packages/agents/{name}.md`    | File    |
| skills    | `~/.css/packages/skills/{name}/`      | Archive |
| workflows | `~/.css/packages/workflows/{name}.yaml` | File    |
| prompts   | `~/.css/packages/prompts/{name}.md`   | File    |
| templates | `~/.css/packages/templates/{name}.json` | File    |
| mcps      | `~/.css/packages/mcps/{name}/`        | Archive |

---

## 5-Phase Implementation

### Phase 1: Update Detection [HIGH 🔴]

**Goal**: Track remote index hash locally, notify frontend when updates available

```python
# In models.py
class MarketplaceMeta(Model):
    name = fields.CharField(max_length=255)
    version = fields.CharField(max_length=20)
    remote_index_hash = fields.CharField(max_length=512, null=True)  # NEW
    local_index_hash = fields.CharField(max_length=512, null=True)   # NEW
    update_available = fields.BooleanField(default=False)             # NEW
    last_index_check = fields.DatetimeField(null=True)               # NEW
```

**In seeder.py**:
```python
async def check_for_updates(self) -> bool:
    """Compare remote vs. local index hash."""
    remote_hash = await self.fetch_index_hash()
    meta = await MarketplaceMeta.get_or_none()
    
    if not meta or remote_hash != meta.remote_index_hash:
        if meta:
            meta.update_available = True
            await meta.save()
        return True
    return False
```

**In endpoints.py**:
```python
@router.get("/status")
async def marketplace_status():
    """Frontend calls to check for updates."""
    meta = await MarketplaceMeta.get_or_none()
    return {
        "updates_available": meta.update_available if meta else False,
        "version": meta.version if meta else "0.0.0",
    }
```

---

### Phase 2: Multi-Type Seeder [HIGH 🔴]

**Goal**: Support all 6 package types, not just agents

**In seeder.py**:
```python
async def seed_if_empty(self, force: bool = False) -> dict:
    """Seed all types: agents, skills, workflows, etc."""
    index_data = await self.fetch_index()
    results = {}
    
    for item_type in ["agents", "skills", "workflows", "prompts", "templates", "mcps"]:
        items = index_data.get(item_type, [])
        created, skipped = await self._seed_type(items, item_type)
        results[item_type] = {"created": created, "skipped": skipped}
    
    return results

async def _seed_type(self, items: list, item_type: str) -> tuple:
    """Process items of a specific type."""
    # Map items to MarketplaceItem records
    # Use _get_install_path() to compute destination

def _get_install_path(self, item: dict, item_type: str) -> str:
    """Return install path based on type mapping."""
    # Return path from table above
```

---

### Phase 3: Installation Implementation [MEDIUM 🟡]

**Goal**: Download, verify checksum, extract packages

**In installer.py**:
```python
async def install_package(self, item_id: str, force: bool = False) -> InstallationResult:
    """Download, verify, extract, update DB."""
    item = await MarketplaceItem.get_or_none(id=item_id)
    
    # 1. Download with timeout
    content = await self._download_package(item.source_url)
    
    # 2. Verify SHA512
    if item.meta.get("sha512"):
        actual = hashlib.sha512(content).hexdigest()
        expected = item.meta["sha512"]
        if actual != expected:
            raise ChecksumMismatch(item_id)
    
    # 3. Extract or write
    install_path = Path(item.install_path).expanduser()
    install_path.parent.mkdir(parents=True, exist_ok=True)
    
    if item.kind in [MarketplaceItemType.mcp, MarketplaceItemType.skill]:
        await self._extract_archive(content, install_path)
    else:
        install_path.write_bytes(content)
    
    # 4. Update DB
    item.installed_at = datetime.now()
    item.status = MarketplaceItemStatus.installed
    await item.save()
```

---

### Phase 4: Frontend Integration [MEDIUM 🟡]

**Goal**: UI components for marketplace browsing and installation

**Endpoints**:
- `GET /marketplace/status` — Updates available?
- `GET /marketplace/items?kind=agent&limit=50` — List packages
- `POST /marketplace/install?item_id=agent-factory` — Install
- `POST /marketplace/reseed` — Force re-fetch from GitHub

**React Components**:
- `<MarketplaceStatus />` — Shows "Updates Available" badge
- `<InstallPackageButton item_id="agent-factory" />` — Install button
- `<MarketplacePackageList />` — Browse/search packages

---

### Phase 5: Startup Integration [HIGH 🔴]

**Goal**: Seed marketplace on first run, background update checks

**In main.py / app initialization**:
```python
async def startup_event():
    # Seed marketplace DB on first run
    try:
        result = await seed_marketplace_on_startup()
        logger.info(f"Marketplace seeded: {result}")
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
    
    # Start background update checker
    asyncio.create_task(periodic_update_check())

async def periodic_update_check():
    """Check for updates every 1 hour."""
    while True:
        try:
            async with MarketplaceSeeder() as seeder:
                await seeder.check_for_updates()
        except Exception as e:
            logger.error(f"Update check failed: {e}")
        
        await asyncio.sleep(3600)  # 1 hour
```

---

## Database Schema

**MarketplaceMeta**:
- `id` — Primary key
- `name` — "default"
- `version` — "0.1.0"
- `remote_index_hash` — SHA512 of current index.json
- `local_index_hash` — SHA512 of last synced index
- `update_available` — Boolean flag
- `last_index_check` — Timestamp

**MarketplaceItem**:
- `id` — Internal BigInt primary key
- `slug` — External item identifier (unique, e.g. kebab-case ID used by API)
- `name` — Description
- `description` — Full text
- `kind` — Type (agent, skill, mcp, etc.)
- `status` — installed/enabled/disabled
- `source_url` — GitHub raw URL
- `install_path` — Local installation path
- `installed_at` — Timestamp
- `meta` — JSONB (file, path, sha512, etc.)

---

## Implementation Checklist

- [ ] **Phase 1**: Update detection (hash tracking, status endpoint)
- [ ] **Phase 2**: Multi-type seeder (_seed_type, _get_install_path)
- [ ] **Phase 3**: Installation (download, verify, extract)
- [ ] **Phase 4**: Batch install (rate limiting)
- [ ] **Phase 5**: Endpoints (GET /status, POST /install, POST /reseed)
- [ ] **Phase 6**: Frontend components (status badge, install button)
- [ ] **Phase 7**: Startup integration (seed, background task)
- [ ] **Phase 8**: Configuration (add MARKETPLACE_CONFIG to config.py)
- [ ] **Phase 9**: Database schema (migration or alembic)
- [ ] **Phase 10**: Tests (unit + integration)

---

## Module Pattern

```python
# src/css/modules/marketplace/__init__.py
"""Remote package manager for agents, skills, workflows, prompts, templates, MCPs."""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .seeder import MarketplaceSeeder, seed_marketplace_on_startup
from .installer import PackageInstaller
from .models import MarketplaceItem, MarketplaceMeta
from .enums import MarketplaceItemType, MarketplaceItemStatus

__all__ = [
    'MarketplaceSeeder',
    'PackageInstaller',
    'MarketplaceItem',
    'MarketplaceMeta',
    'MarketplaceItemType',
    'MarketplaceItemStatus',
    'seed_marketplace_on_startup',
]
```

---

## Configuration

Add to `src/css/config.py`:

```python
MARKETPLACE_CONFIG = {
    "index_url": "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json",
    "index_hash_url": "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main/index.json.sha512",
    "base_url": "https://raw.githubusercontent.com/DCx7C5/ai-marketplace/refs/heads/main",
    "install_root": "~/.css/packages",
    "update_check_interval": 3600,     # 1 hour
    "download_timeout": 60,
    "max_package_size": 100 * 1024 * 1024,  # 100MB
}
```

---

## Dependencies

- `aiohttp` — Async HTTP (already used for seeder)
- `aioredis` / `asyncpg` — Cache backends (via @cache module)
- `tortoise-orm` — ORM (already used)
- `zipfile`, `tarfile` — Archive extraction (stdlib)

---

## Integration Points

- **@cache**: Store marketplace metadata
- **@events**: Emit install/update events for monitoring
- **@orchestration**: Reload agents/skills after install
- **Frontend**: Status badge + package browser

---

## Success Criteria

✅ Marketplace seeds with 50+ agents on first run
✅ Frontend shows "Updates Available" badge when index changes
✅ Users can install any of 6 package types
✅ Packages verify checksums and extract correctly
✅ Background task checks for updates every hour
✅ All endpoints return proper error responses
✅ Database schema supports multi-type packages

---

**Status**: 🟡 Partial | **Priority**: 🔴 High | **Last Updated**: 2026-05-04
## Audit (2026-05-03)

**Status**: Audited by Agent 3 | **Timestamp**: 2026-05-03T19:55
**Details**: See .plan/modules/module-audit-matrix.md for full audit results.

## Audit (2026-05-04)

**Status**: TODO phase4-models-create completed | **Timestamp**: 2026-05-04T09:45
**Changes**:
- Updated MarketplaceMeta ORM: added 4 fields (remote_index_hash, local_index_hash, update_available, last_index_check)
- Created MarketplaceMetaBase + MarketplaceMetaResponse Pydantic models
- Updated __all__ exports to include new models

## Audit (2026-05-04)

**Status**: TODO `db-fix-marketplace-item-pk` completed | **Timestamp**: 2026-05-04T21:10
**Changes**:
- `MarketplaceItem.id` migrated from `CharField` PK to `BigIntField(primary_key=True)`
- Added `MarketplaceItem.slug` as unique external identifier
- Updated marketplace and tag lookup paths to resolve items by `slug` instead of `id`

---

## 🔄 Sync Reminder

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
