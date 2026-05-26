"""Team CRUD endpoints."""
from fastapi import APIRouter, HTTPException, Query, status

from css.core.db.models.scope import SessionScope
from css.core.db.models.team import Team
from css.modules.teams.enums import TeamStatus

router = APIRouter(prefix="/api/teams", tags=["teams"])

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_team(
    session_id: int = Query(...),
    team_name: str = Query(..., min_length=1),
) -> dict[str, object]:
    """Create team."""
    session = await SessionScope.get_or_none(id=session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    existing = await Team.get_or_none(session_id=session_id, team_name=team_name)
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team already exists in session")

    team = await Team.create(session_id=session_id, team_name=team_name)
    team_session_id = int(getattr(team, "session_id"))
    return {"id": team.id, "session_id": team_session_id, "team_name": team.team_name, "status": team.status}


@router.get("/{team_id}")
async def get_team(team_id: int) -> dict[str, object]:
    """Get team."""
    team = await Team.get_or_none(id=team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    team_session_id = int(getattr(team, "session_id"))
    return {
        "id": team.id,
        "session_id": team_session_id,
        "team_name": team.team_name,
        "status": team.status,
        "orchestrator_mode": team.orchestrator_mode,
        "max_orchestrators": team.max_orchestrators,
        "current_orchestrators": team.current_orchestrators,
        "max_tasks": team.max_tasks,
        "completed_tasks": team.completed_tasks,
        "paused_at": team.paused_at.isoformat() if team.paused_at else None,
    }


@router.put("/{team_id}")
async def update_team(
    team_id: int,
    team_name: str | None = Query(None, min_length=1),
    status_value: str | None = Query(None, alias="status"),
) -> dict[str, object]:
    """Update team."""
    team = await Team.get_or_none(id=team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    updates: dict[str, object] = {}
    if team_name is not None and team_name != team.team_name:
        team_session_id = int(getattr(team, "session_id"))
        existing = await Team.get_or_none(session_id=team_session_id, team_name=team_name)
        if existing is not None and existing.id != team_id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Team name already exists in session")
        updates["team_name"] = team_name

    if status_value is not None:
        try:
            updates["status"] = TeamStatus(status_value)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported team status: {status_value}",
            ) from exc

    if updates:
        await team.save_changes(**updates)
        await team.refresh_from_db()

    team_session_id = int(getattr(team, "session_id"))
    return {
        "id": team.id,
        "session_id": team_session_id,
        "team_name": team.team_name,
        "status": team.status,
        "orchestrator_mode": team.orchestrator_mode,
    }


@router.delete("/{team_id}")
async def delete_team(team_id: int) -> dict[str, object]:
    """Delete team."""
    team = await Team.get_or_none(id=team_id)
    if team is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    await team.delete()
    return {"deleted": True, "id": team_id}
