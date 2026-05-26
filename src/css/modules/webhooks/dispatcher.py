"""Async webhook dispatcher with HMAC signing and retry."""


import hashlib
import hmac
import json
from typing import Any

import aiohttp

from .models import WebhookDelivery, WebhookEndpoint


class WebhookDispatcher:
    """Dispatches events to active webhook endpoints."""

    async def dispatch(self, organization_id: int, event_type: str, payload: dict[str, Any]) -> list[WebhookDelivery]:
        endpoints = await WebhookEndpoint.filter(organization_id=organization_id, is_active=True).all()
        deliveries: list[WebhookDelivery] = []
        for endpoint in endpoints:
            if endpoint.event_filter and event_type not in endpoint.event_filter:
                continue
            deliveries.append(await self._deliver_with_retry(endpoint, event_type, payload))
        return deliveries

    async def _deliver_with_retry(
        self,
        endpoint: WebhookEndpoint,
        event_type: str,
        payload: dict[str, Any],
    ) -> WebhookDelivery:
        retry_policy = endpoint.retry_policy or {}
        max_attempts = int(retry_policy.get("max_attempts", 3))
        base_delay = float(retry_policy.get("base_delay_seconds", 2))
        body = json.dumps(payload, separators=(",", ":"))

        delivery = await WebhookDelivery.create(
            endpoint_id=endpoint.id,
            event_type=event_type,
            payload=payload,
            attempt=1,
            status="pending",
        )

        for attempt in range(1, max_attempts + 1):
            headers = self._build_headers(endpoint.secret, event_type, body)
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.post(endpoint.url, data=body, headers=headers)
                    response_text = await response.text()
                    if 200 <= response.status < 300:
                        delivery.attempt = attempt
                        delivery.status = "success"
                        delivery.response_code = response.status
                        delivery.response_body = response_text[:2048]
                        await delivery.save()
                        return delivery
                    delivery.attempt = attempt
                    delivery.status = "retrying" if attempt < max_attempts else "failed"
                    delivery.response_code = response.status
                    delivery.response_body = response_text[:2048]
                    await delivery.save()
                except aiohttp.ClientError as exc:
                    delivery.attempt = attempt
                    delivery.status = "retrying" if attempt < max_attempts else "failed"
                    delivery.error = str(exc)
                    await delivery.save()

            if attempt < max_attempts:
                await asyncio_sleep(base_delay * (2 ** (attempt - 1)))
        return delivery

    @staticmethod
    def _build_headers(secret: str, event_type: str, payload: str) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "X-Webhook-Event": event_type}
        if secret:
            signature = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
            headers["X-Webhook-Signature"] = f"sha256={signature}"
        return headers


async def asyncio_sleep(seconds: float) -> None:
    import asyncio

    await asyncio.sleep(seconds)
