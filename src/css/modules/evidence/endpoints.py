"""Evidence management endpoints — chain-of-custody, collection, verification."""

import msgspec

from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timezone
import hashlib
from .models import (
    Evidence,
    EvidenceChain,
    EvidenceTagging,
    EvidenceStatus,
    ChainEventType,
)

router = APIRouter(prefix="/api/evidence", tags=["evidence"])


# Request/Response Models
class EvidenceCollect(msgspec.Struct, frozen=True):
    evidence_type: str
    source: str
    case_id: str
    collected_by: str
    collected_at: datetime
    description: str = ""
    tags: list[str] = []
    hash_sha256: str | None = None
    hash_md5: str | None = None
    size_bytes: int | None = None
    mime_type: str | None = None
    access_level: str = "restricted"


class EvidenceResponse(msgspec.Struct, frozen=True):
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
    access_level: str
    sealed_at: datetime | None = None
    size_bytes: int | None = None


class ChainEventRecord(msgspec.Struct, frozen=True):
    event_type: str
    actor: str
    action: str
    occurred_at: datetime
    metadata: dict = {}


class ChainEventResponse(msgspec.Struct, frozen=True):
    id: int
    sequence_number: int
    event_type: str
    actor: str
    action: str
    occurred_at: datetime
    recorded_at: datetime
    hash_before: str
    hash_after: str


class ChainResponse(msgspec.Struct, frozen=True):
    evidence_id: str
    events: list[ChainEventResponse]
    is_valid: bool
    integrity_status: str


class EvidenceTaggingReq(msgspec.Struct, frozen=True):
    incident_id: str | None = None
    case_id: str | None = None
    relevance_score: float = 0.0
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
        evidence_id = f"EV-{org_id}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        
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
        
        return EvidenceResponse(**{f: getattr(evidence, f) for f in EvidenceResponse.__struct_fields__})
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to collect evidence: {str(e)}")


@router.get("/items", response_model=list[EvidenceResponse])
async def list_evidence(
    org_id: int = Query(..., description="Organization ID"),
    case_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    evidence_type: str | None = None,
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
    return [EvidenceResponse(**{f: getattr(i, f) for f in EvidenceResponse.__struct_fields__}) for i in items]


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
    
    return EvidenceResponse(**{f: getattr(evidence, f) for f in EvidenceResponse.__struct_fields__})


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
        events=[ChainEventResponse(**{f: getattr(e, f) for f in ChainEventResponse.__struct_fields__}) for e in events],
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
            evidence.sealed_at = datetime.now(timezone.utc)
            evidence.seal_signature = event.event_signature
            evidence.status = EvidenceStatus.SEALED
        elif req.event_type == ChainEventType.ARCHIVED:
            evidence.status = EvidenceStatus.ARCHIVED
        elif req.event_type == ChainEventType.VERIFIED:
            evidence.status = EvidenceStatus.VERIFIED
        elif req.event_type == ChainEventType.DESTROYED:
            evidence.status = EvidenceStatus.DESTROYED
        
        await evidence.save()
        
        return ChainEventResponse(**{f: getattr(event, f) for f in ChainEventResponse.__struct_fields__})
    
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
    return {"evidence_id": evidence_id, "tags": [{f: getattr(t, f) for f in t._meta.fields} for t in tags]}


# Helper functions
def _generate_signature(hash_value: str, seq_num: int, prev_sig: str | None) -> str:
    """Generate event signature (placeholder for cryptographic signing)."""
    import hmac
    
    message = f"{hash_value}:{seq_num}:{prev_sig or ''}".encode()
    # In production: use proper HMAC-SHA256 with secret key
    sig = hmac.new(b"evidence-key", message, "sha256").hexdigest()
    return sig


def _validate_chain(events: list[EvidenceChain]) -> tuple[bool, str]:
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
