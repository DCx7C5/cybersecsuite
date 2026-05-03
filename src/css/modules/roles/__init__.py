"""Orchestration-specific roles module.

Defines roles for orchestration architecture:
- Orchestrator: process-level coordinator
- TeamLeader: in-process coordinator
- TeamMember: in-process executor
"""

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

__all__ = [
    "OrchestrationRole",
    "OrchestratorRole",
    "TeamLeaderRole",
    "TeamMemberRole",
    "ORCHESTRATOR",
    "TEAM_LEADER",
    "TEAM_MEMBER",
    "get",
]
