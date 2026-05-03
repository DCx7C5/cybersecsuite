# Core Items Schema

## Marketplace Index Tier System

The marketplace index (`index.json` from GitHub) categorizes items into tiers to guide bootstrap behavior and user decision-making.

### Tier Definitions

**`tier` field in index.json item**:

```json
{
  "id": "ai-marketplace",
  "tier": "core",
  "name": "AI Marketplace",
  "version": "1.0.0",
  "source": "https://github.com/DCx7C5/ai-marketplace",
  "type": "mcp"
}
```

#### `"core"` (mandatory)
- Downloaded and installed during `OnFirstSetupEvent`
- Bootstrap blocks until successful installation
- Examples: `ai-marketplace`, critical system MCPs
- User cannot disable; can only remove manually

#### `"recommended"` (highly useful, optional)
- Offered during bootstrap with user consent
- Dashboard shows installation option
- Examples: `canvas-mcp`, `vault-mcp`, common provider integrations
- User can skip or install later from dashboard

#### `"optional"` (community, experimental)
- Available in marketplace but not auto-installed
- Visible in dashboard; user-initiated installation only
- Examples: community tools, experimental MCPs, third-party integrations
- User has full control

### JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "index": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "type", "tier"],
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "version": {"type": "string"},
          "tier": {"enum": ["core", "recommended", "optional"]},
          "type": {"enum": ["mcp", "agents", "skills"]},
          "source": {"type": "string", "format": "uri"},
          "description": {"type": "string"},
          "tags": {"type": "array", "items": {"type": "string"}}
        }
      }
    }
  }
}
```

### Bootstrap Behavior by Tier

**`OnFirstSetupEvent`**:

1. Read global + app settings
2. Download `index.json` from GitHub
3. Filter by tier:
   - **`core`**: Mandatory → must install all
   - **`recommended`**: Optional → offer to user, or auto-install with consent
   - **`optional`**: Ignore during bootstrap
4. Install core items (block on success/failure)
5. Optionally: prompt user for recommended items
6. Mark bootstrap complete

**Dashboard**:

- **Install tab** shows core items (already installed, no action)
- **Available tab** shows recommended + optional (user can install)
- Filter/sort by tier

### Implementation

In `src/registries/marketplace.py`:

```python
def get_core_items(index: dict) -> list[dict]:
    """Return items with tier='core'."""
    return [item for item in index.get("index", []) if item.get("tier") == "core"]

def get_recommended_items(index: dict) -> list[dict]:
    """Return items with tier='recommended'."""
    return [item for item in index.get("index", []) if item.get("tier") == "recommended"]

def get_optional_items(index: dict) -> list[dict]:
    """Return items with tier='optional'."""
    return [item for item in index.get("index", []) if item.get("tier") == "optional"]
```

---

**Version**: 1.0
**Last Updated**: 2025-04-28
