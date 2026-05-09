# core/marketplace — Catalog, Install State, and Package Control Plane

**Location**: `src/css/core/marketplace/`  
**Status**: ✅ Implemented control plane, with Phase 9 registry/service cleanup still pending

## Purpose

`core/marketplace` owns the **catalog and install lifecycle** for platform packages:
- agents
- skills
- prompts
- MCP server bundles/config entries
- future connector packages

It is **not** the runtime execution layer for MCP, tools, or SIEM integrations. It tracks what is available, installed, enabled, and described in metadata.

## Current Code Reality

| File | Reality |
|------|---------|
| `registry.py` | DB-backed `MarketplaceItemRegistry` around `MarketplaceItem` ORM rows |
| `endpoints.py` | Real FastAPI CRUD/install/toggle/list/detail routes |
| `seeder.py` | Seeds built-in marketplace items, including `MarketplaceItemType.mcp` |
| `cache.py` | Local in-memory TTL cache, not Redis-backed |
| `installer.py` / `package_manager.py` | Package install/uninstall and local package orchestration |
| `types.py` | Request/response schemas |

## Architectural Role

Marketplace sits between planning/distribution and runtime modules:

```text
Marketplace item/package metadata
        ↓ install / enable / disable
Runtime modules load configuration from DB
        ↓
mcps/ connects to MCP servers
tools/ exposes callable tool entries
siem/ consumes installed MCP connectors
```

## Boundaries

- `core/marketplace` owns package metadata, status, install state, and seed data.
- `modules/mcps` owns MCP runtime config, connections, discovery, and tool calls.
- `modules/tools` owns provider builtin tool metadata plus the shared execution registry surface.
- `modules/siem` will consume installed MCP-backed connector packages, but does not own the marketplace.

## Known Drift / Planned Cleanup

- `MarketplaceItemRegistry` currently performs DB CRUD directly. Phase 9 will split this into:
  - a pure cache/registry contract
  - a DB-writing service layer
- Registry invalidation wiring now reacts to item-level change events (`marketplace.item.changed`) and supports targeted cache eviction + `reload()` from manager-backed DB reads.
- Registry surface is now read/cache focused (`get`, `list`, `invalidate`, `reload`) with no DB write operations.
- The local cache is process memory today. Redis remains optional future infrastructure, not current behavior.

## Practical Rule

If a feature asks **“what packages/connectors are available or installed?”**, it belongs here.  
If it asks **“connect to this MCP server and call its tool”**, it belongs in `modules/mcps`.
