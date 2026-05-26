"""MITRE ATT&CK endpoints."""

from fastapi import APIRouter, Query, status
from typing import List, Optional
from css.core.types.base_endpoint import EndpointModel
from .models import MITRETechnique, ThreatActor, Tactic

router = APIRouter(prefix="/api/mitre", tags=["mitre"])


class TechniqueResponse(EndpointModel, kw_only=True):
    id: int
    technique_id: str
    subtechnique_id: Optional[str]
    tactic: str
    name: str
    description: str


class ThreatActorResponse(EndpointModel, kw_only=True):
    id: int
    actor_name: str
    actor_aliases: List[str]
    actor_type: str
    tactics: List[str]
    techniques: List[str]


class TechniqueMappingCreate(EndpointModel, kw_only=True):
    technique_id: str
    evidence: str
    confidence: str


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
    return [TechniqueResponse(**{f: getattr(t, f) for f in TechniqueResponse.__struct_fields__}) for t in techniques]


@router.get("/threat-actors", response_model=List[ThreatActorResponse])
async def list_threat_actors(
    org_id: int = Query(..., description="Organization ID"),
):
    """List known threat actors."""
    actors = await ThreatActor.filter(organization_id=org_id).all()
    return [ThreatActorResponse(**{f: getattr(a, f) for f in ThreatActorResponse.__struct_fields__}) for a in actors]


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
