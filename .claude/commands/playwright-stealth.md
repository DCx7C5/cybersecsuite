# Playwright Stealth Browser

Interact with the playwright-stealth MCP server for headless browser automation with anti-detection.

## Server
- **Location**: `/home/daen/Projects/AI/mcps/playwright-stealth-mcp/`
- **MCP key**: `playwright-stealth`
- **Transport**: stdio (auto-started by MCP config)

## Available Tools

| Tool              | Usage                                                             |
|-------------------|-------------------------------------------------------------------|
| `navigate`        | Navigate to a URL: `navigate(url="https://...")`                  |
| `click`           | Click an element: `click(selector="button#id")`                   |
| `type_text`       | Type with human delays: `type_text(selector="input", text="...")` |
| `take_screenshot` | Full-page screenshot (base64, high token cost)                    |
| `get_full_html`   | Extract full page HTML (high token cost)                          |

## Usage

If an argument is provided after `/playwright-stealth`, treat it as a URL and navigate to it using the `mcp__playwright-stealth__navigate` tool.

Example: `/playwright-stealth google.com` → navigate to `https://google.com`

If no argument is provided, show the status of the playwright-stealth MCP server and list available tools.

## Stealth Features
- Canvas fingerprint noise
- Navigator spoofing (hardwareConcurrency=8, deviceMemory=8)
- Human-like click/type delays (50–150ms)
- Persistent Brave profile
- Timezone: Europe/Berlin, Locale: en-US

## Quick Start (manual)
```bash
cd ~/Projects/AI/mcps/playwright-stealth-mcp
uv sync
uv run playwright install chromium
uv run python main.py
```
