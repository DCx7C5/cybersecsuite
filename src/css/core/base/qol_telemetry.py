"""QoL injection telemetry events published via core events emitter."""

from asyncio import gather
from time import monotonic

from css.core.events.emitter import emit_event
from css.core.settings.qol import QoLSecurityError, QoLSettings

_ALLOWED_SCOPES = {"session", "project", "global", "preset"}


def _safe_scope(scope: str) -> str:
    normalized = scope.strip().lower()
    if normalized in _ALLOWED_SCOPES:
        return normalized
    return "session"


def _sorted_toggle_names(settings: QoLSettings) -> list[str]:
    return sorted(toggle.value for toggle in settings.enabled_toggles)


def _int_value(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


class QoLTelemetryBridge:
    """Build and emit sanitized QoL telemetry payloads."""

    @staticmethod
    def build_success_payload(
        *,
        settings: QoLSettings,
        latency_ms: float,
        metadata: dict[str, object],
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, object]:
        toggle_names = _sorted_toggle_names(settings)
        return {
            "scope": _safe_scope(settings.scope),
            "toggle_names": toggle_names,
            "toggle_count": len(toggle_names),
            "latency_ms": round(latency_ms, 3),
            "token_budget_overrun": bool(metadata.get("token_budget_overrun", False)),
            "estimated_tokens": _int_value(metadata.get("estimated_tokens", 0)),
            "token_budget": _int_value(metadata.get("token_budget", 0)),
            "session_id": session_id,
            "agent_id": agent_id,
        }

    @staticmethod
    def build_failure_payload(
        *,
        settings: QoLSettings,
        error: BaseException,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, object]:
        return {
            "scope": _safe_scope(settings.scope),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "session_id": session_id,
            "agent_id": agent_id,
        }

    @staticmethod
    def build_security_payload(
        *,
        error: QoLSecurityError,
        settings: QoLSettings,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> dict[str, object]:
        context = error.context
        return {
            "scope": _safe_scope(settings.scope),
            "error_code": context.get("error_code"),
            "combination": list(context.get("combination", [])),
            "active_toggles": list(context.get("active_toggles", [])),
            "session_id": session_id,
            "agent_id": agent_id,
        }

    async def emit_injection_success(
        self,
        *,
        settings: QoLSettings,
        started_at: float,
        metadata: dict[str, object],
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> bool:
        payload = self.build_success_payload(
            settings=settings,
            latency_ms=(monotonic() - started_at) * 1000.0,
            metadata=metadata,
            session_id=session_id,
            agent_id=agent_id,
        )
        result = await gather(emit_event("qol.injection", payload), return_exceptions=True)
        return not isinstance(result[0], BaseException)

    async def emit_injection_failure(
        self,
        *,
        settings: QoLSettings,
        error: BaseException,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> bool:
        payload = self.build_failure_payload(
            settings=settings,
            error=error,
            session_id=session_id,
            agent_id=agent_id,
        )
        result = await gather(emit_event("qol.injection_failure", payload), return_exceptions=True)
        return not isinstance(result[0], BaseException)

    async def emit_security_rejected(
        self,
        *,
        settings: QoLSettings,
        error: QoLSecurityError,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> bool:
        payload = self.build_security_payload(
            error=error,
            settings=settings,
            session_id=session_id,
            agent_id=agent_id,
        )
        result = await gather(emit_event("qol.security_rejected", payload), return_exceptions=True)
        return not isinstance(result[0], BaseException)
