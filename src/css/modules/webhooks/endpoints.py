"""Webhook management endpoints."""

from __future__ import annotations

from typing import Any

import msgspec
from css.core.types.base_endpoint import EndpointModel
from fastapi import APIRouter, HTTPException, Query, status

from .dispatcher import WebhookDispatcher
from .models import WebhookDelivery, WebhookEndpoint

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
dispatcher = WebhookDispatcher()


class WebhookCreateRequest(EndpointModel, kw_only=True):
    name: str
    url: str
    secret: str = ""
    event_filter: list[str] = []
    retry_policy: dict[str, Any] = msgspec.field(
        default_factory=lambda: {"max_attempts": 3, "base_delay_seconds": 2},
    )


@router.post("/endpoints", status_code=status.HTTP_201_CREATED)
async def create_endpoint(req: WebhookCreateRequest, org_id: int = Query(..., description="Organization ID")) -> dict:
    endpoint = await WebhookEndpoint.create(
        organization_id=org_id,
        name=req.name,
        url=req.url,
        secret=req.secret,
        event_filter=req.event_filter,
        retry_policy=req.retry_policy,
    )
    return {"id": endpoint.id, "name": endpoint.name, "status": "created"}


@router.get("/endpoints")
async def list_endpoints(org_id: int = Query(..., description="Organization ID")) -> list[dict]:
    endpoints = await WebhookEndpoint.filter(organization_id=org_id).all()
    return [
        {
            "id": endpoint.id,
            "name": endpoint.name,
            "url": endpoint.url,
            "event_filter": endpoint.event_filter,
            "is_active": endpoint.is_active,
        }
        for endpoint in endpoints
    ]


@router.post("/dispatch", status_code=status.HTTP_202_ACCEPTED)
async def dispatch_event(
    event_type: str = Query(..., min_length=1),
    org_id: int = Query(..., description="Organization ID"),
    payload: dict[str, Any] | None = None,
) -> dict:
    deliveries = await dispatcher.dispatch(
        organization_id=org_id,
        event_type=event_type,
        payload=payload or {},
    )
    return {"status": "dispatched", "delivery_count": len(deliveries)}


@router.get("/deliveries")
async def list_deliveries(
    org_id: int = Query(..., description="Organization ID"),
    event_type: str | None = None,
    limit: int = Query(100, ge=1, le=1000),
) -> list[dict]:
    endpoint_ids = [endpoint.id for endpoint in await WebhookEndpoint.filter(organization_id=org_id).all()]
    if not endpoint_ids:
        return []

    query = WebhookDelivery.filter(endpoint_id__in=endpoint_ids)
    if event_type:
        query = query.filter(event_type=event_type)

    deliveries = await query.order_by("-dispatched_at").limit(limit).all()
    return [
        {
            "id": delivery.id,
            "endpoint_id": delivery.endpoint_id,
            "event_type": delivery.event_type,
            "attempt": delivery.attempt,
            "status": delivery.status,
            "response_code": delivery.response_code,
            "error": delivery.error,
            "dispatched_at": delivery.dispatched_at.isoformat(),
        }
        for delivery in deliveries
    ]


@router.delete("/endpoints/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_endpoint(endpoint_id: int, org_id: int = Query(..., description="Organization ID")) -> None:
    endpoint = await WebhookEndpoint.get_or_none(id=endpoint_id, organization_id=org_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    await endpoint.delete()
