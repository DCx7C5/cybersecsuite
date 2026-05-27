"""Tests for QoL built-in presets."""

import msgspec

from css.core.settings.qol import BUILTIN_PRESETS, QoLSettings, QoLToggle


def test_builtin_presets_exact_toggle_membership():
    expected: dict[str, set[QoLToggle]] = {
        "silent": {QoLToggle.NO_THINKING, QoLToggle.NO_CHAT, QoLToggle.MINIMAL},
        "code-only": {QoLToggle.FILE_ONLY, QoLToggle.NO_CHAT, QoLToggle.NO_MARKDOWN},
        "structured": {QoLToggle.STRUCTURED_ONLY, QoLToggle.NO_CHAT},
        "audit": {QoLToggle.APPEND_AUDIT_TRAIL, QoLToggle.REDACT_SECRETS},
        "plain-text": {QoLToggle.NO_MARKDOWN},
    }

    assert set(BUILTIN_PRESETS.keys()) == set(expected.keys())
    for preset_name, expected_toggles in expected.items():
        preset = BUILTIN_PRESETS[preset_name]
        assert preset.enabled_toggles == expected_toggles
        assert preset.scope == "preset"
        assert preset.preset_name == preset_name


def test_builtin_presets_do_not_share_toggle_sets():
    toggle_set_ids = [id(preset.enabled_toggles) for preset in BUILTIN_PRESETS.values()]
    assert len(toggle_set_ids) == len(set(toggle_set_ids))


def test_builtin_presets_roundtrip_serialization():
    for preset_name, preset in BUILTIN_PRESETS.items():
        encoded = msgspec.json.encode(preset)
        decoded = msgspec.json.decode(encoded, type=QoLSettings)

        assert decoded.enabled_toggles == preset.enabled_toggles
        assert decoded.scope == "preset"
        assert decoded.preset_name == preset_name
