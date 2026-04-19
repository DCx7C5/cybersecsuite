# Agent SDK Integration

> How `.claude/agents/` definitions flow through the SDK to 60 AI providers.

## Architecture

```
.claude/agents/*.md          (36 agent definitions — frontmatter + persona)
        │
        ▼
  agent_loader.py            (parse frontmatter: name, model, tools, role)
        │
        ▼
  agent_sdk.py               (cache AgentDefinitions, build ClaudeAgentOptions)
        │                     run_agent_query("cybersec-analyst", prompt)
        │                       → reads agent's model from definition
        │                       → prepends [AGENT CONTEXT] persona block
        │                       → shallow-copies options (never mutates cache)
        │
        ▼
  claude-agent-sdk query()   (SDK sends request to ANTHROPIC_BASE_URL)
        │
        ▼
  AI Proxy /v1/*             (http://localhost:8000/v1)
        │                     → 13 routing strategies (combo.py)
        │                     → circuit breaker per provider
        │                     → budget guard
        ▼
  60 AI Providers            (Anthropic, DeepSeek, Gemini, Groq, OpenRouter, …)
```

## Two Execution Paths

| Path | Entry Point | Flow |
|------|-------------|------|
| **Agent SDK** (internal) | `query()` / `run_agent_query()` | SDK → Proxy → Provider → response |
| **A2A Protocol** (external) | `POST /a2a` JSON-RPC | → `CybersecA2AAgent.execute()` → skill handler → `run_agent_query()` → SDK → Proxy |

Both paths converge on `run_agent_query()` which reads `.claude/agents/*.md` definitions.

## Per-Agent Model Routing

Each `.claude/agents/*.md` frontmatter declares a `model:` field:

```yaml
---
name: python-developer
model: deepseek-v3
tools: [Read, Write, Edit, Bash, Glob, Grep]
---
```

When `run_agent_query("python-developer", prompt)` is called:

1. `build_agent_definitions()` returns the cached `AgentDefinition` with `model="deepseek-v3"`
2. `_copy_options_with()` creates a shallow copy of the cached options with `model="deepseek-v3"`
3. The SDK sends the request with `model=deepseek-v3` to the proxy
4. The proxy routes to DeepSeek via its provider registry

**No code changes needed per agent** — just update the `model:` field in the `.md` file.

### Model Mapping

The SDK maps common shorthand names to full model IDs:

| Shorthand | Model ID |
|-----------|----------|
| `haiku` | `claude-haiku-4-5` |
| `sonnet` | `claude-sonnet-4-5` |
| `opus` | `claude-opus-4-5` |
| (full ID) | passed through as-is (e.g. `deepseek-v3`, `gemini-2.0-flash`) |

## Session Continuity

The SDK allocates a `session_id` on the first query. Subsequent queries can resume the same session for multi-turn conversations:

```python
from a2a.agent_sdk import run_agent_query

session_out: dict = {}
result = await run_agent_query(
    "cybersec-analyst",
    "Analyze CVE-2024-1234",
    session_id=None,              # first call — no session yet
    _session_out=session_out,
)
# session_out["session_id"] now contains the SDK session ID

# Resume the conversation
result2 = await run_agent_query(
    "cybersec-analyst",
    "What about lateral movement?",
    session_id=session_out["session_id"],  # resume
    _session_out=session_out,
)
```

In A2A skill handlers, `task.session_id` is threaded through automatically.

## Caching

Two module-level caches avoid re-reading `.md` files and re-initialising MCP servers:

| Cache | Contents | Invalidation |
|-------|----------|--------------|
| `_OPTIONS_CACHE` | `ClaudeAgentOptions` (tools, agents, MCP servers, hooks) | `clear_caches()` |
| `_AGENT_DEFS_CACHE` | `dict[str, AgentDefinition]` from all `.claude/agents/*.md` | `clear_caches()` |

**Important**: Per-call fields (`resume`, `model`) are set via `_copy_options_with()` — the cached object is never mutated directly. This prevents race conditions in concurrent calls.

## Key Functions

| Function | Purpose |
|----------|---------|
| `build_agent_options()` | Build/return cached `ClaudeAgentOptions` with all tools + agents |
| `build_agent_definitions()` | Parse + cache all `.claude/agents/*.md` as `AgentDefinition` dict |
| `run_agent_query(agent, prompt)` | Run a query as a named agent, with model routing + session |
| `run_orchestrator_query(prompt)` | Run a full orchestrator-style query (blue/red/purple mode) |
| `clear_caches()` | Reset all caches (use in tests or after adding agents) |
| `_copy_options_with(base, **kw)` | Shallow-copy options with overrides (never mutates cache) |

## A2A Flow (Simplified)

```
External client
    │
    POST /a2a  {"method": "tasks/send", "params": {"message": {"parts": [{"text": "..."}]}}}
    │
    ▼
A2AServer._jsonrpc()
    │
    ▼
CybersecA2AAgent.execute(task, message)
    │
    ├── CVE keyword?    → _handle_cve()    → DB lookup + run_agent_query("cybersec-analyst")
    ├── IOC keyword?    → _handle_ioc()    → DB lookup + run_agent_query("cybersec-analyst")
    ├── MITRE keyword?  → _handle_mitre()  → DB lookup + run_agent_query("cybersec-analyst")
    ├── artifact?       → _handle_artifact() → crypto signing (no SDK call)
    ├── threat model?   → _handle_threat_model() → DB + run_agent_query("threat-modeler")
    └── anything else   → _handle_generic() → run_agent_query("cybersec-analyst")
                              │
                              ▼
                        SDK → Proxy → Provider
```
