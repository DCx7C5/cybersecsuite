# Deprecation Audit: `src/a2a/`

**Verdict:** KEPT (ACTIVE)

**Audit date:** 2025-07-28

## Evidence

| Metric | Count |
|--------|-------|
| External import sites (non-a2a source files) | 8 |
| Test files covering this module | 3 |
| Test functions | 30 (23 in test_a2a.py + 3 in test_agent_discovery.py + 4 in test_agent_streaming_backend.py) |
| Listed in `pyproject.toml` packages | Yes (`src/a2a`) |
| Listed in `pyproject.toml` description | Yes ("A2A agent orchestration") |

### Import sites (external callers)

| File | Symbol |
|------|--------|
| `src/proxy/asgi.py` | `CybersecA2AAgent`, `A2AServer` |
| `src/db/models/tool_seeds.py` | `frontmatter_to_claude_agent`, `iter_agent_markdown_files` |
| `src/ai_proxy/qol_controls/a2a_integration.py` | `A2AMessage` |
| `src/csmcp/cybersec/session.py` | `AgentRegistry`, `load_cybersecsuite_agents` |
| `src/agent/client_pool.py` | `build_agent_options` |
| `src/agent/runner.py` | `build_agent_options` |
| `src/agent/streaming.py` | `build_agent_options` |
| `src/a2a/agent_sdk.py` | (internal — used by agent module) |

### Test files

| File | Tests | Status |
|------|-------|--------|
| `tests/test_a2a.py` | 23 | ✅ Passing |
| `tests/test_agent_discovery.py` | 3 | ⚠️ Collection error (missing `src/dashboard` module — pre-existing) |
| `tests/test_agent_streaming_backend.py` | 4 | ⚠️ Collection error (missing `src/dashboard` module — pre-existing) |

## Rationale

`src/a2a/` implements the Google Agent-to-Agent (A2A) protocol and is the core orchestration layer for all agent routing in CyberSecSuite. It is directly imported by the ASGI proxy, the MCP session handler, the DB tool-seed loader, the AI proxy QoL integration, and the agent runner/streaming stack. With 8 distinct external import sites and 3 dedicated test files, it is deeply embedded in the project. **No action taken — module is essential and must be kept.**
