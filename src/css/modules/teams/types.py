"""Team types — dataclass entities for team scope and lifecycle.

All team types live entirely within this module. No core base class needed.
"""
import msgspec

from .enums import TeamStatus, OrchestratorMode

@msgspec.struct
class TeamScope:
    """Immutable team context snapshot."""

    team_id: int
    team_name: str
    session_id: int
    max_orchestrators: int = 0
    current_orchestrators: int = 0
    completed_tasks: int = 0
    status: TeamStatus = TeamStatus.PENDING
    created_at: str | None = None
    paused_at: str | None = None

@msgspec.struct
class Team:
    """Team entity — mutable team state with lifecycle management."""

    team_id: int
    team_name: str
    session_id: int
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
        return self.status == TeamStatus.PENDING

    def can_pause(self) -> bool:
        return self.status == TeamStatus.ACTIVE

    def can_resume(self) -> bool:
        return self.status == TeamStatus.PAUSED

    def can_complete(self) -> bool:
        return self.status in (TeamStatus.ACTIVE, TeamStatus.PAUSED)
