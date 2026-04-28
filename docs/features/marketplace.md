# Marketplace

The CyberSecSuite Marketplace is a **provider-agnostic catalog** of installable agents, skills, combos, and templates. Each item targets a specific AI provider but is managed through a single unified interface — CLI, REST API, or the dashboard UI.

Installed agents automatically appear in the `agent_registry` MCP tool alongside filesystem-loaded `.claude/agents/*.md` definitions.

---

## Provider Frontmatter Standards

Each provider uses a different format for agent/skill definitions. The Marketplace normalises these into a common `MarketplaceItem` schema and records provider-specific metadata in the `meta` (`ProviderMeta`) field.

| Provider | Format | Key Frontmatter Fields |
|---|---|---|
| `claude` | `SKILL.md` (Claude Code) | `model`, `tools`, `max_turns`, `domain`, `tags`, `mitre_attack`, `nist_csf` |
| `copilot` | GitHub Copilot agent instructions | `tools`, `tags`, `domain` |
| `cursor` | `.mdc` rule files | `tags` (glob patterns) |
| `openai` | `AGENTS.md` | `model`, `tools`, `max_turns`, `tags` |
| `gemini` | Gemini CLI `AGENTS.md` | `model`, `tools`, `tags`, `capec` |
| `grok` | xAI system-prompt block | `tags`, `mitre_attack` |
| `universal` | `AGENTS.md` + `SKILL.md` dual-format | all fields |

All `ProviderMeta` fields are **optional**; unused fields default to `None` / `[]`.

---

## Item Kinds

| Kind | Description |
|---|---|
| `agent` | Autonomous reasoning agent with tools and instructions |
| `skill` | Single-capability sub-agent or tool wrapper |
| `combo` | Bundled preset combining multiple agents/skills |
| `template` | Rule or template file (e.g. Cursor `.mdc`, YARA skeleton) |

---

## Lifecycle Statuses

| Status | Meaning |
|---|---|
| `available` | In catalog, not installed |
| `installed` | Installed and active in the registry |
| `update_available` | Newer version exists in the catalog |
| `deprecated` | No longer maintained; installation discouraged |

---

## CLI Usage

The `cybersec-proxy marketplace` command provides full catalog management.

```bash
# List all catalog items
cybersec-asgi marketplace list

# Filter by kind and/or provider
cybersec-asgi marketplace list --kind agent
cybersec-asgi marketplace list --provider claude
cybersec-asgi marketplace list --kind skill --provider universal

# Search (substring, case-insensitive across name, description, tags)
cybersec-asgi marketplace search "forensics"
cybersec-asgi marketplace search "osint"

# Show full details for an item
cybersec-asgi marketplace info claude-forensic-analyst

# Install an item
cybersec-asgi marketplace install claude-forensic-analyst

# Uninstall an item
cybersec-asgi marketplace uninstall claude-forensic-analyst
```

---

## REST API Endpoints

All endpoints are mounted under `/api/marketplace` on the dashboard server.

### `GET /api/marketplace`

List catalog items with optional query parameters.

| Param | Type | Description |
|---|---|---|
| `kind` | string | Filter: `agent`, `skill`, `combo`, `template` |
| `provider` | string | Filter: `claude`, `copilot`, `cursor`, `openai`, `gemini`, `grok`, `universal` |
| `tags` | string | Comma-separated list; items must have **all** listed tags |
| `status` | string | Filter: `available`, `installed`, `update_available`, `deprecated` |
| `q` | string | Free-text search (substring, case-insensitive) |

**Response** `200 OK`:
```json
{
  "items": [ { "id": "...", "name": "...", "kind": "agent", ... } ],
  "count": 8
}
```

### `GET /api/marketplace/installed`

List all currently installed items.

**Response** `200 OK`:
```json
{
  "items": [ { "id": "claude-forensic-analyst", "status": "installed", ... } ],
  "count": 1
}
```

### `GET /api/marketplace/{item_id}`

Retrieve a single item by its kebab-case ID.

**Response** `200 OK` | `404 Not Found`

### `POST /api/marketplace/{item_id}/install`

Install an item. Sets `status = installed` and stamps `installed_at`.

**Response** `200 OK`:
```json
{ "ok": true, "item": { "id": "...", "status": "installed", "installed_at": "..." } }
```

### `DELETE /api/marketplace/{item_id}/install`

Uninstall an item. Reverts `status` to `available`.

**Response** `200 OK`:
```json
{ "ok": true, "item_id": "claude-forensic-analyst" }
```

### `POST /api/marketplace/generate-agent` *(stub)*

Agent Factory generation endpoint. Returns `501 Not Implemented` until the `agent-factory` skill is installed.

```json
{
  "status": "not_implemented",
  "message": "Agent Factory generation requires the agent-factory skill"
}
```

---

## Dashboard UI

Two new tabs appear in the **AGENTS** section of the dashboard sidebar:

| Tab | ID | Description |
|---|---|---|
| Marketplace | `marketplace` | Card grid of catalog items with filter bar, install/uninstall buttons |
| Agent Factory ⊕ | `marketplace-factory` | Umbrella-keyword driven agent frontmatter generator |

### Marketplace tab

- Filter bar: search box + kind / provider / status dropdowns
- Card grid: one card per item showing name, provider, kind, status badge, description, tags
- Install / Uninstall buttons trigger REST calls and refresh the grid

### Agent Factory ⊕ tab

- **Umbrella keyword** input — the core concept driving agent specialisation
- **Team mode** selector — Blue (defensive), Red (offensive), Purple (collaborative)
- **Generate Agent** button — POSTs to `/api/marketplace/generate-agent`
- `<pre>` output area — displays generated frontmatter or stub response

---

## Agent Registry Integration

When `agent_registry` (MCP tool) is called, it lists:

1. All agents loaded from `.claude/agents/*.md` on the filesystem
2. All **installed** marketplace items with `kind = "agent"`

Marketplace agents appear with `"source": "marketplace"` in the registry entry:

```json
{
  "name": "claude-forensic-analyst",
  "description": "Deep-dive file system + memory forensics specialist.",
  "source": "marketplace",
  "provider": "claude",
  "tags": ["forensics", "filesystem", "memory"]
}
```

---

## Storage Layout

Marketplace state is stored in `~/.cybersecsuite/marketplace/`:

```
~/.cybersecsuite/marketplace/
├── catalog.json      # Optional custom catalog (overrides seed data when present)
└── installed.json    # Currently installed items (auto-written on install/uninstall)
```

Both files are JSON arrays of serialised `MarketplaceItem` objects.  
The `catalog.json` file is **optional** — if absent, the built-in seed data is used.  
The `installed.json` file is created automatically on first install.

---

## Seed Catalog

The built-in seed catalog (loaded at module import from `src/marketplace/seed.py`) contains:

| ID | Name | Kind | Provider |
|---|---|---|---|
| `claude-forensic-analyst` | Forensic Analyst | agent | claude |
| `copilot-threat-hunter` | Threat Hunter | agent | copilot |
| `cursor-security-rules` | Security Glob Rules | template | cursor |
| `openai-pentest-agent` | PenTest Agent | agent | openai |
| `gemini-network-analyst` | Network Analyst | agent | gemini |
| `grok-osint-researcher` | OSINT Researcher | agent | grok |
| `universal-ioc-scanner` | IOC Scanner | skill | universal |
| `claude-qol-silent` | Silent Mode Preset | combo | claude |
