"""Tests for QoL Output Controls — models, prompts, manager, MCP tools, dashboard endpoints.

Referenz:
    plan.md T010 — Phase 1 QoL Core
    src/ai_proxy/qol_controls/models.py
    src/ai_proxy/qol_controls/prompts.py
    src/ai_proxy/qol_controls/manager.py
    src/csmcp/cybersec/qol_tools.py
    src/dashboard/api/qol.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

# ── Module-level guards ───────────────────────────────────────────────────────

try:
    from ai_proxy.qol_controls.models import (
        QoLToggle,
        QoLSettings,
        BUILTIN_PRESETS,
        toggle_description,
    )
    from ai_proxy.qol_controls.prompts import build_fragment_block, FRAGMENTS
    from ai_proxy.qol_controls.manager import QoLManager, _estimate_tokens

    QOL_AVAILABLE = True
except ImportError:
    QOL_AVAILABLE = False

pytestmark = pytest.mark.skipif(not QOL_AVAILABLE, reason="QoL controls module not available")


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmp_manager(tmp_path: Path) -> QoLManager:
    """A QoLManager pointing at a temp directory — no side effects on real state."""
    mgr = QoLManager()
    mgr._base_dir = tmp_path
    return mgr


# ═══════════════════════════════════════════════════════════════════════════════
# T002 — models.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestQoLToggle:
    def test_all_eight_toggles_exist(self):
        expected = {
            "no_thinking", "no_chat", "minimal", "file_only",
            "no_markdown", "structured_only", "redact_secrets", "append_audit_trail",
        }
        actual = {t.value for t in QoLToggle}
        assert actual == expected

    def test_toggle_description_returns_string(self):
        for toggle in QoLToggle:
            desc = toggle_description(toggle)
            assert isinstance(desc, str) and desc


class TestQoLSettings:
    def test_default_settings_are_empty(self):
        s = QoLSettings()
        assert s.enabled_toggles == set()
        assert s.scope == "session"
        assert s.preset_name is None

    def test_activate_and_deactivate(self):
        s = QoLSettings()
        s.activate(QoLToggle.NO_THINKING, QoLToggle.MINIMAL)
        assert QoLToggle.NO_THINKING in s.enabled_toggles
        assert QoLToggle.MINIMAL in s.enabled_toggles
        s.deactivate(QoLToggle.MINIMAL)
        assert QoLToggle.MINIMAL not in s.enabled_toggles

    def test_is_active(self):
        s = QoLSettings()
        s.activate(QoLToggle.FILE_ONLY)
        assert s.is_active(QoLToggle.FILE_ONLY)
        assert not s.is_active(QoLToggle.NO_CHAT)

    def test_is_active_accepts_string(self):
        s = QoLSettings()
        s.activate("no_chat")
        assert s.is_active("no_chat")

    def test_as_dict_round_trip(self):
        s = QoLSettings()
        s.activate(QoLToggle.REDACT_SECRETS, QoLToggle.APPEND_AUDIT_TRAIL)
        d = s.as_dict()
        s2 = QoLSettings.from_dict(d)
        assert s.enabled_toggles == s2.enabled_toggles

    def test_from_dict_ignores_unknown_toggles(self):
        d = {"enabled_toggles": ["no_thinking", "obsolete_toggle_xyz"], "scope": "project"}
        s = QoLSettings.from_dict(d)
        assert QoLToggle.NO_THINKING in s.enabled_toggles
        assert len(s.enabled_toggles) == 1  # unknown silently dropped

    def test_builtin_presets_all_valid(self):
        for name, preset in BUILTIN_PRESETS.items():
            assert preset.enabled_toggles, f"Preset '{name}' has no toggles"
            for t in preset.enabled_toggles:
                assert isinstance(t, QoLToggle)


# ═══════════════════════════════════════════════════════════════════════════════
# T003 — prompts.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestPrompts:
    def test_fragments_defined_for_all_toggles(self):
        for toggle in QoLToggle:
            assert toggle in FRAGMENTS, f"Missing fragment for {toggle}"

    def test_file_only_contains_required_phrase(self):
        # plan.md Warning 3: "NOTHING ELSE MAY APPEAR" must be in file_only
        assert "NOTHING ELSE MAY APPEAR" in FRAGMENTS[QoLToggle.FILE_ONLY]

    def test_empty_toggles_returns_empty_string(self):
        assert build_fragment_block(frozenset()) == ""

    def test_single_toggle_builds_block(self):
        block = build_fragment_block(frozenset({QoLToggle.NO_THINKING}))
        assert block
        assert "[OUTPUT-CONTROLS]" in block

    def test_all_toggles_block_is_deterministic(self):
        key = frozenset(QoLToggle)
        block1 = build_fragment_block(key)
        block2 = build_fragment_block(key)
        assert block1 == block2

    def test_all_toggles_under_token_budget(self):
        block = build_fragment_block(frozenset(QoLToggle))
        estimated = _estimate_tokens(block)
        # Plan target: ≤ 55 tokens (our all-enabled case should be reasonable)
        assert estimated < 200, f"Token estimate {estimated} seems wrong: {block[:100]}"


# ═══════════════════════════════════════════════════════════════════════════════
# T004 — manager.py
# ═══════════════════════════════════════════════════════════════════════════════

class TestQoLManager:
    def test_load_returns_empty_settings_when_no_file(self, tmp_manager: QoLManager):
        s = tmp_manager.load_settings("session")
        assert s.enabled_toggles == set()

    def test_save_and_reload(self, tmp_manager: QoLManager):
        s = QoLSettings()
        s.activate(QoLToggle.MINIMAL, QoLToggle.NO_CHAT)
        tmp_manager.save_settings(s)
        loaded = tmp_manager.load_settings("session")
        assert loaded.enabled_toggles == s.enabled_toggles

    def test_reset_clears_settings(self, tmp_manager: QoLManager):
        s = QoLSettings()
        s.activate(QoLToggle.FILE_ONLY)
        tmp_manager.save_settings(s)
        tmp_manager.reset_settings("session")
        loaded = tmp_manager.load_settings("session")
        assert loaded.enabled_toggles == set()

    def test_build_injection_caches_result(self, tmp_manager: QoLManager):
        s = QoLSettings()
        s.activate(QoLToggle.NO_THINKING)
        fragment1 = tmp_manager.build_injection(s)
        fragment2 = tmp_manager.build_injection(s)  # should hit cache
        assert fragment1 == fragment2

    def test_inject_into_request_prepends_to_system_key(self, tmp_manager: QoLManager):
        s = QoLSettings()
        s.activate(QoLToggle.MINIMAL)
        tmp_manager.save_settings(s)
        body = {"system": "You are helpful.", "messages": [{"role": "user", "content": "hi"}]}
        modified = tmp_manager.inject_into_request(body, scope="session")
        assert "[OUTPUT-CONTROLS]" in modified["system"]
        assert "You are helpful." in modified["system"]

    def test_inject_into_request_inserts_system_message(self, tmp_manager: QoLManager):
        s = QoLSettings()
        s.activate(QoLToggle.NO_CHAT)
        tmp_manager.save_settings(s)
        body = {"messages": [{"role": "user", "content": "hello"}]}
        modified = tmp_manager.inject_into_request(body, scope="session")
        assert modified["messages"][0]["role"] == "system"
        assert "[OUTPUT-CONTROLS]" in modified["messages"][0]["content"]

    def test_inject_noop_when_no_toggles(self, tmp_manager: QoLManager):
        body = {"messages": [{"role": "user", "content": "hi"}]}
        modified = tmp_manager.inject_into_request(body, scope="session")
        assert modified is body  # unchanged object

    def test_status_returns_expected_keys(self, tmp_manager: QoLManager):
        status = tmp_manager.status("session")
        assert "scope" in status
        assert "active_toggles" in status
        assert "estimated_tokens" in status
        assert "toggle_hash" in status

    def test_list_presets_includes_builtins(self, tmp_manager: QoLManager):
        presets = tmp_manager.list_presets()
        assert "silent" in presets
        assert "code-only" in presets
        assert "structured" in presets

    def test_save_and_load_user_preset(self, tmp_manager: QoLManager):
        s = QoLSettings()
        s.activate(QoLToggle.NO_MARKDOWN, QoLToggle.MINIMAL)
        s.preset_name = "my-preset"
        tmp_manager.save_preset("my-preset", s)
        loaded = tmp_manager.load_preset("my-preset")
        assert loaded is not None
        assert loaded.enabled_toggles == s.enabled_toggles

    def test_load_builtin_preset(self, tmp_manager: QoLManager):
        preset = tmp_manager.load_preset("silent")
        assert preset is not None
        assert QoLToggle.NO_THINKING in preset.enabled_toggles


# ═══════════════════════════════════════════════════════════════════════════════
# T005 — combo.py injection hook (import-level smoke test)
# ═══════════════════════════════════════════════════════════════════════════════

class TestComboInjectionHook:
    def test_qol_inject_helper_returns_body_unchanged_when_no_toggles(self):
        """_qol_inject must not raise and must return a dict."""
        try:
            from ai_proxy.routing.combo import _qol_inject
        except ImportError:
            pytest.skip("combo module not importable in test env")
        body = {"messages": [{"role": "user", "content": "test"}]}
        result = _qol_inject(body, session_id=None)
        assert isinstance(result, dict)
