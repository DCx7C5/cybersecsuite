"""Tests for pure helper functions in main.py."""
import time
import pytest
from unittest.mock import patch, MagicMock
from hypothesis import given, settings, strategies as st

import main
from main import _hash, _estimate_tokens, _rate_check, _audit, _cache_get, _cache_set, _cache_delete


# ── _hash ────────────────────────────────────────────────────────────────────────────
class TestHash:
    def test_returns_16_char_hex(self):
        assert len(_hash("hello")) == 16

    def test_hex_chars_only(self):
        result = _hash("hello")
        assert all(c in "0123456789abcdef" for c in result)

    def test_deterministic(self):
        assert _hash("same text") == _hash("same text")

    def test_different_inputs_differ(self):
        assert _hash("foo") != _hash("bar")

    def test_empty_string_ok(self):
        assert len(_hash("")) == 16

    @given(st.text())
    def test_always_16_chars(self, text):
        assert len(_hash(text)) == 16

    @given(st.text())
    def test_always_deterministic(self, text):
        assert _hash(text) == _hash(text)


# ── _estimate_tokens ────────────────────────────────────────────────────────────────────────
class TestEstimateTokens:
    def test_known_model_uses_ratio(self):
        assert _estimate_tokens("a" * 38, "gpt-4o") == 10

    def test_claude_ratio(self):
        assert _estimate_tokens("a" * 37, "claude-3-5-sonnet") == 10

    def test_unknown_model_uses_default_ratio(self):
        assert _estimate_tokens("a" * 38, "future-model") == 10

    def test_minimum_is_one(self):
        assert _estimate_tokens("", "gpt-4o") == 1

    def test_returns_int(self):
        assert isinstance(_estimate_tokens("hello", "gpt-4o"), int)

    @given(st.text(), st.sampled_from(list(main._TOKEN_RATIOS.keys())))
    def test_always_positive(self, text, model):
        assert _estimate_tokens(text, model) >= 1


# ── _rate_check ──────────────────────────────────────────────────────────────────────────
class TestRateCheck:
    def test_allows_calls_below_limit(self):
        for _ in range(5):
            _rate_check("clean_client")

    def test_raises_when_limit_exceeded(self):
        for _ in range(main.RATE_LIMIT_PM):
            main._rate_store["overload"].append(time.time())
        with pytest.raises(PermissionError, match="Rate limit exceeded"):
            _rate_check("overload")

    def test_evicts_expired_timestamps(self):
        main._rate_store["evict"] = [time.time() - 70] * 200
        _rate_check("evict")

    def test_clients_are_independent(self):
        for _ in range(main.RATE_LIMIT_PM):
            main._rate_store["full_client"].append(time.time())
        _rate_check("empty_client")

    def test_appends_timestamp_after_success(self):
        before = len(main._rate_store["new_client"])
        _rate_check("new_client")
        assert len(main._rate_store["new_client"]) == before + 1


# ── _audit ─────────────────────────────────────────────────────────────────────────────
class TestAudit:
    def test_prints_when_enabled(self, capsys):
        with patch.object(main, "AUDIT", True):
            _audit("my_action", key="val")
        out = capsys.readouterr().out
        assert "AUDIT" in out
        assert "my_action" in out

    def test_silent_when_disabled(self, capsys):
        with patch.object(main, "AUDIT", False):
            _audit("my_action")
        assert capsys.readouterr().out == ""

    def test_includes_kwargs(self, capsys):
        with patch.object(main, "AUDIT", True):
            _audit("action", foo="bar", baz=42)
        out = capsys.readouterr().out
        assert "foo=bar" in out
        assert "baz=42" in out

    def test_timestamp_in_output(self, capsys):
        with patch.object(main, "AUDIT", True):
            _audit("ts_test")
        out = capsys.readouterr().out
        assert "AUDIT [" in out


# ── cache backend (in-memory) ────────────────────────────────────────────────────────────────
class TestCacheMemoryBackend:
    def test_set_and_get(self):
        _cache_set("k1", {"data": "value"})
        assert _cache_get("k1") == {"data": "value"}

    def test_missing_key_returns_none(self):
        assert _cache_get("ghost") is None

    def test_delete_existing_key(self):
        _cache_set("del", {"x": 1})
        assert _cache_delete("del") is True
        assert _cache_get("del") is None

    def test_delete_missing_key_returns_false(self):
        assert _cache_delete("ghost") is False

    def test_overwrite_existing_key(self):
        _cache_set("ow", {"v": 1})
        _cache_set("ow", {"v": 2})
        assert _cache_get("ow") == {"v": 2}

    def test_ttl_param_ignored_in_memory(self):
        _cache_set("ttl_k", {"x": 1}, ttl=60)
        assert _cache_get("ttl_k") == {"x": 1}


# ── cache backend (Redis mock) ───────────────────────────────────────────────────────────────────
class TestCacheRedisBackend:
    @pytest.fixture
    def mock_redis(self):
        r = MagicMock()
        with patch.object(main, "_redis", r):
            yield r

    def test_get_hit(self, mock_redis):
        mock_redis.get.return_value = '{"data": "ok"}'
        assert _cache_get("k") == {"data": "ok"}
        mock_redis.get.assert_called_once_with("k")

    def test_get_miss(self, mock_redis):
        mock_redis.get.return_value = None
        assert _cache_get("k") is None

    def test_set_calls_setex(self, mock_redis):
        _cache_set("k", {"v": 1}, ttl=300)
        mock_redis.setex.assert_called_once()

    def test_delete_existing(self, mock_redis):
        mock_redis.delete.return_value = 1
        assert _cache_delete("k") is True

    def test_delete_missing(self, mock_redis):
        mock_redis.delete.return_value = 0
        assert _cache_delete("k") is False
