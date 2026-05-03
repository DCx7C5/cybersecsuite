# MCP Server Configuration (`mcp.json`)

Configures MCP servers available to Claude Code.

---

## Active Servers

`mcp.json` in the project root declares the MCP servers:

```json
{
  "mcpServers": {
    "cybersec": {
      "command": "uv",
      "args": ["run", "python", "-m", "csmcp.cybersec.server"],
      "env": { "PYTHONPATH": "src" }
    },
      "command": "uv",
      "env": { "PYTHONPATH": "src" }
    }
  }
}
```

| Server      | Tools | Runtime          | Module                          |
|-------------|-------|------------------|---------------------------------|
| cybersec    | 88    | Python (uv)      | `csmcp.cybersec.server`         |

---

## `playwright-stealth` (Optional, developer-local)

An additional MCP server for browser automation is available but requires a local installation path:

```json
"playwright-stealth": {
  "command": "/path/to/playwright-stealth-mcp/server",
  "env": {}
}
```

This path is developer-specific and not committed to `mcp.json` by default.

---

## `.claude/settings.json`

Project-level Claude Code config (does **not** affect the running application):

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "agent": "cybersec-agents",
  "mcp": {
    "tool_prefix": "mcp__"
  }
}
```

| Key                                          | Value              | Description                                                           |
|----------------------------------------------|--------------------|-----------------------------------------------------------------------|
| `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`   | `"1"`              | Enables Claude Code team mode (required for blue/red/purple teams)    |
| `agent`                                      | `"cybersec-agent"` | Default orchestrator agent loaded at session start                    |
| `mcp.tool_prefix`                            | `"mcp__"`          | Prefix for all MCP tool names                                         |

---

## Tool Name Prefixes

| Server    | Prefix              | Example                          |
|-----------|---------------------|----------------------------------|
| cybersec  | `mcp__cybersec__`   | `mcp__cybersec__add_finding`     |
