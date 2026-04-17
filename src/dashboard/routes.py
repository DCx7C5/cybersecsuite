"""Dashboard router — wires all handlers into Starlette routes."""
from __future__ import annotations

from starlette.routing import Route, Router

from dashboard._handlers import (
    dashboard_page,
    api_overview, api_providers, api_usage, api_health,
    api_crypto, api_a2a, api_investigations, api_db_counts,
    api_agents, api_routing, api_agent_factory, api_prompts,
    api_cases, api_tasks, api_task_cancel, api_task_create, api_task_get,
    api_findings, api_iocs, api_yara, api_network,
    api_intelligence, api_audit, api_compliance,
    api_nist_csf, api_nist_ai_rmf, api_telemetry, api_pocs,
    api_models, api_table, api_agent_query,
    sse_cases, sse_tasks, sse_health, sse_telemetry,
)

def create_dashboard_router() -> Router:
    """Create the /dashboard router."""
    return Router(routes=[
        Route("/", dashboard_page, methods=["GET"]),
        Route("/api/overview", api_overview, methods=["GET"]),
        Route("/api/providers", api_providers, methods=["GET"]),
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
        # SSE streaming endpoints
        Route("/sse/cases", sse_cases, methods=["GET"]),
        Route("/sse/tasks", sse_tasks, methods=["GET"]),
        Route("/sse/health", sse_health, methods=["GET"]),
        Route("/sse/telemetry", sse_telemetry, methods=["GET"]),
    ])

