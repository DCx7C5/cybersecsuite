"""
Message Batches API — wrap Anthropic's batch inference endpoint.

Batch API processes up to 10,000 requests asynchronously at 50% cost discount.
Ideal for bulk forensic scans: IOC classification, log analysis, hash scoring.

Routes:
  POST   /v1/messages/batches                    — create a batch
  GET    /v1/messages/batches                    — list recent batches
  GET    /v1/messages/batches/{id}               — get batch status
  GET    /v1/messages/batches/{id}/results       — stream batch results (NDJSON)
  POST   /v1/messages/batches/{id}/cancel        — cancel a batch
  DELETE /v1/messages/batches/{id}               — delete a completed batch
"""


import json
import logging
from typing import Any

import anthropic
from anthropic.types.messages.batch_create_params import Request as BatchRequest
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse

from ai_proxy.providers.registry import get_provider

logger = logging.getLogger("ai_proxy.batches")


def _get_client(provider_id: str = "anthropic") -> anthropic.AsyncAnthropic | None:
    provider = get_provider(provider_id)
    if not provider:
        return None
    api_key = provider.get_api_key()
    if not api_key:
        return None
    return anthropic.AsyncAnthropic(
        api_key=api_key,
        base_url=provider.base_url,
        max_retries=2,
    )


async def create_batch(request: Request) -> JSONResponse:
    """
    POST /v1/messages/batches

    Body: {"requests": [{"custom_id": "req-1", "params": {<messages create params>}}]}
    Optional header X-Provider (default: anthropic).
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            {"error": {"message": "Invalid JSON body", "type": "invalid_request_error"}},
            status_code=400,
        )

    requests_list: list[dict[str, Any]] = body.get("requests") or []
    if not requests_list:
        return JSONResponse(
            {"error": {"message": "requests array is required", "type": "invalid_request_error"}},
            status_code=400,
        )

    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        batch_requests = [
            BatchRequest(
                custom_id=r["custom_id"],
                params=r["params"],
            )
            for r in requests_list
        ]
        batch = await client.messages.batches.create(requests=batch_requests)
        return JSONResponse(batch.model_dump(), status_code=200)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def list_batches(request: Request) -> JSONResponse:
    """GET /v1/messages/batches — list recent batches."""
    provider_id = request.headers.get("x-provider", "anthropic")
    limit = int(request.query_params.get("limit", 20))
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        batches: list[dict[str, Any]] = []
        async for batch in client.messages.batches.list(limit=limit):
            batches.append(batch.model_dump())
        return JSONResponse({"data": batches, "count": len(batches)})
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def get_batch(request: Request) -> JSONResponse:
    """GET /v1/messages/batches/{batch_id} — get batch status."""
    batch_id: str = request.path_params["batch_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        batch = await client.messages.batches.retrieve(batch_id)
        return JSONResponse(batch.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Batch {batch_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def get_batch_results(request: Request) -> StreamingResponse | JSONResponse:
    """
    GET /v1/messages/batches/{batch_id}/results

    Streams NDJSON; each line is a serialised BatchResult.
    Only available when batch.processing_status == 'ended'.
    """
    batch_id: str = request.path_params["batch_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    async def _stream():
        try:
            async for result in await client.messages.batches.results(batch_id):
                yield json.dumps(result.model_dump(), separators=(",", ":")).encode() + b"\n"
        finally:
            await client.close()

    return StreamingResponse(
        _stream(),
        media_type="application/x-ndjson",
        headers={"X-Batch-Id": batch_id},
    )


async def cancel_batch(request: Request) -> JSONResponse:
    """POST /v1/messages/batches/{batch_id}/cancel — cancel an in-progress batch."""
    batch_id: str = request.path_params["batch_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        batch = await client.messages.batches.cancel(batch_id)
        return JSONResponse(batch.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Batch {batch_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()


async def delete_batch(request: Request) -> JSONResponse:
    """DELETE /v1/messages/batches/{batch_id} — delete a completed batch and its results."""
    batch_id: str = request.path_params["batch_id"]
    provider_id = request.headers.get("x-provider", "anthropic")
    client = _get_client(provider_id)
    if not client:
        return JSONResponse(
            {"error": {"message": f"Provider {provider_id!r} not configured", "type": "configuration_error"}},
            status_code=503,
        )

    try:
        result = await client.messages.batches.delete(batch_id)
        return JSONResponse(result.model_dump())
    except anthropic.NotFoundError:
        return JSONResponse({"error": {"message": f"Batch {batch_id!r} not found"}}, status_code=404)
    except anthropic.APIStatusError as exc:
        return JSONResponse(
            {"error": {"message": exc.message, "type": "upstream_error"}},
            status_code=exc.status_code,
        )
    finally:
        await client.close()
