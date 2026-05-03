# Agent SDK Integration

How `.claude/agents/` definitions flow through the SDK to AI providers.

---

## Architecture

```
.claude/agents/*.md
        │
        ▼
  agent_loader.py            (parse YAML frontmatter: name, model, tools, role)
        │
        ▼
  agent_sdk.py               (cache AgentDefinitions, build ClaudeAgentOptions)
        │
        ▼
  claude-agent-sdk query()   (sends to ANTHROPIC_BASE_URL)
        │
        ▼
  AI Proxy /v1/*             (http://localhost:8000/v1)
        │                     → 13 routing strategies
        │                     → circuit breaker per provider
        │                     → budget guard
        ▼
  60 AI Providers            (Anthropic, DeepSeek, Gemini, Groq, OpenRouter, …)
```

---

## Per-Agent Model Routing

Each `.claude/agents/*.md` frontmatter declares `model:`:

```yaml
---
name: python-developer
model: deepseek-v3
tools: [Read, Write, Edit, Bash, Glob, Grep]
---
```

When `run_agent_query("python-developer", prompt)` is called:

1. Returns cached `AgentDefinition` with `model="deepseek-v3"`
2. `_copy_options_with()` creates shallow copy with `model="deepseek-v3"`
3. SDK sends the request with that model to the proxy
4. Proxy routes to DeepSeek

**No code changes needed** — update `model:` in the `.md` file.

### Model Shorthand Mapping

| Shorthand | Resolved to                 |
|-----------|-----------------------------|
| `haiku`   | `claude-haiku-4-5`          |
| `sonnet`  | `claude-sonnet-4-5`         |
| `opus`    | `claude-opus-4-5`           |
| (full ID) | passed through as-is        |

Full IDs like `deepseek-v3`, `gemini-2.0-flash` are forwarded directly.

---

## Key Functions

| Function                         | Purpose                                                           |
|----------------------------------|-------------------------------------------------------------------|
| `build_agent_options()`          | Build/return cached `ClaudeAgentOptions` with all tools + agents  |
| `build_agent_definitions()`      | Parse + cache all `.claude/agents/*.md`                           |
| `run_agent_query(agent, prompt)` | Run a query as a named agent (model routing + session)            |
| `run_orchestrator_query(prompt)` | Full orchestrator-style query (supports team mode)                |
| `clear_caches()`                 | Reset all caches (use in tests or after adding agents)            |
| `_copy_options_with(base, **kw)` | Shallow-copy options with overrides (never mutates cache)         |

---

## Caching

Two module-level caches avoid re-reading `.md` files and re-initialising MCP servers:

| Cache               | Contents                                                    | Invalidation     |
|---------------------|-------------------------------------------------------------|------------------|
| `_OPTIONS_CACHE`    | `ClaudeAgentOptions` (tools, agents, MCP servers, hooks)    | `clear_caches()` |
| `_AGENT_DEFS_CACHE` | `dict[str, AgentDefinition]` from all `.claude/agents/*.md` | `clear_caches()` |

**Important**: Per-call fields (`resume`, `model`) are set via `_copy_options_with()` — the cached object is never mutated directly. This prevents race conditions in concurrent calls.

---

## Session Continuity

```python
from a2a.agent_sdk import run_agent_query

session_out: dict = {}
result = await run_agent_query(
    "cybersec-analyst",
    "Analyze CVE-2024-1234",
    session_id=None,            # first call
    _session_out=session_out,
)

# Resume the conversation
result2 = await run_agent_query(
    "cybersec-analyst",
    "What about lateral movement?",
    session_id=session_out["session_id"],
    _session_out=session_out,
)
```

In A2A skill handlers, `task.session_id` is threaded through automatically.

---

## Hooks Pipeline

Two complementary hook systems:

| System             | Location             | Execution              |
|--------------------|----------------------|------------------------|
| Filesystem hooks   | `.claude/hooks/`     | Subprocess (`python3`) |
| SDK hooks          | `src/agent/hooks.py` | In-process async       |

| Hook Phase  | Hook            | Purpose                       |
|-------------|-----------------|-------------------------------|
| PreToolUse  | `security_hook` | Blocks dangerous commands     |
| PreToolUse  | `audit_hook`    | Logs all tool calls           |
| PostToolUse | `ioc_hook`      | Extracts IOCs from tool output |
| Stop        | `cost_hook`     | Logs session cost              |

---

## MCP Tool Injection

All agents automatically receive 93 in-process MCP tools (88 cybersec + 5 dystopian):

```python
# src/google_a2a/agent_sdk.py
mcp_server = create_sdk_mcp_server()  # wraps SdkMcpServer with all @tools-decorated fns
options = ClaudeAgentOptions(
    mcp_servers=[mcp_server],
    ...
)
```

The MCP server is built once and cached in `_OPTIONS_CACHE`. It is safe to share across concurrent queries because `call_tool()` is stateless.
