"""MITRE ATT&CK endpoints."""

from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional
from .models import MITRETechnique, ThreatActor, Tactic

router = APIRouter(prefix="/api/mitre", tags=["mitre"])


class TechniqueResponse(BaseModel):
    id: int
    technique_id: str
    subtechnique_id: Optional[str]
    tactic: str
    name: str
    description: str


class ThreatActorResponse(BaseModel):
    id: int
    actor_name: str
    actor_aliases: List[str]
    actor_type: str
    tactics: List[str]
    techniques: List[str]


class TechniqueMappingCreate(BaseModel):
    technique_id: str
    evidence: str
    confidence: str = Field("medium", regex="^(low|medium|high)$")


@router.get("/tactics", response_model=List[str])
async def list_tactics():
    """List all MITRE ATT&CK tactics."""
    return [t.value for t in Tactic]


@router.get("/techniques", response_model=List[TechniqueResponse])
async def list_techniques(
    org_id: int = Query(..., description="Organization ID"),
    tactic: Optional[str] = None,
):
    """List MITRE techniques for org."""
    query = MITRETechnique.filter(organization_id=org_id)
    if tactic:
        query = query.filter(tactic=tactic)
    
    techniques = await query.all()
    return [TechniqueResponse.model_validate(t) for t in techniques]


@router.get("/threat-actors", response_model=List[ThreatActorResponse])
async def list_threat_actors(
    org_id: int = Query(..., description="Organization ID"),
):
    """List known threat actors."""
    actors = await ThreatActor.filter(organization_id=org_id).all()
    return [ThreatActorResponse.model_validate(a) for a in actors]


@router.post("/incidents/{incident_id}/techniques", status_code=status.HTTP_201_CREATED)
async def map_incident_technique(
    incident_id: int,
    req: TechniqueMappingCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Map incident to ATT&CK technique."""
    # TODO: Get technique, validate, create mapping
    return {"status": "mapped"}


__all__ = ["router"]
