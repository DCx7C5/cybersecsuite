# MCP Tool Reference

All tools registered in the `cybersec` MCP server. 87 tools across 24 modules (includes 5 crypto tools merged from dystopian).

**Status:** All tools have live backends.

---

## Findings & IOCs — `findings.py` (4 tools, live)

| Tool                   | Description                                                    |
|------------------------|----------------------------------------------------------------|
| `add_finding`          | Record a forensic finding with severity, source, evidence      |
| `add_ioc`              | Add an IOC (IP, domain, hash, URL) to the active investigation |
| `query_findings`       | Query findings by severity, type, session, or keyword          |
| `update_risk_register` | Update risk register entry with score and mitigation status    |

---

## Database — `db.py` (2 tools, live)

| Tool                     | Description                                              |
|--------------------------|----------------------------------------------------------|
| `db_healthcheck`         | Check database connectivity and table counts             |
| `bootstrap_intelligence` | Trigger seeding of MITRE/CVE/CWE/CAPEC intelligence data |

---

## Intelligence — `intelligence.py` (2 tools, live)

| Tool                 | Description                                                   |
|----------------------|---------------------------------------------------------------|
| `suggest_mitre`      | Suggest MITRE ATT&CK techniques matching a description or IOC |
| `get_project_memory` | Retrieve persistent project-scoped memory entries             |

---

## Scope Layers — `layers.py` (2 tools, live)

| Tool              | Description                                             |
|-------------------|---------------------------------------------------------|
| `share_to_layers` | Write a value to a scope layer (session/project/global) |
| `get_layer_value` | Read a value from a scope layer                         |

---

## Cache — `cache.py` (4 tools, live)

| Tool               | Description                                  |
|--------------------|----------------------------------------------|
| `cache_lookup`     | Look up a cached response by key             |
| `cache_store`      | Store a value in the cache with optional TTL |
| `cache_analytics`  | Return cache hit/miss statistics             |
| `cache_invalidate` | Invalidate cache entries by key or pattern   |

---

## AI Proxy — `proxy.py` (10 tools, live)

Backed by `src/ai_proxy/`. Real multi-provider routing.

| Tool                   | Description                                                            |
|------------------------|------------------------------------------------------------------------|
| `proxy_chat`           | Route a chat completion with multi-provider fallback                   |
| `proxy_providers`      | List all configured AI providers with status and rate limits           |
| `proxy_models`         | List all available models, optionally filtered by provider             |
| `proxy_usage`          | Token and cost usage summary by provider                               |
| `proxy_cost`           | Detailed cost breakdown by provider                                    |
| `simulate_route`       | Dry-run routing simulation — shows selected provider without executing |
| `set_budget_guard`     | Set session-level spending budget for a combo or tier key              |
| `get_circuit_breakers` | Return circuit breaker states for all routing targets                  |
| `explain_route`        | Step-by-step explanation of provider selection for a model             |
| `routing_strategies`   | List all available routing strategies                                  |

---

## Session — `session.py` (3 tools, live)

Backed by `src/ai_proxy/` and `src/a2a/`.

| Tool               | Description                                                 |
|--------------------|-------------------------------------------------------------|
| `session_snapshot` | Full snapshot: providers, circuit breakers, usage, budget   |
| `agent_registry`   | List all registered A2A agents with status and capabilities |
| `best_provider`    | Recommend the best provider for a given request type        |

---

## Cases — `cases.py` (2 tools, live)

| Tool          | Description                        |
|---------------|------------------------------------|
| `case_open`   | Open a new investigation case      |
| `case_status` | Get status and findings for a case |

---

## PoC Intel — `poc.py` (2 tools, live)

| Tool         | Description                                                |
|--------------|------------------------------------------------------------|
| `add_poc`    | Add a proof-of-concept record (exploit, technique, sample) |
| `query_pocs` | Query PoC records by CVE, technique, or keyword            |

---

## Quota & Pricing — `quo_pricing.py` (3 tools, live)

Backed by `ai_proxy.services.usage_tracker` and `ai_proxy.providers.registry`.

| Tool                  | Description                                                       |
|-----------------------|-------------------------------------------------------------------|
| `check_quota`         | Check rate limit and budget quota for a provider or all providers |
| `cost_report`         | Cost breakdown by provider with recent request history            |
| `list_models_catalog` | Full model catalog with context window and pricing                |

---

## AI Memory — `ai_memory.py` (3 tools, live)

Backed by filesystem memory store (`~/.cybersecsuite/memory/`).

| Tool            | Description                               |
|-----------------|-------------------------------------------|
| `memory_search` | Search memory entries by type and content |
| `memory_add`    | Store a new memory entry                  |
| `memory_clear`  | Clear memory entries by type and/or age   |

---

## Web Search — `web_search.py` (1 tool, live)

Routes to first available engine from `PERPLEXITY_API_KEY`, `SERPER_API_KEY`, `BRAVE_API_KEY`, `TAVILY_API_KEY`.

| Tool         | Description                                                         |
|--------------|---------------------------------------------------------------------|
| `web_search` | Web search via Perplexity/Serper/Brave/Tavily — title, URL, snippet |

---

## Sync — `sync.py` (1 tool, live)

Reloads provider and pricing config from `~/.cybersecsuite/providers.yaml` or `CYBERSEC_PROVIDERS_CONFIG`.

| Tool           | Description                                                  |
|----------------|--------------------------------------------------------------|
| `sync_pricing` | Reload provider pricing and config from disk; returns count  |

---

## Health — `health.py` (3 tools, live)

Backed by `ai_proxy.providers.registry`, `ai_proxy.routing.combo`, `ai_proxy.services.*`.

| Tool                   | Description                                       |
|------------------------|---------------------------------------------------|
| `get_health`           | System and provider health summary                |
| `get_provider_metrics` | Per-provider latency, success rate, usage metrics |
| `get_session_snapshot` | Full session: cost, tokens, recent requests       |

---

## Template — `template.py` (1 tool, live)

| Tool              | Description                                         |
|-------------------|-----------------------------------------------------|
| `render_template` | Render a named Jinja2 template with extra variables |

---

## Skill Manager — `skill_manager.py` (3 tools, live)

Backed by `template_engine.discovery`.

| Tool           | Description                                |
|----------------|--------------------------------------------|
| `skill_list`   | List available skills from the registry    |
| `skill_search` | Search skills by name or keyword           |
| `skill_load`   | Load and return a skill definition by name |

---

## Vault — `vault_tool.py` (5 tools, live)

Backed by `src/memory/vault/`.

| Tool             | Description                                      |
|------------------|--------------------------------------------------|
| `vault_scaffold` | Create vault directory structure                 |
| `vault_status`   | Return vault health and page counts              |
| `vault_ingest`   | Ingest a source (file or URL) into the vault     |
| `vault_query`    | Query vault knowledge base                       |
| `vault_lint`     | Run vault health check: orphan pages, dead links |

---

## Canvas — `canvas_tool.py` (6 tools, live)

Backed by `src/memory/canvas/`.

| Tool                | Description                              |
|---------------------|------------------------------------------|
| `canvas_create`     | Create a new Obsidian canvas file        |
| `canvas_list`       | List all canvas files                    |
| `canvas_layout`     | Render a canvas with an archetype layout |
| `canvas_add_node`   | Add a node to an existing canvas         |
| `canvas_validate`   | Validate canvas JSON structure           |
| `canvas_archetypes` | List all available canvas archetypes     |

---

## Tool Toggles — `tool_toggles.py` (4 tools, live)

Backed by `~/.cybersecsuite/tool_toggles.json`.

| Tool                | Description                             |
|---------------------|-----------------------------------------|
| `tool_toggle_set`   | Enable or disable a tool by scope       |
| `tool_toggle_get`   | Get the active/disabled state of a tool |
| `tool_toggle_list`  | List all tool toggle states             |
| `tool_toggle_clear` | Reset tool toggles for a scope          |

---

## Structured Extract — `structured_extract.py` (2 tools, live)

Backed by Pydantic v2 + Anthropic SDK.

| Tool                        | Description                                                     |
|-----------------------------|-----------------------------------------------------------------|
| `structured_extract`        | Extract typed forensic entities from text using Pydantic schema |
| `structured_extract_stream` | Streaming version of structured extraction                      |

---

## Thinking Tool — `thinking_tool.py` (2 tools, live)

Backed by Anthropic extended thinking API.

| Tool                   | Description                                               |
|------------------------|-----------------------------------------------------------|
| `invoke_with_thinking` | Run a query with extended Claude thinking (budget tokens) |
| `thinking_stream`      | Streaming version with thinking visible in output         |

---

## Tool Search — `tool_search.py` (3 tools, live)

Backed by introspecting `_ALL_CYBERSEC_TOOLS` + dystopian tools at runtime.

| Tool                   | Description                                        |
|------------------------|----------------------------------------------------|
| `search_tools`         | Search registered MCP tools by name or description |
| `list_tool_categories` | List all tool categories/modules                   |
| `describe_tool`        | Get full description and schema for a tool by name |

---

## Agents Beta — `agents_beta.py` (10 tools, live)

Backed by Anthropic SDK agent patterns.

| Tool                         | Description                            |
|------------------------------|----------------------------------------|
| `agent_env_create`           | Create an isolated agent environment   |
| `agent_vault_create`         | Create a credential vault for an agent |
| `agent_vault_add_credential` | Add a credential to an agent vault     |
| `agent_skill_upload`         | Upload a skill definition to an agent  |
| `agent_remote_create`        | Register a remote agent endpoint       |
| `agent_remote_add_skills`    | Add skills to a remote agent           |
| `agent_versions_list`        | List agent versions                    |
| `agent_session_create`       | Create a new agent session             |
| `agent_session_run`          | Run a query inside an agent session    |
| `agent_file_upload`          | Upload a file into an agent context    |

---

## QoL Output Controls — `qol_tools.py` (4 tools, live)

Server-side injection of output-behaviour directives into every LLM request.
State persisted to `~/.cybersecsuite/data/qol.json`.

| Tool           | Description                                                          |
|----------------|----------------------------------------------------------------------|
| `qol_get`      | Get current QoL settings + token estimate for a scope               |
| `qol_set`      | Enable/disable toggles or load a named preset                        |
| `qol_reset`    | Reset all toggles for a scope back to defaults                       |
| `qol_presets`  | List all available presets (builtin: silent, code-only, structured, audit, plain-text) |

**Toggles:** `no_thinking`, `no_chat`, `minimal`, `file_only`, `no_markdown`, `structured_only`, `redact_secrets`, `append_audit_trail`

**Dashboard:** `GET|POST|DELETE /api/qol`, `GET /api/qol/presets`, `POST /api/qol/presets/{name}`

---
