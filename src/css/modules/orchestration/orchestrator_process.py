"""OrchestratorProcess — main loop for multi-orchestrator instance.

Manages TeamLeader + TeamMembers in a single process.
"""

import asyncio
from typing import Optional
from .team_leader import TeamLeader
from .team_member import TeamMember


class OrchestratorProcess:
    """Single orchestrator process instance.
    
    Contains:
    - TeamLeader (coordinator)
    - N TeamMembers (workers)
    - Task queue (pull-based)
    """
    
    def __init__(self, team_id: int, orchestrator_id: str, num_members: int = 3):
        """Initialize orchestrator process.
        
        Args:
            team_id: Team this orchestrator belongs to
            orchestrator_id: Unique orchestrator identifier
            num_members: Number of TeamMembers to spawn
        """
        self.team_id = team_id
        self.orchestrator_id = orchestrator_id
        self.team_leader = TeamLeader(team_id, orchestrator_id)
        self.members: dict[str, TeamMember] = {}
        self.num_members = num_members
        self._is_running = False
    
    async def initialize(self) -> None:
        """Initialize leader and spawn members."""
        await self.team_leader.initialize()
        
        # Spawn team members
        for i in range(self.num_members):
            member_id = f"{self.orchestrator_id}_member_{i}"
            member = TeamMember(member_id)
            self.members[member_id] = member
            self.team_leader.add_member(member_id, member)
    
    async def start(self) -> None:
        """Start orchestrator main loop."""
        self._is_running = True
        await self.initialize()
        
        # Main loop: pull tasks, delegate, repeat
        while self._is_running:
            # Placeholder: actual task pulling
            await asyncio.sleep(1)
    
    async def shutdown(self) -> None:
        """Graceful shutdown."""
        self._is_running = False
        await self.team_leader.shutdown()
