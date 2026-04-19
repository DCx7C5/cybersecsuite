"""Tests for Agent SDK integration — AgentRunner, SessionManager."""

import pytest

try:
    from agent import AgentRunner, SessionManager
    from agent.sessions import SessionRecord

    AGENT_SDK_AVAILABLE = True
except ImportError as e:
    AGENT_SDK_AVAILABLE = False
    pytest.skip(f"Agent SDK not fully available: {e}", allow_module_level=True)


class TestAgentRunner:
    """Test AgentRunner — multi-turn agent queries."""

    @pytest.fixture
    def runner(self):
        return AgentRunner(agent_name="cybersec-analyst", mode="blue")

    def test_runner_initialization(self, runner):
        assert runner.agent_name == "cybersec-analyst"
        assert runner.mode == "blue"

    def test_red_mode_prefix(self):
        runner = AgentRunner(agent_name="test", mode="red")
        prefix = runner._get_prefix()
        assert "RED" in prefix

    def test_purple_mode_prefix(self):
        runner = AgentRunner(agent_name="test", mode="purple")
        prefix = runner._get_prefix()
        assert "PURPLE" in prefix

    def test_blue_mode_no_prefix(self):
        runner = AgentRunner(agent_name="test", mode="blue")
        prefix = runner._get_prefix()
        assert prefix == ""

    def test_stream_returns_async_generator(self, runner):
        gen = runner.stream("test prompt")
        assert hasattr(gen, "__aiter__")


class TestSessionManager:
    """Test SessionManager — session registration and lookup."""

    @pytest.fixture
    def sm(self):
        return SessionManager()

    def test_register_session(self, sm):
        record = sm.register(
            session_id="test-sess-1",
            agent_name="cybersec-analyst",
            mode="red",
        )
        assert isinstance(record, SessionRecord)
        assert record.agent_name == "cybersec-analyst"
        assert record.mode == "red"
        assert record.session_id == "test-sess-1"

    def test_get_session(self, sm):
        sm.register("sess-get-1", "threat-modeler", "purple")
        record = sm.get("sess-get-1")
        assert record is not None
        assert record.session_id == "sess-get-1"

    def test_get_unknown_returns_none(self, sm):
        assert sm.get("nonexistent-id") is None

    def test_list_local_sessions(self, sm):
        sm.register("list-1", "analyst", "blue")
        sm.register("list-2", "modeler", "red")
        sessions = sm.list_local()
        assert len(sessions) >= 2

    def test_register_with_case_id(self, sm):
        record = sm.register(
            "case-sess", "analyst", "blue",
            case_id="CASE-001",
        )
        assert record.case_id == "CASE-001"

    def test_list_local_by_case_id(self, sm):
        sm.register("case-a", "analyst", "blue", case_id="CASE-X")
        sm.register("case-b", "modeler", "red", case_id="CASE-Y")
        filtered = sm.list_local(case_id="CASE-X")
        assert all(s.case_id == "CASE-X" for s in filtered)


@pytest.mark.anyio
class TestSessionHooks:
    """Test session hooks — security, audit, IOC, cost."""

    async def test_security_hook_runs(self):
        from agent.hooks import security_hook

        result = await security_hook({"prompt": "test"})
        assert isinstance(result, dict)

    async def test_audit_hook_runs(self):
        from agent.hooks import audit_hook

        result = await audit_hook({"agent": "analyst", "prompt": "test"})
        assert isinstance(result, dict)

    async def test_ioc_hook_runs(self):
        from agent.hooks import ioc_hook

        result = await ioc_hook(
            {"response": "IP: 192.168.1.1"},
            output_data={"text": "found IOC"},
        )
        assert isinstance(result, dict)

    async def test_cost_hook_runs(self):
        from agent.hooks import cost_hook

        result = await cost_hook({
            "model": "claude-opus",
            "input_tokens": 100,
            "output_tokens": 200,
        })
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
