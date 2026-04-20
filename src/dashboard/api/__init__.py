"""Dashboard API package — re-exports all handler functions."""

from dashboard.api.core import (
    api_overview,
    api_providers,
    api_usage,
    api_health,
    api_crypto,
    api_local_llm_status,
    api_local_llm_activate,
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
from dashboard.api.agent_stream import (
    api_agent_run_start,
    sse_agent_run,
    api_agent_run_cancel,
)
from dashboard.api.settings import api_settings_get, api_settings_patch
from dashboard.api.settings_toggles import (
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
)
from dashboard.api.team_builder import api_team_agents, api_skills, api_teams, api_team_create, api_team_update, api_team_delete, api_team_get
from dashboard.api.opensearch_stats import api_opensearch
from dashboard.api.page import dashboard_page
from dashboard.api.agent_crud import api_agent_create, api_agent_update, api_agent_delete, api_agent_get, api_agents_generate
from dashboard.api.workflows import api_workflow_create, api_workflow_list, api_workflow_get, api_workflow_cancel
from dashboard.api.projects import (
    api_projects_list,
    api_project_create,
    api_project_get,
    api_project_update,
    api_project_delete,
)
from dashboard.api.template_registry import api_template_registry_list
from dashboard.api.sdk_options import (
    api_sdk_options_get,
    api_sdk_options_post,
    api_sdk_options_scopes_get,
    api_sdk_options_delete,
)

__all__ = [
    # core
    "api_overview",
    "api_providers",
    "api_usage",
    "api_health",
    "api_crypto",
    "api_local_llm_status",
    "api_local_llm_activate",
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
    "api_agent_run_start",
    "api_agent_run_cancel",
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
    "sse_agent_run",
    # settings
    "api_settings_get",
    "api_settings_patch",
    # settings toggles
    "api_settings_mcps_get",
    "api_settings_mcps_patch",
    "api_settings_skills_get",
    "api_settings_skills_patch",
    "api_settings_plugins_get",
    "api_settings_plugins_patch",
    "api_settings_global_get",
    "api_settings_global_mcps_get",
    "api_settings_global_mcps_patch",
    "api_settings_global_env_get",
    "api_settings_project_env_get",
    "api_settings_install_mcp",
    "api_settings_remove_mcp",
    "api_settings_hooks_get",
    "api_settings_hooks_post",
    "api_settings_hooks_delete",
    "api_settings_agent_templates",
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
    "api_agents_generate",
    # workflows
    "api_workflow_create",
    "api_workflow_list",
    "api_workflow_get",
    "api_workflow_cancel",
    # opensearch
    "api_opensearch",
    # page
    "dashboard_page",
    # projects
    "api_projects_list",
    "api_project_create",
    "api_project_get",
    "api_project_update",
    "api_project_delete",
    # templates
    "api_template_registry_list",
    # sdk options
    "api_sdk_options_get",
    "api_sdk_options_post",
    "api_sdk_options_scopes_get",
    "api_sdk_options_delete",
]
