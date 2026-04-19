"""Tests for A2A protocol — task store, agent registry, models."""

import pytest

from a2a.models import (
    Task, TaskStatus, TaskSendParams, Message, TextPart,
    TaskArtifact,
)
from a2a.task_store import TaskStore
from a2a.registry import AgentRegistry
from a2a.enums import TaskState, MessageRole, PartType


# ── Helpers ───────────────────────────────────────────────────────────────────

def _send_params(task_id: str = "t1", text: str = "hello") -> TaskSendParams:
    return TaskSendParams(
        id=task_id,
        message=Message(
            role=MessageRole.USER,
            parts=[TextPart(type=PartType.TEXT, text=text)],
        ),
    )


class TestTaskStore:
    """Test in-memory task store."""

    @pytest.fixture
    def store(self):
        return TaskStore(persist=False)

    def test_create_task(self, store):
        task = store.create(_send_params("t1", "Analyze CVE-2024-1234"))
        assert task.id == "t1"
        assert task.status.state == TaskState.SUBMITTED

    def test_get_task(self, store):
        store.create(_send_params("t1"))
        task = store.get("t1")
        assert task is not None
        assert task.id == "t1"

    def test_get_missing_task(self, store):
        assert store.get("nonexistent") is None

    def test_update_status(self, store):
        store.create(_send_params("t1"))
        store.update_status("t1", TaskState.WORKING)
        task = store.get("t1")
        assert task.status.state == TaskState.WORKING

    def test_add_artifact(self, store):
        store.create(_send_params("t1"))
        artifact = TaskArtifact(
            name="result",
            parts=[TextPart(type=PartType.TEXT, text="IOC1, IOC2")],
        )
        store.add_artifact("t1", artifact)
        task = store.get("t1")
        assert len(task.artifacts) == 1
        assert task.artifacts[0].name == "result"

    def test_cancel_task(self, store):
        store.create(_send_params("t1"))
        result = store.cancel("t1")
        assert result is not None
        assert result.status.state == TaskState.CANCELED

    def test_cancel_completed_task_returns_none(self, store):
        store.create(_send_params("t1"))
        store.update_status("t1", TaskState.COMPLETED)
        assert store.cancel("t1") is None

    def test_list_tasks(self, store):
        for i in range(3):
            store.create(_send_params(f"t{i}"))
        tasks = store.list_tasks()
        assert len(tasks) == 3

    def test_list_tasks_by_session(self, store):
        p1 = _send_params("t1")
        p1.session_id = "s1"
        p2 = _send_params("t2")
        p2.session_id = "s2"
        store.create(p1)
        store.create(p2)
        assert len(store.list_tasks(session_id="s1")) == 1

    def test_generate_id(self, store):
        id1 = store.generate_id()
        id2 = store.generate_id()
        assert id1 != id2


class TestAgentRegistry:
    """Test A2A agent registry."""

    @pytest.fixture
    def registry(self):
        return AgentRegistry()

    def _make_card(self, name: str, skills=None):
        from a2a.models import AgentCard, AgentCapabilities, AgentAuthentication, AgentSkill
        return AgentCard(
            name=name,
            description=f"{name} agent",
            url=f"http://localhost:9000/{name}",
            version="1.0",
            capabilities=AgentCapabilities(),
            authentication=AgentAuthentication(schemes=["none"]),
            skills=skills or [],
        )

    def test_register_agent(self, registry):
        card = self._make_card("test-agent")
        agent = registry.register("http://localhost:9000", card)
        assert agent.card.name == "test-agent"
        assert len(registry.all()) == 1

    def test_find_by_name(self, registry):
        card = self._make_card("analyst")
        registry.register("http://localhost:9001", card)
        agent = registry.find_by_name("analyst")
        assert agent is not None
        assert agent.card.name == "analyst"

    def test_find_by_name_case_insensitive(self, registry):
        card = self._make_card("CybersecAgent")
        registry.register("http://localhost:9002", card)
        assert registry.find_by_name("cybersecagent") is not None

    def test_find_missing_agent(self, registry):
        assert registry.find_by_name("nonexistent") is None

    def test_find_by_skill_id(self, registry):
        from a2a.models import AgentSkill
        card = self._make_card("analyst", skills=[
            AgentSkill(id="cve-lookup", name="CVE Lookup"),
            AgentSkill(id="ioc-analysis", name="IOC Analysis"),
        ])
        registry.register("http://localhost:9003", card)
        matches = registry.find_by_skill_id("cve-lookup")
        assert len(matches) == 1

    def test_find_by_tag(self, registry):
        from a2a.models import AgentSkill
        card = self._make_card("analyst", skills=[
            AgentSkill(id="cve-lookup", name="CVE", tags=["cve", "vuln"]),
        ])
        registry.register("http://localhost:9004", card)
        assert len(registry.find_by_tag("cve")) == 1
        assert len(registry.find_by_tag("unknown")) == 0


class TestA2AModels:
    """Test A2A Pydantic models."""

    def test_task_creation(self):
        task = Task(
            id="task-123",
            status=TaskStatus(state=TaskState.WORKING),
            history=[
                Message(
                    role=MessageRole.USER,
                    parts=[TextPart(type=PartType.TEXT, text="Analyze this")],
                ),
            ],
        )
        assert task.id == "task-123"
        assert task.status.state == TaskState.WORKING
        assert len(task.history) == 1

    def test_task_status_timestamp(self):
        status = TaskStatus(state=TaskState.SUBMITTED)
        assert status.timestamp is not None

    def test_task_send_params(self):
        params = _send_params("t1", "hello")
        assert params.id == "t1"
        assert params.message.role == MessageRole.USER

    def test_text_part(self):
        part = TextPart(text="hello")
        assert part.type == PartType.TEXT

    def test_task_artifact(self):
        artifact = TaskArtifact(
            name="output",
            parts=[TextPart(text="result data")],
        )
        assert artifact.name == "output"
        assert len(artifact.parts) == 1


class TestA2AProtocol:
    """Test A2A JSON-RPC 2.0 protocol format."""

    def test_tasks_send_format(self):
        request = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "params": {
                "id": "task-789",
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": "Investigate CVE-2024-1234"}],
                },
            },
            "id": 1,
        }
        assert request["jsonrpc"] == "2.0"
        assert request["method"] == "tasks/send"

    def test_tasks_get_format(self):
        request = {
            "jsonrpc": "2.0",
            "method": "tasks/get",
            "params": {"id": "task-xyz"},
            "id": 2,
        }
        assert request["method"] == "tasks/get"
        assert request["params"]["id"] == "task-xyz"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
