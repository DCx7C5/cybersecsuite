# Core Marketplace

**Status:** Active  
**Location:** `src/css/core/marketplace/`

## Architecture rules

1. Common enums come from `src/css/core/enums.py`.
2. ORM models live under `src/css/core/db/models/<subdir>.py`.
3. For marketplace, ORM source of truth is `src/css/core/db/models/marketplace.py`.

## Runtime components

- `endpoints.py` — marketplace HTTP API (`/marketplace/*`)
- `installer.py` — install/uninstall logic (download, checksum, extract, DB state update)
- `seeder.py` — remote index seeding and update checks
- `registry.py` — DB-backed item registry helpers
- `cache.py` — in-memory TTL cache for marketplace query results
- `types.py` — API request/response schemas
- `exceptions.py` — marketplace exception types

## Data model

Defined in `src/css/core/db/models/marketplace.py`:

- `MarketplaceMeta`
- `MarketplaceItem`
- `MarketplaceItemTag`

Key fields include:

- `MarketplaceMeta.remote_index_hash`
- `MarketplaceMeta.local_index_hash`
- `MarketplaceMeta.update_available`
- `MarketplaceItem.source_url`
- `MarketplaceItem.install_path`
- `MarketplaceItem.installed_at`
- `MarketplaceItem.meta` (JSON)

## API surface

Mounted from `src/css/core/marketplace/endpoints.py`:

- `GET /marketplace/status`
- `GET /marketplace/items`
- `GET /marketplace/items/{item_id}`
- `GET /marketplace/items/by-tags`
- `POST /marketplace/install` and `POST /marketplace/items/install`
- `POST /marketplace/uninstall` and `POST /marketplace/items/uninstall`
- `POST /marketplace/toggle` and `POST /marketplace/items/toggle`
- `POST /marketplace/upgrade` and `POST /marketplace/items/upgrade`
- `POST /marketplace/update-check`
- `POST /marketplace/reseed`

## Startup behavior

ASGI startup (`src/css/core/asgi/app.py`) performs:

1. seed on startup (`seed_marketplace_on_startup`)
2. periodic update checks based on `MARKETPLACE_CONFIG["update_check_interval"]`

## Frontend integration

Frontend panel path is `@css/core/marketplace/templates`.
