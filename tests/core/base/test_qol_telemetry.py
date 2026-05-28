import pytest

from css.core.settings.qol import QoLSecurityError, QoLSettings, QoLToggle
from css.core.base.qol_injector import QoLInjector
from css.core.base.qol_telemetry import QoLTelemetryBridge


def test_success_payload_is_sanitized() -> None:
    bridge = QoLTelemetryBridge()
    payload = bridge.build_success_payload(
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session"),
        latency_ms=10.0,
        metadata={
            "token_budget_overrun": False,
            "estimated_tokens": 12,
            "token_budget": 128,
            "prompt": "secret prompt",
        },
        session_id="s1",
        agent_id="a1",
    )
    assert "prompt" not in payload
    assert payload["toggle_names"] == ["no_chat"]
    assert payload["toggle_count"] == 1
    assert payload["session_id"] == "s1"
    assert payload["agent_id"] == "a1"


@pytest.mark.asyncio
async def test_injector_emits_success_event(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[tuple[str, dict[str, object]]] = []

    async def _emit(event_type: str, payload: dict[str, object]) -> None:
        captured.append((event_type, payload))

    monkeypatch.setattr("css.core.base.qol_telemetry.emit_event", _emit)
    injector = QoLInjector()
    settings = QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session")

    injected, _ = await injector.inject_into_messages_with_telemetry(
        messages=[{"role": "user", "content": "hello"}],
        qol_settings=settings,
        session_id="s1",
        agent_id="a1",
    )

    assert injected
    assert captured
    assert captured[0][0] == "qol.injection"


@pytest.mark.asyncio
async def test_injector_emits_security_rejected_event(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[tuple[str, dict[str, object]]] = []

    async def _emit(event_type: str, payload: dict[str, object]) -> None:
        captured.append((event_type, payload))

    monkeypatch.setattr("css.core.base.qol_telemetry.emit_event", _emit)
    injector = QoLInjector()
    invalid = QoLSettings(
        enabled_toggles={QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL},
        scope="session",
    )

    with pytest.raises(QoLSecurityError):
        await injector.inject_into_messages_with_telemetry(
            messages=[{"role": "user", "content": "hello"}],
            qol_settings=invalid,
        )

    assert captured
    assert captured[0][0] == "qol.security_rejected"


@pytest.mark.asyncio
async def test_exporter_failure_is_non_fatal(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _emit(_event_type: str, _payload: dict[str, object]) -> None:
        raise RuntimeError("telemetry backend down")

    monkeypatch.setattr("css.core.base.qol_telemetry.emit_event", _emit)
    bridge = QoLTelemetryBridge()
    ok = await bridge.emit_injection_success(
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session"),
        started_at=0.0,
        metadata={"token_budget_overrun": False, "estimated_tokens": 1, "token_budget": 128},
    )
    assert ok is False


@pytest.mark.asyncio
async def test_emit_injection_failure_event(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[tuple[str, dict[str, object]]] = []

    async def _emit(event_type: str, payload: dict[str, object]) -> None:
        captured.append((event_type, payload))

    monkeypatch.setattr("css.core.base.qol_telemetry.emit_event", _emit)
    bridge = QoLTelemetryBridge()
    ok = await bridge.emit_injection_failure(
        settings=QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session"),
        error=ValueError("bad input"),
        session_id="s1",
        agent_id="a1",
    )
    assert ok is True
    assert captured
    assert captured[0][0] == "qol.injection_failure"
    assert captured[0][1]["error_type"] == "ValueError"
