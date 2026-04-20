"""Dashboard router — wires all handlers into Starlette routes."""

from __future__ import annotations

from starlette.routing import Mount, Route, Router, WebSocketRoute
from starlette.staticfiles import StaticFiles

from dashboard._handlers import (
    dashboard_page,
    api_overview,
    api_providers,
    api_providers_hub,
    api_usage,
    api_health,
    api_crypto,
    api_local_llm_status,
    api_local_llm_activate,
    api_a2a,
    api_investigations,
    api_db_counts,
    api_agents,
    api_routing,
    api_agent_factory,
    api_prompts,
    api_cases,
    api_tasks,
    api_task_cancel,
    api_task_create,
    api_task_get,
    api_findings,
    api_iocs,
    api_yara,
    api_network,
    api_intelligence,
    api_audit,
    api_compliance,
    api_nist_csf,
    api_nist_ai_rmf,
    api_telemetry,
    api_pocs,
    api_models,
    api_table,
    api_agent_query,
    api_agent_run_start,
    api_agent_run_cancel,
    api_opensearch,
    api_settings_get,
    api_settings_patch,
    api_settings_mcps_get,
    api_settings_mcps_patch,
    api_settings_skills_get,
    api_settings_skills_patch,
    api_settings_plugins_get,
    api_settings_plugins_patch,
    api_settings_global_get,
    api_settings_global_mcps_get,
    api_settings_global_mcps_patch,
    api_settings_global_env_get,
    api_settings_project_env_get,
    api_settings_install_mcp,
    api_settings_remove_mcp,
    api_settings_hooks_get,
    api_settings_hooks_post,
    api_settings_hooks_delete,
    api_settings_agent_templates,
    api_team_agents,
    api_skills,
    api_teams,
    api_team_create,
    api_team_update,
    api_team_delete,
    api_team_get,
    api_agent_create,
    api_agent_update,
    api_agent_delete,
    api_agent_get,
    api_agents_generate,
    api_workflow_create,
    api_workflow_list,
    api_workflow_get,
    api_workflow_cancel,
    sse_cases,
    sse_tasks,
    sse_health,
    sse_telemetry,
    sse_agent_run,
)
from dashboard._handlers import (
    api_template_registry_list,
)
from dashboard.api.template_registry import (
    api_template_create,
    api_template_delete,
)
from dashboard.api.sdk_tool import api_sdk_tool
from dashboard.api.sdk_session import api_sdk_session_last, api_sdk_session_resume
from dashboard.api.dbus import (
    api_dbus_notify,
    api_dbus_signal,
    api_dbus_status,
)
from dashboard.api.projects import (
    api_projects_list,
    api_project_create,
    api_project_get,
    api_project_update,
    api_project_delete,
)
from dashboard.api.accounts import (
    api_accounts_list,
    api_accounts_create,
    api_accounts_get,
    api_accounts_update,
    api_accounts_delete,
    api_accounts_resolve,
)
from dashboard.api.startup import (
    api_startup_status,
)
from dashboard.api.sdk_options import (
    api_sdk_options_get,
    api_sdk_options_post,
    api_sdk_options_scopes_get,
    api_sdk_options_delete,
)
from dashboard.api.bootstrap import (
    api_bootstrap_status,
    api_bootstrap_run,
    api_bootstrap_skip,
)
from dashboard.api.charts import api_charts
from dashboard.api.flowgraph import api_flowgraph_agents, api_flowgraph_execute
from dashboard.api.plugin import (
    PluginWebSocketEndpoint,
    api_plugin_status,
    api_plugin_events,
    api_plugin_broadcast,
    api_plugin_clear_events,
)
from dashboard.api.ts_proxy import ts_api_proxy


def create_dashboard_router() -> Router:
    """Create the root router (dashboard at /, API at /api/*, SSE at /sse/*)."""
    from starlette.requests import Request
    from starlette.responses import RedirectResponse

    async def redirect_to_root(request: Request) -> RedirectResponse:
        return RedirectResponse("/", status_code=308)

    return Router(
        routes=[
            Mount("/static", app=StaticFiles(directory="src/dashboard/static"), name="static"),
            Route("/dashboard", redirect_to_root, methods=["GET"]),
            Route("/dashboard/", redirect_to_root, methods=["GET"]),
            Route("/", dashboard_page, methods=["GET"]),
            Route("/api/overview", api_overview, methods=["GET"]),
            Route("/api/providers", api_providers, methods=["GET"]),
            Route("/api/providers/hub", api_providers_hub, methods=["GET"]),
            Route("/api/usage", api_usage, methods=["GET"]),
            Route("/api/health", api_health, methods=["GET"]),
            Route("/api/crypto", api_crypto, methods=["GET"]),
            Route("/api/a2a", api_a2a, methods=["GET"]),
            Route("/api/investigations", api_investigations, methods=["GET"]),
            Route("/api/db-counts", api_db_counts, methods=["GET"]),
            Route("/api/agents", api_agents, methods=["GET"]),
            Route("/api/routing", api_routing, methods=["GET"]),
            Route("/api/agent-factory", api_agent_factory, methods=["GET"]),
            Route("/api/prompts", api_prompts, methods=["GET"]),
            # Specific domain endpoints (summaries + recent full-field rows)
            Route("/api/cases", api_cases, methods=["GET"]),
            Route("/api/tasks", api_tasks, methods=["GET"]),
            Route("/api/tasks/{task_id}/cancel", api_task_cancel, methods=["POST"]),
            Route("/api/findings", api_findings, methods=["GET"]),
            Route("/api/iocs", api_iocs, methods=["GET"]),
            Route("/api/yara", api_yara, methods=["GET"]),
            Route("/api/network", api_network, methods=["GET"]),
            Route("/api/intelligence", api_intelligence, methods=["GET"]),
            Route("/api/audit", api_audit, methods=["GET"]),
            Route("/api/compliance", api_compliance, methods=["GET"]),
            Route("/api/nist-csf", api_nist_csf, methods=["GET"]),
            Route("/api/nist-ai-rmf", api_nist_ai_rmf, methods=["GET"]),
            Route("/api/telemetry", api_telemetry, methods=["GET"]),
            Route("/api/pocs", api_pocs, methods=["GET"]),
            Route("/api/tasks/create", api_task_create, methods=["POST"]),
            Route("/api/tasks/{task_id}", api_task_get, methods=["GET"]),
            # Generic model table endpoint — all 82+ Tortoise models
            Route("/api/models", api_models, methods=["GET"]),
            Route("/api/tables/{model}", api_table, methods=["GET"]),
            # Agent-SDK query endpoint
            Route("/api/agent-query", api_agent_query, methods=["POST"]),
            Route("/api/agent-run", api_agent_run_start, methods=["POST"]),
            Route("/api/agent-run/{task_id}", api_agent_run_cancel, methods=["DELETE"]),
            Route("/api/settings", api_settings_get, methods=["GET"]),
            Route("/api/settings", api_settings_patch, methods=["PATCH"]),
            Route("/api/settings/mcps", api_settings_mcps_get, methods=["GET"]),
            Route("/api/settings/mcps", api_settings_mcps_patch, methods=["PATCH"]),
            Route("/api/settings/skills", api_settings_skills_get, methods=["GET"]),
            Route("/api/settings/skills", api_settings_skills_patch, methods=["PATCH"]),
            Route("/api/settings/plugins", api_settings_plugins_get, methods=["GET"]),
            Route("/api/settings/plugins", api_settings_plugins_patch, methods=["PATCH"]),
            Route("/api/settings/global", api_settings_global_get, methods=["GET"]),
            Route("/api/settings/global-mcps", api_settings_global_mcps_get, methods=["GET"]),
            Route("/api/settings/global-mcps", api_settings_global_mcps_patch, methods=["PATCH"]),
            Route("/api/settings/global-env", api_settings_global_env_get, methods=["GET"]),
            Route("/api/settings/project-env", api_settings_project_env_get, methods=["GET"]),
            Route("/api/settings/install-mcp", api_settings_install_mcp, methods=["POST"]),
            Route("/api/settings/remove-mcp", api_settings_remove_mcp, methods=["DELETE"]),
            Route("/api/settings/hooks", api_settings_hooks_get, methods=["GET"]),
            Route("/api/settings/hooks", api_settings_hooks_post, methods=["POST"]),
            Route("/api/settings/hooks", api_settings_hooks_delete, methods=["DELETE"]),
            Route("/api/settings/agent-agents", api_settings_agent_templates, methods=["GET"]),
            Route("/api/team-agents", api_team_agents, methods=["GET"]),
            Route("/api/skills", api_skills, methods=["GET"]),
            Route("/api/teams", api_teams, methods=["GET"]),
            Route("/api/teams", api_team_create, methods=["POST"]),
            Route("/api/teams/{name}", api_team_get, methods=["GET"]),
            Route("/api/teams/{name}", api_team_update, methods=["PUT"]),
            Route("/api/teams/{name}", api_team_delete, methods=["DELETE"]),
            # Agent CRUD
            Route("/api/agents/crud", api_agent_create, methods=["POST"]),
            Route("/api/agents/generate", api_agents_generate, methods=["POST"]),
            Route("/api/agents/crud/{name}", api_agent_get, methods=["GET"]),
            Route("/api/agents/crud/{name}", api_agent_update, methods=["PUT"]),
            Route("/api/agents/crud/{name}", api_agent_delete, methods=["DELETE"]),
            # Workflows
            Route("/api/workflows", api_workflow_list, methods=["GET"]),
            Route("/api/workflows", api_workflow_create, methods=["POST"]),
            Route("/api/workflows/{id}", api_workflow_get, methods=["GET"]),
            Route("/api/workflows/{id}", api_workflow_cancel, methods=["DELETE"]),
            Route("/api/opensearch", api_opensearch, methods=["GET"]),
            # Local LLM
            Route("/api/local-llm/status", api_local_llm_status, methods=["GET"]),
            Route("/api/local-llm/activate", api_local_llm_activate, methods=["POST"]),
            # DBus notifications
            Route("/api/dbus/notify", api_dbus_notify, methods=["POST"]),
            Route("/api/dbus/signal", api_dbus_signal, methods=["POST"]),
            Route("/api/dbus/status", api_dbus_status, methods=["GET"]),
            # Accounts API
            Route("/api/accounts", api_accounts_list, methods=["GET"]),
            Route("/api/accounts", api_accounts_create, methods=["POST"]),
            Route("/api/accounts/{vault_key}", api_accounts_get, methods=["GET"]),
            Route("/api/accounts/{vault_key}", api_accounts_update, methods=["PUT"]),
            Route("/api/accounts/{vault_key}", api_accounts_delete, methods=["DELETE"]),
            Route("/api/accounts/resolve", api_accounts_resolve, methods=["GET"]),
            # Projects CRUD
            Route("/api/projects", api_projects_list, methods=["GET"]),
            Route("/api/projects", api_project_create, methods=["POST"]),
            Route("/api/projects/{id}", api_project_get, methods=["GET"]),
            Route("/api/projects/{id}", api_project_update, methods=["PATCH"]),
            Route("/api/projects/{id}", api_project_delete, methods=["DELETE"]),
            Route("/api/templates", api_template_registry_list, methods=["GET"]),
            Route("/api/templates", api_template_create, methods=["POST"]),
            Route("/api/templates", api_template_delete, methods=["DELETE"]),
            # Startup status
            Route("/api/startup/status", api_startup_status, methods=["GET"]),
            # SDK Options
            Route("/api/sdk/options", api_sdk_options_get, methods=["GET"]),
            Route("/api/sdk/options", api_sdk_options_post, methods=["POST"]),
            Route("/api/sdk/options/scopes", api_sdk_options_scopes_get, methods=["GET"]),
            Route("/api/sdk/options", api_sdk_options_delete, methods=["DELETE"]),
            # SDK Tool
            Route("/api/sdk-tool", api_sdk_tool, methods=["POST"]),
            # SDK Session
            Route("/api/sdk/session/last", api_sdk_session_last, methods=["GET"]),
            Route("/api/sdk/session/resume", api_sdk_session_resume, methods=["POST"]),
            # Bootstrap (first-run)
            Route("/api/bootstrap/status", api_bootstrap_status, methods=["GET"]),
            Route("/api/bootstrap/run", api_bootstrap_run, methods=["POST"]),
            Route("/api/bootstrap/skip", api_bootstrap_skip, methods=["POST"]),
            # Charts data API
            Route("/api/charts/{name}", api_charts, methods=["GET"]),
            # Flowgraph API
            Route("/api/flowgraph/agents", api_flowgraph_agents, methods=["GET"]),
            Route("/api/flowgraph/execute", api_flowgraph_execute, methods=["POST"]),
            # Browser plugin WS/API
            WebSocketRoute("/ws", PluginWebSocketEndpoint),
            WebSocketRoute("/api/plugin/ws", PluginWebSocketEndpoint),
            Route("/api/plugin/status", api_plugin_status, methods=["GET"]),
            Route("/api/plugin/events", api_plugin_events, methods=["GET"]),
            Route("/api/plugin/broadcast", api_plugin_broadcast, methods=["POST"]),
            Route("/api/plugin/events/clear", api_plugin_clear_events, methods=["POST"]),
            # TypeScript SDK API proxy — proxies /ts/* → http://127.0.0.1:8765/ts/*
            Mount("/ts", app=ts_api_proxy),
            # SSE streaming endpoints
            Route("/sse/cases", sse_cases, methods=["GET"]),
            Route("/sse/tasks", sse_tasks, methods=["GET"]),
            Route("/sse/health", sse_health, methods=["GET"]),
            Route("/sse/telemetry", sse_telemetry, methods=["GET"]),
            Route("/sse/agent-run/{task_id}", sse_agent_run, methods=["GET"]),
        ]
    )
