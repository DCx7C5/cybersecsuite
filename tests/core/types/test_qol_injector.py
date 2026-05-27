"""Tests for QoL output-control injector."""

import pytest

from css.core.settings.qol import QoLSettings, QoLToggle, QoLSecurityError
from css.core.types.qol_injector import QoLInjector


def test_build_fragment_block_is_deterministic_for_toggle_order() -> None:
    injector = QoLInjector()
    settings_a = QoLSettings(
        enabled_toggles={QoLToggle.NO_CHAT, QoLToggle.NO_MARKDOWN},
        scope="session",
    )
    settings_b = QoLSettings(
        enabled_toggles={QoLToggle.NO_MARKDOWN, QoLToggle.NO_CHAT},
        scope="session",
    )

    block_a, metadata_a = injector.build_fragment_block(settings_a)
    block_b, metadata_b = injector.build_fragment_block(settings_b)

    assert block_a == block_b
    assert metadata_a["active_toggle_values"] == ["no_chat", "no_markdown"]
    assert metadata_b["active_toggle_values"] == ["no_chat", "no_markdown"]


def test_inject_into_messages_does_not_mutate_input() -> None:
    injector = QoLInjector()
    settings = QoLSettings(enabled_toggles={QoLToggle.NO_CHAT}, scope="session")
    original = [{"role": "user", "content": "hello"}]
    before = [dict(message) for message in original]

    injected, metadata = injector.inject_into_messages(original, settings)

    assert original == before
    assert injected[0]["role"] == "system"
    assert isinstance(injected[0]["content"], str)
    assert metadata["injected"] is True


def test_inject_rejects_invalid_combinations() -> None:
    injector = QoLInjector()
    invalid = QoLSettings(
        enabled_toggles={QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL},
        scope="session",
    )

    with pytest.raises(QoLSecurityError):
        injector.build_fragment_block(invalid)


def test_empty_settings_are_noop_for_system_and_messages() -> None:
    injector = QoLInjector()
    settings = QoLSettings(enabled_toggles=set(), scope="session")
    messages = [{"role": "user", "content": "x"}]

    injected_messages, msg_meta = injector.inject_into_messages(messages, settings)
    injected_system, sys_meta = injector.inject_into_system("base", settings)

    assert injected_messages == messages
    assert injected_system == "base"
    assert msg_meta["injected"] is False
    assert sys_meta["injected"] is False


def test_token_budget_overrun_flag_is_reported() -> None:
    injector = QoLInjector()
    settings = QoLSettings(
        enabled_toggles={QoLToggle.NO_CHAT, QoLToggle.NO_MARKDOWN, QoLToggle.REDACT_SECRETS},
        scope="session",
    )

    _, metadata = injector.build_fragment_block(settings, token_budget=1)

    assert metadata["injected"] is True
    assert metadata["token_budget_overrun"] is True
