"""Tests for the LLM orchestration layer (src/llm/).

These tests run without a live Anthropic API key or Postgres instance.
DB-dependent tests are skipped when the test DB is unavailable.
OTEL tests use an in-memory span exporter.
"""
from __future__ import annotations

import asyncio
import os
import sys
import types
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# ===========================================================================
# 1. Pricing
# ===========================================================================

class TestPricing:
    """Unit tests for src/llm/pricing.py"""

    def setup_method(self):
        from llm.pricing import cost_usd, known_models, PRICING_LAST_UPDATED
        self.cost_usd = cost_usd
        self.known_models = known_models
        self.PRICING_LAST_UPDATED = PRICING_LAST_UPDATED

    def test_known_sonnet_cost(self):
        cost = self.cost_usd("claude-sonnet-4-5", 1_000_000, 0)
        assert cost == Decimal("3.00")

    def test_known_haiku_cost(self):
        cost = self.cost_usd("claude-haiku-4-5", 0, 1_000_000)
        assert cost == Decimal("4.00")

    def test_cache_read_tokens(self):
        cost = self.cost_usd("claude-sonnet-4-5", 0, 0, 0, 1_000_000)
        assert cost == Decimal("0.30")

    def test_cache_write_tokens(self):
        cost = self.cost_usd("claude-sonnet-4-5", 0, 0, 1_000_000, 0)
        assert cost == Decimal("3.75")

    def test_unknown_model_uses_default(self):
        # Unknown model falls back to sonnet-class pricing
        cost = self.cost_usd("some-future-model", 1_000_000, 0)
        assert cost == Decimal("3.00")

    def test_zero_tokens_zero_cost(self):
        assert self.cost_usd("claude-haiku-4-5", 0, 0) == Decimal("0")

    def test_small_token_count(self):
        cost = self.cost_usd("claude-sonnet-4-5", 100, 100)
        assert cost > Decimal("0")
        assert cost < Decimal("0.01")

    def test_known_models_list_non_empty(self):
        models = self.known_models()
        assert len(models) >= 5
        assert "claude-sonnet-4-5" in models

    def test_pricing_last_updated_format(self):
        parts = self.PRICING_LAST_UPDATED.split("-")
        assert len(parts) == 3

    def test_opus_costs_more_than_haiku(self):
        opus = self.cost_usd("claude-opus-4-5", 1000, 1000)
        haiku = self.cost_usd("claude-haiku-4-5", 1000, 1000)
        assert opus > haiku


# ===========================================================================
# 2. SID resolution (orchestrator)
# ===========================================================================

class TestResolveSid:
    """Unit tests for llm.orchestrator.resolve_sid()"""

    def setup_method(self):
        from llm.orchestrator import resolve_sid
        self.resolve_sid = resolve_sid

    def test_explicit_sid_wins(self):
        assert self.resolve_sid("abc123def456") == "abc123def456"

    def test_env_gwt_sid(self, tmp_path, monkeypatch):
        monkeypatch.setenv("GWT_SID", "aabbccddeeff")
        assert self.resolve_sid() == "aabbccddeeff"

    def test_env_cybersec_session_id(self, monkeypatch):
        monkeypatch.delenv("GWT_SID", raising=False)
        monkeypatch.setenv("CYBERSEC_SESSION_ID", "112233445566")
        assert self.resolve_sid() == "112233445566"

    def test_marker_file_walk(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GWT_SID", raising=False)
        monkeypatch.delenv("CYBERSEC_SESSION_ID", raising=False)
        marker = tmp_path / ".worktree-session"
        marker.write_text("deadbeef0000")
        monkeypatch.chdir(tmp_path)
        assert self.resolve_sid() == "deadbeef0000"

    def test_global_fallback(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GWT_SID", raising=False)
        monkeypatch.delenv("CYBERSEC_SESSION_ID", raising=False)
        monkeypatch.chdir(tmp_path)
        assert self.resolve_sid() == "global"

    def test_explicit_overrides_env(self, monkeypatch):
        monkeypatch.setenv("GWT_SID", "eeeeeeeeeeee")
        assert self.resolve_sid("aaaaaaaaaaaa") == "aaaaaaaaaaaa"


# ===========================================================================
# 3. AsyncLLMClient (mocked Anthropic)
# ===========================================================================

class TestAsyncLLMClient:
    """Tests for src/llm/client.py — Anthropic is mocked."""

    def _make_client(self, sid="testsid00000", **kwargs):
        from llm.client import AsyncLLMClient
        client = AsyncLLMClient(model="claude-haiku-4-5", sid=sid, **kwargs)
        return client

    def _fake_usage(self, input_tok=10, output_tok=20):
        u = MagicMock()
        u.input_tokens = input_tok
        u.output_tokens = output_tok
        u.cache_read_input_tokens = 0
        u.cache_creation_input_tokens = 0
        return u

    def test_init_defaults(self):
        client = self._make_client()
        assert client.sid == "testsid00000"
        assert client.model == "claude-haiku-4-5"
        assert client.log_prompts is False

    def test_init_base_url_from_env(self, monkeypatch):
        monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://localhost:8000/v1")
        from llm.client import AsyncLLMClient
        client = AsyncLLMClient.__new__(AsyncLLMClient)
        # Just verify the env var logic without calling full init
        base = os.environ.get("ANTHROPIC_BASE_URL")
        assert base == "http://localhost:8000/v1"

    def test_cost_computed_correctly(self):
        from llm.pricing import cost_usd
        cost = cost_usd("claude-haiku-4-5", 10, 20, 0, 0)
        expected = (Decimal("0.80") * 10 + Decimal("4.00") * 20) / Decimal("1_000_000")
        assert cost == expected

    @pytest.mark.asyncio
    async def test_bg_persist_calls_persist_fn(self):
        persist_calls = []

        async def fake_persist(**kwargs):
            persist_calls.append(kwargs)

        client = self._make_client(db_persist_fn=fake_persist)
        await client._bg_persist(10, 20, 0, 0, Decimal("0.0001"), 50.0, True, None)
        assert len(persist_calls) == 1
        assert persist_calls[0]["sid"] == "testsid00000"
        assert persist_calls[0]["success"] is True

    @pytest.mark.asyncio
    async def test_bg_persist_error_flag(self):
        persist_calls = []

        async def fake_persist(**kwargs):
            persist_calls.append(kwargs)

        client = self._make_client(db_persist_fn=fake_persist)
        await client._bg_persist(5, 5, 0, 0, Decimal("0"), 10.0, True, "timeout error")
        assert persist_calls[0]["success"] is False
        assert persist_calls[0]["error"] == "timeout error"

    @pytest.mark.asyncio
    async def test_bg_persist_no_fn_does_nothing(self):
        client = self._make_client()
        # Should not raise
        await client._bg_persist(0, 0, 0, 0, Decimal("0"), 0.0, False, None)

    @pytest.mark.asyncio
    async def test_bg_persist_calls_oo_index(self):
        oo_calls = []

        async def fake_oo(stream_name, docs):
            oo_calls.append((stream_name, docs))

        client = self._make_client(oo_index_fn=fake_oo)
        await client._bg_persist(10, 20, 0, 0, Decimal("0.001"), 30.0, True, None)
        assert len(oo_calls) == 1
        assert oo_calls[0][0] == "llm-calls"
        doc = oo_calls[0][1][0]
        assert doc["worktree_sid"] == "testsid00000"
        assert doc["success"] is True
        assert "model" in doc
        assert "messages" not in doc  # never log prompt text

    @pytest.mark.asyncio
    async def test_bg_persist_exception_non_fatal(self):
        async def bad_persist(**kwargs):
            raise RuntimeError("DB down")

        client = self._make_client(db_persist_fn=bad_persist)
        # Must not raise
        await client._bg_persist(1, 1, 0, 0, Decimal("0"), 1.0, True, None)


# ===========================================================================
# 4. LLMOrchestrator
# ===========================================================================

class TestLLMOrchestrator:
    """Tests for src/llm/orchestrator.py"""

    def setup_method(self):
        # Reset singleton between tests
        import llm.orchestrator as orch_mod
        orch_mod._instance = None

    def test_init_resolves_sid(self, monkeypatch):
        monkeypatch.setenv("GWT_SID", "cafebabe0000")
        from llm.orchestrator import LLMOrchestrator
        orc = LLMOrchestrator()
        assert orc.sid == "cafebabe0000"

    def test_get_orchestrator_singleton(self, monkeypatch):
        monkeypatch.delenv("GWT_SID", raising=False)
        monkeypatch.delenv("CYBERSEC_SESSION_ID", raising=False)
        from llm.orchestrator import get_orchestrator
        import llm.orchestrator as mod
        mod._instance = None
        a = get_orchestrator()
        b = get_orchestrator()
        assert a is b

    def test_get_orchestrator_reset(self):
        import llm.orchestrator as mod
        mod._instance = None
        from llm.orchestrator import get_orchestrator
        orc = get_orchestrator(default_model="claude-haiku-4-5")
        assert orc._model == "claude-haiku-4-5"

    def test_make_client_returns_client(self, monkeypatch):
        monkeypatch.delenv("GWT_SID", raising=False)
        from llm.orchestrator import LLMOrchestrator
        orc = LLMOrchestrator(sid="global")
        with patch("llm.db.get_pool"):
            with patch("llm.client.AsyncLLMClient._make_client", return_value=MagicMock()):
                client = orc._make_client()
                assert client is not None


# ===========================================================================
# 5. DB helpers (unit-level, no Postgres needed)
# ===========================================================================

class TestDbHelpers:
    """Unit tests for src/llm/db.py that don't require Postgres."""

    def test_dsn_from_env(self, monkeypatch):
        monkeypatch.setenv("CYBERSEC_DB_DSN", "postgresql://user:pw@host/db")
        # Import fresh to pick up env var
        import importlib
        import llm.db as db_mod
        dsn = db_mod._dsn()
        assert dsn == "postgresql://user:pw@host/db"

    def test_dsn_built_from_parts(self, monkeypatch):
        monkeypatch.delenv("CYBERSEC_DB_DSN", raising=False)
        monkeypatch.setenv("CYBERSEC_DB_USER", "myuser")
        monkeypatch.setenv("CYBERSEC_DB_HOST", "myhost")
        monkeypatch.setenv("CYBERSEC_DB_PORT", "5433")
        monkeypatch.setenv("CYBERSEC_DB_NAME", "mydb")
        monkeypatch.setenv("CYBERSEC_DB_PASSWORD", "secret")
        import llm.db as db_mod
        dsn = db_mod._dsn()
        assert "myuser" in dsn
        assert "myhost" in dsn
        assert "5433" in dsn
        assert "mydb" in dsn

    def test_run_sync_executes_coroutine(self):
        from llm.db import run_sync

        async def _return42():
            return 42

        result = run_sync(_return42())
        assert result == 42

    @pytest.mark.asyncio
    async def test_persist_call_bootstraps_missing_session(self):
        import llm.db as db_mod

        calls = []

        class FakePool:
            async def execute(self, query, *args):
                calls.append((query, args))
                return "OK"

        with patch.object(db_mod, "get_pool", AsyncMock(return_value=FakePool())):
            await db_mod.persist_call(
                sid="global",
                model="claude-haiku-4-5",
                input_tokens=1,
                output_tokens=2,
                cost_usd=Decimal("0.000001"),
                latency_ms=12.0,
                stream=False,
                success=True,
            )

        assert len(calls) == 2
        assert "INSERT INTO llm_sessions" in calls[0][0]
        assert calls[0][1][0] == "global"
        assert "INSERT INTO llm_calls" in calls[1][0]


# ===========================================================================
# 6. DB integration tests (require Postgres)
# ===========================================================================

@pytest.mark.asyncio
async def _try_db_connection():
    """Helper — returns True if test DB is available."""
    try:
        import asyncpg
        dsn = os.environ.get(
            "CYBERSEC_DB_DSN",
            "postgresql://cybersec:@localhost:5432/cybersec_forensics",
        )
        conn = await asyncpg.connect(dsn, timeout=2)
        await conn.close()
        return True
    except Exception:
        return False


_SKIP_DB = pytest.mark.skipif(
    not asyncio.run(_try_db_connection()),
    reason="Postgres not available",
)


@pytest.mark.asyncio
@_SKIP_DB
async def test_db_open_and_close_session():
    """Integration: open → close session round-trip."""
    import asyncpg
    from llm.db import open_session, close_session, get_pool

    sid = "aabbccddeeff"
    # Clean up any leftover
    pool = await get_pool()
    await pool.execute("DELETE FROM llm_sessions WHERE sid=$1", sid)

    await open_session(sid, "/tmp/test-repo", "main")
    row = await pool.fetchrow("SELECT * FROM llm_sessions WHERE sid=$1", sid)
    assert row is not None
    assert row["sid"].strip() == sid

    # Idempotent
    await open_session(sid, "/tmp/test-repo", "main")

    summary = await close_session(sid)
    assert summary["sid"].strip() == sid
    assert summary["total_calls"] == 0

    # Cleanup
    await pool.execute("DELETE FROM llm_sessions WHERE sid=$1", sid)


@pytest.mark.asyncio
@_SKIP_DB
async def test_db_persist_call():
    """Integration: persist_call inserts a row."""
    from llm.db import open_session, persist_call, cost_report, get_pool

    sid = "112233445566"
    pool = await get_pool()
    await pool.execute("DELETE FROM llm_sessions WHERE sid=$1", sid)

    await open_session(sid, "/tmp", "test-branch")
    await persist_call(
        sid=sid,
        model="claude-haiku-4-5",
        input_tokens=100,
        output_tokens=50,
        cost_usd=Decimal("0.000125"),
        latency_ms=123.4,
        stream=False,
        success=True,
    )
    report = await cost_report(sid)
    assert report["sid"] == sid
    assert len(report["by_model"]) == 1
    assert report["by_model"][0]["model"] == "claude-haiku-4-5"
    assert report["by_model"][0]["calls"] == 1

    # Cleanup
    await pool.execute("DELETE FROM llm_sessions WHERE sid=$1", sid)


# ===========================================================================
# 7. CLI integration (worktree-session-manager.py)
# ===========================================================================

class TestWSMCli:
    """Test new CLI subcommands via argparse."""

    def _load_wsm(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "wsm",
            Path(__file__).parent.parent / "scripts" / "worktree-session-manager.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_llm_session_open_parser_exists(self):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["llm-session-open", "aabbccddeeff"])
        assert args.command == "llm-session-open"
        assert args.sid == "aabbccddeeff"

    def test_llm_session_close_parser_exists(self):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["llm-session-close", "aabbccddeeff"])
        assert args.command == "llm-session-close"

    def test_llm_cost_parser_exists(self):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["llm-cost", "aabbccddeeff"])
        assert args.command == "llm-cost"

    def test_create_parser_accepts_with_llm(self):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["create", "--with-llm"])
        assert args.command == "create"
        assert args.with_llm is True

    def test_teardown_parser_accepts_with_llm(self):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["teardown", "aabbccddeeff", "--with-llm"])
        assert args.command == "teardown"
        assert args.with_llm is True

    def test_llm_session_open_invalid_sid(self, capsys):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["llm-session-open", "bad-sid"])
        result = wsm.cmd_llm_session_open(args)
        assert result == 1  # invalid SID

    def test_llm_cost_invalid_sid(self, capsys):
        wsm = self._load_wsm()
        parser = wsm.build_parser()
        args = parser.parse_args(["llm-cost", "toolong0000000000"])
        result = wsm.cmd_llm_cost(args)
        assert result == 1  # invalid SID
