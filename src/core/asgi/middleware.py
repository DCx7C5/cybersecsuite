"""Starlette ASGI middleware that records HTTP request latency per endpoint."""


import re
import time
from typing import Callable, List, Tuple

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse

from .app import TLS_AVAILABLE, ASGI_TLS_PORT
from telemetry import record_event

PathPattern = Tuple[re.Pattern, str]

# Paths to skip
_SKIP_PREFIXES = ("/health", "/static", "/favicon")

# Normalize dynamic segments to avoid cardinality explosion
_ID_PATTERNS = [
    (re.compile(r"/\d{1,18}(?=/|$)"), "/{id}"),
    (re.compile(r"/[0-9a-fA-F-]{32,}(?=/|$)"), "/{uuid}"),
]

def should_skip_path(path: str, skip_prefixes: List[str]) -> bool:
    """Check if a path should be skipped based on prefix list."""
    return any(path.startswith(p) for p in skip_prefixes)



def normalize_path_patterns(path: str, patterns: List[PathPattern]) -> str:
    """Normalize path by replacing patterns (e.g., numeric IDs with placeholders)."""
    for pat, rep in patterns:
        path = pat.sub(rep, path)
    return path


class TelemetryMiddleware(BaseHTTPMiddleware):
    """Record latency_ms for every HTTP request as a TelemetryEvent."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if should_skip_path(path, _SKIP_PREFIXES):
            return await call_next(request)

        key = normalize_path_patterns(path, _ID_PATTERNS)
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


class HTTPSRedirectMiddleware:
    """Redirect HTTP to HTTPS if TLS is enabled, otherwise no-op."""

    def __init__(self, app, tls_enabled: bool = TLS_AVAILABLE) -> None:
        self.app = app
        self.tls_enabled = tls_enabled

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] == "http" and self.tls_enabled:
            headers = dict(scope.get("headers", []))
            host = headers.get(b"host", b"localhost:8000").decode()
            if ":" in host:
                host = host.rsplit(":", 1)[0]
            path = scope.get("root_path", "") + scope.get("path", "/")
            new_url = f"https://{host}:{ASGI_TLS_PORT}{path}"
            response = RedirectResponse(new_url)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)
