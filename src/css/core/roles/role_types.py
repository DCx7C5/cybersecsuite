"""Orchestration-specific roles: Orchestrator, TeamLeader, TeamMember/Worker.

These roles define capabilities, permissions, and heartbeat requirements for
the orchestration architecture (process-level and in-process roles).
"""
import msgspec

class OrchestrationRole(msgspec.Struct, tag=True):
    """Base class for orchestration-specific roles (not tied to system-wide roles)."""

    role_id: str
    name: str
    description: str
    permissions: list[str] = msgspec.field(default_factory=list)
    capabilities: dict[str, bool] = msgspec.field(default_factory=dict)
    heartbeat_timeout_seconds: int = 30
    can_pause_team: bool = False
    can_delegate: bool = False
    can_execute_tasks: bool = False

class OrchestratorRole(OrchestrationRole):
    """Orchestrator: process-level coordinator — spawns sub-processes, monitors heartbeat."""

    role_id: str = "orchestrator"
    name: str = "Orchestrator"
    description: str = (
        "Process-level coordinator — spawns orchestrator instances, "
        "monitors team heartbeat, detects crashes, triggers recovery."
    )
    permissions: list[str] = msgspec.field(
        default_factory=lambda: [
            "orchestrator:spawn",
            "orchestrator:kill",
            "team:monitor",
            "team:pause",
            "team:resume",
            "heartbeat:check",
            "crash:recover",
        ]
    )
    capabilities: dict[str, bool] = msgspec.field(
        default_factory=lambda: {
            "can_spawn_orchestrators": True,
            "can_monitor_health": True,
            "can_trigger_recovery": True,
            "can_dispatch_tasks": True,
        }
    )
    heartbeat_timeout_seconds: int = 60
    can_pause_team: bool = True
    can_delegate: bool = True
    can_execute_tasks: bool = False

class TeamLeaderRole(OrchestrationRole):
    """TeamLeader: in-process coordinator — delegates tasks, retries on failure, manages team."""

    role_id: str = "team-leader"
    name: str = "Team Leader"
    description: str = (
        "In-process coordinator — receives Query objects, delegates to TeamMembers, "
        "retries with backoff, enforces timeouts, reports results."
    )
    permissions: list[str] = msgspec.field(
        default_factory=lambda: [
            "task:delegate",
            "task:retry",
            "task:cancel",
            "member:assign",
            "member:reassign",
            "result:aggregate",
            "timeout:enforce",
        ]
    )
    capabilities: dict[str, bool] = msgspec.field(
        default_factory=lambda: {
            "can_delegate_tasks": True,
            "can_retry_failures": True,
            "can_enforce_timeout": True,
            "can_reassign_members": True,
            "can_report_results": True,
        }
    )
    heartbeat_timeout_seconds: int = 30
    can_pause_team: bool = False
    can_delegate: bool = True
    can_execute_tasks: bool = False

class TeamMemberRole(OrchestrationRole):
    """TeamMember/Worker: in-process executor — executes Task objects, reports completion."""

    role_id: str = "team-member"
    name: str = "Team Member"
    description: str = (
        "In-process executor — receives Task objects from TeamLeader, "
        "executes with tool context, returns Result with execution_time_ms."
    )
    permissions: list[str] = msgspec.field(
        default_factory=lambda: [
            "task:execute",
            "tool:use",
            "result:report",
            "error:catch",
        ]
    )
    capabilities: dict[str, bool] = msgspec.field(
        default_factory=lambda: {
            "can_execute_tasks": True,
            "can_use_tools": True,
            "can_report_results": True,
            "can_handle_errors": True,
        }
    )
    heartbeat_timeout_seconds: int = 15
    can_pause_team: bool = False
    can_delegate: bool = False
    can_execute_tasks: bool = True

class PlannerRole(OrchestrationRole):
    """Planner: planning & decision-making for PlanScope — read project, write .css/plan/ only."""

    role_id: str = "planner"
    name: str = "Planner"
    description: str = (
        "Planning & decision-making for PlanScope — "
        "reads project metadata, writes plan files (.css/plan/) only."
    )
    permissions: list[str] = msgspec.field(
        default_factory=lambda: [
            "project:read",
            "plan:write",
            "scope:read",
        ]
    )
    capabilities: dict[str, bool] = msgspec.field(
        default_factory=lambda: {
            "can_orchestrate": True,
            "can_broadcast": False,
            "can_spawn_subagents": False,
            "can_plan": True,
            "can_analyze": True,
        }
    )
    heartbeat_timeout_seconds: int = 30
    can_pause_team: bool = False
    can_delegate: bool = False
    can_execute_tasks: bool = False

# Built-in role singletons
ORCHESTRATOR = OrchestratorRole()
TEAM_LEADER = TeamLeaderRole()
TEAM_MEMBER = TeamMemberRole()
PLANNER = PlannerRole()

# Role registry for lookup
REGISTRY: dict[str, OrchestrationRole] = {
    r.role_id: r for r in (ORCHESTRATOR, TEAM_LEADER, TEAM_MEMBER, PLANNER)
}

def get(role_id: str) -> OrchestrationRole | None:
    """Return an orchestration role by ID, or None if not found."""
    return REGISTRY.get(role_id)
