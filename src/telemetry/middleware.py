"""Starlette ASGI middleware that records HTTP request latency per endpoint."""
from __future__ import annotations

import re
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from telemetry import record_event

# Paths to skip
_SKIP_PREFIXES = ("/health", "/static", "/favicon")

# Normalise dynamic segments to avoid cardinality explosion
_ID_PATTERNS = [
    (re.compile(r"/\d{1,18}(?=/|$)"), "/{id}"),
    (re.compile(r"/[0-9a-fA-F-]{32,}(?=/|$)"), "/{uuid}"),
]


def _normalise(path: str) -> str:
    for pat, rep in _ID_PATTERNS:
        path = pat.sub(rep, path)
    return path


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Record latency_ms for every HTTP request as a TelemetryEvent."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        key = _normalise(path)
        t0 = time.perf_counter()
        status = 0
        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            latency_ms = (time.perf_counter() - t0) * 1000
            await record_event(
                f"http.latency.{key}",
                latency_ms,
                labels={"method": request.method, "status": str(status)},
            )
        return response
