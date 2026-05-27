"""Browser plugin relay endpoints and bounded in-memory request state."""

import asyncio
from datetime import UTC, datetime, timedelta
from typing import Any, Literal, TypedDict
import uuid

from fastapi import APIRouter, Body, HTTPException, Query, status

from css.core.types.base_endpoint import BaseEndpoint

RequestStatus = Literal["pending", "in_progress", "completed", "failed", "expired"]


class PluginRegistrationRequest(BaseEndpoint, kw_only=True, frozen=True):
    """Payload sent by the browser extension on startup and refresh."""

    domain: str = "browser-plugin"
    version: str = "3.0"
    timestamp: int | None = None
    session_id: str | None = None


class PluginRegistrationResponse(BaseEndpoint, kw_only=True, frozen=True):
    """Session metadata returned to the browser extension."""

    plugin_session_id: str
    dashboard_version: str
    expires_at: datetime


class PluginHeartbeatRequest(BaseEndpoint, kw_only=True, frozen=True):
    plugin_session_id: str


class PluginHeartbeatResponse(BaseEndpoint, kw_only=True, frozen=True):
    plugin_session_id: str
    status: str
    expires_at: datetime


class BrowserInjectionRequest(BaseEndpoint, kw_only=True, frozen=True):
    """Queue one browser-side execution request."""

    session_id: str
    prompt: str
    provider: str = "browser-relay"
    model: str = "browser-relay/default"
    request_id: str | None = None
    ttl_seconds: int | None = None
    metadata: dict[str, str] | None = None


class BrowserInjectionAccepted(BaseEndpoint, kw_only=True, frozen=True):
    request_id: str
    session_id: str
    status: str
    expires_at: datetime


class BrowserResultSubmission(BaseEndpoint, kw_only=True, frozen=True):
    """Store browser-side completion result for a queued relay request."""

    session_id: str
    request_id: str
    status: Literal["completed", "failed"] = "completed"
    content: str = ""
    stop_reason: str = "stop"
    error_code: str | None = None
    error_message: str | None = None
    usage: dict[str, Any] | None = None


class BrowserResultResponse(BaseEndpoint, kw_only=True, frozen=True):
    request_id: str
    session_id: str
    status: str
    provider: str
    model: str
    expires_at: datetime
    content: str | None = None
    stop_reason: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    usage: dict[str, Any] | None = None


class BrowserNextInjectionResponse(BaseEndpoint, kw_only=True, frozen=True):
    available: bool
    request_id: str | None = None
    session_id: str | None = None
    prompt: str | None = None
    provider: str | None = None
    model: str | None = None
    expires_at: datetime | None = None


class StoredResult(TypedDict):
    content: str
    stop_reason: str
    error_code: str | None
    error_message: str | None
    usage: dict[str, Any]


class StoredRequest(TypedDict):
    request_id: str
    session_id: str
    provider: str
    model: str
    prompt: str
    status: RequestStatus
    created_at: datetime
    expires_at: datetime
    metadata: dict[str, str]
    result: StoredResult | None


class BrowserPluginSessionStore:
    """Bounded in-memory state for browser relay sessions and requests."""

    def __init__(
        self,
        *,
        session_ttl_seconds: int = 90,
        request_ttl_seconds: int = 120,
        retention_ttl_seconds: int = 180,
    ) -> None:
        self._session_ttl = timedelta(seconds=max(10, session_ttl_seconds))
        self._request_ttl_seconds = max(1, request_ttl_seconds)
        self._retention_ttl = timedelta(seconds=max(10, retention_ttl_seconds))
        self._sessions: dict[str, datetime] = {}
        self._requests: dict[str, StoredRequest] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)

    def _prune_locked(self, now: datetime) -> None:
        expired_sessions = [
            session_id
            for session_id, expires_at in self._sessions.items()
            if expires_at <= now
        ]
        for session_id in expired_sessions:
            self._sessions.pop(session_id, None)

        for record in self._requests.values():
            if record["status"] in {"pending", "in_progress"} and record["expires_at"] <= now:
                record["status"] = "expired"
                record["result"] = None

        removable_ids = [
            request_id
            for request_id, record in self._requests.items()
            if record["expires_at"] + self._retention_ttl <= now
        ]
        for request_id in removable_ids:
            self._requests.pop(request_id, None)

    def _ensure_session_locked(self, session_id: str, now: datetime) -> None:
        expires_at = self._sessions.get(session_id)
        if expires_at is None or expires_at <= now:
            self._sessions.pop(session_id, None)
            raise KeyError(session_id)

    async def register_plugin(self, session_id: str | None = None) -> tuple[str, datetime]:
        now = self._now()
        async with self._lock:
            self._prune_locked(now)
            plugin_session_id = session_id.strip() if isinstance(session_id, str) and session_id.strip() else f"plugin_{uuid.uuid4().hex}"
            expires_at = now + self._session_ttl
            self._sessions[plugin_session_id] = expires_at
            return plugin_session_id, expires_at

    async def heartbeat(self, session_id: str) -> datetime:
        now = self._now()
        async with self._lock:
            self._prune_locked(now)
            self._ensure_session_locked(session_id, now)
            expires_at = now + self._session_ttl
            self._sessions[session_id] = expires_at
            return expires_at

    async def submit_injection(
        self,
        *,
        session_id: str,
        prompt: str,
        provider: str,
        model: str,
        request_id: str | None = None,
        ttl_seconds: int | None = None,
        metadata: dict[str, str] | None = None,
    ) -> StoredRequest:
        now = self._now()
        async with self._lock:
            self._prune_locked(now)
            self._ensure_session_locked(session_id, now)

            resolved_request_id = request_id.strip() if isinstance(request_id, str) and request_id.strip() else f"relay_{uuid.uuid4().hex}"
            if resolved_request_id in self._requests:
                raise ValueError(f"request_id already exists: {resolved_request_id}")

            request_ttl = timedelta(seconds=max(1, ttl_seconds if isinstance(ttl_seconds, int) else self._request_ttl_seconds))
            record: StoredRequest = {
                "request_id": resolved_request_id,
                "session_id": session_id,
                "provider": provider,
                "model": model,
                "prompt": prompt,
                "status": "pending",
                "created_at": now,
                "expires_at": now + request_ttl,
                "metadata": dict(metadata or {}),
                "result": None,
            }
            self._requests[resolved_request_id] = record
            return record

    async def submit_result(
        self,
        *,
        session_id: str,
        request_id: str,
        status: Literal["completed", "failed"] = "completed",
        content: str,
        stop_reason: str = "stop",
        error_code: str | None = None,
        error_message: str | None = None,
        usage: dict[str, Any] | None = None,
    ) -> StoredRequest:
        now = self._now()
        async with self._lock:
            self._prune_locked(now)
            self._ensure_session_locked(session_id, now)

            record = self._requests.get(request_id)
            if record is None:
                raise KeyError(request_id)
            if record["session_id"] != session_id:
                raise PermissionError(request_id)
            if record["status"] == "expired":
                raise TimeoutError(request_id)

            record["status"] = status
            record["result"] = {
                "content": content,
                "stop_reason": stop_reason,
                "error_code": error_code,
                "error_message": error_message,
                "usage": dict(usage or {}),
            }
            return record

    async def claim_next_injection(self, *, session_id: str) -> StoredRequest | None:
        now = self._now()
        async with self._lock:
            self._prune_locked(now)
            self._ensure_session_locked(session_id, now)

            pending = [
                record
                for record in self._requests.values()
                if record["session_id"] == session_id and record["status"] == "pending"
            ]
            if not pending:
                return None

            pending.sort(key=lambda record: record["created_at"])
            record = pending[0]
            record["status"] = "in_progress"
            return record

    async def fetch_result(self, *, session_id: str, request_id: str) -> StoredRequest | None:
        now = self._now()
        async with self._lock:
            self._prune_locked(now)
            self._ensure_session_locked(session_id, now)

            record = self._requests.get(request_id)
            if record is None:
                return None
            if record["session_id"] != session_id:
                raise PermissionError(request_id)
            if record["status"] in {"pending", "in_progress"} and record["expires_at"] <= now:
                record["status"] = "expired"
                record["result"] = None
            return record

    async def put_result(
        self,
        *,
        session_id: str,
        request_id: str,
        status: Literal["completed", "failed"] = "completed",
        content: str,
        stop_reason: str = "stop",
        error_code: str | None = None,
        error_message: str | None = None,
        usage: dict[str, Any] | None = None,
    ) -> StoredRequest:
        return await self.submit_result(
            session_id=session_id,
            request_id=request_id,
            status=status,
            content=content,
            stop_reason=stop_reason,
            error_code=error_code,
            error_message=error_message,
            usage=usage,
        )

    async def get_result(self, *, session_id: str, request_id: str) -> StoredRequest | None:
        return await self.fetch_result(session_id=session_id, request_id=request_id)

    async def reset(self) -> None:
        async with self._lock:
            self._sessions.clear()
            self._requests.clear()


router = APIRouter(prefix="/api/plugin", tags=["browser-plugin"])
_SESSION_STORE = BrowserPluginSessionStore()


def get_browser_plugin_session_store() -> BrowserPluginSessionStore:
    return _SESSION_STORE


@router.post("/register", response_model=PluginRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_plugin(req: PluginRegistrationRequest = Body(...)) -> PluginRegistrationResponse:
    session_id, expires_at = await _SESSION_STORE.register_plugin(req.session_id)
    return PluginRegistrationResponse(
        plugin_session_id=session_id,
        dashboard_version="local-dev",
        expires_at=expires_at,
    )


@router.post("/heartbeat", response_model=PluginHeartbeatResponse)
async def heartbeat_plugin(req: PluginHeartbeatRequest = Body(...)) -> PluginHeartbeatResponse:
    try:
        expires_at = await _SESSION_STORE.heartbeat(req.plugin_session_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="plugin session not found") from exc
    return PluginHeartbeatResponse(
        plugin_session_id=req.plugin_session_id,
        status="ok",
        expires_at=expires_at,
    )


@router.post("/inject", response_model=BrowserInjectionAccepted, status_code=status.HTTP_202_ACCEPTED)
async def submit_injection(req: BrowserInjectionRequest = Body(...)) -> BrowserInjectionAccepted:
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="prompt must not be empty",
        )
    try:
        record = await _SESSION_STORE.submit_injection(
            session_id=req.session_id,
            prompt=prompt,
            provider=req.provider.strip() or "browser-relay",
            model=req.model.strip() or "browser-relay/default",
            request_id=req.request_id,
            ttl_seconds=req.ttl_seconds,
            metadata=req.metadata,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="plugin session not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return BrowserInjectionAccepted(
        request_id=record["request_id"],
        session_id=record["session_id"],
        status=record["status"],
        expires_at=record["expires_at"],
    )


@router.get("/inject/next", response_model=BrowserNextInjectionResponse)
async def fetch_next_injection(
    session_id: str = Query(..., min_length=1),
) -> BrowserNextInjectionResponse:
    try:
        record = await _SESSION_STORE.claim_next_injection(session_id=session_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="plugin session not found") from exc

    if record is None:
        return BrowserNextInjectionResponse(available=False)

    return BrowserNextInjectionResponse(
        available=True,
        request_id=record["request_id"],
        session_id=record["session_id"],
        prompt=record["prompt"],
        provider=record["provider"],
        model=record["model"],
        expires_at=record["expires_at"],
    )


@router.post("/result", response_model=BrowserResultResponse)
async def submit_result(req: BrowserResultSubmission = Body(...)) -> BrowserResultResponse:
    try:
        record = await _SESSION_STORE.put_result(
            session_id=req.session_id,
            request_id=req.request_id,
            status=req.status,
            content=req.content,
            stop_reason=req.stop_reason,
            error_code=req.error_code,
            error_message=req.error_message,
            usage=req.usage,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="relay request or session not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="relay request belongs to a different session") from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="relay request has expired") from exc

    result = record["result"]
    return BrowserResultResponse(
        request_id=record["request_id"],
        session_id=record["session_id"],
        status=record["status"],
        provider=record["provider"],
        model=record["model"],
        expires_at=record["expires_at"],
        content=result["content"] if result is not None else None,
        stop_reason=result["stop_reason"] if result is not None else None,
        error_code=result["error_code"] if result is not None else None,
        error_message=result["error_message"] if result is not None else None,
        usage=result["usage"] if result is not None else None,
    )


@router.get("/result/{request_id}", response_model=BrowserResultResponse)
async def fetch_result(
    request_id: str,
    session_id: str = Query(..., min_length=1),
) -> BrowserResultResponse:
    try:
        record = await _SESSION_STORE.get_result(session_id=session_id, request_id=request_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="plugin session not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="relay request belongs to a different session") from exc

    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="relay request not found")

    result = record["result"]
    return BrowserResultResponse(
        request_id=record["request_id"],
        session_id=record["session_id"],
        status=record["status"],
        provider=record["provider"],
        model=record["model"],
        expires_at=record["expires_at"],
        content=result["content"] if result is not None else None,
        stop_reason=result["stop_reason"] if result is not None else None,
        error_code=result["error_code"] if result is not None else None,
        error_message=result["error_message"] if result is not None else None,
        usage=result["usage"] if result is not None else None,
    )


__all__ = [
    "BrowserPluginSessionStore",
    "get_browser_plugin_session_store",
    "register_plugin",
    "submit_injection",
    "fetch_next_injection",
    "fetch_result",
    "router",
]
