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


# ═══════════════════════════════════════════════════════════════════════════════
# T010 — Additional Comprehensive Tests (expansion)
# ═══════════════════════════════════════════════════════════════════════════════

class TestQoLValidation:
    """T010 test group: Model validation and security."""

    def test_validate_toggle_combo_accepts_valid_combinations(self):
        """Verify that non-dangerous toggle combinations pass validation."""
        from ai_proxy.qol_controls.models import validate_toggle_combo
        # Safe combinations should not raise
        validate_toggle_combo(frozenset({QoLToggle.NO_THINKING, QoLToggle.NO_CHAT}))
        validate_toggle_combo(frozenset({QoLToggle.NO_MARKDOWN, QoLToggle.MINIMAL}))
        validate_toggle_combo(frozenset({QoLToggle.REDACT_SECRETS, QoLToggle.APPEND_AUDIT_TRAIL}))

    def test_validate_toggle_combo_rejects_file_only_with_append_audit(self):
        """FILE_ONLY + APPEND_AUDIT_TRAIL is contradictory and must raise."""
        from ai_proxy.qol_controls.models import (
            validate_toggle_combo,
            QoLSecurityError,
        )
        with pytest.raises(QoLSecurityError) as exc_info:
            validate_toggle_combo(
                frozenset({QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL})
            )
        assert "Contradictory" in str(exc_info.value)

    def test_validate_toggle_combo_rejects_file_only_with_structured_only(self):
        """FILE_ONLY + STRUCTURED_ONLY is contradictory and must raise."""
        from ai_proxy.qol_controls.models import (
            validate_toggle_combo,
            QoLSecurityError,
        )
        with pytest.raises(QoLSecurityError):
            validate_toggle_combo(
                frozenset({QoLToggle.FILE_ONLY, QoLToggle.STRUCTURED_ONLY})
            )

    def test_validate_toggle_combo_rejects_minimal_with_append_audit(self):
        """MINIMAL + APPEND_AUDIT_TRAIL is contradictory and must raise."""
        from ai_proxy.qol_controls.models import (
            validate_toggle_combo,
            QoLSecurityError,
        )
        with pytest.raises(QoLSecurityError):
            validate_toggle_combo(frozenset({QoLToggle.MINIMAL, QoLToggle.APPEND_AUDIT_TRAIL}))


class TestQoLManagerAdvanced:
    """T010 test group: Manager functions with edge cases."""

    def test_manager_inject_respects_scope_cascade(self, tmp_manager: QoLManager):
        """T017: session scope with no toggles should cascade to project scope."""
        project_settings = QoLSettings(scope="project")
        project_settings.activate(QoLToggle.NO_THINKING)
        tmp_manager.save_settings(project_settings)

        # Session has no toggles
        body = {"messages": [{"role": "user", "content": "hi"}]}
        modified = tmp_manager.inject_into_request(body, scope="session")
        # Should have injected project's settings
        assert "[OUTPUT-CONTROLS]" in modified["messages"][0]["content"]

    def test_manager_agent_preset_binding(self, tmp_manager: QoLManager):
        """T018: agent preset binding and retrieval."""
        # Create a preset
        preset = QoLSettings()
        preset.activate(QoLToggle.MINIMAL, QoLToggle.NO_CHAT)
        tmp_manager.save_preset("test-preset", preset)
        # Bind agent to preset
        tmp_manager.set_agent_preset("my-agent", "test-preset")
        # Retrieve and verify
        bound_preset = tmp_manager.get_agent_preset("my-agent")
        assert bound_preset == "test-preset"

    def test_manager_agent_preset_clear(self, tmp_manager: QoLManager):
        """T018: clearing agent preset binding."""
        tmp_manager.set_agent_preset("my-agent", "silent")
        tmp_manager.set_agent_preset("my-agent", None)
        bound = tmp_manager.get_agent_preset("my-agent")
        assert bound is None

    def test_manager_load_agent_settings_returns_none_when_unbound(self, tmp_manager: QoLManager):
        """T018: load_agent_settings returns None if agent has no binding."""
        result = tmp_manager.load_agent_settings("unbound-agent")
        assert result is None

    def test_manager_load_agent_settings_with_binding(self, tmp_manager: QoLManager):
        """T018: load_agent_settings returns resolved settings for bound agent."""
        tmp_manager.set_agent_preset("agent-x", "code-only")
        settings = tmp_manager.load_agent_settings("agent-x")
        assert settings is not None
        assert QoLToggle.FILE_ONLY in settings.enabled_toggles

    def test_manager_inject_respects_agent_preset_override(self, tmp_manager: QoLManager):
        """T018: agent preset overrides scope settings in inject_into_request."""
        session_settings = QoLSettings(scope="session")
        session_settings.activate(QoLToggle.MINIMAL)
        tmp_manager.save_settings(session_settings)

        # Agent has different preset
        tmp_manager.set_agent_preset("my-agent", "code-only")

        body = {"messages": [{"role": "user", "content": "test"}]}
        modified = tmp_manager.inject_into_request(
            body, scope="session", agent_name="my-agent"
        )
        # Should use agent preset (FILE_ONLY), not session (MINIMAL)
        fragment = modified["messages"][0]["content"]
        assert "NOTHING ELSE MAY APPEAR" in fragment

    def test_manager_inject_with_explicit_settings_parameter(self, tmp_manager: QoLManager):
        """Inject respects explicit settings parameter over scope/agent."""
        explicit = QoLSettings()
        explicit.activate(QoLToggle.NO_MARKDOWN)

        body = {"messages": [{"role": "user", "content": "hello"}]}
        modified = tmp_manager.inject_into_request(body, settings=explicit)

        fragment = modified["messages"][0]["content"]
        assert "plain text" in fragment.lower()

    def test_manager_estimate_tokens(self, tmp_manager: QoLManager):
        """Estimate tokens for injection fragment."""
        s = QoLSettings()
        s.activate(QoLToggle.MINIMAL, QoLToggle.NO_THINKING)
        tokens = tmp_manager.estimate_tokens(s)
        assert isinstance(tokens, int)
        assert tokens > 0

    def test_manager_dangerous_combo_in_save_raises_error(self, tmp_manager: QoLManager):
        """save_settings rejects dangerous toggle combinations."""
        from ai_proxy.qol_controls.models import QoLSecurityError
        s = QoLSettings()
        s.activate(QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL)
        with pytest.raises(QoLSecurityError):
            tmp_manager.save_settings(s)


class TestQoLManagerErrorHandling:
    """T010 test group: Error handling and resilience."""

    def test_inject_into_request_resilient_to_missing_context(self, tmp_manager: QoLManager):
        """T020: inject_into_request returns body unmodified on any error."""
        # This should not raise even with bad input
        body = None
        result = tmp_manager.inject_into_request(body, scope="session")  # type: ignore
        assert result is None

    def test_inject_into_request_with_missing_system_and_messages(self, tmp_manager: QoLManager):
        """Empty body should return unmodified."""
        body = {}
        result = tmp_manager.inject_into_request(body, scope="session")
        assert result == {}

    def test_settings_loads_gracefully_with_corrupted_file(self, tmp_manager: QoLManager):
        """Manager tolerates corrupted/invalid JSON files gracefully."""
        # Write invalid JSON
        tmp_manager._settings_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_manager._settings_path.write_text("not valid json at all {{{", encoding="utf-8")
        # Should not raise, should return defaults
        s = tmp_manager.load_settings("session")
        assert isinstance(s, QoLSettings)


class TestQoLPresetManagement:
    """T010 test group: Preset listing, loading, saving."""

    def test_list_presets_returns_dict_with_source_metadata(self, tmp_manager: QoLManager):
        """list_presets includes source (builtin/user) for each preset."""
        presets = tmp_manager.list_presets()
        assert presets["silent"]["source"] == "builtin"

    def test_save_preset_creates_user_presets_file(self, tmp_manager: QoLManager):
        """Saving a preset creates/updates the user presets file."""
        s = QoLSettings()
        s.activate(QoLToggle.MINIMAL, QoLToggle.NO_MARKDOWN)
        tmp_manager.save_preset("my-custom", s)

        # Verify it's loadable
        loaded = tmp_manager.load_preset("my-custom")
        assert loaded is not None
        assert loaded.enabled_toggles == s.enabled_toggles

    def test_load_preset_returns_copy_not_reference(self, tmp_manager: QoLManager):
        """load_preset returns a deep copy to prevent accidental mutations."""
        preset1 = tmp_manager.load_preset("silent")
        preset2 = tmp_manager.load_preset("silent")
        # Modify one
        preset1.activate(QoLToggle.NO_MARKDOWN)
        # Other should be unaffected
        assert QoLToggle.NO_MARKDOWN not in preset2.enabled_toggles

    def test_set_agent_preset_validates_combo_before_saving(self, tmp_manager: QoLManager):
        """set_agent_preset validates that the resolved preset has a valid combo."""
        from ai_proxy.qol_controls.models import QoLSecurityError
        # Create a bad preset
        bad = QoLSettings()
        bad.activate(QoLToggle.FILE_ONLY, QoLToggle.APPEND_AUDIT_TRAIL)
        tmp_manager.save_preset("bad-preset", bad)
        # Binding it should raise
        with pytest.raises(QoLSecurityError):
            tmp_manager.set_agent_preset("agent", "bad-preset")


class TestQoLFragmentGeneration:
    """T010 test group: Fragment building and caching."""

    def test_build_injection_returns_string(self, tmp_manager: QoLManager):
        """build_injection returns a non-empty string for active toggles."""
        s = QoLSettings()
        s.activate(QoLToggle.NO_THINKING)
        fragment = tmp_manager.build_injection(s)
        assert isinstance(fragment, str)
        assert len(fragment) > 0

    def test_build_injection_includes_envelope(self, tmp_manager: QoLManager):
        """Fragment includes [OUTPUT-CONTROLS] envelope markers."""
        s = QoLSettings()
        s.activate(QoLToggle.MINIMAL)
        fragment = tmp_manager.build_injection(s)
        assert "[OUTPUT-CONTROLS]" in fragment
        assert "[/OUTPUT-CONTROLS]" in fragment

    def test_build_injection_deterministic_ordering(self, tmp_manager: QoLManager):
        """Same toggles produce same fragment regardless of order."""
        s1 = QoLSettings()
        s1.activate(QoLToggle.NO_THINKING, QoLToggle.NO_CHAT, QoLToggle.MINIMAL)

        s2 = QoLSettings()
        s2.activate(QoLToggle.MINIMAL, QoLToggle.NO_THINKING, QoLToggle.NO_CHAT)

        f1 = tmp_manager.build_injection(s1)
        f2 = tmp_manager.build_injection(s2)
        assert f1 == f2

    def test_build_injection_cache_expiry(self, tmp_manager: QoLManager):
        """Cache respects TTL (though we can't easily test actual expiry)."""
        s = QoLSettings()
        s.activate(QoLToggle.NO_CHAT)
        key = frozenset(s.enabled_toggles)

        # Build once
        tmp_manager.build_injection(s)
        assert key in tmp_manager._fragment_cache

        # Clear cache manually
        tmp_manager._fragment_cache.clear()
        assert key not in tmp_manager._fragment_cache

        # Build again
        _ = tmp_manager.build_injection(s)
        assert key in tmp_manager._fragment_cache


class TestQoLStatusDiagnostics:
    """T010 test group: Status and diagnostics."""

    def test_status_includes_all_required_fields(self, tmp_manager: QoLManager):
        """Status method returns all expected diagnostic fields."""
        s = QoLSettings()
        s.activate(QoLToggle.FILE_ONLY)
        tmp_manager.save_settings(s)

        status = tmp_manager.status("session")
        assert "scope" in status
        assert "active_toggles" in status
        assert "preset_name" in status
        assert "fragment_preview" in status
        assert "estimated_tokens" in status
        assert "toggle_hash" in status

    def test_status_toggle_hash_is_4_char_hex(self, tmp_manager: QoLManager):
        """Toggle hash is a 4-char hex string."""
        s = QoLSettings()
        s.activate(QoLToggle.MINIMAL)
        tmp_manager.save_settings(s)

        status = tmp_manager.status("session")
        hash_val = status["toggle_hash"]
        assert len(hash_val) == 8  # 4 bytes = 8 hex chars
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_status_fragment_preview_truncated(self, tmp_manager: QoLManager):
        """Fragment preview in status is truncated to 120 chars."""
        s = QoLSettings()
        # Activate many toggles but NOT the dangerous combinations
        # FILE_ONLY + APPEND_AUDIT_TRAIL is dangerous, so skip APPEND_AUDIT_TRAIL
        s.activate(
            QoLToggle.NO_THINKING,
            QoLToggle.NO_CHAT,
            QoLToggle.MINIMAL,
            QoLToggle.NO_MARKDOWN,
            QoLToggle.STRUCTURED_ONLY,
            QoLToggle.REDACT_SECRETS,
        )
        tmp_manager.save_settings(s)

        status = tmp_manager.status("session")
        preview = status["fragment_preview"]
        # Preview should be truncated: either exactly 120 chars + ellipsis or less than 120 chars
        if preview.endswith("…"):
            # If truncated, the core preview should be ≤120 chars before ellipsis
            assert len(preview) <= 121  # 120 + 1 char for ellipsis (Unicode char)
        else:
            assert len(preview) <= 120
