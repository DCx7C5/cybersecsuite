"""Team CRUD endpoints."""
from fastapi import APIRouter
router = APIRouter(prefix="/teams", tags=["teams"])

@router.post("/teams")
async def create_team(session_id: int, team_name: str):
    """Create team."""
    pass

@router.get("/teams/{team_id}")
async def get_team(team_id: int):
    """Get team."""
    pass

@router.put("/teams/{team_id}")
async def update_team(team_id: int):
    """Update team."""
    pass

@router.delete("/teams/{team_id}")
async def delete_team(team_id: int):
    """Delete team."""
    pass
