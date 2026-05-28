"""Orchestration-specific roles module.

Defines roles for orchestration architecture:
- Orchestrator: process-level coordinator
- TeamLeader: in-process coordinator
- TeamMember: in-process executor
- Planner: planning & decision-making
"""

from css.core.logger import getLogger
from css.core.enums import Permission
from css.core.exceptions import BaseCoreException
from .role_types import (
    OrchestrationRole,
    OrchestratorRole,
    TeamLeaderRole,
    TeamMemberRole,
    PlannerRole,
    ORCHESTRATOR,
    TEAM_LEADER,
    TEAM_MEMBER,
    PLANNER,
    get,
)

class RoleType:
    """Namespace for built-in role type constants."""
    ORCHESTRATOR = "orchestrator"
    TEAM_LEADER = "team_leader"
    TEAM_MEMBER = "team_member"
    PLANNER = "planner"

class BaseRoleException(BaseCoreException):
    pass

class RoleNotFoundError(BaseRoleException):
    pass

class PermissionDeniedError(BaseRoleException):
    pass

class InvalidRoleError(BaseRoleException):
    pass

logger = getLogger(__name__)

logger.info("Roles module loaded")
