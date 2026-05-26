"""Incident management endpoints — CRUD, timeline, tasks."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional, Dict
from datetime import datetime, timezone
import msgspec
from css.core.types.base_endpoint import EndpointModel
from .models import (
    Incident,
    IncidentTimeline,
    IncidentTask,
    TimelineEventType,
)

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

# Request/Response Models
class IncidentCreate(EndpointModel, kw_only=True):
    title: str
    description: str = ""
    severity: str = "medium"
    source: str
    detected_at: datetime
    detection_method: str = ""
    affected_assets: List[str] = []
    affected_data_types: List[str] = []

class IncidentUpdate(EndpointModel, kw_only=True):
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

class IncidentResponse(EndpointModel, kw_only=True):
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

class TimelineEventCreate(EndpointModel, kw_only=True):
    event_type: str
    title: str
    description: str = ""
    metadata: Dict = {}
    occurred_at: datetime

class TimelineEventResponse(EndpointModel, kw_only=True):
    id: int
    sequence_number: int
    event_type: str
    actor: str
    title: str
    description: str
    occurred_at: datetime
    recorded_at: datetime

class IncidentTaskCreate(EndpointModel, kw_only=True):
    title: str
    description: str = ""
    task_type: str
    assigned_to: Optional[str] = None
    priority: str = "medium"
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None

class IncidentTaskResponse(EndpointModel, kw_only=True):
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

def _orm_to_struct(struct_type, orm_instance):
    return struct_type(**{f: getattr(orm_instance, f) for f in struct_type.__struct_fields__})

# Incident CRUD Endpoints
@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    req: IncidentCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create new incident."""
    
    try:
        incident_id = f"INC-{org_id}-{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        
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
            created_by="system",
        )
        
        await IncidentTimeline.create(
            incident_id=incident.id,
            sequence_number=1,
            event_type=TimelineEventType.CREATED,
            actor="system",
            title=f"Incident created from {req.source}",
            description=req.description,
            occurred_at=datetime.now(timezone.utc),
        )
        
        return _orm_to_struct(IncidentResponse, incident)
    
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
    
    query = Incident.filter(organization_id=org_id)
    if status_filter:
        query = query.filter(status=status_filter)
    if severity:
        query = query.filter(severity=severity)
    if assigned_to:
        query = query.filter(assigned_to=assigned_to)
    
    incidents = await query.order_by("-detected_at").limit(limit).all()
    return [_orm_to_struct(IncidentResponse, i) for i in incidents]

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get specific incident."""
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return _orm_to_struct(IncidentResponse, incident)

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: str,
    req: IncidentUpdate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update incident details."""
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    now = datetime.now(timezone.utc)
    update_data = {f: getattr(req, f) for f in req.__struct_fields__ if getattr(req, f) is not None}
    
    if "status" in update_data and update_data["status"] != incident.status:
        old_status = incident.status
        new_status = update_data["status"]
        
        await IncidentTimeline.create(
            incident_id=incident.id,
            sequence_number=len(await IncidentTimeline.filter(incident_id=incident.id)) + 1,
            event_type=TimelineEventType.STATUS_CHANGED,
            actor="system",
            title=f"Status changed from {old_status} to {new_status}",
            metadata={"from": old_status, "to": new_status},
            occurred_at=now,
        )
        
        if new_status == "investigating":
            incident.investigation_started_at = now
        elif new_status == "contained":
            incident.containment_completed_at = now
        elif new_status == "remediated":
            incident.remediation_completed_at = now
        elif new_status == "resolved":
            incident.resolved_at = now
        elif new_status == "closed":
            incident.closed_at = now
    
    await incident.update_from_dict(update_data).save()
    return _orm_to_struct(IncidentResponse, incident)

@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """Delete incident (typically only for drafts/duplicates)."""
    
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
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    events = await IncidentTimeline.filter(incident_id=incident.id).order_by("sequence_number").all()
    return [_orm_to_struct(TimelineEventResponse, e) for e in events]

@router.post("/{incident_id}/timeline", response_model=TimelineEventResponse, status_code=status.HTTP_201_CREATED)
async def add_timeline_event(
    incident_id: str,
    req: TimelineEventCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Record event in incident timeline."""
    
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
            actor="system",
            title=req.title,
            description=req.description,
            metadata=req.metadata,
            occurred_at=req.occurred_at,
        )
        
        return _orm_to_struct(TimelineEventResponse, event)
    
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
        return _orm_to_struct(IncidentTaskResponse, task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create task: {str(e)}")

@router.get("/{incident_id}/tasks", response_model=List[IncidentTaskResponse])
async def list_incident_tasks(
    incident_id: str,
    org_id: int = Query(..., description="Organization ID"),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List tasks for incident."""
    
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
    return [_orm_to_struct(IncidentTaskResponse, t) for t in tasks]

@router.put("/{incident_id}/tasks/{task_id}", response_model=IncidentTaskResponse)
async def update_incident_task(
    incident_id: str,
    task_id: int,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update incident task status or assignment."""
    
    incident = await Incident.get_or_none(
        organization_id=org_id,
        incident_id=incident_id,
    )
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    task = await IncidentTask.get_or_none(id=task_id, incident_id=incident.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    now = datetime.now(timezone.utc)
    update_data = {}
    if status:
        update_data["status"] = status
        if status == "completed":
            update_data["completed_at"] = now
        elif status == "in_progress" and not task.started_at:
            update_data["started_at"] = now
    
    if assigned_to:
        update_data["assigned_to"] = assigned_to
    
    await task.update_from_dict(update_data).save()
    return _orm_to_struct(IncidentTaskResponse, task)

__all__ = ["router"]
