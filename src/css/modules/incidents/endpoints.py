"""Incident management endpoints — CRUD, timeline, tasks."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from .models import (
    Incident,
    IncidentTimeline,
    IncidentTask,
    SeverityLevel,
    IncidentStatus,
    IncidentSource,
    TimelineEventType,
)

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


# Request/Response Models
class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    severity: str = Field("medium", regex="^(low|medium|high|critical)$")
    source: str = Field(..., regex="^(alert|scan|manual_report|threat_intel|hunt|log_analysis|edr|other)$")
    detected_at: datetime
    detection_method: str = ""
    affected_assets: List[str] = Field(default_factory=list)
    affected_data_types: List[str] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    assigned_team_id: Optional[str] = None
    assigned_to: Optional[str] = None
    affected_assets: Optional[List[str]] = None
    affected_data_types: Optional[List[str]] = None
    root_cause: Optional[str] = None
    lessons_learned: Optional[str] = None


class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    title: str
    description: str
    severity: str
    source: str
    status: str
    detected_at: datetime
    affected_assets: List[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime


class TimelineEventCreate(BaseModel):
    event_type: str = Field(..., regex="^(created|updated|escalated|assigned|status_changed|investigation_started|containment_started|containment_completed|remediation_started|remediation_completed|resolved|closed|comment|reopened)$")
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    metadata: Dict = Field(default_factory=dict)
    occurred_at: datetime = Field(..., description="When event occurred")


class TimelineEventResponse(BaseModel):
    id: int
    sequence_number: int
    event_type: str
    actor: str
    title: str
    description: str
    occurred_at: datetime
    recorded_at: datetime


class IncidentTaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    task_type: str = Field(..., regex="^(triage|investigation|containment|remediation|recovery|forensics)$")
    assigned_to: Optional[str] = None
    priority: str = Field("medium", regex="^(low|medium|high|critical)$")
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None


class IncidentTaskResponse(BaseModel):
    id: int
    incident_id: int
    title: str
    description: str
    task_type: str
    status: str
    assigned_to: Optional[str]
    priority: str
    created_at: datetime
    updated_at: datetime


# Incident CRUD Endpoints
@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    req: IncidentCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create new incident."""
    # TODO: Check org authorization
    
    try:
        # Generate incident ID
        incident_id = f"INC-{org_id}-{int(datetime.utcnow().timestamp() * 1000)}"
        
        incident = await Incident.create(
            organization_id=org_id,
            incident_id=incident_id,
            title=req.title,
            description=req.description,
            severity=req.severity,
            source=req.source,
            detected_at=req.detected_at,
            first_detection_at=req.detected_at,
            detection_method=req.detection_method,
            affected_assets=req.affected_assets,
            affected_data_types=req.affected_data_types,
            status="open",
            created_by="system",  # TODO: Get from auth context
        )
        
        # Create initial timeline event
        await IncidentTimeline.create(
            incident_id=incident.id,
            sequence_number=1,
            event_type=TimelineEventType.CREATED,
            actor="system",
            title=f"Incident created from {req.source}",
            description=req.description,
            occurred_at=datetime.utcnow(),
        )
        
        return IncidentResponse.model_validate(incident)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create incident: {str(e)}")


@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    org_id: int = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
):
    """List incidents for organization."""
    # TODO: Check org authorization
    
    query = Incident.filter(organization_id=org_id)
    if status_filter:
        query = query.filter(status=status_filter)
    if severity:
        query = query.filter(severity=severity)
    if assigned_to:
        query = query.filter(assigned_to=assigned_to)
    
    incidents = await query.order_by("-detected_at").limit(limit).all()
    return [IncidentResponse.model_validate(i) for i in incidents]


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get specific incident."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return IncidentResponse.model_validate(incident)


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    req: IncidentUpdate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update incident details."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    update_data = req.model_dump(exclude_unset=True)
    
    # Track status changes in timeline
    if "status" in update_data and update_data["status"] != incident.status:
        old_status = incident.status
        new_status = update_data["status"]
        
        await IncidentTimeline.create(
            incident_id=incident.id,
            sequence_number=len(await IncidentTimeline.filter(incident_id=incident.id)) + 1,
            event_type=TimelineEventType.STATUS_CHANGED,
            actor="system",  # TODO: Get from auth context
            title=f"Status changed from {old_status} to {new_status}",
            metadata={"from": old_status, "to": new_status},
            occurred_at=datetime.utcnow(),
        )
        
        # Update lifecycle timestamps based on status
        if new_status == "investigating":
            incident.investigation_started_at = datetime.utcnow()
        elif new_status == "contained":
            incident.containment_completed_at = datetime.utcnow()
        elif new_status == "remediated":
            incident.remediation_completed_at = datetime.utcnow()
        elif new_status == "resolved":
            incident.resolved_at = datetime.utcnow()
        elif new_status == "closed":
            incident.closed_at = datetime.utcnow()
    
    await incident.update_from_dict(update_data).save()
    return IncidentResponse.model_validate(incident)


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Delete incident (typically only for drafts/duplicates)."""
    # TODO: Check org authorization
    # TODO: Add audit log entry
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    await incident.delete()


# Timeline Endpoints
@router.get("/{incident_id}/timeline", response_model=List[TimelineEventResponse])
async def get_incident_timeline(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get incident timeline — all events in sequence."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    events = await IncidentTimeline.filter(incident_id=incident.id).order_by("sequence_number").all()
    return [TimelineEventResponse.model_validate(e) for e in events]


@router.post("/{incident_id}/timeline", response_model=TimelineEventResponse, status_code=status.HTTP_201_CREATED)
async def add_timeline_event(
    incident_id: str,
    req: TimelineEventCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Record event in incident timeline."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    try:
        seq_num = len(await IncidentTimeline.filter(incident_id=incident.id)) + 1
        
        event = await IncidentTimeline.create(
            incident_id=incident.id,
            sequence_number=seq_num,
            event_type=req.event_type,
            actor="system",  # TODO: Get from auth context
            title=req.title,
            description=req.description,
            metadata=req.metadata,
            occurred_at=req.occurred_at,
        )
        
        return TimelineEventResponse.model_validate(event)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create timeline event: {str(e)}")


# Task Endpoints
@router.post("/{incident_id}/tasks", response_model=IncidentTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_task(
    incident_id: str,
    req: IncidentTaskCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create task for incident investigation/remediation."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    try:
        task = await IncidentTask.create(
            incident_id=incident.id,
            title=req.title,
            description=req.description,
            task_type=req.task_type,
            assigned_to=req.assigned_to,
            priority=req.priority,
            estimated_hours=req.estimated_hours,
            due_date=req.due_date,
        )
        return IncidentTaskResponse.model_validate(task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create task: {str(e)}")


@router.get("/{incident_id}/tasks", response_model=List[IncidentTaskResponse])
async def list_incident_tasks(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List tasks for incident."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    query = IncidentTask.filter(incident_id=incident.id)
    if status_filter:
        query = query.filter(status=status_filter)
    
    tasks = await query.all()
    return [IncidentTaskResponse.model_validate(t) for t in tasks]


@router.put("/{incident_id}/tasks/{task_id}", response_model=IncidentTaskResponse)
async def update_incident_task(
    incident_id: str,
    task_id: int,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update incident task status or assignment."""
    # TODO: Check org authorization
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    task = await IncidentTask.get_or_none(id=task_id, incident_id=incident.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data = {}
    if status:
        update_data["status"] = status
        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
        elif status == "in_progress" and not task.started_at:
            update_data["started_at"] = datetime.utcnow()
    
    if assigned_to:
        update_data["assigned_to"] = assigned_to
    
    await task.update_from_dict(update_data).save()
    return IncidentTaskResponse.model_validate(task)


__all__ = ["router"]
