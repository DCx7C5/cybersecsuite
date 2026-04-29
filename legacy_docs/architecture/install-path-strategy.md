# Installation Path Unification

## Current State (Before Phase 0.5)

Marketplace items are scattered across multiple paths:

```
~/.cybersecsuite/
├── agents/           # AgentRegistry stores RemoteAgent metadata
├── marketplace/      # MarketplaceRegistry stores Skill metadata
│   └── index.json    # Downloaded index snapshot
└── skills/           # Individual skill directories
```

**Problem**: No single source of truth; path logic scattered across codebase.

## Unified Path Strategy (Phase 0.5+)

**Single location for all marketplace items**:

```
~/.cybersecsuite/marketplace/
├── index.json                    # Downloaded index snapshot
├── index.json.sha512             # SHA512 of index
├── .bootstrap_status.json        # Bootstrap state tracking
├── mcps/
│   ├── ai-marketplace/
│   │   └── manifest.json
│   ├── vault-mcp/
│   │   └── manifest.json
│   └── canvas-mcp/
│       └── manifest.json
├── agents/
│   ├── analyst/
│   │   └── agent.json
│   └── orchestrator/
│       └── agent.json
└── skills/
    ├── vault-skill/
    │   └── skill.json
    └── research-skill/
        └── skill.json
```

**Benefits**:
- All marketplace items in one place
- Single `MarketplaceRegistry` manages all types
- Easy to backup/restore `~/.cybersecsuite/marketplace/`
- Clear separation from global `~/.claude/`

## Migration Path

### Phase 1: (Current)
- Keep existing paths during transition
- New bootstrap writes to `marketplace/`
- Both paths readable for backward compat

### Phase 2: (Future)
- Migrate existing items from `agents/`, `skills/` → `marketplace/{type}/`
- Update all loaders to read from unified path
- Shim old paths for compatibility

### Phase 3: (Future)
- Remove old path shims
- Keep only `marketplace/` as canonical

## Implementation

In `src/registries/marketplace.py`:

```python
MARKETPLACE_ROOT = Path.home() / ".cybersecsuite" / "marketplace"
MCP_PATH = MARKETPLACE_ROOT / "mcps"
AGENT_PATH = MARKETPLACE_ROOT / "agents"
SKILL_PATH = MARKETPLACE_ROOT / "skills"

def get_install_path(item_id: str, item_type: str) -> Path:
    """Return unified install path for an item."""
    if item_type == "mcp":
        return MCP_PATH / item_id
    elif item_type == "agent":
        return AGENT_PATH / item_id
    elif item_type == "skill":
        return SKILL_PATH / item_id
    else:
        raise ValueError(f"Unknown item type: {item_type}")

def list_all_items() -> dict[str, list[dict]]:
    """List all installed items by type."""
    return {
        "mcps": list_items(MCP_PATH),
        "agents": list_items(AGENT_PATH),
        "skills": list_items(SKILL_PATH),
    }
```

## Dashboard Impact

**Marketplace view** shows unified list:

```
INSTALLED ITEMS
MCPs:
  • ai-marketplace (v1.0.0)
  • vault-mcp (v2.1.0)
Agents:
  • analyst (remote)
Skills:
  • vault-skill (v1.2.0)
```

All install/uninstall/update operations use unified path logic.

---

**Version**: 1.0
**Last Updated**: 2025-04-28
