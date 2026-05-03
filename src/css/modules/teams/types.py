"""Team types — dataclass entities for team scope and lifecycle."""

from dataclasses import dataclass
from typing import Optional
from .enums import TeamStatus, OrchestratorMode


@dataclass
class TeamScope:
    """TeamScope — immutable team context snapshot.
    
    Read-only representation of team state for operation context.
    """
    team_id: int
    team_name: str
    status: TeamStatus
    session_id: int
    max_orchestrators: int
    current_orchestrators: int
    completed_tasks: int = 0
    created_at: Optional[str] = None
    paused_at: Optional[str] = None


@dataclass
class Team:
    """Team entity — mutable team state with lifecycle management.
    
    Tracks orchestrator pool, task queue, and status transitions:
    pending → active → paused ↔ active → completed
    """
    team_id: int
    team_name: str
    session_id: int
    status: TeamStatus = TeamStatus.PENDING
    orchestrator_mode: OrchestratorMode = OrchestratorMode.ROUND_ROBIN
    max_orchestrators: int = 5
    current_orchestrators: int = 0
    max_tasks: int = 100
    completed_tasks: int = 0
    created_at: Optional[str] = None
    paused_at: Optional[str] = None
    
    def to_scope(self) -> TeamScope:
        """Convert Team entity to immutable TeamScope snapshot."""
        return TeamScope(
            team_id=self.team_id,
            team_name=self.team_name,
            status=self.status,
            session_id=self.session_id,
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
