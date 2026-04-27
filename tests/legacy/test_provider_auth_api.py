from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from ai_proxy.providers.registry import AuthType
from dashboard.api import provider_auth as provider_auth_api


class DummyAccountManager:
    def __init__(self) -> None:
        self._accounts: dict[str, SimpleNamespace] = {}
        self._counter = 0

    async def add(
        self,
        provider_id: str,
        secret: str | dict,
        label: str | None = None,
        *,
        auth_method: str = "api_key",
        display_name: str | None = None,
        subject: str | None = None,
        email: str | None = None,
        tenant: str | None = None,
    ) -> SimpleNamespace:
        self._counter += 1
        vault_key = f"{provider_id}-{self._counter}"
        account = SimpleNamespace(
            vault_key=vault_key,
            provider_id=provider_id,
            label=label,
            active=True,
            auth_method=auth_method,
            display_name=display_name,
            subject=subject,
            email=email,
            tenant=tenant,
            test_status="untested",
            secret=secret,
        )
        self._accounts[vault_key] = account
        return account

    async def delete(self, vault_key: str) -> bool:
        if vault_key not in self._accounts:
            return False
        del self._accounts[vault_key]
        return True

    async def list_all(self) -> list[SimpleNamespace]:
        return list(self._accounts.values())


class DummyRequest:
    def __init__(self, provider_id: str, payload: dict | None = None) -> None:
        self.path_params = {"provider_id": provider_id}
        self._payload = payload or {}

    async def json(self) -> dict:
        return dict(self._payload)


def response_json(response) -> dict:
    return json.loads(response.body.decode("utf-8"))


@pytest.fixture
def auth_setup(monkeypatch: pytest.MonkeyPatch) -> DummyAccountManager:
    provider_auth_api._PENDING_AUTH_FLOWS.clear()
    manager = DummyAccountManager()

    provider = SimpleNamespace(
        id="openai",
        name="OpenAI",
        base_url="https://platform.openai.com",
        auth_type=AuthType.API_KEY,
        extra={
            "auth_methods": [
                {"name": "api_key", "config": {}},
                {"name": "oauth", "config": {"authorization_url": "https://example.com/oauth"}},
                {"name": "device_flow", "config": {"verification_uri": "https://example.com/device", "interval": 1}},
            ]
        },
    )

    monkeypatch.setattr(provider_auth_api, "get_account_manager", lambda: manager)
    monkeypatch.setattr(provider_auth_api, "get_provider", lambda provider_id: provider if provider_id == "openai" else None)
    return manager


@pytest.mark.asyncio
async def test_initiate_oauth_returns_flow(auth_setup: DummyAccountManager) -> None:
    _ = auth_setup
    response = await provider_auth_api.api_provider_auth_initiate(
        DummyRequest("openai", {"auth_method": "oauth"})
    )
    assert response.status_code == 200
    payload = response_json(response)
    assert payload["status"] == "oauth_pending"
    assert payload["auth_flow_id"]
    assert payload["state"]
    assert "oauth_url" in payload


@pytest.mark.asyncio
async def test_verify_oauth_creates_account(auth_setup: DummyAccountManager) -> None:
    _ = auth_setup
    start = await provider_auth_api.api_provider_auth_initiate(DummyRequest("openai", {"auth_method": "oauth"}))
    flow = response_json(start)

    verify = await provider_auth_api.api_provider_auth_verify(
        DummyRequest(
            "openai",
            {
                "auth_method": "oauth",
                "auth_flow_id": flow["auth_flow_id"],
                "state": flow["state"],
                "code": "oauth-code-123",
                "label": "Primary OAuth",
            },
        )
    )
    assert verify.status_code == 200
    payload = response_json(verify)
    assert payload["status"] == "active"
    assert payload["account"]["provider_id"] == "openai"
    assert payload["account"]["auth_method"] == "oauth"


@pytest.mark.asyncio
async def test_device_flow_pending_then_active(auth_setup: DummyAccountManager) -> None:
    _ = auth_setup
    start = await provider_auth_api.api_provider_auth_initiate(DummyRequest("openai", {"auth_method": "device_flow"}))
    flow = response_json(start)

    pending_1 = await provider_auth_api.api_provider_auth_verify(
        DummyRequest("openai", {"auth_method": "device_flow", "auth_flow_id": flow["auth_flow_id"]})
    )
    pending_2 = await provider_auth_api.api_provider_auth_verify(
        DummyRequest("openai", {"auth_method": "device_flow", "auth_flow_id": flow["auth_flow_id"]})
    )
    active = await provider_auth_api.api_provider_auth_verify(
        DummyRequest("openai", {"auth_method": "device_flow", "auth_flow_id": flow["auth_flow_id"]})
    )

    assert pending_1.status_code == 200
    assert response_json(pending_1)["status"] == "pending"
    assert pending_2.status_code == 200
    assert response_json(pending_2)["status"] == "pending"
    assert active.status_code == 200
    assert response_json(active)["status"] == "active"
    assert response_json(active)["account"]["auth_method"] == "device_flow"


@pytest.mark.asyncio
async def test_api_key_verify_requires_key(auth_setup: DummyAccountManager) -> None:
    _ = auth_setup
    response = await provider_auth_api.api_provider_auth_verify(
        DummyRequest("openai", {"auth_method": "api_key"})
    )
    assert response.status_code == 400
    assert "api_key is required" in response_json(response)["error"]


@pytest.mark.asyncio
async def test_revoke_and_accounts_listing(auth_setup: DummyAccountManager) -> None:
    _ = auth_setup
    created = await provider_auth_api.api_provider_auth_verify(
        DummyRequest(
            "openai",
            {"auth_method": "api_key", "api_key": "sk-test-key", "label": "API key account"},
        )
    )
    assert created.status_code == 200
    account_id = response_json(created)["account"]["account_id"]

    listed = await provider_auth_api.api_provider_accounts(DummyRequest("openai"))
    assert listed.status_code == 200
    assert len(response_json(listed)["accounts"]) == 1

    revoked = await provider_auth_api.api_provider_auth_revoke(
        DummyRequest("openai", {"account_id": account_id})
    )
    assert revoked.status_code == 200
    assert response_json(revoked)["ok"] is True

    listed_after = await provider_auth_api.api_provider_accounts(DummyRequest("openai"))
    assert listed_after.status_code == 200
    assert response_json(listed_after)["accounts"] == []
