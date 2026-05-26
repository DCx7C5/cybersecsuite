import asyncio
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


def test_plugin_submit_and_fetch_completed_result() -> None:
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

        submit_result = client.post(
            "/api/plugin/result",
            json={
                "session_id": session_id,
                "request_id": request_id,
                "content": "completed response",
                "stop_reason": "stop",
                "usage": {"prompt_tokens": 10, "completion_tokens": 4},
            },
        )
        assert submit_result.status_code == 200

        fetched_result = client.get(
            f"/api/plugin/result/{request_id}",
            params={"session_id": session_id},
        )
        assert fetched_result.status_code == 200
        payload = fetched_result.json()
        assert payload["status"] == "completed"
        assert payload["content"] == "completed response"


@pytest.mark.asyncio
async def test_css_client_routes_browser_relay_buffered_calls() -> None:
    store = get_browser_plugin_session_store()
    await store.reset()
    session_id, _ = await store.register_plugin()

    client = CSSLLMClient()
    response = await client.call_buffered(
        provider_id="browser-relay",
        model_id="browser-relay/default",
        messages=[{"role": "user", "content": "hello from relay"}],
        browser_plugin_session_id=session_id,
    )
    assert isinstance(response, LLMResponse)
    assert response.stop_reason == "relay_pending"
    request_id = str(response.usage["request_id"])

    stored_request = await store.fetch_result(session_id=session_id, request_id=request_id)
    assert stored_request is not None
    assert stored_request["status"] == "pending"


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
