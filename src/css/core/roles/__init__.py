"""Orchestration-specific roles module.

Defines roles for orchestration architecture:
- Orchestrator: process-level coordinator
- TeamLeader: in-process coordinator
- TeamMember: in-process executor
- Planner: planning & decision-making
"""

from css.core.logger import getLogger
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
from .enums import RoleType, Permission
from .exceptions import (
    BaseRoleException,
    RoleNotFoundError,
    PermissionDeniedError,
    InvalidRoleError,
)

logger = getLogger(__name__)

__all__ = [
    # Role types
    "OrchestrationRole",
    "OrchestratorRole",
    "TeamLeaderRole",
    "TeamMemberRole",
    "PlannerRole",
    
    # Built-in roles
    "ORCHESTRATOR",
    "TEAM_LEADER",
    "TEAM_MEMBER",
    "PLANNER",
    
    # Enums
    "RoleType",
    "Permission",
    
    # Exceptions
    "BaseRoleException",
    "RoleNotFoundError",
    "PermissionDeniedError",
    "InvalidRoleError",
    
    # Functions
    "get",
]

logger.info("Roles module loaded")