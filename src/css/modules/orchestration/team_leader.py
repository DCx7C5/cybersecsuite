"""TeamLeader — in-process orchestrator coordinator.

Manages a Team and delegates work to TeamMember(s) within the same process.
Holds persistent FK to Team model.
"""

from typing import Any, Optional
from css.core.db.models import Team as TeamModel


class TeamLeader:
    """In-process coordinator for a Team + Orchestrator.
    
    Responsibilities:
    - Hold FK reference to Team (persistent)
    - Coordinate task distribution to TeamMember(s)
    - Aggregate results
    - Handle team lifecycle (pause, resume, complete)
    """
    
    def __init__(self, team_id: int, orchestrator_id: str):
        """Initialize TeamLeader for a specific Team.
        
        Args:
            team_id: FK to Team model (persistent)
            orchestrator_id: Unique orchestrator identifier
        """
        self.team_id = team_id
        self.orchestrator_id = orchestrator_id
        self.team_model: Optional[TeamModel] = None
        self._members: dict[str, "TeamMember"] = {}
    
    async def initialize(self) -> None:
        """Load Team model and validate."""
        from tortoise.exceptions import DoesNotExist
        try:
            self.team_model = await TeamModel.get(id=self.team_id)
        except DoesNotExist:
            raise ValueError(f"Team {self.team_id} not found")
    
    def add_member(self, member_id: str, member: "TeamMember") -> None:
        """Register a TeamMember."""
        self._members[member_id] = member
    
    async def delegate(self, task_data: dict[str, Any]) -> Any:
        """Delegate task to best available TeamMember.
        
        Args:
            task_data: Task payload
            
        Returns:
            Task result from TeamMember
        """
        if not self._members:
            raise RuntimeError(f"No team members available for team {self.team_id}")
        
        # Simple round-robin for now (use orchestrator_mode for smarter selection)
        for member in self._members.values():
            if member.is_available():
                return await member.execute(task_data)
        
        raise RuntimeError(f"No available members for team {self.team_id}")
    
    async def pause_team(self) -> None:
        """Pause all team members."""
        for member in self._members.values():
            await member.pause()
    
    async def resume_team(self) -> None:
        """Resume all team members."""
        for member in self._members.values():
            await member.resume()
    
    async def shutdown(self) -> None:
        """Shutdown all team members."""
        for member in self._members.values():
            await member.shutdown()
