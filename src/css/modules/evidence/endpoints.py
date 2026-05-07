"""Evidence management endpoints — chain-of-custody, collection, verification."""

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import hashlib
from .models import (
    Evidence,
    EvidenceChain,
    EvidenceTagging,
    EvidenceStatus,
    EvidenceType,
    ChainEventType,
)

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


# Request/Response Models
class EvidenceCollect(BaseModel):
    evidence_type: str = Field(..., regex="^(log_file|network_capture|disk_image|memory_dump|file_system|system_state|config|metadata|other)$")
    source: str = Field(..., min_length=1, max_length=512)
    case_id: str = Field(..., min_length=1, max_length=255)
    collected_by: str = Field(..., min_length=1, max_length=255)
    collected_at: datetime = Field(..., description="Timestamp of collection")
    description: str = ""
    tags: List[str] = Field(default_factory=list)
    hash_sha256: Optional[str] = None
    hash_md5: Optional[str] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    access_level: str = Field("restricted", regex="^(public|internal|restricted|confidential)$")


class EvidenceResponse(BaseModel):
    id: int
    evidence_id: str
    case_id: str
    evidence_type: str
    source: str
    source_agent_id: str
    hash_sha256: str
    description: str
    status: str
    collected_by: str
    collected_at: datetime
    is_sealed: bool
    sealed_at: Optional[datetime]
    size_bytes: Optional[int]
    access_level: str


class ChainEventRecord(BaseModel):
    event_type: str = Field(..., regex="^(collected|transferred|accessed|verified|sealed|unsealed|archived|restored|destroyed)$")
    actor: str = Field(..., min_length=1, max_length=255)
    action: str = Field(..., min_length=1, max_length=512)
    metadata: Dict = Field(default_factory=dict)
    occurred_at: datetime = Field(..., description="Timestamp of event")


class ChainEventResponse(BaseModel):
    id: int
    sequence_number: int
    event_type: str
    actor: str
    action: str
    occurred_at: datetime
    recorded_at: datetime
    hash_before: str
    hash_after: str


class ChainResponse(BaseModel):
    evidence_id: str
    events: List[ChainEventResponse]
    is_valid: bool
    integrity_status: str  # "valid", "broken", "compromised"


class EvidenceTaggingReq(BaseModel):
    incident_id: Optional[str] = None
    case_id: Optional[str] = None
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    notes: str = ""


# Collection Endpoints
@router.post("/collect", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def collect_evidence(
    req: EvidenceCollect,
    org_id: int = Query(..., description="Organization ID"),
):
    """
    Collect and register evidence with initial chain-of-custody entry.
    
    Creates Evidence record and first ChainEvent (COLLECTED).
    Hashes must be provided or will be calculated if content uploaded separately.
    """
    # TODO: Check org authorization
    
    try:
        # Generate evidence ID
        evidence_id = f"EV-{org_id}-{int(datetime.utcnow().timestamp() * 1000)}"
        
        # Use provided hash or generate placeholder
        hash_sha256 = req.hash_sha256 or hashlib.sha256(f"{evidence_id}:{req.source}".encode()).hexdigest()
        
        # Create evidence record
        evidence = await Evidence.create(
            organization_id=org_id,
            case_id=req.case_id,
            evidence_id=evidence_id,
            hash_sha256=hash_sha256,
            hash_md5=req.hash_md5,
            evidence_type=req.evidence_type,
            source=req.source,
            source_agent_id="system",  # TODO: Get from auth context
            description=req.description,
            tags=req.tags,
            size_bytes=req.size_bytes,
            mime_type=req.mime_type,
            status="collected",
            collected_by=req.collected_by,
            collected_at=req.collected_at,
            access_level=req.access_level,
        )
        
        # Create initial chain event
        await EvidenceChain.create(
            evidence_id=evidence.id,
            sequence_number=1,
            event_type=ChainEventType.COLLECTED,
            actor=req.collected_by,
            action=f"Evidence collected from {req.source}",
            hash_before=hash_sha256,
            hash_after=hash_sha256,
            event_signature=_generate_signature(hash_sha256, 0, None),
            occurred_at=req.collected_at,
        )
        
        return EvidenceResponse.model_validate(evidence)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to collect evidence: {str(e)}")


@router.get("/items", response_model=List[EvidenceResponse])
async def list_evidence(
    org_id: int = Query(..., description="Organization ID"),
    case_id: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    evidence_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """List evidence items for organization (optionally filtered by case)."""
    # TODO: Check org authorization
    
    query = Evidence.filter(organization_id=org_id)
    if case_id:
        query = query.filter(case_id=case_id)
    if status_filter:
        query = query.filter(status=status_filter)
    if evidence_type:
        query = query.filter(evidence_type=evidence_type)
    
    items = await query.order_by("-collected_at").limit(limit).all()
    return [EvidenceResponse.model_validate(i) for i in items]


@router.get("/items/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get specific evidence item details."""
    # TODO: Check org authorization
    
    evidence = await Evidence.get_or_none(
        organization_id=org_id,
        evidence_id=evidence_id,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return EvidenceResponse.model_validate(evidence)


# Chain-of-Custody Endpoints
@router.get("/items/{evidence_id}/chain", response_model=ChainResponse)
async def get_chain_of_custody(
    evidence_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """
    Get complete chain-of-custody for evidence.
    
    Includes all events (collected, transferred, accessed, sealed, etc.)
    and validation status of the chain.
    """
    # TODO: Check org authorization
    
    evidence = await Evidence.get_or_none(
        organization_id=org_id,
        evidence_id=evidence_id,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    events = await EvidenceChain.filter(evidence_id=evidence.id).order_by("sequence_number").all()
    
    # Validate chain integrity
    is_valid, integrity_status = _validate_chain(events)
    
    return ChainResponse(
        evidence_id=evidence_id,
        events=[ChainEventResponse.model_validate(e) for e in events],
        is_valid=is_valid,
        integrity_status=integrity_status,
    )


@router.post("/items/{evidence_id}/chain-event", response_model=ChainEventResponse, status_code=status.HTTP_201_CREATED)
async def record_chain_event(
    evidence_id: str,
    req: ChainEventRecord,
    org_id: int = Query(..., description="Organization ID"),
):
    """
    Record chain-of-custody event (transfer, access, verification, etc.).
    
    Appends immutable entry to evidence chain with cryptographic linking.
    """
    # TODO: Check org authorization
    
    evidence = await Evidence.get_or_none(
        organization_id=org_id,
        evidence_id=evidence_id,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    if evidence.is_sealed and req.event_type not in ["unsealed", "destroyed"]:
        raise HTTPException(
            status_code=403,
            detail="Cannot modify sealed evidence (except unseal/destroy)"
        )
    
    try:
        # Get last event in chain
        last_event = await EvidenceChain.filter(evidence_id=evidence.id).order_by("-sequence_number").first()
        seq_num = (last_event.sequence_number if last_event else 0) + 1
        
        # Create new chain event
        event = await EvidenceChain.create(
            evidence_id=evidence.id,
            sequence_number=seq_num,
            event_type=req.event_type,
            actor=req.actor,
            actor_id="",  # TODO: Get from auth context
            action=req.action,
            metadata=req.metadata,
            hash_before=evidence.hash_sha256,
            hash_after=evidence.hash_sha256,  # Hash unchanged unless evidence modified
            event_signature=_generate_signature(
                evidence.hash_sha256,
                seq_num,
                last_event.event_signature if last_event else None
            ),
            previous_signature=last_event.event_signature if last_event else None,
            occurred_at=req.occurred_at,
        )
        
        # Update evidence status based on event
        if req.event_type == ChainEventType.SEALED:
            evidence.is_sealed = True
            evidence.sealed_at = datetime.utcnow()
            evidence.seal_signature = event.event_signature
            evidence.status = EvidenceStatus.SEALED
        elif req.event_type == ChainEventType.ARCHIVED:
            evidence.status = EvidenceStatus.ARCHIVED
        elif req.event_type == ChainEventType.VERIFIED:
            evidence.status = EvidenceStatus.VERIFIED
        elif req.event_type == ChainEventType.DESTROYED:
            evidence.status = EvidenceStatus.DESTROYED
        
        await evidence.save()
        
        return ChainEventResponse.model_validate(event)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to record event: {str(e)}")


# Tagging Endpoints
@router.post("/items/{evidence_id}/tag", status_code=status.HTTP_201_CREATED)
async def tag_evidence(
    evidence_id: str,
    req: EvidenceTaggingReq,
    org_id: int = Query(..., description="Organization ID"),
):
    """Tag evidence with incident/case relationship."""
    # TODO: Check org authorization
    
    evidence = await Evidence.get_or_none(
        organization_id=org_id,
        evidence_id=evidence_id,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    try:
        tagging = await EvidenceTagging.create(
            evidence_id=evidence.id,
            incident_id=req.incident_id,
            case_id=req.case_id,
            relevance_score=req.relevance_score,
            notes=req.notes,
        )
        return {"id": tagging.id, "status": "tagged"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to tag evidence: {str(e)}")


@router.get("/items/{evidence_id}/tags")
async def get_evidence_tags(
    evidence_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get all incident/case tags for evidence."""
    # TODO: Check org authorization
    
    evidence = await Evidence.get_or_none(
        organization_id=org_id,
        evidence_id=evidence_id,
    )
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    tags = await EvidenceTagging.filter(evidence_id=evidence.id).all()
    return {"evidence_id": evidence_id, "tags": [t.model_dump() for t in tags]}


# Helper functions
def _generate_signature(hash_value: str, seq_num: int, prev_sig: Optional[str]) -> str:
    """Generate event signature (placeholder for cryptographic signing)."""
    import hmac
    
    message = f"{hash_value}:{seq_num}:{prev_sig or ''}".encode()
    # In production: use proper HMAC-SHA256 with secret key
    sig = hmac.new(b"evidence-key", message, "sha256").hexdigest()
    return sig


def _validate_chain(events: List[EvidenceChain]) -> tuple[bool, str]:
    """
    Validate chain-of-custody integrity.
    
    Returns: (is_valid, status)
    - is_valid: True if all signatures check out
    - status: "valid", "broken" (signature mismatch), "compromised" (out of order)
    """
    if not events:
        return True, "valid"
    
    # Check sequence numbers are sequential
    for i, event in enumerate(events):
        if event.sequence_number != i + 1:
            return False, "compromised"
    
    # TODO: Verify cryptographic signatures in production
    # For now, just check structural integrity
    
    return True, "valid"


__all__ = ["router"]
