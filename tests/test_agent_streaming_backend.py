"""Tests for dashboard streaming backend (Task N)."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

from a2a import agent_sdk
from dashboard.routes import create_dashboard_router


class _FakeResponse:
    def __init__(self, lines: list[str], status_code: int = 200, error_body: bytes = b"") -> None:
        self._lines = lines
        self.status_code = status_code
        self._error_body = error_body

    async def __aenter__(self) -> "_FakeResponse":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def aiter_lines(self):  # type: ignore[override]
        for line in self._lines:
            yield line

    async def aread(self) -> bytes:
        return self._error_body


class _FakeClient:
    def __init__(
        self,
        *,
        lines: list[str],
        status_code: int,
        error_body: bytes,
        capture: dict[str, Any],
    ) -> None:
        self._lines = lines
        self._status_code = status_code
        self._error_body = error_body
        self._capture = capture

    async def __aenter__(self) -> "_FakeClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def stream(self, method: str, url: str, json: dict[str, Any], headers: dict[str, str]) -> _FakeResponse:
        self._capture["method"] = method
        self._capture["url"] = url
        self._capture["json"] = json
        self._capture["headers"] = headers
        return _FakeResponse(self._lines, self._status_code, self._error_body)


def _patch_stream_client(
    monkeypatch: pytest.MonkeyPatch,
    *,
    lines: list[str],
    status_code: int = 200,
    error_body: bytes = b"",
) -> dict[str, Any]:
    capture: dict[str, Any] = {}

    def _factory(*args, **kwargs):  # noqa: ANN002, ANN003
        return _FakeClient(
            lines=lines,
            status_code=status_code,
            error_body=error_body,
            capture=capture,
        )

    monkeypatch.setattr(agent_sdk.httpx, "AsyncClient", _factory)
    return capture


def _drain_queue(q: asyncio.Queue[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    while not q.empty():
        out.append(q.get_nowait())
    return out


@pytest.mark.anyio
async def test_run_agent_stream_emits_tokens_and_done(monkeypatch: pytest.MonkeyPatch) -> None:
    capture = _patch_stream_client(
        monkeypatch,
        lines=[
            'data: {"choices":[{"delta":{"content":"Hel"}}]}',
            'data: {"choices":[{"delta":{"content":"lo"}}]}',
            'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}',
            "data: [DONE]",
        ],
    )
    monkeypatch.setattr(
        agent_sdk,
        "build_agent_definitions",
        lambda: {"cybersec-agent": SimpleNamespace(model="claude-test", prompt="ctx")},
    )

    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    await agent_sdk.run_agent_stream("cybersec-agent", "hello", q, stream=True)
    events = _drain_queue(q)

    assert [e["type"] for e in events] == ["token", "token", "done"]
    assert "".join(e["text"] for e in events if e["type"] == "token") == "Hello"
    assert events[-1]["stop_reason"] == "end_turn"
    assert capture["method"] == "POST"
    assert capture["json"]["stream"] is True
    assert capture["json"]["model"] == "claude-test"


@pytest.mark.anyio
async def test_run_agent_stream_non_stream_mode_returns_full_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_stream_client(
        monkeypatch,
        lines=[
            'data: {"choices":[{"delta":{"content":"A"}}]}',
            'data: {"choices":[{"delta":{"content":"B"}}]}',
            'data: {"choices":[{"delta":{},"finish_reason":"stop"}]}',
            "data: [DONE]",
        ],
    )
    monkeypatch.setattr(agent_sdk, "build_agent_definitions", lambda: {})

    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    await agent_sdk.run_agent_stream("unknown-agent", "hello", q, stream=False)
    events = _drain_queue(q)

    assert len(events) == 1
    assert events[0]["type"] == "done"
    assert events[0]["text"] == "AB"


@pytest.mark.anyio
async def test_run_agent_stream_emits_error_on_http_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_stream_client(
        monkeypatch,
        lines=[],
        status_code=502,
        error_body=b"upstream failure",
    )
    monkeypatch.setattr(agent_sdk, "build_agent_definitions", lambda: {})

    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    await agent_sdk.run_agent_stream("agent", "prompt", q, stream=True)
    events = _drain_queue(q)

    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "stream request failed" in events[0]["error"]


def test_dashboard_routes_include_agent_stream_endpoints() -> None:
    router = create_dashboard_router()

    def has_route(path: str, method: str) -> bool:
        for route in router.routes:
            route_path = getattr(route, "path", None)
            route_methods = getattr(route, "methods", None) or set()
            if route_path == path and method in route_methods:
                return True
        return False

    assert has_route("/api/agent-run", "POST")
    assert has_route("/api/agent-run/{task_id}", "DELETE")
    assert has_route("/sse/agent-run/{task_id}", "GET")
