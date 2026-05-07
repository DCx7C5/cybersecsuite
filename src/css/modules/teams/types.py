"""Team types — dataclass entities for team scope and lifecycle."""

from dataclasses import dataclass

from css.core.types.base_workflow import BaseTeam, BaseTeamScope
from .enums import TeamStatus, OrchestratorMode


@dataclass
class TeamScope(BaseTeamScope):
    """TeamScope — immutable team context snapshot."""

    status: TeamStatus = TeamStatus.PENDING
    created_at: str | None = None
    paused_at: str | None = None


@dataclass
class Team(BaseTeam):
    """Team entity — mutable team state with lifecycle management."""

    status: TeamStatus = TeamStatus.PENDING
    orchestrator_mode: OrchestratorMode = OrchestratorMode.ROUND_ROBIN
    max_orchestrators: int = 5
    current_orchestrators: int = 0
    max_tasks: int = 100
    completed_tasks: int = 0
    created_at: str | None = None
    paused_at: str | None = None
    
    def to_scope(self) -> TeamScope:
        """Convert Team entity to immutable TeamScope snapshot."""
        return TeamScope(
            team_id=self.team_id,
            team_name=self.team_name,
            session_id=self.session_id,
            status=self.status,
            max_orchestrators=self.max_orchestrators,
            current_orchestrators=self.current_orchestrators,
            completed_tasks=self.completed_tasks,
            created_at=self.created_at,
            paused_at=self.paused_at,
        )
    
    def can_activate(self) -> bool:
        """Check if team can transition to active state."""
        return self.status == TeamStatus.PENDING
    
    def can_pause(self) -> bool:
        """Check if team can transition to paused state."""
        return self.status == TeamStatus.ACTIVE
    
    def can_resume(self) -> bool:
        """Check if team can transition from paused back to active."""
        return self.status == TeamStatus.PAUSED
    
    def can_complete(self) -> bool:
        """Check if team can transition to completed state."""
        return self.status in (TeamStatus.ACTIVE, TeamStatus.PAUSED)
