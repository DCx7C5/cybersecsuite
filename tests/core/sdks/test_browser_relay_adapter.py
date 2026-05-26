import asyncio
from typing import Literal
import time

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from css.core.sdks.adapters.browser_relay import BrowserRelayAdapter
from css.core.sdks.css_client import CSSLLMClient
from css.core.types.base_messages import LLMResponse
from css.modules.llm_proxy.browser_plugin import (
    get_browser_plugin_session_store,
    router as plugin_router,
)


def _build_plugin_app() -> FastAPI:
    app = FastAPI()
    app.include_router(plugin_router)
    return app


async def _claim_and_submit(
    session_id: str,
    *,
    status: Literal["completed", "failed"],
    content: str,
    stop_reason: str = "stop",
    error_code: str | None = None,
    error_message: str | None = None,
) -> None:
    store = get_browser_plugin_session_store()
    for _ in range(200):
        record = await store.claim_next_injection(session_id=session_id)
        if record is not None:
            await store.put_result(
                session_id=session_id,
                request_id=record["request_id"],
                status=status,
                content=content,
                stop_reason=stop_reason,
                error_code=error_code,
                error_message=error_message,
                usage={"prompt_tokens": 8, "completion_tokens": 3},
            )
            return
        await asyncio.sleep(0.01)
    raise AssertionError("timed out waiting for relay request to become claimable")


def test_plugin_register_inject_missing_session_and_timeout_fetch() -> None:
    store = get_browser_plugin_session_store()
    asyncio.run(store.reset())

    app = _build_plugin_app()
    with TestClient(app) as client:
        register_response = client.post(
            "/api/plugin/register",
            json={"domain": "browser-plugin", "version": "3.0"},
        )
        assert register_response.status_code == 201
        register_payload = register_response.json()
        session_id = str(register_payload["plugin_session_id"])
        assert register_payload["dashboard_version"] == "local-dev"

        unknown_result = client.get(
            "/api/plugin/result/missing-request",
            params={"session_id": session_id},
        )
        assert unknown_result.status_code == 404

        missing_session = client.post(
            "/api/plugin/inject",
            json={"session_id": "missing", "prompt": "hello"},
        )
        assert missing_session.status_code == 404

        inject_response = client.post(
            "/api/plugin/inject",
            json={
                "session_id": session_id,
                "prompt": "relay this",
                "ttl_seconds": 1,
            },
        )
        assert inject_response.status_code == 202
        request_id = str(inject_response.json()["request_id"])

        pending_result = client.get(
            f"/api/plugin/result/{request_id}",
            params={"session_id": session_id},
        )
        assert pending_result.status_code == 200
        assert pending_result.json()["status"] == "pending"

        time.sleep(1.1)
        expired_result = client.get(
            f"/api/plugin/result/{request_id}",
            params={"session_id": session_id},
        )
        assert expired_result.status_code == 200
        assert expired_result.json()["status"] == "expired"


def test_plugin_claim_next_and_submit_failed_result() -> None:
    store = get_browser_plugin_session_store()
    asyncio.run(store.reset())

    app = _build_plugin_app()
    with TestClient(app) as client:
        register_response = client.post(
            "/api/plugin/register",
            json={"domain": "browser-plugin", "version": "3.0"},
        )
        session_id = str(register_response.json()["plugin_session_id"])

        inject_response = client.post(
            "/api/plugin/inject",
            json={"session_id": session_id, "prompt": "test prompt"},
        )
        request_id = str(inject_response.json()["request_id"])

        claim_response = client.get(
            "/api/plugin/inject/next",
            params={"session_id": session_id},
        )
        assert claim_response.status_code == 200
        claim_payload = claim_response.json()
        assert claim_payload["available"] is True
        assert claim_payload["request_id"] == request_id

        in_progress = client.get(
            f"/api/plugin/result/{request_id}",
            params={"session_id": session_id},
        )
        assert in_progress.status_code == 200
        assert in_progress.json()["status"] == "in_progress"

        submit_result = client.post(
            "/api/plugin/result",
            json={
                "session_id": session_id,
                "request_id": request_id,
                "status": "failed",
                "content": "",
                "stop_reason": "relay_failed",
                "error_code": "injection_failed",
                "error_message": "input element not available",
            },
        )
        assert submit_result.status_code == 200

        fetched_result = client.get(
            f"/api/plugin/result/{request_id}",
            params={"session_id": session_id},
        )
        assert fetched_result.status_code == 200
        payload = fetched_result.json()
        assert payload["status"] == "failed"
        assert payload["error_code"] == "injection_failed"
        assert payload["error_message"] == "input element not available"


@pytest.mark.asyncio
async def test_css_client_routes_browser_relay_buffered_calls_completed() -> None:
    store = get_browser_plugin_session_store()
    await store.reset()
    session_id, _ = await store.register_plugin()

    producer = asyncio.create_task(
        _claim_and_submit(
            session_id,
            status="completed",
            content="relay complete",
        )
    )
    client = CSSLLMClient()
    response = await client.call_buffered(
        provider_id="browser-relay",
        model_id="browser-relay/default",
        messages=[{"role": "user", "content": "hello from relay"}],
        browser_plugin_session_id=session_id,
        poll_interval_seconds=0.01,
        poll_timeout_seconds=2.0,
    )
    await producer

    assert isinstance(response, LLMResponse)
    assert response.stop_reason == "stop"
    assert response.text == "relay complete"
    assert str(response.usage["session_id"]) == session_id


@pytest.mark.asyncio
async def test_browser_relay_adapter_failed_timeout_unknown_and_cancelled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = get_browser_plugin_session_store()
    await store.reset()
    session_id, _ = await store.register_plugin()

    adapter = BrowserRelayAdapter()
    failed_producer = asyncio.create_task(
        _claim_and_submit(
            session_id,
            status="failed",
            content="",
            stop_reason="relay_failed",
            error_code="tab_closed",
            error_message="tab not reachable",
        )
    )
    failed = await adapter.call_llm_buffered(
        model_id="browser-relay/default",
        messages=[{"role": "user", "content": "fail me"}],
        browser_plugin_session_id=session_id,
        poll_interval_seconds=0.01,
        poll_timeout_seconds=2.0,
    )
    await failed_producer
    assert failed.stop_reason == "tab_closed"
    assert str(failed.usage["error_code"]) == "tab_closed"
    assert str(failed.usage["error_message"]) == "tab not reachable"

    timeout = await adapter.call_llm_buffered(
        model_id="browser-relay/default",
        messages=[{"role": "user", "content": "timeout me"}],
        browser_plugin_session_id=session_id,
        poll_interval_seconds=0.01,
        poll_timeout_seconds=0.05,
    )
    assert timeout.stop_reason == "relay_timeout"

    async def _missing_result(*, session_id: str, request_id: str) -> None:
        return None

    monkeypatch.setattr(store, "get_result", _missing_result)
    unknown = await adapter.call_llm_buffered(
        model_id="browser-relay/default",
        messages=[{"role": "user", "content": "unknown id"}],
        browser_plugin_session_id=session_id,
        poll_interval_seconds=0.01,
        poll_timeout_seconds=0.2,
    )
    assert unknown.stop_reason == "relay_unknown_request"

    cancel_event = asyncio.Event()
    cancel_event.set()
    cancelled = await adapter.call_llm_buffered(
        model_id="browser-relay/default",
        messages=[{"role": "user", "content": "cancelled"}],
        browser_plugin_session_id=session_id,
        cancel_event=cancel_event,
        poll_interval_seconds=0.01,
        poll_timeout_seconds=0.2,
    )
    assert cancelled.stop_reason == "relay_cancelled"


@pytest.mark.asyncio
async def test_browser_relay_streaming_fails_explicitly() -> None:
    store = get_browser_plugin_session_store()
    await store.reset()
    session_id, _ = await store.register_plugin()

    adapter = BrowserRelayAdapter()
    with pytest.raises(NotImplementedError):
        await adapter.call_llm(
            model_id="browser-relay/default",
            messages=[{"role": "user", "content": "hello"}],
            browser_plugin_session_id=session_id,
            streaming=True,
        )
