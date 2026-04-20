"""Reverse proxy for the TypeScript SDK API server (port 8765).

All requests to /ts/* are forwarded to http://127.0.0.1:8765/ts/*.
Streaming responses (SSE) are passed through as StreamingResponse so
the browser receives events incrementally.
"""

from __future__ import annotations

import os

import httpx
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp, Receive, Scope, Send

_TS_API_URL = os.getenv("TS_API_URL", "http://127.0.0.1:8765")

_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
    }
)


async def _ts_proxy_handler(request: Request) -> Response:
    path = request.url.path
    query = request.url.query
    target = f"{_TS_API_URL}{path}"
    if query:
        target = f"{target}?{query}"

    fwd_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP
    }

    body = await request.body()

    async def _stream_upstream():
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                request.method,
                target,
                content=body,
                headers=fwd_headers,
            ) as resp:
                async for chunk in resp.aiter_raw():
                    yield chunk

    # Probe the response headers before deciding whether to stream.
    # We do a non-streaming call for non-SSE responses to capture headers.
    content_type = ""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                request.method,
                target,
                content=body,
                headers=fwd_headers,
            )
        content_type = resp.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            # Fall through to streaming path below
            raise _IsSSE()

        # Filter hop-by-hop headers from upstream
        resp_headers = {
            k: v
            for k, v in resp.headers.items()
            if k.lower() not in _HOP_BY_HOP
        }
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
            media_type=content_type or None,
        )
    except _IsSSE:
        pass
    except httpx.ConnectError:
        return Response(
            content='{"error":"TypeScript API server not running (port 8765)"}',
            status_code=502,
            media_type="application/json",
        )

    # SSE: stream bytes through
    return StreamingResponse(
        _stream_upstream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


class _IsSSE(Exception):
    pass


class _TsApiProxyApp:
    """ASGI app for the TypeScript API proxy mount."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return
        request = Request(scope, receive, send)
        response = await _ts_proxy_handler(request)
        await response(scope, receive, send)


ts_api_proxy: ASGIApp = _TsApiProxyApp()
