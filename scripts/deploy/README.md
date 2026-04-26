# Deployment Tools

Automation scripts for deploying and bootstrapping MCPs.

## Scripts

### `install-mcp-core.sh`
Bootstrap and install all MCPs from the ai-marketplace.

**Usage:**
```bash
bash scripts/deploy/install-mcp-core.sh [options]
```

**Options:**
- `--verify` — Verify existing MCP installations
- `--rebuild` — Rebuild all MCPs from source
- `--marketplace-path <path>` — Custom marketplace location (default: ai-marketplace/)
- `--dry-run` — Show what would be done without making changes

**Output:**
- Creates `config/mcps.json` MCP registry
- Installs/verifies 6 MCPs (csscore, canvas, memory, template, playwright, crypto)
- Returns 0 on success, 1 on failure
- Execution time: < 4 seconds

**Example:**
```bash
bash scripts/deploy/install-mcp-core.sh --verify
# ✓ csscore-mcp verified
# ✓ canvas-mcp verified
# ✓ memory-mcp verified
# ✓ template-mcp verified
# ✓ playwright-mcp verified
# ✓ crypto-mcp verified
```

**Prerequisites:**
- Bash 4.0+
- jq (JSON query tool)
- Python 3.9+
- ai-marketplace cloned to `../ai-marketplace/`

## When to Use

- Fresh CyberSecSuite installation
- MCP infrastructure troubleshooting
- Production deployment
- CI/CD pipeline integration

## Exit Codes

- `0` — Success
- `1` — MCP verification failed
- `2` — Configuration error
- `3` — Marketplace not found

## CI/CD Integration

Used in GitHub Actions workflows:
- `.github/workflows/qa-main.yml` (Tier 2)
- `.github/workflows/qa-release.yml` (Tier 3)

## See Also

- `scripts/test/` — Testing tools
- `scripts/data/` — Data processing
- `scripts/dev/` — Developer tools
