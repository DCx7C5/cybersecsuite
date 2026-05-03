"""Orchestration-specific roles module.

Defines roles for orchestration architecture:
- Orchestrator: process-level coordinator
- TeamLeader: in-process coordinator
- TeamMember: in-process executor
"""

import logging
from css.core.logger import getLogger

logger = getLogger(__name__)

from .role_types import (
    OrchestrationRole,
    OrchestratorRole,
    TeamLeaderRole,
    TeamMemberRole,
    ORCHESTRATOR,
    TEAM_LEADER,
    TEAM_MEMBER,
    get,
)
from .enums import RoleType, Permission
from .exceptions import (
    BaseRoleException,
    RoleNotFoundError,
    PermissionDeniedError,
    InvalidRoleError,
)

__all__ = [
    # Role types
    "OrchestrationRole",
    "OrchestratorRole",
    "TeamLeaderRole",
    "TeamMemberRole",
    
    # Built-in roles
    "ORCHESTRATOR",
    "TEAM_LEADER",
    "TEAM_MEMBER",
    
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

