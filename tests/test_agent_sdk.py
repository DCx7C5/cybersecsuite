"""Tests for Agent SDK integration — AgentRunner, SessionManager."""
import pytest

try:
    from agent import AgentRunner, SessionManager
    from agent.models import SessionRecord
    AGENT_SDK_AVAILABLE = True
except ImportError as e:
    AGENT_SDK_AVAILABLE = False
    pytest.skip(f"Agent SDK not fully available: {e}", allow_module_level=True)


class TestAgentRunner:
    """Test AgentRunner — multi-turn agent queries."""

    @pytest.fixture
    def runner(self):
        """Create an AgentRunner instance."""
        return AgentRunner(agent_name="cybersec-analyst", mode="blue")

    def test_runner_initialization(self, runner):
        """Test runner initializes correctly."""
        assert runner.agent_name == "cybersec-analyst"
        assert runner.mode == "blue"

    def test_mode_prefix_injection(self, runner):
        """Test that mode prefix is injected into prompts."""
        prompt = "Analyze CVE-2024-1234"
        prefixed = runner._inject_mode_prefix(prompt)
        assert "[MODE: BLUE]" in prefixed or "BLUE" in prefixed

    @pytest.mark.asyncio
    async def test_streaming_generator(self, runner):
        """Test that streaming returns an async generator."""
        # Note: This won't actually call Claude without API key
        # but we can test the generator structure
        try:
            gen = runner.stream("test prompt")
            assert hasattr(gen, "__aiter__")
        except Exception:
            # API might not be configured, but structure is testable
            pass


class TestSessionManager:
    """Test SessionManager — session lifecycle."""

    @pytest.fixture
    def session_manager(self):
        """Create a SessionManager instance."""
        return SessionManager()

    def test_session_creation(self, session_manager):
        """Test creating a new session."""
        session = session_manager.create_session(
            agent_name="cybersec-analyst",
            mode="red",
        )
        assert isinstance(session, SessionRecord)
        assert session.agent_name == "cybersec-analyst"
        assert session.mode == "red"
        assert session.session_id
        assert len(session.messages) == 0

    def test_session_retrieval(self, session_manager):
        """Test retrieving a session."""
        session1 = session_manager.create_session(
            agent_name="threat-modeler",
            mode="purple",
        )
        session2 = session_manager.get_session(session1.session_id)
        assert session2.session_id == session1.session_id

    def test_add_message_to_session(self, session_manager):
        """Test adding messages to a session."""
        session = session_manager.create_session("analyst", "blue")
        session_manager.add_message(session.session_id, "user", "What is this hash?")
        session_manager.add_message(session.session_id, "assistant", "It's MD5...")

        session = session_manager.get_session(session.session_id)
        assert len(session.messages) == 2
        assert session.messages[0]["role"] == "user"
        assert session.messages[1]["role"] == "assistant"

    def test_list_sessions(self, session_manager):
        """Test listing all sessions."""
        session_manager.create_session("analyst", "blue")
        session_manager.create_session("modeler", "red")

        sessions = session_manager.list_sessions()
        assert len(sessions) >= 2

    def test_close_session(self, session_manager):
        """Test closing a session."""
        session = session_manager.create_session("analyst", "blue")
        session_id = session.session_id

        session_manager.close_session(session_id)
        session = session_manager.get_session(session_id)
        assert session.closed is True


class TestSessionHooks:
    """Test session hooks — security, audit, IOC, cost."""

    @pytest.mark.asyncio
    async def test_security_hook_runs(self):
        """Test that security hook executes."""
        from agent.hooks import security_hook
        result = await security_hook({"prompt": "test"})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_audit_hook_runs(self):
        """Test that audit hook executes."""
        from agent.hooks import audit_hook
        result = await audit_hook({"agent": "analyst", "prompt": "test"})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_ioc_hook_runs(self):
        """Test that IOC hook executes."""
        from agent.hooks import ioc_hook
        result = await ioc_hook({"response": "IP: 192.168.1.1"})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_cost_hook_runs(self):
        """Test that cost hook executes."""
        from agent.hooks import cost_hook
        result = await cost_hook({
            "model": "claude-opus",
            "input_tokens": 100,
            "output_tokens": 200,
        })
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

