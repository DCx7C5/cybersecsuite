"""Compliance management endpoints — frameworks, controls, mappings, reports."""

from css.core.types.base_endpoint import EndpointModel

from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timezone
from .models import (
    ComplianceFramework,
    FrameworkControl,
    ControlMapping,
    ComplianceReport,
    ComplianceStatus,
)
from .generator import ComplianceReportGenerator

router = APIRouter(prefix="/api/compliance", tags=["compliance"])
report_generator = ComplianceReportGenerator()

# Request/Response Models
class ComplianceFrameworkCreate(EndpointModel, kw_only=True):
    framework_type: str
    name: str
    description: str = ""
    version: str = "1.0"

class ComplianceFrameworkResponse(EndpointModel, kw_only=True):
    id: int
    framework_type: str
    name: str
    description: str
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

class FrameworkControlCreate(EndpointModel, kw_only=True):
    control_id: str
    name: str
    description: str = ""
    category: str
    cwe_ids: list[str] = []
    mitre_techniques: list[str] = []
    priority: str = "medium"
    risk_impact: str = ""

class FrameworkControlResponse(EndpointModel, kw_only=True):
    id: int
    control_id: str
    name: str
    description: str
    category: str
    cwe_ids: list[str]
    mitre_techniques: list[str]
    priority: str
    risk_impact: str

class ControlMappingCreate(EndpointModel, kw_only=True):
    control_id: int
    finding_type: str
    finding_id: str
    status: str
    evidence: str = ""
    remediation_notes: str = ""
    found_at: datetime | None = None

class ControlMappingUpdate(EndpointModel, kw_only=True):
    status: str | None = None
    evidence: str | None = None
    remediation_notes: str | None = None
    verified_at: datetime | None = None

class ControlMappingResponse(EndpointModel, kw_only=True):
    id: int
    control_id: int
    finding_type: str
    finding_id: str
    status: str
    evidence: str
    remediation_notes: str
    found_at: datetime
    remediated_at: datetime | None = None
    verified_at: datetime | None = None

class ComplianceReportResponse(EndpointModel, kw_only=True):
    id: int
    framework_id: int
    total_controls: int
    compliant_controls: int
    partially_compliant_controls: int
    non_compliant_controls: int
    compliance_percentage: float
    risk_score: float
    trend: str
    scope: str
    generated_at: datetime

# Frameworks Endpoints
@router.post("/frameworks", response_model=ComplianceFrameworkResponse, status_code=status.HTTP_201_CREATED)
async def create_framework(
    req: ComplianceFrameworkCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create compliance framework for organization."""
    
    try:
        framework = await ComplianceFramework.create(
            organization_id=org_id,
            framework_type=req.framework_type,
            name=req.name,
            description=req.description,
            version=req.version,
        )
        return ComplianceFrameworkResponse(**{f: getattr(framework, f) for f in ComplianceFrameworkResponse.__struct_fields__})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create framework: {str(e)}")

@router.get("/frameworks", response_model=list[ComplianceFrameworkResponse])
async def list_frameworks(
    org_id: int = Query(..., description="Organization ID"),
    is_active: bool | None = None,
):
    """List compliance frameworks for organization."""
    
    query = ComplianceFramework.filter(organization_id=org_id)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    frameworks = await query.all()
    return [ComplianceFrameworkResponse(**{f: getattr(fw, f) for f in ComplianceFrameworkResponse.__struct_fields__}) for fw in frameworks]

@router.get("/frameworks/{framework_id}", response_model=ComplianceFrameworkResponse)
async def get_framework(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get specific compliance framework."""
    
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    return ComplianceFrameworkResponse(**{f: getattr(framework, f) for f in ComplianceFrameworkResponse.__struct_fields__})

# Controls Endpoints
@router.post("/frameworks/{framework_id}/controls", response_model=FrameworkControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(
    framework_id: int,
    req: FrameworkControlCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create control within framework."""
    
    # Verify framework exists
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    try:
        control = await FrameworkControl.create(
            framework_id=framework_id,
            control_id=req.control_id,
            name=req.name,
            description=req.description,
            category=req.category,
            cwe_ids=req.cwe_ids,
            mitre_techniques=req.mitre_techniques,
            priority=req.priority,
            risk_impact=req.risk_impact,
        )
        return FrameworkControlResponse(**{f: getattr(control, f) for f in FrameworkControlResponse.__struct_fields__})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create control: {str(e)}")

@router.get("/frameworks/{framework_id}/controls", response_model=list[FrameworkControlResponse])
async def list_controls(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
    category: str | None = None,
):
    """List controls in framework."""
    
    # Verify framework exists
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    query = FrameworkControl.filter(framework_id=framework_id)
    if category:
        query = query.filter(category=category)
    
    controls = await query.all()
    return [FrameworkControlResponse(**{f: getattr(c, f) for f in FrameworkControlResponse.__struct_fields__}) for c in controls]

# Mappings Endpoints
@router.post("/mappings", response_model=ControlMappingResponse, status_code=status.HTTP_201_CREATED)
async def create_mapping(
    req: ControlMappingCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Map finding to compliance control."""
    
    # Verify control exists in org's framework
    control = await FrameworkControl.get_or_none(id=req.control_id)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    framework = await ComplianceFramework.get_or_none(id=control.framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=403, detail="Control not in org's framework")
    
    try:
        mapping = await ControlMapping.create(
            organization_id=org_id,
            control_id=req.control_id,
            finding_type=req.finding_type,
            finding_id=req.finding_id,
            status=req.status,
            evidence=req.evidence,
            remediation_notes=req.remediation_notes,
            found_at=req.found_at or datetime.now(timezone.utc),
        )
        return ControlMappingResponse(**{f: getattr(mapping, f) for f in ControlMappingResponse.__struct_fields__})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create mapping: {str(e)}")

@router.get("/mappings", response_model=list[ControlMappingResponse])
async def list_mappings(
    org_id: int = Query(..., description="Organization ID"),
    status_filter: str | None = Query(None, alias="status"),
    finding_type: str | None = None,
):
    """List control mappings for organization."""
    
    query = ControlMapping.filter(organization_id=org_id)
    if status_filter:
        query = query.filter(status=status_filter)
    if finding_type:
        query = query.filter(finding_type=finding_type)
    
    mappings = await query.order_by("-updated_at").all()
    return [ControlMappingResponse(**{f: getattr(m, f) for f in ControlMappingResponse.__struct_fields__}) for m in mappings]

@router.put("/mappings/{mapping_id}", response_model=ControlMappingResponse)
async def update_mapping(
    mapping_id: int,
    req: ControlMappingUpdate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update control mapping status and evidence."""
    
    mapping = await ControlMapping.get_or_none(id=mapping_id, organization_id=org_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    update_data = {f: getattr(req, f) for f in req.__struct_fields__ if getattr(req, f) is not None}
    # Remove None values (msgspec struct always has all fields)
    
    # Handle remediation date tracking
    if req.status == ComplianceStatus.COMPLIANT and not mapping.remediated_at:
        update_data["remediated_at"] = datetime.now(timezone.utc)
    
    await mapping.update_from_dict(update_data).save()
    return ControlMappingResponse(**{f: getattr(mapping, f) for f in ControlMappingResponse.__struct_fields__})

# Reports Endpoints
@router.post("/reports/{framework_id}/generate", response_model=ComplianceReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_report(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
    scope: str = Query("all systems", description="Report scope"),
):
    """
    Generate compliance report for framework.
    
    Calculates:
    - Compliant / partially compliant / non-compliant control counts
    - Overall compliance percentage
    - Risk score
    - Trend vs previous report
    """
    
    try:
        report_data = await report_generator.generate_report(org_id, framework_id, scope)
        
        report = await ComplianceReport.create(**report_data)
        return ComplianceReportResponse(**{f: getattr(report, f) for f in ComplianceReportResponse.__struct_fields__})
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate report: {str(e)}")

@router.get("/reports/{framework_id}", response_model=list[ComplianceReportResponse])
async def list_reports(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
    limit: int = Query(10, ge=1, le=100),
):
    """List compliance reports for framework (most recent first)."""
    
    # Verify framework exists in org
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    reports = await ComplianceReport.filter(
        organization_id=org_id,
        framework_id=framework_id,
    ).order_by("-generated_at").limit(limit).all()
    
    return [ComplianceReportResponse(**{f: getattr(r, f) for f in ComplianceReportResponse.__struct_fields__}) for r in reports]

@router.get("/reports/{framework_id}/latest", response_model=ComplianceReportResponse)
async def get_latest_report(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get most recent compliance report for framework."""
    
    report = await ComplianceReport.filter(
        organization_id=org_id,
        framework_id=framework_id,
    ).order_by("-generated_at").first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No reports found for framework")
    
    return ComplianceReportResponse(**{f: getattr(report, f) for f in ComplianceReportResponse.__struct_fields__})

__all__ = ["router"]
