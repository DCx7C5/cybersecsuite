"""Compliance management endpoints — frameworks, controls, mappings, reports."""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from datetime import datetime
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
class ComplianceFrameworkCreate(BaseModel):
    framework_type: str = Field(..., regex="^(nist_csf|nist_800_53|soc2|iso27001|cis|mitre_attck|hipaa|pci_dss)$")
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    version: str = "1.0"


class ComplianceFrameworkResponse(BaseModel):
    id: int
    framework_type: str
    name: str
    description: str
    version: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FrameworkControlCreate(BaseModel):
    control_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    category: str = Field(..., min_length=1, max_length=128)
    cwe_ids: list[str] = Field(default_factory=list)
    mitre_techniques: list[str] = Field(default_factory=list)
    priority: str = Field("medium", regex="^(critical|high|medium|low)$")
    risk_impact: str = ""


class FrameworkControlResponse(BaseModel):
    id: int
    control_id: str
    name: str
    description: str
    category: str
    cwe_ids: list[str]
    mitre_techniques: list[str]
    priority: str
    risk_impact: str


class ControlMappingCreate(BaseModel):
    control_id: int = Field(..., description="FrameworkControl ID")
    finding_type: str = Field(..., regex="^(incident|scan|evidence|assessment|audit)$")
    finding_id: str = Field(..., min_length=1, max_length=255)
    status: str = Field(..., regex="^(compliant|non_compliant|partially_compliant|not_applicable|unknown)$")
    evidence: str = ""
    remediation_notes: str = ""
    found_at: datetime | None = None


class ControlMappingUpdate(BaseModel):
    status: str | None = None
    evidence: str | None = None
    remediation_notes: str | None = None
    verified_at: datetime | None = None


class ControlMappingResponse(BaseModel):
    id: int
    control_id: int
    finding_type: str
    finding_id: str
    status: str
    evidence: str
    remediation_notes: str
    found_at: datetime
    remediated_at: datetime | None
    verified_at: datetime | None


class ComplianceReportResponse(BaseModel):
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
    # TODO: Check org authorization
    
    try:
        framework = await ComplianceFramework.create(
            organization_id=org_id,
            framework_type=req.framework_type,
            name=req.name,
            description=req.description,
            version=req.version,
        )
        return ComplianceFrameworkResponse.model_validate(framework)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create framework: {str(e)}")


@router.get("/frameworks", response_model=list[ComplianceFrameworkResponse])
async def list_frameworks(
    org_id: int = Query(..., description="Organization ID"),
    is_active: bool | None = None,
):
    """List compliance frameworks for organization."""
    # TODO: Check org authorization
    
    query = ComplianceFramework.filter(organization_id=org_id)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    frameworks = await query.all()
    return [ComplianceFrameworkResponse.model_validate(f) for f in frameworks]


@router.get("/frameworks/{framework_id}", response_model=ComplianceFrameworkResponse)
async def get_framework(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get specific compliance framework."""
    # TODO: Check org authorization
    
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    return ComplianceFrameworkResponse.model_validate(framework)


# Controls Endpoints
@router.post("/frameworks/{framework_id}/controls", response_model=FrameworkControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(
    framework_id: int,
    req: FrameworkControlCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create control within framework."""
    # TODO: Check org authorization + framework ownership
    
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
        return FrameworkControlResponse.model_validate(control)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create control: {str(e)}")


@router.get("/frameworks/{framework_id}/controls", response_model=list[FrameworkControlResponse])
async def list_controls(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
    category: str | None = None,
):
    """List controls in framework."""
    # TODO: Check org authorization + framework ownership
    
    # Verify framework exists
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    query = FrameworkControl.filter(framework_id=framework_id)
    if category:
        query = query.filter(category=category)
    
    controls = await query.all()
    return [FrameworkControlResponse.model_validate(c) for c in controls]


# Mappings Endpoints
@router.post("/mappings", response_model=ControlMappingResponse, status_code=status.HTTP_201_CREATED)
async def create_mapping(
    req: ControlMappingCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Map finding to compliance control."""
    # TODO: Check org authorization
    
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
            found_at=req.found_at or datetime.utcnow(),
        )
        return ControlMappingResponse.model_validate(mapping)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create mapping: {str(e)}")


@router.get("/mappings", response_model=list[ControlMappingResponse])
async def list_mappings(
    org_id: int = Query(..., description="Organization ID"),
    status_filter: str | None = Query(None, alias="status"),
    finding_type: str | None = None,
):
    """List control mappings for organization."""
    # TODO: Check org authorization
    
    query = ControlMapping.filter(organization_id=org_id)
    if status_filter:
        query = query.filter(status=status_filter)
    if finding_type:
        query = query.filter(finding_type=finding_type)
    
    mappings = await query.order_by("-updated_at").all()
    return [ControlMappingResponse.model_validate(m) for m in mappings]


@router.put("/mappings/{mapping_id}", response_model=ControlMappingResponse)
async def update_mapping(
    mapping_id: int,
    req: ControlMappingUpdate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update control mapping status and evidence."""
    # TODO: Check org authorization
    
    mapping = await ControlMapping.get_or_none(id=mapping_id, organization_id=org_id)
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    update_data = req.model_dump(exclude_unset=True)
    
    # Handle remediation date tracking
    if req.status == ComplianceStatus.COMPLIANT and not mapping.remediated_at:
        update_data["remediated_at"] = datetime.utcnow()
    
    await mapping.update_from_dict(update_data).save()
    return ControlMappingResponse.model_validate(mapping)


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
    # TODO: Check org authorization + framework ownership
    
    try:
        report_data = await report_generator.generate_report(org_id, framework_id, scope)
        
        report = await ComplianceReport.create(**report_data)
        return ComplianceReportResponse.model_validate(report)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate report: {str(e)}")


@router.get("/reports/{framework_id}", response_model=list[ComplianceReportResponse])
async def list_reports(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
    limit: int = Query(10, ge=1, le=100),
):
    """List compliance reports for framework (most recent first)."""
    # TODO: Check org authorization
    
    # Verify framework exists in org
    framework = await ComplianceFramework.get_or_none(id=framework_id, organization_id=org_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    reports = await ComplianceReport.filter(
        organization_id=org_id,
        framework_id=framework_id,
    ).order_by("-generated_at").limit(limit).all()
    
    return [ComplianceReportResponse.model_validate(r) for r in reports]


@router.get("/reports/{framework_id}/latest", response_model=ComplianceReportResponse)
async def get_latest_report(
    framework_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get most recent compliance report for framework."""
    # TODO: Check org authorization
    
    report = await ComplianceReport.filter(
        organization_id=org_id,
        framework_id=framework_id,
    ).order_by("-generated_at").first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No reports found for framework")
    
    return ComplianceReportResponse.model_validate(report)


__all__ = ["router"]
