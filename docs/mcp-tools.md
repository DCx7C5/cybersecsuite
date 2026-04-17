# MCP Tools Reference

All 29 MCP tools exposed by `mcp_server.py` via FastMCP stdio transport.

Start the MCP server: `make mcp`

Tool name prefix: `cybersec.`

---

## Findings & IOCs

### `cybersec.add_finding`
Record a security finding in the database.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | string | yes | Short finding title |
| `severity` | string | yes | `low`, `medium`, `high`, `critical` |
| `description` | string | yes | Full finding details |
| `category` | string | no | Finding category (e.g. `malware`, `network`) |
| `mitre_technique` | string | no | ATT&CK technique ID (e.g. `T1055`) |
| `status` | string | no | `open`, `investigating`, `confirmed`, `resolved` |

---

### `cybersec.add_ioc`
Record an Indicator of Compromise.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `ioc_type` | string | yes | `ip`, `domain`, `hash`, `url`, `email`, `filename` |
| `value` | string | yes | The IOC value |
| `confidence` | string | no | `low`, `medium`, `high`, `confirmed` |
| `status` | string | no | `active`, `cleared`, `watchlist`, `expired` |
| `description` | string | no | Context/notes |

---

### `cybersec.query_findings`
Query findings from the database.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `severity` | string | no | Filter by severity |
| `status` | string | no | Filter by status |
| `limit` | int | no | Max results (default 50) |
| `scope` | string | no | `workspace`, `project`, `session` |

---

### `cybersec.update_risk_register`
Update a finding's risk assessment.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `finding_id` | int | yes | Finding database ID |
| `risk_score` | float | yes | Risk score 0.0–10.0 |
| `notes` | string | no | Risk assessment notes |

---

### `cybersec.get_project_memory`
Retrieve investigation memory for the current project scope.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | no | Filter/search term |

---

## Cases

### `cybersec.case_open`
Open a new investigation case with full intake questionnaire.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | string | yes | Case title |
| `description` | string | yes | Case description |
| `severity` | string | no | `low`, `medium`, `high`, `critical` |
| `assigned_to` | string | no | Assignee |

---

### `cybersec.case_status`
Get status of one or all investigation cases.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `case_id` | int | no | Specific case ID (omit for all) |

---

## Intelligence

### `cybersec.db_healthcheck`
Check database connectivity and model counts.

**Parameters:** none

---

### `cybersec.bootstrap_intelligence`
Seed MITRE ATT&CK, CVE, CWE, and CAPEC datasets into the database.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `force` | bool | no | Re-seed even if already seeded (default: false) |

---

### `cybersec.suggest_mitre`
Suggest MITRE ATT&CK techniques matching a description.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `description` | string | yes | Behavior to match (e.g. "process injection via ptrace") |
| `category` | string | no | ATT&CK tactic (e.g. `persistence`, `execution`) |

---

### `cybersec.share_to_layers`
Share data across scope layers (workspace → project → session).

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | string | yes | Layer key |
| `value` | any | yes | Data to store |
| `target_scopes` | list[string] | no | `["workspace", "project", "session"]` |

---

### `cybersec.get_layer_value`
Retrieve a value from a scope layer.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | string | yes | Layer key |
| `scope` | string | no | `workspace`, `project`, `session` |

---

## Cache

### `cybersec.cache_lookup`
Look up a value in the encrypted cache.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | string | yes | Cache key |

---

### `cybersec.cache_store`
Store a value in the encrypted cache.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | string | yes | Cache key |
| `value` | any | yes | Value to cache |
| `ttl_seconds` | int | no | Time-to-live in seconds |

---

### `cybersec.cache_analytics`
Get cache hit/miss statistics.

**Parameters:** none

---

### `cybersec.cache_invalidate`
Invalidate a cache entry.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `key` | string | yes | Cache key to invalidate |
| `pattern` | bool | no | Treat key as glob pattern (default: false) |

---

## AI Proxy

### `cybersec.proxy_chat`
Send a chat request via the multi-provider AI proxy.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `message` | string | yes | User message |
| `provider` | string | no | Force specific provider ID |
| `model` | string | no | Force specific model ID |
| `strategy` | string | no | Routing strategy (default: `priority`) |

---

### `cybersec.proxy_providers`
List all configured AI providers and their status.

**Parameters:** none

---

### `cybersec.proxy_models`
List available models.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `provider` | string | no | Filter by provider ID |

---

### `cybersec.proxy_usage`
Token and cost usage statistics by provider.

**Parameters:** none

---

### `cybersec.proxy_cost`
Cost breakdown by provider and model.

**Parameters:** none

---

### `cybersec.simulate_route`
Simulate routing without sending a real request.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `message` | string | yes | Sample message to route |
| `strategy` | string | no | Routing strategy |

---

### `cybersec.explain_route`
Explain how a request would be routed and why.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `message` | string | yes | Message to explain routing for |

---

### `cybersec.routing_strategies`
List all 13 available routing strategies with descriptions.

**Parameters:** none

---

### `cybersec.set_budget_guard`
Set a spend limit for the current session.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `limit_usd` | float | yes | Maximum spend in USD |

---

### `cybersec.get_circuit_breakers`
Get circuit breaker state for all providers.

**Parameters:** none

---

### `cybersec.best_provider`
Recommend the best provider for a given task.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `task_description` | string | yes | What you need the provider for |
| `prefer_free` | bool | no | Prefer free-tier providers (default: false) |

---

## Session & Agents

### `cybersec.session_snapshot`
Get a full snapshot of the current session state (scope, findings, IOCs, cases).

**Parameters:** none

---

### `cybersec.agent_registry`
List all registered A2A agents.

**Parameters:** none

---

## Tool Return Format

All tools return:

```json
{
  "content": [
    {
      "type": "text",
      "text": "{...json-encoded result...}"
    }
  ]
}
```

Error responses include `"error": true` and `"message": "..."` in the result dict.
