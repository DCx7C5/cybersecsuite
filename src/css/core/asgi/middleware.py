"""Starlette ASGI middleware for telemetry, HTTPS redirect, and rate limiting."""


import re
import time
import os
from pathlib import Path
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, RedirectResponse

from telemetry import record_event

PathPattern = tuple[re.Pattern, str]
ASGI_TLS_PORT = int(os.environ.get("ASGI_TLS_PORT", "8433"))
_TLS_CERT = os.environ.get("ASGI_TLS_CERT", str(Path.home() / ".css" / "certs" / "cert.pem"))
_TLS_KEY = os.environ.get("ASGI_TLS_KEY", str(Path.home() / ".css" / "certs" / "key.pem"))
TLS_AVAILABLE = Path(_TLS_CERT).is_file() and Path(_TLS_KEY).is_file()

# Paths to skip
_SKIP_PREFIXES = ("/health", "/static", "/favicon")

# Normalize dynamic segments to avoid cardinality explosion
_ID_PATTERNS = [
    (re.compile(r"/\d{1,18}(?=/|$)"), "/{id}"),
    (re.compile(r"/[0-9a-fA-F-]{32,}(?=/|$)"), "/{uuid}"),
]

def should_skip_path(path: str, skip_prefixes: list[str]) -> bool:
    """Check if a path should be skipped based on prefix list."""
    return any(path.startswith(p) for p in skip_prefixes)



def normalize_path_patterns(path: str, patterns: list[PathPattern]) -> str:
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


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory request limiter keyed by team and provider.

    Limits are request-per-minute windows and are enforced for API routes.
    Team and provider are resolved from request headers/query params:
      - team: ``x-team-id`` header or ``team_id`` query param
      - provider: ``x-provider`` header or ``provider`` query param
    """

    def __init__(
        self,
        app,
        team_limit_per_minute: int = 120,
        provider_limit_per_minute: int = 240,
    ) -> None:
        super().__init__(app)
        self.team_limit = max(1, team_limit_per_minute)
        self.provider_limit = max(1, provider_limit_per_minute)
        self._team_hits: dict[str, deque[float]] = defaultdict(deque)
        self._provider_hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _check_limit(self, bucket: dict[str, deque[float]], key: str, limit: int, now: float) -> tuple[bool, int]:
        window_start = now - 60.0
        q = bucket[key]
        while q and q[0] < window_start:
            q.popleft()
        if len(q) >= limit:
            retry_after = max(1, int(60 - (now - q[0])))
            return False, retry_after
        q.append(now)
        return True, 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if not path.startswith("/api") or should_skip_path(path, _SKIP_PREFIXES):
            return await call_next(request)

        team_id = request.headers.get("x-team-id") or request.query_params.get("team_id") or "anonymous"
        provider = request.headers.get("x-provider") or request.query_params.get("provider") or "default"
        now = time.time()

        with self._lock:
            team_ok, team_retry_after = self._check_limit(self._team_hits, team_id, self.team_limit, now)
            provider_ok, provider_retry_after = self._check_limit(
                self._provider_hits, provider, self.provider_limit, now
            )

        if not team_ok:
            return JSONResponse(
                status_code=429,
                content={"detail": "Team rate limit exceeded", "team_id": team_id, "retry_after": team_retry_after},
                headers={"Retry-After": str(team_retry_after)},
            )
        if not provider_ok:
            return JSONResponse(
                status_code=429,
                content={"detail": "Provider rate limit exceeded", "provider": provider, "retry_after": provider_retry_after},
                headers={"Retry-After": str(provider_retry_after)},
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Team-Limit"] = str(self.team_limit)
        response.headers["X-RateLimit-Provider-Limit"] = str(self.provider_limit)
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
