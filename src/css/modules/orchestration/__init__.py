"""Orchestration module — multi-orchestrator coordination.

Contains:
- TeamLeader: In-process coordinator (holds Team FK)
- TeamMember: In-process worker (executes tasks)
- OrchestratorProcess: Main loop (manages leader + members)
- Pull-based task queue, heartbeat, crash recovery, load balancing
"""

from .team_leader import TeamLeader
from .team_member import TeamMember
from .orchestrator_process import OrchestratorProcess

__all__ = [
    "TeamLeader",
    "TeamMember",
    "OrchestratorProcess",
]
