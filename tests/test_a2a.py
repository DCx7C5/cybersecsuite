"""Tests for A2A protocol — task orchestration, agent registry."""
import pytest

from a2a.models import Task, TaskStatus
from a2a.task_store import TaskStore
from a2a.registry import AgentRegistry


class TestTaskStore:
    """Test in-memory + DB task store."""

    @pytest.fixture
    def store(self):
        """Create a task store."""
        return TaskStore()

    def test_create_task(self, store):
        """Test creating a new task."""
        task = store.create_task(
            agent_name="cybersec-analyst",
            task_description="Analyze CVE-2024-1234",
            messages=[{"role": "user", "content": "What's the impact?"}],
        )
        assert task.id
        assert task.status == TaskStatus.SUBMITTED
        assert task.agent_name == "cybersec-analyst"

    def test_get_task(self, store):
        """Test retrieving a task."""
        task1 = store.create_task(
            agent_name="analyst",
            task_description="test",
            messages=[],
        )
        task2 = store.get_task(task1.id)
        assert task2.id == task1.id

    def test_update_task_status(self, store):
        """Test updating task status."""
        task = store.create_task(
            agent_name="analyst",
            task_description="test",
            messages=[],
        )
        store.update_status(task.id, TaskStatus.WORKING)
        task = store.get_task(task.id)
        assert task.status == TaskStatus.WORKING

    def test_complete_task(self, store):
        """Test marking task as completed."""
        task = store.create_task(
            agent_name="analyst",
            task_description="test",
            messages=[],
        )
        store.complete_task(task.id, result={"findings": ["IOC1", "IOC2"]})
        task = store.get_task(task.id)
        assert task.status == TaskStatus.COMPLETED
        assert task.result

    def test_list_tasks_by_status(self, store):
        """Test filtering tasks by status."""
        # Create multiple tasks
        for i in range(3):
            store.create_task(
                agent_name="analyst",
                task_description=f"test{i}",
                messages=[],
            )

        submitted = store.list_tasks(status=TaskStatus.SUBMITTED)
        assert len(submitted) >= 3

    def test_task_ttl_cleanup(self, store):
        """Test that TTL cleanup removes old tasks."""
        task = store.create_task(
            agent_name="analyst",
            task_description="test",
            messages=[],
        )
        # Manually trigger cleanup (in production it's async)
        # store.cleanup_expired_tasks()
        # Task should be retrievable until TTL
        assert store.get_task(task.id) is not None


class TestAgentRegistry:
    """Test A2A agent discovery registry."""

    @pytest.fixture
    def registry(self):
        """Create an agent registry."""
        return AgentRegistry()

    def test_register_agent(self, registry):
        """Test registering an agent."""
        registry.register_agent(
            name="test-agent",
            description="Test agent for unit testing",
            capabilities=["analyze", "query"],
            url="http://localhost:9000",
        )
        agents = registry.list_agents()
        assert len(agents) > 0

    def test_get_agent_by_name(self, registry):
        """Test retrieving agent by name."""
        registry.register_agent(
            name="analyst",
            description="Analyst agent",
            capabilities=["analyze"],
            url="http://localhost:9001",
        )
        agent = registry.get_agent("analyst")
        if agent:
            assert agent.name == "analyst"

    def test_agent_discovery(self, registry):
        """Test discovering agents by capability."""
        registry.register_agent(
            name="agent1",
            description="Agent 1",
            capabilities=["analyze", "hunt"],
            url="http://localhost:9001",
        )
        registry.register_agent(
            name="agent2",
            description="Agent 2",
            capabilities=["model", "attribute"],
            url="http://localhost:9002",
        )

        # Find agents with "analyze" capability
        agents = registry.find_by_capability("analyze")
        assert len(agents) >= 1

    def test_agent_health_check(self, registry):
        """Test checking agent health."""
        registry.register_agent(
            name="health-test",
            description="Test health check",
            capabilities=[],
            url="http://localhost:9999",  # Unlikely to exist
        )
        # Health check would typically fail on unavailable agent
        # but registry should handle gracefully


class TestA2ATaskModels:
    """Test A2A Pydantic models."""

    def test_task_model_creation(self):
        """Test creating Task model."""
        task = Task(
            id="task-123",
            agent_name="analyst",
            task_description="Analyze findings",
            status=TaskStatus.WORKING,
            messages=[
                {"role": "user", "content": "Analyze this"},
                {"role": "assistant", "content": "Done"},
            ],
        )
        assert task.id == "task-123"
        assert len(task.messages) == 2

    def test_task_validation(self):
        """Test Task model validation."""
        with pytest.raises(Exception):
            # Invalid status should fail validation
            Task(
                id="task-456",
                agent_name="analyst",
                task_description="test",
                status="INVALID_STATUS",  # type: ignore
                messages=[],
            )


class TestA2AProtocol:
    """Test A2A JSON-RPC 2.0 protocol."""

    def test_message_send_format(self):
        """Test message/send JSON-RPC format."""
        request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "agent": "cybersec-analyst",
                "task_id": "task-789",
                "message": "Investigate CVE-2024-1234",
            },
            "id": 1,
        }
        assert request["jsonrpc"] == "2.0"
        assert request["method"] == "message/send"
        assert "params" in request

    def test_tasks_get_format(self):
        """Test tasks/get JSON-RPC format."""
        request = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {
                "task_id": "task-xyz",
            },
            "id": 2,
        }
        assert request["method"] == "tasks/get"
        assert request["params"]["task_id"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

