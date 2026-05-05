# Settings Merge Strategy

## Dual-Scope Architecture

CyberSecSuite maintains two separate settings scopes:

1. **Global Scope** (`~/.claude/settings.json`)
   - Managed by Anthropic's Claude desktop app
   - READ-ONLY for CyberSecSuite (for display + runtime use)
   - Contains globally configured MCPs, agents, skills, and tools
   - All users on the machine share this scope

2. **App Scope** (`~/.cybersecsuite/settings.json`)
   - Managed exclusively by CyberSecSuite
   - READ-WRITE for customization and locally installed items
   - Contains app-specific MCPs, agents, skills, overrides, preferences
   - Isolated to this application

## Merge Precedence Rule

**App scope overrides global scope.**

When resolving a setting (e.g., "is MCP X enabled?"):

```
result = global_setting
if (item_id in app_settings):
    result = app_settings[item_id]  ← app wins on conflict
```

### Rationale

- **Global scope is a platform baseline**: Ensures MCPs/agents configured for the whole system are available
- **App scope enables customization**: Users can disable, override, or replace items locally
- **Installation priority**: Items installed locally (→ app scope) take precedence over global defaults
- **User intent**: If a user explicitly configures something in the app, honor it

## Dashboard Display

The settings dashboard shows **two tabs**:

1. **Global Settings** (read-only)
   - Lists all MCPs, agents, skills from `~/.claude/settings.json`
   - Shows status but no edit/install/uninstall buttons
   - Read-only checkboxes (informational only)

2. **App Settings** (read-write)
   - Lists app-specific MCPs, agents, skills from `~/.cybersecsuite/settings.json`
   - Full controls: install, uninstall, enable, disable, upgrade, toggle
   - Overrides take precedence over global settings
   - Locally installed items appear here

## Implementation

In `src/registries/settings.py`:

```python
def resolve_setting(key: str, global_settings: dict, app_settings: dict) -> Any:
    """Resolve a setting with app scopes taking precedence."""
    if key in app_settings:
        return app_settings[key]
    return global_settings.get(key)

def is_item_enabled(item_id: str, global_scope: dict, app_scope: dict) -> bool:
    """Check if an item (MCP/skills/agents) is enabled."""
    # If explicitly configured in app scopes, use that
    if item_id in app_scope:
        return app_scope[item_id].get("enabled", False)
    # Fall back to global scopes
    if item_id in global_scope:
        return global_scope[item_id].get("enabled", True)
    return False
```

## Conflict Resolution Examples

### Example 1: MCP installed locally

- **Global**: `openai-mcp` enabled (from global `~/.claude/`)
- **App**: `openai-mcp` installed locally, marked `enabled: true`
- **Result**: App scope takes precedence → use local version

### Example 2: Skill disabled by user

- **Global**: `vault-skill` enabled
- **App**: `vault-skill` exists with `enabled: false`
- **Result**: App scope override → skill is disabled for this app

### Example 3: New item in global, no override

- **Global**: `new-agent` enabled
- **App**: `new-agent` not present
- **Result**: Fall back to global → agent is enabled

## Bootstrap Integration

When `OnFirstSetupEvent` runs:

1. Read global settings from `~/.claude/settings.json`
2. Read/initialize app settings from `~/.cybersecsuite/settings.json`
3. **Merge rule applied**: App scope items override global items
4. Seed `MarketplaceRegistry` with merged result
5. Download core marketplace items (stored in app scope)
6. Both scopes available at runtime; merge applied on all queries

---

**Version**: 1.0
**Last Updated**: 2025-04-28
