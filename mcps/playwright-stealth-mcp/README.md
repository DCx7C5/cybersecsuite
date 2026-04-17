# playwright-stealth-mcp  v0.1.0

Production-ready **Model Context Protocol** server for headless Brave browser automation with anti-bot detection, fingerprint spoofing, and human-like interaction patterns.

## Features

- **Stealth Mode**: playwright-stealth plugin + canvas/navigator fingerprint randomization
- **Human Interaction**: click/type with realistic delays (50–150ms per char)
- **Anti-Detection**: Disable blink automation flags, proxy WebGL/canvas operations
- **Browser Tools**: Screenshot, full HTML extraction (high-cost tools)
- **Persistent Profile**: User data directory + timezone + locale spoofing
- **Cross-Platform**: Auto-detect Brave path (Windows/macOS/Linux)

## Tools

| Tool | Description | Token Cost |
|------|-------------|------------|
| `click` | Click element with human-like delay | Low |
| `type_text` | Type text with realistic character delays | Low |
| `navigate` | Go to URL with stealth headers | Low |
| `take_screenshot` | Full-page screenshot (base64) | High |
| `get_full_html` | Extract full page HTML | High |

## Quick Start

```bash
cd playwright-stealth-mcp
uv sync

# Start MCP server
uv run main.py

# Connect via stdio (Claude Code / Copilot)
# or SSE: http://127.0.0.1:8000/sse
```

## Environment Variables

```bash
export BRAVE_PATH=/usr/bin/brave-browser        # Custom Brave path
export USER_DATA_DIR=./brave_profile             # Persistent profile dir
```

## Configuration

### Browser Args
```python
# config.py
USER_DATA_DIR = "../brave_stealth_profile"       # Persistent user data

def get_brave_path() -> str:
    # Auto-detect Brave binary (or use BRAVE_PATH env var)
```

### Stealth Features
- Canvas fingerprint: random pixel noise (prevents detection)
- Navigator spoofing: hardwareConcurrency=8, deviceMemory=8, plugins=[]
- WebGL: intercepted and randomized
- User agent: Chrome/Windows mimicry
- Timezone: Europe/Berlin
- Locale: en-US

## Example Usage

```python
# Click button with human-like delay
await click("button#submit")

# Type password with realistic character timing
await type_text("input#password", "super_secret_pass")

# Navigate with stealth headers
await navigate("https://example.com")

# Take screenshot for analysis
screenshot = await take_screenshot()

# Extract full page for parsing
html = await get_full_html()
```

## Architecture

```
playwright-stealth-mcp/
├── main.py              ← FastMCP entry point
├── config.py            ← Brave path detection + config
├── navigation.py        ← Browser lifecycle + stealth init
├── interaction.py       ← Human-like click/type tools
├── lifespan.py          ← Async context manager for browser
├── heavy.py             ← High-cost tools (screenshot, HTML)
├── utils.py             ← Helper functions
├── pyproject.toml       ← Dependencies
└── README.md            ← This file
```

## Security & Ethics

- **Anti-detection is for legitimate research only**
- Respect websites' ToS and robots.txt
- Use only on systems you own/control
- Fingerprint spoofing helps avoid false bot detection

## Dependencies

- `fastapi` — Web framework for MCP
- `mcp-server` — Model Context Protocol server
- `playwright-stealth` — Automation detection bypass
- `uvicorn` — ASGI server

## Testing

```bash
uv run pytest   # Run test suite (when available)
```

## License

MIT
