"""CyberSecSuite QoL System — Phase 2 Documentation (T016-T022).

## Overview

The QoL (Quality of Life) system provides fine-grained control over LLM output formatting
and behavior through eight independent toggles that can be combined in safe ways.

**Phase 1** (complete) established the core QoL architecture with settings persistence,
preset management, and basic injection.

**Phase 2** (this document) adds hardening features:
- T016: OpenObserve metrics emission with graceful degradation
- T017: A2A protocol propagation for state synchronization across agents
- T018: Per-agent preset binding with independent policies
- T019: Security validation preventing dangerous toggle combinations
- T020: Graceful degradation when injection fails or dependencies unavailable
- T021: Environment variable configuration with sensible defaults
- T022: Comprehensive documentation and troubleshooting

---

## Configuration Reference (T021)

### Environment Variables

All QoL configuration can be set via environment variables:

#### Core QoL Settings
- `QOL_ENABLED` — Enable/disable QoL injection globally (default: `true`)
- `QOL_DEFAULT_SCOPE` — Default scope for settings (default: `session`)
  - Valid values: `session`, `project`, `global`
- `QOL_MAX_TOKENS` — Maximum token budget for injection (default: `100`)
- `QOL_DEFAULT_TOGGLES` — Comma-separated default toggles (default: empty)
  - Example: `QOL_DEFAULT_TOGGLES=no_thinking,no_chat,minimal`

#### Storage Paths
- `CYBERSEC_BASE_DIR` — Override settings directory (default: `~/.cybersecsuite/data`)
- `MALWAREHUNTER_BASE_DIR` — Fallback settings directory
- `PLUGIN_DATA_DIR` — Plugin data directory override
- `CYBERSECSUITE_HOME` — Home directory override (default: `~/.cybersecsuite`)

#### OpenObserve Metrics (T016)
- `OPENOBSERVE_ENABLED` — Enable metrics emission (default: `true`)
- `OPENOBSERVE_HOST` — OpenObserve host:port (default: `http://127.0.0.1:5080`)
- `OPENOBSERVE_ORG` — Organization name (default: `default`)
- `OPENOBSERVE_EMAIL` — Authentication email (default: `admin@cybersec.local`)
- `OPENOBSERVE_PASSWORD` — Authentication password

#### A2A Protocol (T017)
- `A2A_ENABLED` — Enable A2A propagation (default: `true`)
- `QOL_PROPAGATE_SETTINGS` — Propagate settings to all agents (default: `false`)

### Configuration File (config.yaml / config.json)

Fallback configuration files are checked in order:
1. `~/.cybersecsuite/config.yaml`
2. `~/.cybersecsuite/config.json`
3. Environment variables

Example config.yaml:
```yaml
qol:
  enabled: true
  default_scope: session
  max_tokens: 100
  default_toggles:
    - no_thinking
    - no_chat

openobserve:
  enabled: true
  host: http://localhost:5080
  org: default

a2a:
  enabled: true
  propagate_settings: false
```

---

## Toggles Reference

### Output Suppression

**no_thinking** — Suppress reasoning/thinking blocks
- Use when: You want concise responses without intermediate reasoning
- Incompatible with: Nothing
- Token cost: Low

**no_chat** — Suppress conversational filler
- Use when: You want only the requested artifact, no pleasantries
- Incompatible with: Nothing
- Token cost: Low

**minimal** — Absolute minimum output
- Use when: You need one-liners or direct answers only
- Incompatible with: `append_audit_trail`
- Token cost: Very low

### Format Controls

**no_markdown** — Plain text only, no Markdown formatting
- Use when: Output will be parsed by a non-Markdown-aware tool
- Incompatible with: Nothing
- Token cost: Low

**structured_only** — JSON/YAML/table output only
- Use when: You need machine-parseable structured data
- Incompatible with: `file_only`
- Token cost: Medium

**file_only** — File/code output only, NOTHING ELSE
- Use when: You want pure code/file output without any explanation
- Incompatible with: `append_audit_trail`, `structured_only`
- Token cost: Low

### Safety & Audit

**redact_secrets** — Auto-redact API keys, passwords, tokens
- Use when: Output will be logged/shared publicly
- Incompatible with: Nothing
- Token cost: Low
- Note: Uses pattern-based redaction, not foolproof

**append_audit_trail** — Append audit entry to every response
- Use when: You need compliance/audit trail for regulatory requirements
- Incompatible with: `file_only`, `minimal`
- Token cost: Medium
- Appends: Timestamp, model, toggle hash, user

---

## API Reference

### REST Endpoints

#### QoL Settings Management

**GET /api/qol?scope=session**
Get current QoL settings for a scope.

Query Parameters:
- `scope` — Scope name: `session`, `project`, or `global` (default: `session`)

Response (200):
```json
{
  "scope": "session",
  "active_toggles": ["no_thinking", "minimal"],
  "preset_name": "silent",
  "fragment_preview": "You are an expert assistant...",
  "estimated_tokens": 42,
  "toggle_hash": "a1b2c3d4"
}
```

**POST /api/qol**
Enable/disable toggles or load a preset.

Request:
```json
{
  "scope": "session",
  "preset": "silent",
  "enable": ["no_markdown"],
  "disable": ["no_chat"]
}
```

Response (200):
```json
{
  "ok": true,
  "scope": "session",
  "active_toggles": ["no_thinking", "no_markdown", "minimal"],
  "preset_name": "silent"
}
```

Error (409 - Security Violation):
```json
{
  "error": "Security violation: Contradictory QoL toggle combination: [file_only, append_audit_trail]. These directives cannot coexist — disable one before enabling the other."
}
```

**DELETE /api/qol?scope=session**
Reset all toggles for a scope.

Response (200):
```json
{
  "ok": true,
  "scope": "session",
  "active_toggles": []
}
```

#### Preset Management

**GET /api/qol/presets**
List all available presets.

Response (200):
```json
{
  "presets": {
    "silent": {
      "enabled_toggles": ["no_thinking", "no_chat", "minimal"],
      "scope": "session",
      "source": "builtin"
    },
    "code-only": {
      "enabled_toggles": ["file_only", "no_thinking", "no_chat"],
      "source": "builtin"
    },
    "my-custom": {
      "enabled_toggles": ["no_markdown"],
      "source": "user"
    }
  },
  "count": 6
}
```

**POST /api/qol/presets/{name}**
Save current session settings as a named preset.

Request:
```json
{
  "scope": "session"
}
```

Response (200):
```json
{
  "ok": true,
  "name": "my-preset",
  "enabled_toggles": ["no_thinking", "no_chat"],
  "scope": "session"
}
```

#### Per-Agent Presets (T018)

**GET /api/qol/agent/{agent_id}/preset**
Get the preset bound to an agent.

Response (200):
```json
{
  "agent": "cybersec-main",
  "preset": "silent",
  "toggles": ["no_thinking", "no_chat", "minimal"]
}
```

Response (200, no binding):
```json
{
  "agent": "cybersec-main",
  "preset": null
}
```

**POST /api/qol/agent/{agent_id}/preset**
Bind a preset to an agent (T017/T018).

Request:
```json
{
  "preset": "silent"
}
```

Response (200):
```json
{
  "ok": true,
  "agent": "cybersec-main",
  "preset": "silent",
  "toggles": ["no_thinking", "no_chat", "minimal"]
}
```

Error (409 - Security Validation):
```json
{
  "error": "Security violation: [file_only, append_audit_trail] cannot coexist"
}
```

**DELETE /api/qol/agent/{agent_id}/preset**
Unbind a preset from an agent.

Response (200):
```json
{
  "ok": true,
  "agent": "cybersec-main",
  "preset": null
}
```

---

## Security (T019)

### Dangerous Combinations

The following toggle combinations are **blocked** and return HTTP 409 Conflict:

1. **file_only + append_audit_trail**
   - Contradiction: file-only output cannot have trailing audit text
   - Error: "file-only but append text"

2. **file_only + structured_only**
   - Contradiction: files are not structured data
   - Error: "file-only vs structured-data-only"

3. **minimal + append_audit_trail**
   - Contradiction: minimal output cannot have audit trail
   - Error: "minimal but append audit text"

### Validation Points

Security validation is performed at:
- **Settings save** — `manager.save_settings(settings)` validates before persist
- **Preset binding** — `manager.set_agent_preset(agent, preset)` validates before bind
- **Injection** — `manager.inject_into_request(...)` validates before injection
- **API requests** — All POST endpoints validate request body

### Audit Logging

All validation failures are logged with full context:
```
WARNING qol.security: blocked dangerous combo — Contradictory QoL toggle combination: [file_only, append_audit_trail]
```

---

## Metrics & Observability (T016)

### OpenObserve Streams

Metrics are emitted to OpenObserve in the following streams:

#### qol_metrics Stream
Events emitted on every injection:
```json
{
  "@timestamp": "2026-04-27T10:00:00Z",
  "event_type": "qol.injection",
  "tokens": 42,
  "latency_ms": 3.2,
  "total_injections": 1234,
  "scope": "session",
  "toggle_count": 3,
  "toggle_names": "no_thinking,no_chat,minimal",
  "session_id": "sess_abc123",
  "agent_name": "cybersec-main",
  "over_budget": false
}
```

#### qol_security Stream
Security events on violation attempts:
```json
{
  "@timestamp": "2026-04-27T10:00:00Z",
  "event_type": "qol.combo_violation",
  "combo": "file_only,append_audit_trail",
  "agent": "agent_id",
  "total_violations": 5
}
```

#### qol_audit_trail Stream
Audit events for toggle changes:
```json
{
  "@timestamp": "2026-04-27T10:00:00Z",
  "event_type": "qol.settings_saved",
  "scope": "session",
  "toggles": "no_thinking,minimal",
  "user": "admin",
  "total_saves": 42
}
```

### Metrics API

**GET /api/qol/metrics**
Return current QoL metrics.

Response (200):
```json
{
  "injection_count": 1234,
  "injection_failures": 2,
  "injection_token_total": 52410,
  "injection_token_avg": 42,
  "injection_latency_avg_ms": 3.1,
  "settings_save_count": 18,
  "preset_save_count": 5,
  "agent_preset_bind_count": 12,
  "toggle_combo_errors": 3,
  "last_injection_tokens": 42
}
```

### Graceful Degradation (T020)

If OpenObserve becomes unavailable:
1. Metrics are logged locally (DEBUG level) instead of emitted
2. Retry logic kicks in with exponential backoff (100ms, 200ms, 400ms)
3. **Injection always succeeds** — metrics emission never blocks routing
4. Once OpenObserve recovers, metrics resume emission

Example log output when degraded:
```
DEBUG openobserve.writer: OpenObserve client unavailable, skipping event emission
DEBUG openobserve.writer: OpenObserve emission error: Connection refused
```

---

## A2A Integration (T017)

### Toggle Propagation

When QoL toggles are changed, events are published via A2A protocol:

**qol.toggle_changed Event:**
```json
{
  "type": "qol.toggle_changed",
  "agent": "agent_id",
  "scope": "session",
  "toggle": "no_thinking",
  "enabled": true
}
```

**qol.preset_bound Event:**
```json
{
  "type": "qol.preset_bound",
  "agent": "agent_id",
  "preset": "silent"
}
```

### Subscription Example

```python
from ai_proxy.qol_controls.a2a_integration import get_subscriber

subscriber = get_subscriber()

async def on_toggle_changed(agent, scope, toggle, enabled):
    print(f"Agent {agent} toggled {toggle}={enabled}")

subscriber.on_toggle_changed(on_toggle_changed)

# Events are dispatched to callbacks when received via A2A
```

### State Synchronization

- **No global state** — Each agent maintains independent settings
- **Per-agent preset binding** — Presets are agent-specific, not global
- **Override policy** — Agent presets override scope settings
- **Failure handling** — A2A failures don't affect local QoL functionality

---

## Troubleshooting

### "Injection fails silently" (T020)

**Symptom:** QoL settings are configured but not being applied to requests.

**Diagnosis:**
1. Check if QoL is enabled: `curl http://localhost:8000/api/qol`
2. Verify settings are saved: Response should show `active_toggles` non-empty
3. Check logs for: `qol.inject_into_request failed unexpectedly`

**Solutions:**
- Validate toggle combination: no dangerous combos allowed (T019)
- Check JSON file integrity: `~/.cybersecsuite/data/qol.json`
- Verify scope is correct: use `scope=session` for default

### "OpenObserve metrics not appearing" (T016)

**Symptom:** Metrics are not appearing in OpenObserve dashboard.

**Diagnosis:**
1. Check OpenObserve is running: `curl http://localhost:5080/healthz`
2. Check metrics API: `GET /api/qol/metrics` should show `events_sent > 0`
3. Check logs for: `OpenObserve emission failed`

**Solutions:**
- Verify OpenObserve credentials: `OPENOBSERVE_EMAIL`, `OPENOBSERVE_PASSWORD`
- Check network connectivity: `telnet localhost 5080`
- Ensure `OPENOBSERVE_ENABLED=true`
- Check OpenObserve organization: `OPENOBSERVE_ORG`

### "A2A events not propagating" (T017)

**Symptom:** Toggle changes in one agent don't propagate to others.

**Diagnosis:**
1. Check A2A is enabled: `A2A_ENABLED=true`
2. Check agent connectivity: verify A2A network accessible
3. Check logs for: `A2A message sent` or `Failed to publish`

**Solutions:**
- Verify A2A network configuration
- Check agent registry is accessible
- Ensure `QOL_PROPAGATE_SETTINGS` matches deployment policy
- Verify agents have correct agent names

### "Can't bind preset to agent" (T018)

**Symptom:** POST /api/qol/agent/{agent_id}/preset returns 409 Conflict.

**Diagnosis:**
1. Check preset exists: `GET /api/qol/presets`
2. Check for dangerous combos: response message indicates which

**Solutions:**
- Use a safe preset: e.g., `silent`, `code-only`, `structured`
- Create a custom safe preset using API
- Disable one of the conflicting toggles

### "Environment variables not being used" (T021)

**Symptom:** QOL_DEFAULT_TOGGLES or other env vars don't seem to work.

**Diagnosis:**
1. Verify env var is set: `echo $QOL_DEFAULT_TOGGLES`
2. Check app was restarted after setting env var
3. Check for typos in toggle names

**Solutions:**
- Verify toggle names are valid: see Toggles Reference
- Use comma-separated format without spaces: `no_thinking,no_chat`
- Restart application after changing env vars
- Use config file as fallback: `~/.cybersecsuite/config.yaml`

---

## Performance Characteristics

### Token Budget
- Target: 100 tokens per injection (configurable via `QOL_MAX_TOKENS`)
- Typical range: 20–60 tokens depending on toggles
- Warning threshold: >100 tokens

### Latency
- Fragment cache lookup: <1ms
- Build injection: 2–5ms
- Total injection overhead: <10ms

### Memory
- Fragment cache: ~1KB per unique toggle combination
- Settings in memory: ~1KB per scope
- Negligible overall impact

### Metrics Emission
- Local collection: <1ms
- OpenObserve async emit: 10–50ms (non-blocking)
- Batch processing: up to 100 events per flush

---

## Examples

### Example 1: Enable silent mode for session

```bash
curl -X POST http://localhost:8000/api/qol \
  -H "Content-Type: application/json" \
  -d '{
    "scopes": "session",
    "preset": "silent"
  }'
```

### Example 2: Bind agent to code-only preset

```bash
curl -X POST http://localhost:8000/api/qol/agent/cybersec-main/preset \
  -H "Content-Type: application/json" \
  -d '{"preset": "code-only"}'
```

### Example 3: Check metrics

```bash
curl http://localhost:8000/api/qol/metrics | jq .
```

### Example 4: Set defaults via env

```bash
export QOL_DEFAULT_SCOPE=project
export QOL_DEFAULT_TOGGLES=no_thinking,no_chat
export QOL_MAX_TOKENS=80
export OPENOBSERVE_ENABLED=true
```

### Example 5: Python API usage

```python
from ai_proxy.qol_controls.manager import get_manager
from ai_proxy.qol_controls.models import QoLToggle, QoLSettings

manager = get_manager()

# Load settings
settings = manager.load_settings("session")

# Enable toggles
settings.activate(QoLToggle.NO_THINKING, QoLToggle.MINIMAL)
manager.save_settings(settings)

# Inject into request
body = {"system": "Hello", "messages": []}
injected = manager.inject_into_request(body, scope="session")

# Check metrics
metrics = manager.get_metrics()
print(f"Injections: {metrics['injection_count']}")
```

---

## See Also

- API Reference: [qol.md](./qol.md)
- Phase 1 Documentation: [Phase 1 QoL System](./phase1_qol.md)
- Security: [Security Policy](./SECURITY.md)
- Troubleshooting: See "Troubleshooting" section above
"""
