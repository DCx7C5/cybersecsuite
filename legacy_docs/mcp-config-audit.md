# MCP Config Audit

**Scope:** `mcp.json`, `scripts/deploy/install-mcp-core.sh`, `~/.claude/settings.json`  
**Date:** 2025-07-25  
**Auditor:** Copilot  

---

## MCP Coverage Table

| MCP Name | In `mcp.json` | In `install-mcp-core.sh` | Gap? |
|---|---|---|---|
| `cybersec` / `csscore-mcp` | ✅ (`cybersec`) | ✅ (`csscore-mcp`) | Name mismatch only — same server |
| `canvas-mcp` | ✅ (added by this audit) | ✅ | Was missing; now fixed |
| `memory-mcp` | ✅ (added by this audit) | ✅ | Was missing; now fixed |
| `template-mcp` | ✅ (added by this audit) | ✅ | Was missing; now fixed |
| `dystopian-crypto-mcp` | ✅ (added by this audit) | ✅ | Was missing; now fixed |
| `custom-mcp` | ✅ (added by this audit) | ✅ | Was missing; now fixed |
| `playwright-stealth` | ✅ | — | Present in mcp.json, not in install script |
| `playwright-mcp` | — | ✅ | In install script; `playwright-stealth` is the preferred variant for this project |
| `kerneldev` | ✅ | — | Not in install script (separate deployment) |
| `token-optimization` | ✅ | — | Not in install script (built-in module) |

---

## Settings Patch Flow

### How `~/.claude/settings.json` gets populated

The settings patch happens in the `css-first-setup` Makefile target, step `[2/5]`:

```makefile
@echo "==> [2/5] Patching ~/.claude/settings.json..."
@python3 -c "\
import json, pathlib; \
p = pathlib.Path.home() / '.claude' / 'settings.json'; \
d = json.loads(p.read_text()) if p.exists() else {}; \
env = d.setdefault('env', {}); \
env.setdefault('CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', '1'); \
p.parent.mkdir(parents=True, exist_ok=True); \
p.write_text(json.dumps(d, indent=2) + '\n'); \
print('  OK: CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS set')"
```

**What this does:**
- Reads `~/.claude/settings.json` (creates it if missing)
- Sets `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS = "1"`
- Writes back to disk

**What this does NOT do:**
- Does **not** copy any MCP server entries from `mcp.json` into `settings.json`
- Does **not** merge `mcpServers` from the project's `mcp.json`

### Current state of `~/.claude/settings.json`

```json
{
  "mcpServers": {}
}
```

The `mcpServers` object is **empty**. Claude Code picks up MCP servers from project-level `mcp.json` (or `.mcp.json`) automatically when it loads a workspace — the empty `mcpServers` in `~/.claude/settings.json` is therefore **not a blocking gap**. Claude Code resolves MCPs in this priority order:

1. Project-level `mcp.json` (workspace root) — ← where CyberSecSuite MCPs live  
2. User-level `~/.claude/settings.json` `mcpServers` — global overrides  

MCPs in `mcp.json` at the workspace root are auto-available whenever Claude Code opens this project. No manual settings merge is required.

### `install-mcp-core.sh` flow

The install script (`scripts/deploy/install-mcp-core.sh`):
1. Validates Python 3.11+ and `uv` are present
2. Iterates the 7 MCPs in `MCPS` / `MCP_PATHS` arrays
3. For each MCP: installs from local source path (`uv pip install -e .`) or falls back to PyPI
4. Verifies each MCP via `python3 -c "import <module>"`
5. Writes a summary report

The script installs the Python packages but does **not** register MCPs in `mcp.json` — that's a manual/static configuration step.

---

## Gaps (Pre-fix State)

Before this audit, the following MCPs were installed by `install-mcp-core.sh` but had **no entry in `mcp.json`**:

| MCP | Module | Source Path |
|---|---|---|
| `canvas-mcp` | `canvas_mcp` | `/home/daen/Projects/ai-marketplace/mcps/canvas-mcp` |
| `memory-mcp` | `memory_mcp` | `/home/daen/Projects/ai-marketplace/mcps/memory-mcp` |
| `template-mcp` | `template_mcp` | `/home/daen/Projects/ai-marketplace/mcps/template-mcp` |
| `dystopian-crypto-mcp` | `dystopian_crypto_mcp` | `/home/daen/Projects/ai-marketplace/mcps/dystopian-crypto-mcp` |
| `custom-mcp` | `custom_mcp` | `src/csmcp/mcps/custom-mcp` |

**`playwright-mcp` gap:** The install script installs `playwright-mcp` (base version, 10 tools). `mcp.json` registers `playwright-stealth` (enhanced stealth variant from `playwright-stealth-mcp`). These are different packages. The stealth variant is preferred for this security-focused project and covers the playwright-mcp use case.

---

## Recommendations

### R1 — Align `install-mcp-core.sh` MCP name with `mcp.json` key for csscore (Low)

The install script refers to the main SDK as `csscore-mcp` while `mcp.json` uses the key `cybersec`. These are the same server. Either rename the install script's reference to `cybersec-mcp` or add a comment linking them.

### R2 — Replace `playwright-mcp` in install script with `playwright-stealth` (Medium)

The install script installs `playwright-mcp` from the marketplace, but `mcp.json` uses `playwright-stealth` from a different source (`/home/daen/Projects/AI/mcps/playwright-stealth-mcp`). The install script should install `playwright-stealth-mcp` instead to be consistent with the registered MCP.

### R3 — Add `mcp.json` sync step to `css-first-setup` (Low)

The `css-first-setup` step [2/5] only patches `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`. It does not validate or merge MCPs. Since Claude Code auto-discovers `mcp.json`, this is not blocking, but a validation step (check that all MCP `command` paths are resolvable) would catch deployment issues early.

### R4 — Makefile step numbering is inconsistent (Cosmetic)

`css-first-setup` labels steps `[1/5]`, `[2/5]`, `[3/5]`, `[4/5]` then switches to `[5/7]`, `[6/7]`, `[7/7]`. Update to consistent `[N/7]` numbering.

### R5 — `custom-mcp` is a stub (Medium)

`src/csmcp/mcps/custom-mcp/` contains only `__init__.py` and `pyproject.toml`. There is no `src/custom_mcp/__main__.py` or server implementation. The `mcp.json` entry added by this audit will fail until the module is implemented. Mark as placeholder until implemented.
