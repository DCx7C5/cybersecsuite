"""Tests for QoL toggle-combination validation."""

import pytest

from css.core.settings.qol import QoLSecurityError, QoLToggle, validate_toggle_combo


@pytest.mark.parametrize(
    "toggles",
    [
        {QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL},
        {QoLToggle.FILE_ONLY, QoLToggle.STRUCTURED_ONLY},
        {QoLToggle.MINIMAL, QoLToggle.APPEND_AUDIT_TRAIL},
    ],
)
def test_validate_toggle_combo_rejects_dangerous_sets(toggles: set[QoLToggle]) -> None:
    with pytest.raises(QoLSecurityError) as exc:
        validate_toggle_combo(toggles)

    assert exc.value.context["error_code"] == "qol.dangerous_combo"
    assert set(exc.value.context["combination"]) <= set(exc.value.context["active_toggles"])


def test_validate_toggle_combo_accepts_safe_set() -> None:
    validate_toggle_combo({QoLToggle.NO_CHAT, QoLToggle.NO_MARKDOWN})


def test_validate_toggle_combo_accepts_string_inputs() -> None:
    validate_toggle_combo(["no_chat", "structured_only"])
