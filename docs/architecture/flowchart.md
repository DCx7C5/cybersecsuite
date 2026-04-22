# CyberSecSuite — Full Architecture Flowchart

All 19 layers from external clients down to infrastructure.

```mermaid
flowchart TD

%% ─────────────────────────────────────────────────────────────
%% LAYER 0 — External Clients
%% ─────────────────────────────────────────────────────────────
subgraph L0["Layer 0 — External Clients"]
    BP["🔌 Browser Plugin\nsrc/browser-plugin/\nbackground.js · content.js · popup\nStorage key: css_cfg"]
    CC["🖥 Claude Code / OpenAI-compat clients\ncurl · SDK · third-party\nANTHROPIC_BASE_URL=localhost:8000"]
    TSNODE["⚙ TypeScript Agent Node\nsrc/agent_ts/index.ts\nHook runner process"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 1 — ASGI Entry
%% ─────────────────────────────────────────────────────────────
subgraph L1["Layer 1 — ASGI Entry · src/proxy/asgi.py · :8000"]
    PROXY_V1["POST /v1/* → AI Proxy"]
    PROXY_API["GET /api/* → Dashboard REST"]
    PROXY_SSE["GET /sse/* → SSE Stream"]
    PROXY_A2A["GET /a2a/* → A2A Protocol"]
    PROXY_DASH["GET / → Dashboard HTML"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 2 — AI Proxy
%% ─────────────────────────────────────────────────────────────
subgraph L2["Layer 2 — AI Proxy · src/ai_proxy/"]
    PROXYROUTES["routes.py\nRequest intake + response dispatch"]
    subgraph QOL["qol_controls/"]
        QOLMGR["manager.py\nOutput-control injection\nscope cascade: session → project"]
        QOLPROMPTS["prompts.py · models.py"]
    end
    subgraph ROUTING["routing/combo.py — 13 Strategies"]
        STRAT["priority · round-robin · cost-optimized\nweighted · random · least-used\nfill-first · p2c · strict-random\nauto · lkgp · context-optimized · context-relay"]
        CB["Circuit Breaker / Budget Guard"]
    end
    subgraph TRANS["translators/core.py"]
        FMT["OpenAI ↔ Anthropic ↔ Gemini\nformat translation"]
    end
    subgraph EXEC["executors/"]
        EX_ANTHROPIC["anthropic_sdk.py"]
        EX_BEDROCK["bedrock.py"]
        EX_FOUNDRY["foundry.py"]
        EX_VERTEX["vertex.py"]
        EX_PLAYWRIGHT["playwright.py"]
    end
    subgraph SRVCS["services/"]
        RATELIM["rate_limiter.py\nToken-bucket RPM/TPM per provider"]
        TOKCNT["token_counter.py\nPre-flight token estimation"]
        USAGETRK["usage_tracker.py\nIn-memory cost + latency log"]
    end
    PROVIDERS["providers/registry.py\n60 provider configs\n(ApiFormat · AuthType · ProviderConfig)"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 3 — A2A Protocol
%% ─────────────────────────────────────────────────────────────
subgraph L3["Layer 3 — A2A Protocol · src/a2a/"]
    A2ASERVER["server.py\nHTTP A2A task handler"]
    CYBAGENT["cybersec_agent.py\nCybersecA2AAgent\nCVE · IOC · MITRE · artifact signing"]
    AGENTSDK["agent_sdk.py\nbuild_agent_options()\nrun_agent_query()\nrun_agent_stream_with_memory()\nSession continuity · _session_out dict"]
    AGENTREG["registry.py\nRemoteAgent discovery by skill\nLoads .claude/agents/*.md"]
    TASKSTORE["task_store.py\nIn-memory task lifecycle"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 4 — Claude Agent SDK (external)
%% ─────────────────────────────────────────────────────────────
subgraph L4["Layer 4 — claude_agent_sdk (external package)"]
    SDK_QUERY["query()\nMulti-turn conversation engine"]
    SDK_OPTS["ClaudeAgentOptions\nAgentDefinition · HookMatcher"]
    SDK_MSGS["SystemMessage · AssistantMessage\nResultMessage · TextBlock\nToolUseBlock · ToolResultBlock"]
    SDK_MEM["BetaLocalFilesystemMemoryTool\ntool_runner"]
    AGENTDEFS[".claude/agents/*.md\n33 specialist agent definitions\ncybersec-agent (orchestrator)\n+ 32 domain specialists"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 5 — Agent Runner
%% ─────────────────────────────────────────────────────────────
subgraph L5["Layer 5 — Agent Runner · src/agent/"]
    RUNNER["runner.py · AgentRunner\nMulti-turn ClaudeSDKClient wrapper\nmode: blue/red/purple"]
    CPOOL["client_pool.py\nPool of SDK clients"]
    STREAMING["streaming.py\nSSE adapter\ntext · tool_use · tool_result · result · error"]
    SESSLINK["session_linking.py\nDB sessions ↔ SDK session IDs"]
    SESSIONS["sessions.py\nSession management"]
    OPTSMGR["options_manager.py\nAgent option builder"]
    AGENTHOOKS["hooks.py\nHook registration helpers"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 6 — MCP Server
%% ─────────────────────────────────────────────────────────────
subgraph L6["Layer 6 — MCP Server · src/csmcp/"]
    SDKCOMPAT["_sdk_compat.py\n@tool decorator · SdkMcpServer shim\nReal SDK or lightweight fallback"]
    MCPSERVER["cybersec/server.py\nmcp.server.Server stdio bridge\n(Claude Code mcp.json)"]
    subgraph CYBERTOOLS["cybersec/ — 56 tools"]
        T_FINDINGS["findings.py\nadd_finding · add_ioc · query_findings · update_risk_register"]
        T_PROXY["proxy.py\nproxy_chat · proxy_providers · proxy_models\nproxy_usage · proxy_cost · simulate_route\nset_budget_guard · get_circuit_breakers\nexplain_route · routing_strategies"]
        T_ROUTING["(routing)\ncombo_list · combo_metrics · combo_switch\ncombo_test · route_request · set_routing_strategy\nset_resilience_profile · best_combo_for_task"]
        T_CACHE["cache.py\ncache_lookup · cache_store\ncache_analytics · cache_invalidate"]
        T_SESSION["session.py\nsession_snapshot · agent_registry · best_provider"]
        T_CASES["cases.py\ncase_open · case_status"]
        T_POC["poc.py\nadd_poc · query_pocs"]
        T_DB["db.py\ndb_healthcheck · bootstrap_intelligence"]
        T_INTEL["intelligence.py\nsuggest_mitre · get_project_memory"]
        T_LAYERS["layers.py\nshare_to_layers · get_layer_value"]
        T_MEM["ai_memory.py\nmemory_search · memory_add · memory_clear"]
        T_QOL["qol_tools.py\nqol_get · qol_set · qol_reset · qol_presets"]
        T_SYNC["sync.py\nsync_pricing"]
        T_HEALTH["health.py\nget_health · get_provider_metrics · get_session_snapshot"]
        T_WEBSEARCH["web_search.py\nweb_search"]
        T_QUOTA["quo_pricing.py\ncheck_quota · cost_report · list_models_catalog"]
        T_CANVAS["canvas_tool.py · vault_tool.py\ntemplate.py · thinking_tool.py\ntool_search.py · tool_toggles.py\nskill_manager.py · structured_extract.py\nplaywright_tool.py · agents_beta.py"]
    end
    subgraph DYSTO["dystopian — 5 tools"]
        T_CRYPTO["dystopian.py\ncrypto_generate_keypair · crypto_sign_artifact\ncrypto_verify_artifact · crypto_list_keys\ncrypto_rotate_key"]
        DYSTOSERVER["dystopian_server.py\nmcp stdio bridge"]
    end
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 7 — Hooks
%% ─────────────────────────────────────────────────────────────
subgraph L7["Layer 7 — Hooks"]
    subgraph PYHOOKS["src/hooks/ (Python)"]
        SDKHOOKS["sdk_hooks.py\nHookMatcher — audit + path safety\nwrites hooks/audit.jsonl"]
        IPCRECV["ipc_receiver.py\nUnix socket /tmp/cybersecsuite-hooks.sock\nReceives JSON lines from TypeScript"]
        SESSSTART["session_start.py · session_end.py"]
        ROOTCMD["root_command_executed.py\nuser_prompt_submit.py · threat_detected.py\ntermmate_idle.py"]
        YARA["yara_rule_generator.py\nyara_rule_optimizer.py\nyara_rule_tester.py"]
    end
    subgraph TSHOOKS["src/agent_ts/hooks/ (TypeScript)"]
        CSS_SETUP["css_first_setup.ts\nOne-time setup sentinel\nruns make css-first-setup"]
        TS_CONFIG["config.ts · setup.ts"]
        TS_SESSION["session.ts"]
        TS_TASKS["tasks.ts · team.ts"]
    end
    IPC_BRIDGE["src/agent_ts/ipc.ts\nTypeScript → Unix socket → Python IPC bridge"]
    CLAUDEHOOKS[".claude/hooks/\npost-tool-call.py\nroot_commands.jsonl · violations.jsonl · audit.jsonl"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 8 — Dashboard
%% ─────────────────────────────────────────────────────────────
subgraph L8["Layer 8 — Dashboard · src/dashboard/ + src/ts_api/ + src/frontend/"]
    DASHROUTES["routes.py\nStarlette route mounting"]
    subgraph DASHAPI["api/ — 40+ REST handlers"]
        API_CORE["core.py · forensic.py · charts.py · agents.py"]
        API_AGENT["agent_crud.py · agent_stream.py · a2a_crud.py"]
        API_OO["openobserve_stats.py\nOO stream doc_num + storage_size"]
        API_SSE["sse.py\nSSE event stream"]
        API_TSPROXY["ts_proxy.py\nProxy → ts_api Node server"]
        API_MISC["bootstrap.py · intel_sources.py · marketplace.py\nmemory_chat.py · vault_status.py · workflows.py\naccounts.py · settings.py · settings_toggles.py\nqol.py · projects.py · page.py · plugin.py\nprompts_crud.py · sdk_options.py · sdk_session.py\nsdk_tool.py · ops.py · tables.py · team_builder.py\ntemplate_registry.py · flowgraph.py · dbus.py"]
    end
    subgraph DASHTPL["templates/ (Jinja2)"]
        TPL_BASE["_base.py · _components.py · _panels.py\n_tabs.py · _bootstrap_modal.py\njinja_env.py · panel_helpers.py"]
    end
    TSAPI["src/ts_api/server.ts (Node/Express)\nroutes: memory · stream · structured · thinking · tools"]
    REACT["src/frontend/ (React + Vite)\nApp.tsx · main.tsx"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 9 — SDK / Scope
%% ─────────────────────────────────────────────────────────────
subgraph L9["Layer 9 — CyberSecSuiteSDK · src/cybersecsuite/ + src/template_engine/"]
    CSSDK["CyberSecSuiteSDK\nsdk.py\nsession() · resume() · set() · render()\nset_pov() · set_mitre_tactic()"]
    CTXMOD["_context.py\nget_context() → template_engine/context.py"]
    SESSIO["_session_io.py\nsession-manifest.json · .last_session\nlatest symlink · new_session_id()"]
    subgraph TPLENG["template_engine/"]
        CTX4["context.py\n4-scope deep-merge\n~/.claude → ~/.cybersecsuite → .claude/ → .css/sessions/<id>/"]
        SCOPE["session_scope.py\nCYBERSEC_SESSION_SCOPE resolver\nproject_session_scope_dir() · project_sessions_dir()"]
        RENDERER["renderer.py\nJinja2 ChoiceLoader · _SilentUndefined\nFilters: severity_badge · mitre_format · now_utc"]
        DISCOVERY["discovery.py\nTemplate filesystem discovery"]
    end
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 10 — LLM Client
%% ─────────────────────────────────────────────────────────────
subgraph L10["Layer 10 — LLM Client · src/llm/"]
    LLMORCHESTRATOR["orchestrator.py\nopen_session() · close_session()\nLifecycle management"]
    LLMCLIENT["client.py\nAnthropic SDK thin wrapper"]
    LLMDB["db.py\nllm_sessions PG writes\ncost_report() — session totals"]
    LLMPRICING["pricing.py\nPer-model cost calculation"]
    LLMOTEL["otel.py\nOpenTelemetry integration"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 11 — Cryptography
%% ─────────────────────────────────────────────────────────────
subgraph L11["Layer 11 — Cryptography · src/crypto/"]
    SSLSIGNER["ssl_signer.py\nRSA-2048 signature gen/verify"]
    KEYMGR["key_manager.py\nPassword-protected key lifecycle\nKeyManager · PasswordManager"]
    ARTIFMGR["artifact_manager.py\nArtifact CRUD + auto-sign"]
    VAULT["vault.py\nFile-based encrypted secret storage"]
    CRYPTOCACHE["cache.py\nKey cache"]
    CRYPTOCLI["cli_integration.py\nmanage.py ssl-genkey · ssl-info · ssl-verify"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 12 — Memory
%% ─────────────────────────────────────────────────────────────
subgraph L12["Layer 12 — Memory · src/memory/"]
    subgraph MBACKENDS["backends/"]
        OBSIDIAN["obsidian.py + obsidian_async.py\nObsidian vault read/write"]
    end
    subgraph MCANVAS["canvas/"]
        CANVGEN["generator.py\nObsidian Canvas JSON generation"]
        CANVVAL["canvas_validate.py\nCanvas validation"]
    end
    subgraph MVAULT["vault/"]
        VAULTMGR["manager.py\nVault CRUD"]
        HOTCACHE["hot_cache.py\nIn-memory vault cache"]
    end
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 13 — Telemetry
%% ─────────────────────────────────────────────────────────────
subgraph L13["Layer 13 — Telemetry · src/telemetry/"]
    TELSTORE["store.py\nMetricsStore ring buffer\np50/p95/p99 percentiles"]
    TELCOLLECTOR["collector.py\nMetric aggregation"]
    TELMIDDLEWARE["middleware.py\nStarlette request timing middleware"]
    TELDECORATORS["decorators.py\n@record_latency · @track_call"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 14 — Database
%% ─────────────────────────────────────────────────────────────
subgraph L14["Layer 14 — Database · src/db/"]
    DBBOOT["bootstrap.py\nTortoise ORM init · asyncpg\nauto-create DB option"]
    subgraph DBMODELS["models/ — 41 ORM models"]
        MOD_SCOPE["scope.py · core.py · settings.py"]
        MOD_INTEL["cve.py · cve_entry.py · ioc.py · ioc_entry.py\ncwe.py · capec.py · mitre_technique.py\nmitre_actor.py · mitre_software.py\nfeed_snapshot.py · threat_intel.py\nmisp.py · opencti.py · references.py\nintel_feed_source.py"]
        MOD_FORENSIC["investigation.py · forensic.py · baselines.py\nnetwork.py · kernel.py · machine.py\nyara_rule.py · threat_profile_entry.py\nartifact.py · artifacts.py · poc.py"]
        MOD_COMPLIANCE["compliance.py · nist_csf.py · nist_ai_rmf.py\nvulnerability.py · defense.py"]
        MOD_INFRA["api_account.py · provider.py · provider_model.py\ntool_registry.py · llm_session.py\na2a_task.py · case_intake.py · layers.py\ntag.py · user_guidance.py · prompt.py"]
    end
    subgraph DBINTEL["intel/"]
        INTELBSTRAP["bootstrap.py\nIntel seeding\nOO write path (bulk_index)\n_snapshot_is_current() checksumming"]
        INTELSNAP["_snapshot.py · _loaders.py · _utils.py"]
    end
    subgraph DBSEEDS["seeds/"]
        SEEDS["mitre_full.py · capec_full.py · cwe_full.py\nnvd.py · intel_feed_sources.py"]
    end
    DBMIGRATION["migration/scope_v2.py\nScope path migration"]
    DBSHIMS["intel_loader.py\nBackwards-compat shim → db.intel"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 15 — Accounts
%% ─────────────────────────────────────────────────────────────
subgraph L15["Layer 15 — Accounts · src/accounts/"]
    ACCMGR["manager.py\nAccount CRUD"]
    ACCREG["registry.py\nProvider account registry"]
    ACCSYNC["sync.py\nAccount sync"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 16 — Marketplace
%% ─────────────────────────────────────────────────────────────
subgraph L16["Layer 16 — Marketplace · src/marketplace/"]
    MKTMODELS["models.py"]
    MKTREG["registry.py"]
    MKTSEED["seed.py"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 17 — Startup
%% ─────────────────────────────────────────────────────────────
subgraph L17["Layer 17 — Startup · src/startup/"]
    FIRSTRUN["first_run.py\nFirst-run DB init check\nSentinel file creation"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 18 — Infrastructure (Docker Compose)
%% ─────────────────────────────────────────────────────────────
subgraph L18["Layer 18 — Infrastructure · docker-compose.yml"]
    PG["🐘 PostgreSQL 16\nport 5432 · asyncpg\nTortoise ORM — 41 models"]
    REDIS["🔴 Redis\nport 6379\nSession cache"]
    OO["📊 OpenObserve\nport 5080\nStreams: audit-logs · api-usage\nllm-calls · intel-update-log"]
    OS["🔍 OpenSearch\nport 9200\nWazuh-only (not yet wired)"]
    DBUS["🔔 src/dbus/notifier.py\nD-Bus desktop notifications"]
end

%% ─────────────────────────────────────────────────────────────
%% LAYER 19 — Scripts & Tooling
%% ─────────────────────────────────────────────────────────────
subgraph L19["Layer 19 — Scripts & Tooling"]
    MANAGE["src/manage.py (shim)\n→ src/manage/__init__.py\nCLI dispatcher: schema · seed · status\ninstall · migrate-* · drop · ssl-*"]
    WTM["scripts/worktree-session-manager.py\nGit worktree + session isolation\nHook isolation per worktree"]
    FIXSKILLS["scripts/fix_skills.py\nSkill YAML normalizer"]
    MAKEFILE["Makefile\nschema · seed · serve · status\ncss-first-setup · dashboard · shell"]
end

%% ─────────────────────────────────────────────────────────────
%% CONNECTIONS — top to bottom
%% ─────────────────────────────────────────────────────────────

BP -->|"HTTP :8000"| L1
CC -->|"HTTP :8000"| L1
TSNODE -->|"spawns hooks\nIPC socket"| IPC_BRIDGE

PROXY_V1 --> PROXYROUTES
PROXY_API --> DASHROUTES
PROXY_SSE --> API_SSE
PROXY_A2A --> A2ASERVER
PROXY_DASH --> DASHTPL

PROXYROUTES --> QOL
QOL --> ROUTING
ROUTING --> TRANS
TRANS --> EXEC
EXEC --> RATELIM
EXEC --> TOKCNT
EXEC -->|"logs cost+latency"| USAGETRK
PROVIDERS --> ROUTING

A2ASERVER --> CYBAGENT
A2ASERVER --> AGENTSDK
AGENTSDK -->|"loads"| AGENTDEFS
AGENTSDK -->|"calls"| SDK_QUERY
AGENTSDK -->|"builds"| SDK_OPTS
AGENTREG --> A2ASERVER

SDK_QUERY --> RUNNER
SDK_OPTS --> RUNNER
RUNNER --> CPOOL
RUNNER --> STREAMING
RUNNER --> SESSLINK
SDK_MEM --> AGENTSDK

AGENTSDK -->|"provides all_servers()"| SDKCOMPAT
SDKCOMPAT --> MCPSERVER
SDKCOMPAT --> CYBERTOOLS
SDKCOMPAT --> DYSTO

SDKHOOKS -->|"HookMatcher callbacks"| SDK_QUERY
IPC_BRIDGE -->|"JSON lines"| IPCRECV
TSHOOKS --> IPC_BRIDGE
CLAUDEHOOKS -->|"post-tool-call"| SDKHOOKS

DASHROUTES --> DASHAPI
DASHROUTES --> DASHTPL
API_TSPROXY --> TSAPI
TSAPI -->|"memory · stream tools"| L4
REACT -->|"fetch /api/*"| DASHAPI
API_OO -->|"GET /api/{org}/{stream}"| OO

CSSDK --> CTXMOD
CSSDK --> SESSIO
CTXMOD --> CTX4
CTX4 --> SCOPE
CSSDK --> RENDERER
RENDERER --> DISCOVERY

LLMORCHESTRATOR --> LLMCLIENT
LLMORCHESTRATOR --> LLMDB
LLMCLIENT -->|"via proxy"| PROXY_V1
LLMDB --> PG
LLMPRICING --> LLMORCHESTRATOR

CYBAGENT --> ARTIFMGR
ARTIFMGR --> SSLSIGNER
ARTIFMGR --> KEYMGR
ARTIFMGR --> VAULT
T_CRYPTO --> SSLSIGNER

OBSIDIAN --> T_MEM
CANVGEN --> T_CANVAS
VAULTMGR --> T_CANVAS
HOTCACHE --> VAULTMGR

TELMIDDLEWARE --> L1
TELSTORE --> API_HEALTH["health.py"]
TELDECORATORS --> L2

DBBOOT --> PG
DBMODELS --> DBBOOT
DBINTEL -->|"bulk_index()"| OO
DBSEEDS --> DBBOOT

ACCREG --> PROVIDERS
ACCSYNC --> ACCREG

MKTREG --> T_MISC["marketplace MCP tool"]

FIRSTRUN --> DBBOOT
FIRSTRUN -->|"sentinel .css-initialized"| MAKEFILE

MANAGE -->|"schema/seed/migrate"| DBBOOT
WTM -->|"git worktree create/teardown"| L19
MAKEFILE --> MANAGE
```

---

## Layer Index

| # | Layer | Package(s) | Key responsibility |
|---|-------|------------|--------------------|
| 0 | External Clients | browser-plugin, agent_ts, external | Entry points |
| 1 | ASGI Entry | proxy/asgi.py | Route demultiplexing :8000 |
| 2 | AI Proxy | ai_proxy/ | 13 strategies, 60 providers, format translation |
| 3 | A2A Protocol | a2a/ | Agent-to-agent task protocol |
| 4 | Claude Agent SDK | claude_agent_sdk (ext) | Multi-turn query engine, 33 agent defs |
| 5 | Agent Runner | agent/ | SDK wrapper, SSE streaming, session linking |
| 6 | MCP Server | csmcp/ | 56 cybersec + 5 crypto tools via stdio/in-process |
| 7 | Hooks | hooks/, agent_ts/hooks/, .claude/hooks/ | Pre/post-tool audit, IPC bridge |
| 8 | Dashboard | dashboard/, ts_api/, frontend/ | 40+ REST, SSE, React SPA, Node API |
| 9 | SDK / Scope | cybersecsuite/, template_engine/ | 4-scope context merge, Jinja2, session I/O |
| 10 | LLM Client | llm/ | Anthropic SDK, session lifecycle, pricing, OTEL |
| 11 | Cryptography | crypto/ | RSA-2048, key vault, artifact signing |
| 12 | Memory | memory/ | Obsidian vault, Canvas gen, hot cache |
| 13 | Telemetry | telemetry/ | Ring buffer, p50/p95/p99, Starlette middleware |
| 14 | Database | db/ | 41 ORM models, intel seeding, OO write path |
| 15 | Accounts | accounts/ | Provider account CRUD + sync |
| 16 | Marketplace | marketplace/ | Plugin registry |
| 17 | Startup | startup/ | First-run init, sentinel |
| 18 | Infrastructure | docker-compose.yml | PostgreSQL, Redis, OpenObserve, OpenSearch |
| 19 | Scripts & Tooling | scripts/, Makefile, src/manage.py | CLI, worktree manager, skill fixer |
