"""Dashboard API package — re-exports all handler functions."""

from dashboard.api.core import (
    api_overview,
    api_providers,
    api_usage,
    api_health,
    api_crypto,
)
from dashboard.api.agents import (
    api_a2a,
    api_agents,
    api_routing,
    api_agent_factory,
    api_agent_query,
)
from dashboard.api.forensic import (
    api_findings,
    api_iocs,
    api_yara,
    api_network,
    api_intelligence,
    api_audit,
    api_compliance,
    api_nist_csf,
    api_nist_ai_rmf,
)
from dashboard.api.ops import (
    api_cases,
    api_tasks,
    api_task_cancel,
    api_task_create,
    api_task_get,
    api_pocs,
)
from dashboard.api.tables import (
    api_db_counts,
    api_investigations,
    api_models,
    api_table,
    api_prompts,
    api_telemetry,
)
from dashboard.api.sse import (
    sse_cases,
    sse_tasks,
    sse_health,
    sse_telemetry,
)
from dashboard.api.settings import api_settings_get, api_settings_patch
from dashboard.api.team_builder import api_team_agents, api_skills, api_teams, api_team_create, api_team_update, api_team_delete, api_team_get
from dashboard.api.opensearch_stats import api_opensearch
from dashboard.api.page import dashboard_page
from dashboard.api.agent_crud import api_agent_create, api_agent_update, api_agent_delete, api_agent_get
from dashboard.api.workflows import api_workflow_create, api_workflow_list, api_workflow_get, api_workflow_cancel

__all__ = [
    # core
    "api_overview",
    "api_providers",
    "api_usage",
    "api_health",
    "api_crypto",
    # agents
    "api_a2a",
    "api_agents",
    "api_routing",
    "api_agent_factory",
    "api_agent_query",
    # forensic
    "api_findings",
    "api_iocs",
    "api_yara",
    "api_network",
    "api_intelligence",
    "api_audit",
    "api_compliance",
    "api_nist_csf",
    "api_nist_ai_rmf",
    # ops
    "api_cases",
    "api_tasks",
    "api_task_cancel",
    "api_task_create",
    "api_task_get",
    "api_pocs",
    # tables
    "api_db_counts",
    "api_investigations",
    "api_models",
    "api_table",
    "api_prompts",
    "api_telemetry",
    # sse
    "sse_cases",
    "sse_tasks",
    "sse_health",
    "sse_telemetry",
    # settings
    "api_settings_get",
    "api_settings_patch",
    # team builder
    "api_team_agents",
    "api_skills",
    "api_teams",
    "api_team_create",
    "api_team_update",
    "api_team_delete",
    "api_team_get",
    # agent crud
    "api_agent_create",
    "api_agent_update",
    "api_agent_delete",
    "api_agent_get",
    # workflows
    "api_workflow_create",
    "api_workflow_list",
    "api_workflow_get",
    "api_workflow_cancel",
    # opensearch
    "api_opensearch",
    # page
    "dashboard_page",
]
