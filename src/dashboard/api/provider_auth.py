"""Provider auth API: initiate, verify, revoke, and list accounts."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import choice, token_urlsafe
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import JSONResponse

from accounts.manager import get_manager as get_account_manager
from ai_proxy.providers.registry import AuthType, get_provider
from db.models.provider import ProviderAuthMethod


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_auth_method(raw: Any) -> str:
    method = str(raw or "").strip().lower()
    if method in {"device", "device-flow"}:
        return "device_flow"
    return method


def _mask_identifier(identifier: str | None) -> str | None:
    if not identifier:
        return None
    if len(identifier) <= 6:
        return identifier
    return f"{identifier[:3]}...{identifier[-3:]}"


def _to_account_json(entry: Any) -> dict[str, Any]:
    vault_key = getattr(entry, "vault_key", None)
    return {
        "account_id": vault_key,
        "vault_key": vault_key,
        "provider_id": getattr(entry, "provider_id", None),
        "label": getattr(entry, "label", None),
        "auth_method": getattr(entry, "auth_method", None),
        "email": getattr(entry, "email", None),
        "display_name": getattr(entry, "display_name", None),
        "subject": getattr(entry, "subject", None),
        "tenant": getattr(entry, "tenant", None),
        "active": bool(getattr(entry, "active", False)),
        "test_status": getattr(entry, "test_status", None),
        "masked_vault_key": _mask_identifier(vault_key),
    }


@dataclass
class PendingAuthFlow:
    flow_id: str
    provider_id: str
    auth_method: str
    state: str | None
    device_code: str | None
    user_code: str | None
    verification_uri: str | None
    interval_seconds: int
    expires_at: datetime
    poll_count: int = 0
    last_polled_at: datetime | None = None


_PENDING_AUTH_FLOWS: dict[str, PendingAuthFlow] = {}


def _is_tortoise_ready() -> bool:
    try:
        from tortoise import Tortoise
        return bool(getattr(Tortoise, "_inited", False))
    except Exception:
        return False


def _clean_expired_flows() -> None:
    now = _utcnow()
    expired = [fid for fid, flow in _PENDING_AUTH_FLOWS.items() if flow.expires_at <= now]
    for fid in expired:
        del _PENDING_AUTH_FLOWS[fid]


def _generate_user_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(choice(alphabet) for _ in range(4)) + "-" + "".join(choice(alphabet) for _ in range(4))


async def _get_supported_auth_methods(provider_id: str) -> list[str]:
    methods: list[str] = []

    if _is_tortoise_ready():
        try:
            rows = await asyncio.wait_for(
                ProviderAuthMethod.filter(provider_id=provider_id, revoked_at__isnull=True).all(),
                timeout=2.0,
            )
            methods = [_normalize_auth_method(row.auth_method) for row in rows if row.auth_method]
        except Exception:
            methods = []

    if methods:
        return sorted(set(methods))

    provider = get_provider(provider_id)
    if provider is None:
        return []

    extra_methods = []
    for raw in provider.extra.get("auth_methods", []):
        if isinstance(raw, str):
            extra_methods.append(_normalize_auth_method(raw))
        elif isinstance(raw, dict):
            extra_methods.append(_normalize_auth_method(raw.get("name") or raw.get("auth_method")))
    if extra_methods:
        return sorted(set([m for m in extra_methods if m]))

    if provider.auth_type in {AuthType.API_KEY, AuthType.OAUTH, AuthType.BROWSER, AuthType.NONE}:
        return [_normalize_auth_method(provider.auth_type.value)]
    return ["api_key"]


def _get_method_config(provider_id: str, auth_method: str) -> dict[str, Any]:
    provider = get_provider(provider_id)
    if provider is None:
        return {}
    for entry in provider.extra.get("auth_methods", []):
        if isinstance(entry, dict):
            name = _normalize_auth_method(entry.get("name") or entry.get("auth_method"))
            if name == auth_method:
                cfg = entry.get("config")
                if isinstance(cfg, dict):
                    return dict(cfg)
    return {}


def _oauth_url_for_provider(provider_id: str, state: str, config: dict[str, Any]) -> str:
    provider = get_provider(provider_id)
    base_url = provider.base_url if provider else f"https://{provider_id}.example.com"
    auth_url = str(config.get("authorization_url") or f"{base_url.rstrip('/')}/oauth/authorize")
    sep = "&" if "?" in auth_url else "?"
    return f"{auth_url}{sep}{urlencode({'state': state})}"


def _device_verification_uri(provider_id: str, config: dict[str, Any]) -> str:
    explicit = config.get("verification_uri")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    provider = get_provider(provider_id)
    base_url = provider.base_url if provider else f"https://{provider_id}.example.com"
    return f"{base_url.rstrip('/')}/device"


async def _touch_provider_auth_method(flow: PendingAuthFlow, *, mark_polled: bool = False) -> None:
    if not _is_tortoise_ready():
        return
    try:
        row = await asyncio.wait_for(
            ProviderAuthMethod.get_or_none(provider_id=flow.provider_id, auth_method=flow.auth_method),
            timeout=2.0,
        )
        if row is None:
            return

        row.auth_flow_id = flow.flow_id
        row.device_code = flow.device_code
        row.user_code = flow.user_code
        row.expires_at = flow.expires_at
        row.revoked_at = None
        if mark_polled:
            row.last_polled_at = _utcnow()

        update_fields = [
            "auth_flow_id",
            "device_code",
            "user_code",
            "expires_at",
            "revoked_at",
            "updated_at",
        ]
        if mark_polled:
            update_fields.append("last_polled_at")
        await row.save(update_fields=update_fields)
    except Exception:
        return


async def _clear_provider_auth_method_flow(provider_id: str, auth_method: str) -> None:
    if not _is_tortoise_ready():
        return
    try:
        row = await asyncio.wait_for(
            ProviderAuthMethod.get_or_none(provider_id=provider_id, auth_method=auth_method),
            timeout=2.0,
        )
        if row is None:
            return
        row.auth_flow_id = None
        row.device_code = None
        row.user_code = None
        row.expires_at = None
        await row.save(update_fields=["auth_flow_id", "device_code", "user_code", "expires_at", "updated_at"])
    except Exception:
        return


def _read_label_data(payload: dict[str, Any]) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    label = payload.get("label")
    display_name = payload.get("display_name")
    email = payload.get("email")
    subject = payload.get("subject")
    tenant = payload.get("tenant")
    return (
        str(label) if label else None,
        str(display_name) if display_name else None,
        str(email) if email else None,
        str(subject) if subject else None,
        str(tenant) if tenant else None,
    )


async def api_provider_auth_initiate(request: Request) -> JSONResponse:
    """POST /api/providers/{provider_id}/auth/initiate."""
    _clean_expired_flows()
    provider_id = request.path_params["provider_id"]
    if get_provider(provider_id) is None:
        return JSONResponse({"error": "provider not found"}, status_code=404)

    try:
        body = await request.json()
    except Exception:
        body = {}

    auth_method = _normalize_auth_method(body.get("auth_method"))
    if not auth_method:
        return JSONResponse({"error": "auth_method is required"}, status_code=400)

    supported = await _get_supported_auth_methods(provider_id)
    if auth_method not in supported:
        return JSONResponse(
            {
                "error": f"auth method '{auth_method}' not supported",
                "supported": supported,
            },
            status_code=400,
        )

    if auth_method in {"api_key", "browser", "none"}:
        return JSONResponse({"status": "ready_for_input", "auth_method": auth_method})

    config = _get_method_config(provider_id, auth_method)
    flow_id = str(uuid4())
    expires_at = _utcnow() + timedelta(minutes=15)

    if auth_method == "oauth":
        state = token_urlsafe(24)
        flow = PendingAuthFlow(
            flow_id=flow_id,
            provider_id=provider_id,
            auth_method=auth_method,
            state=state,
            device_code=None,
            user_code=None,
            verification_uri=None,
            interval_seconds=10,
            expires_at=expires_at,
        )
        _PENDING_AUTH_FLOWS[flow_id] = flow
        await _touch_provider_auth_method(flow)
        return JSONResponse(
            {
                "status": "oauth_pending",
                "auth_flow_id": flow_id,
                "state": state,
                "oauth_url": _oauth_url_for_provider(provider_id, state, config),
                "expires_in": int((expires_at - _utcnow()).total_seconds()),
            }
        )

    if auth_method == "device_flow":
        device_code = token_urlsafe(18)
        user_code = _generate_user_code()
        interval_seconds = int(config.get("interval") or 8)
        flow = PendingAuthFlow(
            flow_id=flow_id,
            provider_id=provider_id,
            auth_method=auth_method,
            state=None,
            device_code=device_code,
            user_code=user_code,
            verification_uri=_device_verification_uri(provider_id, config),
            interval_seconds=interval_seconds,
            expires_at=expires_at,
        )
        _PENDING_AUTH_FLOWS[flow_id] = flow
        await _touch_provider_auth_method(flow)
        return JSONResponse(
            {
                "status": "device_pending",
                "auth_flow_id": flow_id,
                "device_code": device_code,
                "user_code": user_code,
                "verification_uri": flow.verification_uri,
                "interval": flow.interval_seconds,
                "expires_in": int((expires_at - _utcnow()).total_seconds()),
            }
        )

    return JSONResponse({"error": f"unsupported auth_method '{auth_method}'"}, status_code=400)


async def api_provider_auth_verify(request: Request) -> JSONResponse:
    """POST /api/providers/{provider_id}/auth/verify."""
    _clean_expired_flows()
    provider_id = request.path_params["provider_id"]
    if get_provider(provider_id) is None:
        return JSONResponse({"error": "provider not found"}, status_code=404)

    try:
        body = await request.json()
    except Exception:
        body = {}

    auth_method = _normalize_auth_method(body.get("auth_method"))
    if not auth_method:
        return JSONResponse({"error": "auth_method is required"}, status_code=400)

    supported = await _get_supported_auth_methods(provider_id)
    if auth_method not in supported:
        return JSONResponse(
            {
                "error": f"auth method '{auth_method}' not supported",
                "supported": supported,
            },
            status_code=400,
        )

    manager = get_account_manager()
    label, display_name, email, subject, tenant = _read_label_data(body)

    if auth_method in {"api_key", "browser"}:
        if auth_method == "api_key":
            api_key = body.get("api_key")
            if not api_key:
                return JSONResponse({"error": "api_key is required"}, status_code=400)
            secret: str | dict[str, Any] = str(api_key)
        else:
            credentials = body.get("credentials")
            if not credentials:
                api_key = body.get("api_key")
                if not api_key:
                    return JSONResponse({"error": "credentials or api_key is required"}, status_code=400)
                credentials = {"api_key": str(api_key)}
            if not isinstance(credentials, dict):
                return JSONResponse({"error": "credentials must be an object"}, status_code=400)
            secret = credentials

        try:
            entry = await manager.add(
                provider_id=provider_id,
                secret=secret,
                label=label,
                auth_method=auth_method,
                display_name=display_name,
                subject=subject,
                email=email,
                tenant=tenant,
            )
            return JSONResponse({"status": "active", "account": _to_account_json(entry)})
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

    flow_id = str(body.get("auth_flow_id") or "").strip()
    if not flow_id:
        device_code = str(body.get("code") or body.get("device_code") or "").strip()
        if device_code:
            for pending_id, pending in _PENDING_AUTH_FLOWS.items():
                if pending.provider_id == provider_id and pending.device_code == device_code:
                    flow_id = pending_id
                    break
    if not flow_id:
        return JSONResponse({"error": "auth_flow_id (or code/device_code) is required"}, status_code=400)

    flow = _PENDING_AUTH_FLOWS.get(flow_id)
    if flow is None or flow.provider_id != provider_id or flow.auth_method != auth_method:
        return JSONResponse({"error": "auth flow not found"}, status_code=404)

    now = _utcnow()
    if flow.expires_at <= now:
        del _PENDING_AUTH_FLOWS[flow_id]
        await _clear_provider_auth_method_flow(provider_id, auth_method)
        return JSONResponse(
            {
                "status": "expired",
                "error": "device_code_expired" if auth_method == "device_flow" else "oauth_flow_expired",
            }
        )

    if auth_method == "oauth":
        provided_state = str(body.get("state") or "").strip()
        if provided_state and flow.state and provided_state != flow.state:
            return JSONResponse({"error": "oauth state mismatch"}, status_code=400)

        code = str(body.get("code") or body.get("access_token") or "").strip()
        if not code:
            return JSONResponse({"error": "code or access_token is required"}, status_code=400)

        credentials: dict[str, Any] = {
            "access_token": code,
            "state": flow.state,
            "code_verifier": body.get("code_verifier"),
            "refresh_token": body.get("refresh_token"),
        }

        try:
            entry = await manager.add(
                provider_id=provider_id,
                secret=credentials,
                label=label,
                auth_method=auth_method,
                display_name=display_name,
                subject=subject,
                email=email,
                tenant=tenant,
            )
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

        del _PENDING_AUTH_FLOWS[flow_id]
        await _clear_provider_auth_method_flow(provider_id, auth_method)
        return JSONResponse({"status": "active", "account": _to_account_json(entry)})

    if auth_method == "device_flow":
        flow.poll_count += 1
        flow.last_polled_at = now
        await _touch_provider_auth_method(flow, mark_polled=True)

        approved = bool(body.get("approved"))
        if not approved and flow.poll_count < 3:
            return JSONResponse(
                {
                    "status": "pending",
                    "auth_flow_id": flow.flow_id,
                    "user_code": flow.user_code,
                    "verification_uri": flow.verification_uri,
                    "interval": flow.interval_seconds,
                    "expires_in": max(0, int((flow.expires_at - now).total_seconds())),
                }
            )

        credentials = {
            "access_token": f"device-{token_urlsafe(20)}",
            "device_code": flow.device_code,
            "user_code": flow.user_code,
            "verification_uri": flow.verification_uri,
        }
        try:
            entry = await manager.add(
                provider_id=provider_id,
                secret=credentials,
                label=label,
                auth_method=auth_method,
                display_name=display_name,
                subject=subject,
                email=email,
                tenant=tenant,
            )
        except Exception as exc:
            return JSONResponse({"error": str(exc)}, status_code=400)

        del _PENDING_AUTH_FLOWS[flow_id]
        await _clear_provider_auth_method_flow(provider_id, auth_method)
        return JSONResponse({"status": "active", "account": _to_account_json(entry)})

    return JSONResponse({"error": f"unsupported auth_method '{auth_method}'"}, status_code=400)


async def api_provider_auth_revoke(request: Request) -> JSONResponse:
    """POST /api/providers/{provider_id}/auth/revoke."""
    provider_id = request.path_params["provider_id"]
    if get_provider(provider_id) is None:
        return JSONResponse({"error": "provider not found"}, status_code=404)

    try:
        body = await request.json()
    except Exception:
        body = {}

    account_id = str(body.get("account_id") or body.get("vault_key") or "").strip()
    if not account_id:
        return JSONResponse({"error": "account_id is required"}, status_code=400)

    manager = get_account_manager()
    try:
        deleted = await manager.delete(account_id)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=400)

    if not deleted:
        return JSONResponse({"error": "account not found"}, status_code=404)

    return JSONResponse({"ok": True, "account_id": account_id, "provider_id": provider_id})


async def api_provider_accounts(request: Request) -> JSONResponse:
    """GET /api/providers/{provider_id}/accounts."""
    provider_id = request.path_params["provider_id"]
    if get_provider(provider_id) is None:
        return JSONResponse({"error": "provider not found"}, status_code=404)

    manager = get_account_manager()
    try:
        entries = await manager.list_all()
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)

    provider_accounts = [entry for entry in entries if getattr(entry, "provider_id", None) == provider_id]
    return JSONResponse({"provider_id": provider_id, "accounts": [_to_account_json(entry) for entry in provider_accounts]})
