# core/marketplace — Central Registry

**Location**: `src/css/core/marketplace/`
**Status**: ✅ Moved from `modules/marketplace/`

## Purpose

Central skill/agent/tool/MCP registry. Lives in `core/` because all business modules
(skills, agents, teams, mcp) push into it — the reverse would create inverted dependencies.

## Files

| File | Contents |
|------|---------|
| `models.py` | `MarketplaceItem`, `MarketplaceItemTag` ORM models |
| `enums.py` | `MarketplaceItemType`, `MarketplaceItemStatus` |
| `types.py` | Request/response Pydantic schemas |
| `registry.py` | `MarketplaceRegistry` — in-memory item store |
| `cache.py` | `marketplace_cache` — Redis-backed cache |
| `installer.py` | `PackageInstaller` — package install/uninstall logic |
| `seeder.py` | Dev-mode seed data |
| `endpoints.py` | FastAPI router (`/marketplace/...`) |
| `exceptions.py` | Domain exceptions |

## Bridge

`SkillMarketplaceBridge` lives in `modules/skills/marketplace_bridge.py`
(not here — it imports from `modules/skills`, so it belongs in the module layer).
