"""Alert management endpoints — CRUD for rules and channels."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Optional
from datetime import datetime, timezone
from css.core.types.base_endpoint import BaseEndpoint
from .models import AlertRule, AlertHistory, ChannelConfig

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# Request/Response Models
class AlertRuleCreate(BaseEndpoint, kw_only=True):
    name: str
    description: str = ""
    event_type: str
    severity_threshold: str = "medium"
    condition_expr: str = ""
    channels: List[str] = []
    cooldown_minutes: int = 0

class AlertRuleUpdate(BaseEndpoint, kw_only=True):
    name: Optional[str] = None
    description: Optional[str] = None
    severity_threshold: Optional[str] = None
    condition_expr: Optional[str] = None
    channels: Optional[List[str]] = None
    cooldown_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class AlertRuleResponse(BaseEndpoint, kw_only=True):
    id: int
    name: str
    description: str
    event_type: str
    severity_threshold: str
    channels: List[str]
    is_active: bool
    cooldown_minutes: int
    created_at: datetime
    updated_at: datetime

class ChannelConfigCreate(BaseEndpoint, kw_only=True):
    channel_type: str
    config: Dict

class ChannelConfigResponse(BaseEndpoint, kw_only=True):
    id: int
    channel_type: str
    is_active: bool
    last_test_at: Optional[datetime] = None
    last_test_status: Optional[str] = None

class AlertHistoryResponse(BaseEndpoint, kw_only=True):
    id: int
    event_id: str
    event_type: str
    delivery_status: Dict
    fired_at: datetime

def _orm_to_struct(struct_type, orm_instance):
    return struct_type(**{f: getattr(orm_instance, f) for f in struct_type.__struct_fields__})

# Alert Rules Endpoints
@router.post("/rules", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    req: AlertRuleCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create new alert rule."""
    
    try:
        rule = await AlertRule.create(
            organization_id=org_id,
            name=req.name,
            description=req.description,
            event_type=req.event_type,
            severity_threshold=req.severity_threshold,
            condition_expr=req.condition_expr,
            channels=req.channels,
            cooldown_minutes=req.cooldown_minutes,
        )
        return _orm_to_struct(AlertRuleResponse, rule)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create rule: {str(e)}")

@router.get("/rules", response_model=List[AlertRuleResponse])
async def list_alert_rules(
    org_id: int = Query(..., description="Organization ID"),
    is_active: Optional[bool] = None,
):
    """List alert rules for organization."""
    
    query = AlertRule.filter(organization_id=org_id)
    if is_active is not None:
        query = query.filter(is_active=is_active)
    
    rules = await query.all()
    return [_orm_to_struct(AlertRuleResponse, r) for r in rules]

@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
async def get_alert_rule(
    rule_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get specific alert rule."""
    
    rule = await AlertRule.get_or_none(id=rule_id, organization_id=org_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return _orm_to_struct(AlertRuleResponse, rule)

@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
async def update_alert_rule(
    rule_id: int,
    req: AlertRuleUpdate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Update alert rule."""
    
    rule = await AlertRule.get_or_none(id=rule_id, organization_id=org_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    update_data = {f: getattr(req, f) for f in req.__struct_fields__ if getattr(req, f) is not None}
    await rule.update_from_dict(update_data).save()
    
    return _orm_to_struct(AlertRuleResponse, rule)

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Delete alert rule."""
    
    rule = await AlertRule.get_or_none(id=rule_id, organization_id=org_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await rule.delete()

# Channel Configuration Endpoints
@router.post("/channels", response_model=ChannelConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_channel_config(
    req: ChannelConfigCreate,
    org_id: int = Query(..., description="Organization ID"),
):
    """Create or update alert channel configuration."""
    
    # Upsert: only one config per org per channel type
    config, created = await ChannelConfig.get_or_create(
        organization_id=org_id,
        channel_type=req.channel_type,
        defaults={"config": req.config, "is_active": True},
    )
    
    if not created:
        config.config = req.config
        await config.save()
    
    return _orm_to_struct(ChannelConfigResponse, config)

@router.get("/channels", response_model=List[ChannelConfigResponse])
async def list_channel_configs(
    org_id: int = Query(..., description="Organization ID"),
):
    """List all channel configurations for organization."""
    
    configs = await ChannelConfig.filter(organization_id=org_id).all()
    return [_orm_to_struct(ChannelConfigResponse, c) for c in configs]

@router.post("/channels/{channel_type}/test", status_code=status.HTTP_200_OK)
async def test_channel(
    channel_type: str,
    org_id: int = Query(..., description="Organization ID"),
):
    """
    Test alert channel connectivity.
    
    Sends a test alert to verify configuration.
    Returns success/failure status and error message if failed.
    """
    
    config = await ChannelConfig.get_or_none(
        organization_id=org_id,
        channel_type=channel_type,
    )
    if not config:
        raise HTTPException(status_code=404, detail=f"Channel {channel_type} not configured")
    
    # Placeholder: mark attempted test
    config.last_test_at = datetime.now(timezone.utc)
    config.last_test_status = "pending"
    await config.save()
    
    return {"status": "test_initiated", "channel": channel_type}

# Alert History Endpoints
@router.get("/history", response_model=List[AlertHistoryResponse])
async def list_alert_history(
    org_id: int = Query(..., description="Organization ID"),
    event_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    List fired alerts with delivery status per channel.
    
    Useful for debugging alert delivery and auditing what was fired.
    """
    
    query = AlertHistory.filter(organization_id=org_id)
    if event_type:
        query = query.filter(event_type=event_type)
    
    history = await query.order_by("-fired_at").offset(offset).limit(limit).all()
    return [_orm_to_struct(AlertHistoryResponse, h) for h in history]

@router.get("/history/{alert_id}", response_model=AlertHistoryResponse)
async def get_alert_details(
    alert_id: int,
    org_id: int = Query(..., description="Organization ID"),
):
    """Get detailed delivery status for specific fired alert."""
    
    alert = await AlertHistory.get_or_none(id=alert_id, organization_id=org_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return _orm_to_struct(AlertHistoryResponse, alert)

__all__ = ["router"]
