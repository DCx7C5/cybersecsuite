# token-optimization-mcp  v0.2.0

Production-ready **Model Context Protocol** server for token counting, prompt compression,
model routing and semantic caching. Zero external API calls — works fully offline.

## Tools

| Tool                   | Description                                                           |
|------------------------|-----------------------------------------------------------------------|
| `estimate_tokens`      | Count tokens for any text+model (calibrated chars/token ratios)       |
| `compress_prompt`      | Shrink prompts with `trim`, `summarize_hint` or `aggressive` strategy |
| `route_model`          | Pick cheapest model meeting quality + context requirements            |
| `cache_lookup`         | Semantic cache hit/miss by prompt or pre-computed key                 |
| `cache_store`          | Store prompt+result with token-savings metadata                       |
| `cache_invalidate`     | Remove one or all cache entries                                       |
| `analyze_context`      | Conversation health: role breakdown, issues, recommendations          |
| `savings_report`       | Session-level token/USD savings dashboard                             |
| `deduplicate_messages` | Remove duplicate turns, count saved tokens                            |

## Quick Start

```bash
cd mcps/token-optimization-mcp
uv sync

# stdio – Claude Code / Copilot
uv run main.py

# SSE – LangGraph / CrewAI / browser
uv run main.py --sse --port 8001
```

## Environment Variables

| Variable               | Default                    | Description               |
|------------------------|----------------------------|---------------------------|
| `USE_REDIS`            | `false`                    | Enable Redis backend      |
| `REDIS_URL`            | `redis://localhost:6379/1` | Redis connection URL      |
| `CACHE_TTL_SECONDS`    | `86400`                    | Default cache TTL (1 day) |
| `RATE_LIMIT_PER_MIN`   | `120`                      | Requests/min per client   |
| `AUDIT_LOG_ENABLED`    | `true`                     | Print audit log to stdout |

## Registration

### Claude Code (`~/.claude/settings.json`)
```json
{
  "mcpServers": {
    "token-optimization": {
      "command": "uv",
      "args": ["run", "/path/to/token-optimization-mcp/main.py"]
    }
  }
}
```

### VS Code Copilot (`.vscode/mcp.json`)
```json
{
  "servers": {
    "token-optimization": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "${workspaceFolder}/mcps/token-optimization-mcp/main.py"]
    }
  }
}
```

### SSE (LangGraph / CrewAI / Cursor)
```
http://127.0.0.1:8001/sse
```

## Supported Models (routing catalogue)

| Model               | Context | Quality | Cost/1k   |
|---------------------|---------|---------|-----------|
| `github:copilot`    | 128k    | 8       | **free**  |
| `gpt-4o-mini`       | 128k    | 7       | $0.00015  |
| `claude-3-5-haiku`  | 200k    | 7       | $0.00025  |
| `gemini-1.5-flash`  | 1M      | 6       | $0.000075 |
| `gpt-4o`            | 128k    | 9       | $0.005    |
| `claude-3-5-sonnet` | 200k    | 9       | $0.003    |
| `claude-3-opus`     | 200k    | 10      | $0.015    |

## Testing

```bash
uv run --group test pytest
# 118 tests, 100% coverage
```

## Architecture

```
token-optimization-mcp/
├── main.py                      ← FastMCP server (9 tools)
├── pyproject.toml
├── README.md
├── tests/
│   ├── conftest.py              ← state-reset fixtures
│   ├── test_helpers.py          ← unit tests + Hypothesis
│   └── test_tools.py            ← integration tests per tool
└── mcp-servers/
    └── context-cache-server/    ← standalone Redis-backed sub-server
        ├── server.py
        ├── config.py
        └── security.py
```
