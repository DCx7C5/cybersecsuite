"""Scan management endpoints."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timezone
import msgspec
from .models import Scan, Finding

router = APIRouter(prefix="/api/scans", tags=["scans"])


class ScanCreate(msgspec.Struct, frozen=True):
    scan_type: str
    target: str
    scope: str = ""
    scheduled_at: datetime


class ScanResponse(msgspec.Struct, frozen=True):
    id: int
    scan_id: str
    scan_type: str
    target: str
    status: str
    findings_count: int


class FindingResponse(msgspec.Struct, frozen=True):
    id: int
    finding_id: str
    title: str
    severity: str
    cve_id: Optional[str]
    status: str


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    req: ScanCreate,
    org_id: int = Query(...),
):
    """Create new scan."""
    scan_id = f"SCAN-{org_id}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    scan = await Scan.create(
        organization_id=org_id,
        scan_id=scan_id,
        scan_type=req.scan_type,
        target=req.target,
        scope=req.scope,
        scheduled_at=req.scheduled_at,
    )
    return ScanResponse(**{f: getattr(scan, f) for f in ScanResponse.__struct_fields__})


@router.get("/", response_model=List[ScanResponse])
async def list_scans(
    org_id: int = Query(...),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List scans."""
    query = Scan.filter(organization_id=org_id)
    if status_filter:
        query = query.filter(status=status_filter)
    scans = await query.order_by("-created_at").all()
    return [ScanResponse(**{f: getattr(s, f) for f in ScanResponse.__struct_fields__}) for s in scans]


@router.get("/{scan_id}/findings", response_model=List[FindingResponse])
async def list_findings(
    scan_id: str,
    org_id: int = Query(...),
):
    """List findings for scan."""
    scan = await Scan.get_or_none(organization_id=org_id, scan_id=scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    findings = await Finding.filter(scan_id=scan.id).all()
    return [FindingResponse(**{f: getattr(fnd, f) for f in FindingResponse.__struct_fields__}) for fnd in findings]


__all__ = ["router"]
