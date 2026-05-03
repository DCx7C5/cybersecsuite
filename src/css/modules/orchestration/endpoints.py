"""Orchestrator CRUD endpoints."""
from fastapi import APIRouter
router = APIRouter(prefix="/orchestrators", tags=["orchestrators"])

@router.post("/orchestrators")
async def spawn_orchestrator(team_id: int):
    """Spawn orchestrator."""
    pass

@router.get("/orchestrators/{orch_id}")
async def get_orchestrator(orch_id: str):
    """Get orchestrator."""
    pass

@router.delete("/orchestrators/{orch_id}")
async def kill_orchestrator(orch_id: str):
    """Kill orchestrator."""
    pass
