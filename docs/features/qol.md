# QoL Output Controls

Quality of Life (QoL) output controls enable fine-grained configuration of AI model behavior and response formatting in CyberSecSuite. Control what models output, how they structure responses, and optimize for specific use cases without code changes.

_Last updated: 2026-04_

---

## What is QoL?

QoL is a **server-side injection system** that modifies AI prompts before they reach providers. It works by:

1. Reading QoL settings (toggles + presets) from configuration
2. Building a prompt injection block with enabled toggles
3. Prepending the injection to the system message in every request
4. Logging the injection for audit and observability

QoL enables you to:
- **Silence certain outputs** — disable reasoning, code blocks, step-by-step explanations
- **Force output formats** — JSON-only, structured code, plain text
- **Optimize costs** — reduce token usage by disabling verbose explanations
- **Audit compliance** — enforce output constraints across all agent requests
- **Custom presets** — save and reuse configuration combinations

---

## Feature Matrix

### Available Toggles

| Toggle | Description | Effect | Use Case |
|--------|-------------|--------|----------|
| `REASONING_SILENT` | Disable thinking/reasoning | Removes `<thinking>` blocks from Claude 3.5 | Cost reduction, privacy |
| `CODE_ONLY` | Only code blocks allowed | Strips all prose text | Developer scripts, CI/CD |
| `JSON_STRUCTURED` | Enforce JSON output | Wraps response in `{"content": "..."}` | API integration, parsing |
| `FILE_ONLY` | Output only file contents | Single artifact output, no commentary | Deployment automation |
| `STEP_BY_STEP_SILENT` | Hide step-by-step reasoning | Removes enumerated reasoning steps | Concise output |
| `PLAIN_TEXT_ONLY` | No markdown, no code blocks | Forces plain text only | Log compatibility, audit |
| `NO_CITATIONS` | Remove source citations | Strips `[1]`, `[src]` references | Clean output |
| `AUDIT_MODE` | Force detailed logging | Adds provenance metadata | Compliance, forensics |

### Builtin Presets

| Preset | Toggles | Purpose |
|--------|---------|---------|
| `silent` | `REASONING_SILENT`, `STEP_BY_STEP_SILENT` | Minimal chatter, quick answers |
| `code-only` | `CODE_ONLY`, `REASONING_SILENT` | Pure code output for automation |
| `structured` | `JSON_STRUCTURED`, `AUDIT_MODE` | Machine-parseable with provenance |
| `audit` | `AUDIT_MODE`, `PLAIN_TEXT_ONLY` | Forensic compliance logging |
| `plain-text` | `PLAIN_TEXT_ONLY`, `NO_CITATIONS` | Clean plain text output |

---

## Use Cases

### Scenario 1: Cost Optimization

**Goal:** Reduce token usage for routine investigations

**Configuration:**
```json
{
  "enabled_toggles": ["REASONING_SILENT", "STEP_BY_STEP_SILENT"],
  "preset": "silent"
}
```

**Effect:** Claude 3.5 skips reasoning blocks; models output direct answers without enumeration. Typical 30% token reduction.

---

### Scenario 2: Forensic Audit

**Goal:** Maintain chain of custody with full logging

**Configuration:**
```json
{
  "enabled_toggles": ["AUDIT_MODE", "PLAIN_TEXT_ONLY"],
  "preset": "audit"
}
```

**Effect:** All responses include provenance headers; plain text only for log compatibility and legal admissibility.

---

### Scenario 3: Automated Deployment

**Goal:** Extract artifacts for automated processing

**Configuration:**
```json
{
  "enabled_toggles": ["CODE_ONLY", "REASONING_SILENT", "FILE_ONLY"],
  "preset": "code-only"
}
```

**Effect:** Only code blocks output; no reasoning; single file artifact per request. Parser-friendly for CI/CD integration.

---

### Scenario 4: API Integration

**Goal:** Ensure consistent, parseable responses

**Configuration:**
```json
{
  "enabled_toggles": ["JSON_STRUCTURED", "AUDIT_MODE"],
  "preset": "structured"
}
```

**Effect:** All responses wrapped in JSON structure; audit metadata included; downstream systems parse deterministically.

---

### Scenario 5: User Investigation (Default)

**Goal:** Balanced output for manual investigation

**Configuration:**
```json
{
  "enabled_toggles": [],
  "preset": null
}
```

**Effect:** No restrictions; models output naturally. Suitable for interactive security investigations.

---

## Configuration

### Scope Hierarchy

QoL settings are stored per scope:

| Scope | Level | Storage | Applies To |
|-------|-------|---------|-----------|
| **Global** | System-wide | `~/.cybersecsuite/qol_global.json` | All requests (unless overridden) |
| **Project** | Investigation project | `~/.cybersecsuite/<project_id>/qol.json` | All requests in project (unless overridden) |
| **Session** | Chat/task session | `~/.cybersecsuite/<project_id>/sessions/<session_id>/qol.json` | Single session only |
| **Request** | Single LLM request | HTTP header or JSON field | One-off override |

### Loading Priority (highest → lowest)

1. **Request-level override** — `X-QoL-Settings` HTTP header or task parameter
2. **Session-level settings** — Current session configuration
3. **Project-level settings** — Investigation project configuration
4. **Global settings** — System-wide defaults

### File Format

```json
{
  "enabled_toggles": [
    "REASONING_SILENT",
    "CODE_ONLY"
  ],
  "preset": "code-only",
  "custom_fragment": null,
  "created_at": "2026-04-22T10:30:00Z",
  "updated_at": "2026-04-22T10:30:00Z"
}
```

### Environment Variable Overrides

| Variable | Purpose | Example |
|----------|---------|---------|
| `CYBERSEC_QOL_PRESET` | Set global preset | `CYBERSEC_QOL_PRESET=audit` |
| `CYBERSEC_QOL_TOGGLES` | Enable toggles globally | `CYBERSEC_QOL_TOGGLES=REASONING_SILENT,AUDIT_MODE` |
| `CYBERSEC_QOL_DISABLED` | Disable all QoL injection | `CYBERSEC_QOL_DISABLED=true` |

---

## API Reference

### Dashboard REST Endpoints

All QoL endpoints are mounted at `/api/qol/`.

#### Get Current Settings

```
GET /api/qol
```

Returns current QoL settings for the active scope.

**Response:**
```json
{
  "scope": "session",
  "scope_id": "sess-abc123",
  "enabled_toggles": ["REASONING_SILENT"],
  "preset": "silent",
  "token_estimate": 50
}
```

---

#### Update Settings

```
POST /api/qol
Content-Type: application/json

{
  "enabled_toggles": ["CODE_ONLY", "REASONING_SILENT"],
  "preset": "code-only",
  "scope": "session"
}
```

**Response:** Updated settings (same as GET).

**Error codes:**
- `400` — Invalid toggle name or preset
- `403` — Permission denied for scope
- `409` — Conflicting settings (e.g., `JSON_STRUCTURED` + `FILE_ONLY`)

---

#### Reset to Defaults

```
DELETE /api/qol
```

Resets current scope to factory defaults (no toggles, no preset).

**Response:**
```json
{
  "scope": "session",
  "enabled_toggles": [],
  "preset": null
}
```

---

#### List Builtin Presets

```
GET /api/qol/presets
```

Returns all available builtin presets.

**Response:**
```json
{
  "presets": {
    "silent": {
      "name": "silent",
      "description": "Minimal chatter, quick answers",
      "toggles": ["REASONING_SILENT", "STEP_BY_STEP_SILENT"],
      "token_estimate": 45
    },
    "code-only": {
      "name": "code-only",
      "description": "Pure code output for automation",
      "toggles": ["CODE_ONLY", "REASONING_SILENT"],
      "token_estimate": 30
    },
    "structured": {
      "name": "structured",
      "description": "Machine-parseable with provenance",
      "toggles": ["JSON_STRUCTURED", "AUDIT_MODE"],
      "token_estimate": 65
    },
    "audit": {
      "name": "audit",
      "description": "Forensic compliance logging",
      "toggles": ["AUDIT_MODE", "PLAIN_TEXT_ONLY"],
      "token_estimate": 55
    },
    "plain-text": {
      "name": "plain-text",
      "description": "Clean plain text output",
      "toggles": ["PLAIN_TEXT_ONLY", "NO_CITATIONS"],
      "token_estimate": 40
    }
  }
}
```

---

#### Apply Builtin Preset

```
POST /api/qol/presets/{preset_name}
```

Apply a builtin preset (e.g., `/api/qol/presets/audit`).

**Response:** Updated settings with the preset applied.

---

### MCP Tools

QoL tools are available in Claude Code via the `cybersec` MCP server (4 tools).

#### `qol_get`

Get current QoL settings.

**Input:**
```json
{
  "scope": "session"
}
```

**Output:**
```json
{
  "enabled_toggles": ["REASONING_SILENT"],
  "preset": "silent"
}
```

---

#### `qol_set`

Update QoL settings.

**Input:**
```json
{
  "scope": "session",
  "enabled_toggles": ["CODE_ONLY", "REASONING_SILENT"],
  "preset": "code-only"
}
```

**Output:** Updated settings.

---

#### `qol_reset`

Reset to defaults.

**Input:**
```json
{
  "scope": "session"
}
```

**Output:** Reset confirmation.

---

#### `qol_presets`

List all builtin presets.

**Input:** (empty)

**Output:**
```json
{
  "silent": {
    "toggles": ["REASONING_SILENT", "STEP_BY_STEP_SILENT"],
    "description": "Minimal chatter..."
  },
  ...
}
```

---

## Examples

### Example 1: Cost-Optimized Investigation

**Goal:** Investigate 100 IOCs quickly with minimal token usage.

**Setup:**
```bash
# Apply cost-optimized preset to project
curl -X POST http://localhost:8000/api/qol \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "project",
    "preset": "silent"
  }'
```

**Effect:** All agent queries in the investigation use the `silent` preset, reducing token count by ~30%.

---

### Example 2: Forensic Report Generation

**Goal:** Generate an audit-compliant report with chain of custody.

**Setup:**
```bash
# Enable audit preset for compliance
curl -X POST http://localhost:8000/api/qol \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "session",
    "preset": "audit",
    "enabled_toggles": ["AUDIT_MODE", "PLAIN_TEXT_ONLY"]
  }'
```

**Effect:** All responses are plain text with provenance metadata; log entries are admissible in court.

---

### Example 3: Automated Extraction via MCP

**Goal:** Extract malware analysis from Claude Code into CI/CD pipeline.

**MCP Tool Chain:**
```
1. qol_set(scope="session", preset="code-only")
2. <ask Claude for malware analysis>
3. Claude outputs only code artifacts
4. qol_reset(scope="session")
```

**Claude Code Usage:**
```
Claude: I'll analyze the malware and switch to code-only output.

<use_mcp_tool>
  <server_name>cybersec</server_name>
  <tool_name>qol_set</tool_name>
  <arguments>
    {
      "scope": "session",
      "preset": "code-only"
    }
  </arguments>
</use_mcp_tool>

Now I'll provide only code artifacts for parsing...
```

---

### Example 4: Agent Query with Request-Level Override

**Goal:** One-off override for a specific request.

**Via A2A Protocol:**
```json
{
  "jsonrpc": "2.0",
  "method": "agent.query",
  "params": {
    "agent_id": "apt-analyst",
    "query": "Analyze APT28 IOCs",
    "qol_settings": {
      "enabled_toggles": ["JSON_STRUCTURED"],
      "preset": "structured"
    }
  },
  "id": 1
}
```

**Effect:** This single query uses the structured preset; session/project settings remain unchanged.

---

### Example 5: Disable QoL Globally

**Goal:** Revert to natural output for all models (debugging).

**Setup:**
```bash
# Disable QoL injection system-wide
export CYBERSEC_QOL_DISABLED=true

# Or via API:
curl -X DELETE http://localhost:8000/api/qol?scope=global
```

**Effect:** All AI requests bypass QoL injection; models output naturally.

---

## Security & Compliance Considerations

### Dangerous Toggle Combinations

These combinations may produce unexpected results:

| Combination | Issue | Recommendation |
|-------------|-------|-----------------|
| `JSON_STRUCTURED` + `FILE_ONLY` | Conflicting output formats | Choose one or the other |
| `CODE_ONLY` + `PLAIN_TEXT_ONLY` | Models cannot comply with both | Avoid combination |
| `REASONING_SILENT` + models without reasoning | No-op for some providers | Safe but redundant |
| `AUDIT_MODE` (off) + compliance policy | Missing provenance | Always enable for regulated workloads |

### Audit Trail

All QoL changes are logged to the audit database:

```json
{
  "event_type": "qol.settings_changed",
  "timestamp": "2026-04-22T10:30:00Z",
  "scope": "project",
  "scope_id": "proj-abc123",
  "old_settings": { "enabled_toggles": [], "preset": null },
  "new_settings": { "enabled_toggles": ["AUDIT_MODE"], "preset": "audit" },
  "changed_by": "user@example.com",
  "correlation_id": "corr-xyz789"
}
```

---

### QoL Injection Logging

Every QoL injection is recorded:

```json
{
  "event_type": "qol.injection",
  "timestamp": "2026-04-22T10:30:00Z",
  "request_id": "req-123",
  "model": "claude-3-5-sonnet",
  "provider": "anthropic",
  "enabled_toggles": ["REASONING_SILENT"],
  "injection_token_count": 50,
  "total_request_tokens": 500
}
```

---

## Troubleshooting

### QoL Not Applied

**Symptom:** Settings are configured but responses show full reasoning/prose.

**Diagnosis:**
1. Check if `CYBERSEC_QOL_DISABLED=true`
2. Verify scope hierarchy — request override may be blocking
3. Check QoL toggle syntax for typos
4. Verify injection is logging via telemetry

**Solution:**
```bash
# Check global settings
curl http://localhost:8000/api/qol?scope=global

# Check injection logs
curl http://localhost:8000/sse/telemetry | grep "qol.injection"
```

---

### Token Estimate Mismatch

**Symptom:** Token usage doesn't match QoL estimate.

**Cause:** Different models have different tokenization; estimates are approximations.

**Solution:**
- Use actual token counts from provider responses
- Token estimate shown in API is for the QoL injection block only, not full request
- Monitor actual usage via `/api/usage` dashboard endpoint

---

### Conflicting Toggles Rejected

**Symptom:** API returns 409 Conflict when applying certain toggle combinations.

**Cause:** Certain toggle pairs cannot coexist (e.g., `CODE_ONLY` + `PLAIN_TEXT_ONLY`).

**Solution:**
- Use builtin presets which handle compatibility
- Review toggle definitions in Feature Matrix
- Contact architecture team for custom combinations

---

## Implementation Details

### QoL Manager (Singleton)

The `QoLManager` (in `src/ai_proxy/qol_controls/manager.py`) is a singleton that:

1. **Loads settings** from the scope hierarchy with fallback
2. **Builds injection block** by combining enabled toggle fragments
3. **Injects into requests** by prepending to system message or inserting system message
4. **Estimates tokens** for each injection
5. **Logs events** to telemetry for observability

### Injection Points

QoL injects into AI requests at:

1. **Pre-routing** — After user query, before routing strategy selection
2. **Provider dispatch** — After provider is chosen, before actual API call
3. **A2A tasks** — QoL settings can be passed in A2A `agent.query` params

### Caching

QoL injection blocks are cached with a 5-minute TTL per scope. Changes take effect after TTL expiry or manual cache flush.

---

## Admin Reference

### Check QoL System Health

```bash
curl http://localhost:8000/api/health | jq '.qol'
```

Expected response:
```json
{
  "qol_manager": "ready",
  "injection_cache": "enabled",
  "toggles_available": 8,
  "presets_available": 5,
  "injection_events_today": 1250
}
```

---

### View QoL Telemetry

```bash
# Recent QoL injections
curl "http://localhost:8000/sse/telemetry?filter=qol.*" | grep "qol\."

# QoL settings changes audit
curl "http://localhost:5080/api/logs?query=event_type:qol.settings_changed"
```

---

## See Also

- **Architecture:** [QoL Flow Diagram](../architecture/overview.md#qol-output-controls)
- **API Endpoints:** [QoL REST API](../api/http-endpoints.md#qol-output-controls)
- **MCP Tools:** [qol_get, qol_set, qol_reset, qol_presets](../mcp/overview.md#qol-output-controls)
- **Configuration:** [Scope Model](../configuration/scope-model.md)
- **Changelog:** [QoL Output Controls — Phase 1](../changelog/qol-output-controls-2026-04-22.md)
