"""QoL output-control directive injector."""

from collections.abc import Mapping, Sequence
from time import time

from css.core.settings.qol import QoLSecurityError, QoLSettings, QoLToggle, validate_toggle_combo
from .qol_telemetry import QoLTelemetryBridge

_FRAGMENT_TTL_SECONDS = 300.0
_BLOCK_HEADER = "[OUTPUT-CONTROLS]"
_BLOCK_FOOTER = "[/OUTPUT-CONTROLS]"

FRAGMENTS: dict[QoLToggle, str] = {
    QoLToggle.NO_THINKING: "No reasoning/thinking traces.",
    QoLToggle.NO_CHAT: "No conversational filler.",
    QoLToggle.MINIMAL: "Return minimum viable output.",
    QoLToggle.FILE_ONLY: "Return file/code output only.",
    QoLToggle.NO_MARKDOWN: "Output plain text only.",
    QoLToggle.STRUCTURED_ONLY: "Return structured output only.",
    QoLToggle.REDACT_SECRETS: "Redact secrets in output.",
    QoLToggle.APPEND_AUDIT_TRAIL: "Append a short audit trail.",
}

_fragment_cache: dict[tuple[str, ...], tuple[float, str, int]] = {}


def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def _sorted_toggle_values(qol_settings: QoLSettings) -> tuple[str, ...]:
    return tuple(sorted(toggle.value for toggle in qol_settings.enabled_toggles))


def _build_block(toggle_values: tuple[str, ...]) -> tuple[str, int]:
    lines: list[str] = []
    for toggle_value in toggle_values:
        toggle = QoLToggle(toggle_value)
        lines.append(f"- {toggle.value}: {FRAGMENTS[toggle]}")
    block = f"{_BLOCK_HEADER}\n" + "\n".join(lines) + f"\n{_BLOCK_FOOTER}"
    return block, _estimate_tokens(block)


class QoLInjector:
    """Build and inject deterministic QoL output-control directives."""

    def build_fragment_block(
        self,
        qol_settings: QoLSettings,
        token_budget: int = 128,
    ) -> tuple[str, dict[str, object]]:
        """Return bounded output-control block and telemetry-safe metadata."""
        validate_toggle_combo(qol_settings.enabled_toggles)
        toggle_values = _sorted_toggle_values(qol_settings)
        if not toggle_values:
            return "", {
                "injected": False,
                "active_toggle_values": [],
                "estimated_tokens": 0,
                "token_budget": token_budget,
                "token_budget_overrun": False,
            }

        now = time()
        cached = _fragment_cache.get(toggle_values)
        if cached is not None and cached[0] >= now:
            block = cached[1]
            estimated_tokens = cached[2]
        else:
            block, estimated_tokens = _build_block(toggle_values)
            _fragment_cache[toggle_values] = (now + _FRAGMENT_TTL_SECONDS, block, estimated_tokens)

        return block, {
            "injected": True,
            "active_toggle_values": list(toggle_values),
            "estimated_tokens": estimated_tokens,
            "token_budget": token_budget,
            "token_budget_overrun": estimated_tokens > token_budget,
        }

    def inject_into_system(
        self,
        system_text: str | None,
        qol_settings: QoLSettings,
        token_budget: int = 128,
    ) -> tuple[str | None, dict[str, object]]:
        """Append output-control block to system text without mutating input."""
        block, metadata = self.build_fragment_block(qol_settings=qol_settings, token_budget=token_budget)
        if not block:
            return system_text, metadata
        base_text = system_text or ""
        separator = "\n\n" if base_text else ""
        return f"{base_text}{separator}{block}", metadata

    def inject_into_messages(
        self,
        messages: Sequence[Mapping[str, object]],
        qol_settings: QoLSettings,
        token_budget: int = 128,
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        """Inject output-control block into copied message list."""
        copied_messages: list[dict[str, object]] = [dict(message) for message in messages]
        block, metadata = self.build_fragment_block(qol_settings=qol_settings, token_budget=token_budget)
        if not block:
            return copied_messages, metadata

        last_system_idx: int | None = None
        for idx, message in enumerate(copied_messages):
            if message.get("role") == "system":
                last_system_idx = idx

        if last_system_idx is None:
            copied_messages.insert(0, {"role": "system", "content": block})
            return copied_messages, metadata

        last_system = copied_messages[last_system_idx]
        raw_content = last_system.get("content")
        prior = raw_content if isinstance(raw_content, str) else ""
        separator = "\n\n" if prior else ""
        last_system["content"] = f"{prior}{separator}{block}"
        copied_messages[last_system_idx] = last_system
        return copied_messages, metadata

    async def inject_into_messages_with_telemetry(
        self,
        messages: Sequence[Mapping[str, object]],
        qol_settings: QoLSettings,
        token_budget: int = 128,
        session_id: str | None = None,
        agent_id: str | None = None,
    ) -> tuple[list[dict[str, object]], dict[str, object]]:
        """Inject directives and emit sanitized success/failure/security events."""
        bridge = QoLTelemetryBridge()
        started = time()
        try:
            injected, metadata = self.inject_into_messages(
                messages=messages,
                qol_settings=qol_settings,
                token_budget=token_budget,
            )
            await bridge.emit_injection_success(
                settings=qol_settings,
                started_at=started,
                metadata=metadata,
                session_id=session_id,
                agent_id=agent_id,
            )
            return injected, metadata
        except QoLSecurityError as error:
            await bridge.emit_security_rejected(
                settings=qol_settings,
                error=error,
                session_id=session_id,
                agent_id=agent_id,
            )
            raise
        except (TypeError, ValueError) as error:
            await bridge.emit_injection_failure(
                settings=qol_settings,
                error=error,
                session_id=session_id,
                agent_id=agent_id,
            )
            raise
