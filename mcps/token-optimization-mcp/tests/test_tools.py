"""Tests for all MCP tool functions in main.py."""
import pytest
from unittest.mock import patch, MagicMock

import main
from main import (
    estimate_tokens,
    compress_prompt,
    route_model,
    cache_lookup,
    cache_store,
    cache_invalidate,
    analyze_context,
    savings_report,
    deduplicate_messages,
    _cache_set,
)


# ── estimate_tokens ────────────────────────────────────────────────────────────────────────
class TestEstimateTokensTool:
    def test_returns_token_count(self):
        result = estimate_tokens("hello world", model="gpt-4o")
        assert result["tokens"] >= 1

    def test_fits_in_context_true_for_short_text(self):
        result = estimate_tokens("hi", model="gpt-4o")
        assert result["fits_in_context"] is True

    def test_fits_in_context_false_for_huge_text(self):
        with patch("main._estimate_tokens", return_value=200_000):
            result = estimate_tokens("x", model="gpt-4o")
        assert result["fits_in_context"] is False

    def test_context_used_pct_in_range(self):
        result = estimate_tokens("hello", model="gpt-4o")
        assert 0 <= result["context_used_pct"] <= 100

    def test_unknown_model_uses_128k_window(self):
        result = estimate_tokens("hi", model="unknown-model-xyz")
        assert result["context_window"] == 128_000

    def test_chars_matches_input_length(self):
        text = "hello world"
        result = estimate_tokens(text)
        assert result["chars"] == len(text)

    def test_model_field_echoed(self):
        result = estimate_tokens("test", model="claude-3-5-sonnet")
        assert result["model"] == "claude-3-5-sonnet"

    def test_chars_per_token_matches_known_ratio(self):
        result = estimate_tokens("x", model="gpt-4o")
        assert result["chars_per_token"] == 3.8

    def test_unknown_model_uses_default_ratio(self):
        result = estimate_tokens("x", model="does-not-exist")
        assert result["chars_per_token"] == main._DEFAULT_RATIO


# ── compress_prompt ────────────────────────────────────────────────────────────────────────
class TestCompressPrompt:
    def test_trim_collapses_multiple_newlines(self):
        result = compress_prompt("a\n\n\n\nb", strategy="trim")
        assert "\n\n\n" not in result["compressed_prompt"]

    def test_trim_collapses_multiple_spaces(self):
        result = compress_prompt("word1    word2", strategy="trim")
        assert "    " not in result["compressed_prompt"]

    def test_summarize_hint_wraps_long_paragraphs(self):
        result = compress_prompt("x" * 250, strategy="summarize_hint")
        assert "[SUMMARIZE:" in result["compressed_prompt"]

    def test_summarize_hint_keeps_short_paragraphs(self):
        result = compress_prompt("Short text.", strategy="summarize_hint")
        assert "[SUMMARIZE:" not in result["compressed_prompt"]

    def test_aggressive_strips_hash_comments(self):
        result = compress_prompt("code\n# comment\nmore", strategy="aggressive")
        assert "# comment" not in result["compressed_prompt"]

    def test_aggressive_strips_for_example(self):
        result = compress_prompt("Do this.\nFor example, try X.\nDo that.", strategy="aggressive")
        assert "For example" not in result["compressed_prompt"]

    def test_aggressive_strips_note(self):
        result = compress_prompt("Step 1\nNote: be careful\nStep 2", strategy="aggressive")
        assert "Note:" not in result["compressed_prompt"]

    def test_unknown_strategy_returns_error(self):
        result = compress_prompt("text", strategy="magic_wand")
        assert "error" in result
        assert "Unknown strategy" in result["error"]

    def test_tokens_saved_non_negative(self):
        result = compress_prompt("hello world", strategy="trim")
        assert result["tokens_saved"] >= 0

    def test_target_met_true_when_no_target(self):
        result = compress_prompt("hello", strategy="trim")
        assert result["target_met"] is True

    def test_target_met_false_when_target_too_small(self):
        result = compress_prompt("hello world this is a long prompt", strategy="trim", target_tokens=1)
        assert result["target_met"] is False

    def test_reduction_pct_in_valid_range(self):
        result = compress_prompt("hello world", strategy="trim")
        assert 0 <= result["reduction_pct"] <= 100

    def test_strategy_echoed_in_response(self):
        result = compress_prompt("text", strategy="trim")
        assert result["strategy"] == "trim"

    def test_original_and_compressed_tokens_present(self):
        result = compress_prompt("hello world", strategy="trim")
        assert "original_tokens" in result
        assert "compressed_tokens" in result


# ── route_model ────────────────────────────────────────────────────────────────────────────
class TestRouteModel:
    def test_returns_recommendation(self):
        result = route_model(estimated_tokens=100)
        assert result["recommendation"] is not None

    def test_recommendation_meets_quality(self):
        result = route_model(estimated_tokens=100, min_quality=7)
        assert result["recommendation"]["quality"] >= 7

    def test_no_candidates_for_impossible_token_count(self):
        result = route_model(estimated_tokens=999_999_999)
        assert result["recommendation"] is None
        assert result["all_candidates"] == []

    def test_require_long_context_filters_128k_models(self):
        result = route_model(estimated_tokens=100, require_long_context=True)
        for m in result["all_candidates"]:
            assert m["ctx"] > 128_000

    def test_prefer_free_puts_zero_cost_first(self):
        result = route_model(estimated_tokens=100, min_quality=0, prefer_free=True)
        assert result["all_candidates"][0]["cost_per_1k"] == 0.0

    def test_estimated_tokens_echoed(self):
        result = route_model(estimated_tokens=500)
        assert result["estimated_tokens"] == 500

    def test_max_cost_filter_respected(self):
        result = route_model(estimated_tokens=100, max_cost_per_1k=0.0)
        for m in result["all_candidates"]:
            assert m["cost_per_1k"] <= 0.0

    def test_estimated_cost_usd_present_in_candidates(self):
        result = route_model(estimated_tokens=1000)
        if result["recommendation"]:
            assert "estimated_cost_usd" in result["recommendation"]

    def test_all_candidates_sorted_cheapest_first_default(self):
        result = route_model(estimated_tokens=100, min_quality=0)
        costs = [m["cost_per_1k"] * 0.6 - m["quality"] * 0.4
                 for m in result["all_candidates"]]
        assert costs == sorted(costs)

    def test_no_candidates_when_min_quality_too_high(self):
        result = route_model(estimated_tokens=100, min_quality=11)
        assert result["recommendation"] is None


# ── cache_lookup ──────────────────────────────────────────────────────────────────────────
class TestCacheLookup:
    def test_miss_when_empty(self):
        result = cache_lookup(prompt="hello world")
        assert result["hit"] is False

    def test_hit_after_cache_set(self):
        _cache_set("cache:" + main._hash("my prompt"), {"result": "ans", "tokens_saved": 10})
        result = cache_lookup(prompt="my prompt")
        assert result["hit"] is True
        assert result["result"] == "ans"

    def test_no_prompt_and_no_key_returns_error(self):
        result = cache_lookup()
        assert "error" in result

    def test_lookup_by_explicit_cache_key(self):
        key = "explicit123"
        _cache_set(f"cache:{key}", {"result": "cached", "tokens_saved": 5})
        result = cache_lookup(cache_key=key)
        assert result["hit"] is True

    def test_hit_updates_session_savings(self):
        _cache_set("cache:" + main._hash("save test"), {"result": "ok", "tokens_saved": 42})
        cache_lookup(prompt="save test", client_id="saver")
        assert main._session_savings["saver"] == 42

    def test_miss_does_not_update_savings(self):
        cache_lookup(prompt="not cached", client_id="nosave")
        assert main._session_savings["nosave"] == 0

    def test_key_present_in_miss_response(self):
        result = cache_lookup(prompt="test")
        assert "key" in result

    def test_key_present_in_hit_response(self):
        _cache_set("cache:" + main._hash("p"), {"result": "r", "tokens_saved": 1})
        result = cache_lookup(prompt="p")
        assert "key" in result


# ── cache_store ───────────────────────────────────────────────────────────────────────────
class TestCacheStore:
    def test_stored_true(self):
        result = cache_store(prompt="hello", result="world", tokens_saved=5)
        assert result["stored"] is True

    def test_key_is_16_char_hex(self):
        result = cache_store(prompt="key test", result="res", tokens_saved=1)
        assert len(result["key"]) == 16

    def test_stored_entry_is_retrievable(self):
        cache_store(prompt="my prompt", result="my result", tokens_saved=100)
        lookup = cache_lookup(prompt="my prompt")
        assert lookup["hit"] is True
        assert lookup["result"] == "my result"

    def test_backend_in_memory_when_no_redis(self):
        result = cache_store(prompt="p", result="r", tokens_saved=1)
        assert result["backend"] == "in-memory"

    def test_custom_ttl_returned(self):
        result = cache_store(prompt="ttl", result="r", tokens_saved=1, ttl_seconds=999)
        assert result["ttl"] == 999

    def test_default_ttl_when_none(self):
        result = cache_store(prompt="def", result="r", tokens_saved=1)
        assert result["ttl"] == main.CACHE_TTL

    def test_metadata_stored_and_retrievable(self):
        cache_store(prompt="meta", result="r", tokens_saved=1, metadata={"tag": "test"})
        lookup = cache_lookup(prompt="meta")
        assert lookup.get("metadata", {}).get("tag") == "test"

    def test_tokens_saved_echoed(self):
        result = cache_store(prompt="ts", result="r", tokens_saved=77)
        assert result["tokens_saved"] == 77

    def test_redis_backend_label(self):
        mock_r = MagicMock()
        with patch.object(main, "_redis", mock_r):
            result = cache_store(prompt="p", result="r", tokens_saved=1)
        assert result["backend"] == "redis"
        mock_r.setex.assert_called_once()


# ── cache_invalidate ───────────────────────────────────────────────────────────────────────
class TestCacheInvalidate:
    def test_flush_all_clears_memory(self):
        _cache_set("cache:k1", {"x": 1})
        _cache_set("cache:k2", {"x": 2})
        result = cache_invalidate(flush_all=True)
        assert result["flush_all"] is True
        assert result["deleted"] >= 2
        assert main._mem == {}

    def test_flush_all_zero_when_empty(self):
        result = cache_invalidate(flush_all=True)
        assert result["deleted"] == 0

    def test_delete_single_key_success(self):
        cache_store(prompt="del me", result="r", tokens_saved=1)
        key = main._hash("del me")
        result = cache_invalidate(cache_key=key)
        assert result["deleted"] == 1

    def test_delete_nonexistent_key(self):
        result = cache_invalidate(cache_key="ghost")
        assert result["deleted"] == 0

    def test_no_args_returns_error(self):
        result = cache_invalidate()
        assert "error" in result

    def test_flush_all_redis(self):
        mock_r = MagicMock()
        mock_r.keys.return_value = ["cache:k1", "cache:k2"]
        with patch.object(main, "_redis", mock_r):
            result = cache_invalidate(flush_all=True)
        assert result["deleted"] == 2
        mock_r.delete.assert_called_once()

    def test_flush_all_redis_empty(self):
        mock_r = MagicMock()
        mock_r.keys.return_value = []
        with patch.object(main, "_redis", mock_r):
            result = cache_invalidate(flush_all=True)
        assert result["deleted"] == 0


# ── analyze_context ────────────────────────────────────────────────────────────────────────
class TestAnalyzeContext:
    def test_returns_total_tokens(self):
        msgs = [{"role": "user", "content": "hello"}]
        result = analyze_context(msgs)
        assert result["total_tokens"] >= 1

    def test_role_breakdown(self):
        msgs = [
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": "Hello"},
        ]
        result = analyze_context(msgs)
        assert "system" in result["role_breakdown"]
        assert "user" in result["role_breakdown"]

    def test_per_message_list_length(self):
        msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
        result = analyze_context(msgs)
        assert len(result["per_message"]) == 2
        assert result["per_message"][0]["role"] == "user"
        assert result["per_message"][1]["role"] == "assistant"

    def test_large_system_prompt_triggers_issue(self):
        large = "x " * 4000
        result = analyze_context([{"role": "system", "content": large}])
        assert any("System prompt" in i for i in result["issues"])

    def test_healthy_context_no_issues(self):
        msgs = [{"role": "user", "content": "Hello, how are you?"}]
        result = analyze_context(msgs)
        assert result["issues"] == []
        assert result["recommendations"] == ["Context healthy ✅"]

    def test_high_repetition_triggers_issue(self):
        repeated = "elephant " * 10
        result = analyze_context([{"role": "user", "content": repeated}])
        assert any("repetition" in i.lower() for i in result["issues"])

    def test_near_full_context_triggers_issue(self):
        with patch("main._estimate_tokens", return_value=110_000):
            result = analyze_context([{"role": "user", "content": "x"}], model="gpt-4o")
        assert any("truncation" in i for i in result["issues"])

    def test_context_used_pct_in_range(self):
        msgs = [{"role": "user", "content": "test"}]
        result = analyze_context(msgs)
        assert 0 <= result["context_used_pct"] <= 100

    def test_unknown_model_uses_128k_window(self):
        msgs = [{"role": "user", "content": "hi"}]
        result = analyze_context(msgs, model="future-model")
        assert result["context_window"] == 128_000

    def test_issues_trigger_recommendations(self):
        large = "x " * 4000
        result = analyze_context([{"role": "system", "content": large}])
        assert result["recommendations"] != ["Context healthy ✅"]
        assert len(result["recommendations"]) > 0

    def test_empty_messages(self):
        result = analyze_context([])
        assert result["total_tokens"] == 0
        assert result["role_breakdown"] == {}


# ── savings_report ─────────────────────────────────────────────────────────────────────────
class TestSavingsReport:
    def test_empty_returns_zero(self):
        result = savings_report()
        assert result["session_savings"] == []
        assert result["grand_total_tokens"] == 0

    def test_reports_per_client(self):
        main._session_savings["client_x"] = 500
        result = savings_report()
        assert any(r["client_id"] == "client_x" for r in result["session_savings"])

    def test_grand_total_matches_sum(self):
        main._session_savings["a"] = 300
        main._session_savings["b"] = 200
        result = savings_report()
        assert result["grand_total_tokens"] == 500

    def test_usd_saved_calculation(self):
        main._session_savings["cost_client"] = 1000
        result = savings_report(model="gpt-4o")
        entry = next(r for r in result["session_savings"] if r["client_id"] == "cost_client")
        assert entry["usd_saved"] == round(1000 / 1000 * 0.005, 6)

    def test_cache_entries_count(self):
        _cache_set("cache:k1", {"x": 1})
        result = savings_report()
        assert result["cache_entries"] == 1

    def test_backend_in_memory(self):
        result = savings_report()
        assert result["backend"] == "in-memory"

    def test_generated_at_present(self):
        result = savings_report()
        assert "generated_at" in result

    def test_unknown_model_uses_default_cost(self):
        main._session_savings["unk"] = 1000
        result = savings_report(model="nonexistent-model")
        entry = next(r for r in result["session_savings"] if r["client_id"] == "unk")
        assert entry["usd_saved"] == round(1000 / 1000 * 0.005, 6)

    def test_redis_cache_size_and_backend_label(self):
        mock_r = MagicMock()
        mock_r.keys.return_value = ["cache:k1", "cache:k2", "cache:k3"]
        with patch.object(main, "_redis", mock_r):
            result = savings_report()
        assert result["cache_entries"] == 3
        assert result["backend"] == "redis"


# ── deduplicate_messages ───────────────────────────────────────────────────────────────────
class TestDeduplicateMessages:
    def test_no_duplicates_unchanged(self):
        msgs = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
        result = deduplicate_messages(msgs)
        assert result["removed"] == 0
        assert len(result["deduplicated_messages"]) == 2

    def test_exact_duplicate_removed(self):
        msg = {"role": "user", "content": "hello"}
        result = deduplicate_messages([msg, msg])
        assert result["removed"] == 1
        assert len(result["deduplicated_messages"]) == 1

    def test_keeps_last_occurrence(self):
        msgs = [
            {"role": "user", "content": "dup"},
            {"role": "user", "content": "dup"},
            {"role": "user", "content": "unique"},
        ]
        result = deduplicate_messages(msgs)
        assert result["deduped_count"] == 2

    def test_tokens_saved_non_negative(self):
        msgs = [{"role": "user", "content": "same"}, {"role": "user", "content": "same"}]
        result = deduplicate_messages(msgs)
        assert result["tokens_saved"] >= 0

    def test_original_count_correct(self):
        msgs = [{"role": "user", "content": f"msg{i}"} for i in range(5)]
        result = deduplicate_messages(msgs)
        assert result["original_count"] == 5

    def test_empty_messages(self):
        result = deduplicate_messages([])
        assert result["deduplicated_messages"] == []
        assert result["tokens_saved"] == 0

    def test_different_roles_same_content_not_deduped(self):
        msgs = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hello"}]
        result = deduplicate_messages(msgs)
        assert result["removed"] == 0

    def test_tokens_before_gte_tokens_after(self):
        msgs = [{"role": "user", "content": "dup"}, {"role": "user", "content": "dup"}]
        result = deduplicate_messages(msgs)
        assert result["tokens_before"] >= result["tokens_after"]
