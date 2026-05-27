"""Threat Intelligence endpoints."""

from fastapi import APIRouter, Query, status
from typing import List, Optional
from datetime import datetime, timezone
from css.core.types.base_endpoint import BaseEndpoint
from .models import IOC, ThreatFeed

router = APIRouter(prefix="/api/threat-intel", tags=["threat-intel"])


class IOCCreate(BaseEndpoint, kw_only=True):
    ioc_type: str
    value: str
    threat_level: str = "medium"
    source: str
    description: str = ""
    tags: List[str] = []


class IOCResponse(BaseEndpoint, kw_only=True):
    id: int
    ioc_type: str
    value: str
    threat_level: str
    source: str
    is_active: bool


@router.post("/iocs", response_model=IOCResponse, status_code=status.HTTP_201_CREATED)
async def create_ioc(
    req: IOCCreate,
    org_id: int = Query(...),
):
    """Create IOC."""
    ioc = await IOC.create(
        organization_id=org_id,
        ioc_type=req.ioc_type,
        value=req.value,
        threat_level=req.threat_level,
        source=req.source,
        description=req.description,
        tags=req.tags,
        first_seen_at=datetime.now(timezone.utc),
        last_seen_at=datetime.now(timezone.utc),
    )
    return IOCResponse(**{f: getattr(ioc, f) for f in IOCResponse.__struct_fields__})


@router.get("/iocs", response_model=List[IOCResponse])
async def list_iocs(
    org_id: int = Query(...),
    ioc_type: Optional[str] = None,
    threat_level: Optional[str] = None,
):
    """List IOCs."""
    query = IOC.filter(organization_id=org_id, is_active=True)
    if ioc_type:
        query = query.filter(ioc_type=ioc_type)
    if threat_level:
        query = query.filter(threat_level=threat_level)
    
    iocs = await query.all()
    return [IOCResponse(**{f: getattr(i, f) for f in IOCResponse.__struct_fields__}) for i in iocs]


@router.post("/feeds", status_code=status.HTTP_201_CREATED)
async def create_feed(
    name: str = Query(...),
    feed_url: str = Query(...),
    feed_type: str = Query(...),
    org_id: int = Query(...),
):
    """Create threat feed."""
    feed = await ThreatFeed.create(
        organization_id=org_id,
        name=name,
        feed_url=feed_url,
        feed_type=feed_type,
    )
    return {"id": feed.id, "status": "created"}


__all__ = ["router"]
