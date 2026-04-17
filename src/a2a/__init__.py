"""
A2A package — Google Agent-to-Agent protocol implementation.

Usage:
    # Single agent server
    from a2a import CybersecA2AAgent, A2AServer
    agent = CybersecA2AAgent(base_url="http://localhost:8000")
    server = A2AServer(agent)

    # Multi-agent orchestration — auto-loads all .claude/agents/*.md
    from a2a import AgentRegistry, OrchestratorAgent, A2AServer
    from a2a.dev_agents import create_default_registry

    registry = create_default_registry()          # loads all .claude agents
    orchestrator = OrchestratorAgent(registry=registry)
    server = A2AServer(orchestrator)

    # Client
    from a2a import A2AClient
    async with A2AClient("http://localhost:9000") as client:
        task = await client.send_task("@agent hunter: investigate this IOC")
        task = await client.send_task("@agent cybersec-analyst: CVE-2024-1234")
        task = await client.send_task("@fanout analyze this binary")
        task = await client.send_task("list agents")
"""

from a2a.enums import TaskState, MessageRole, PartType, AuthScheme
from a2a.models import (
    AgentCard, AgentCapabilities, AgentSkill,
    Task, TaskStatus, Message, TaskArtifact,
    TextPart, FilePart, DataPart,
    JSONRPCRequest, JSONRPCResponse, JSONRPCError,
    A2AErrorCodes,
)
from a2a.task_store import TaskStore
from a2a.agent import BaseA2AAgent
from a2a.server import A2AServer
from a2a.client import A2AClient, A2AClientError
from a2a.registry import AgentRegistry, RemoteAgent
from a2a.orchestrator import OrchestratorAgent
from a2a.cybersec_agent import CybersecA2AAgent
from a2a.dev_agents import PythonDeveloperAgent, CppDeveloperAgent, create_default_registry
from a2a.agent_loader import ClaudeAgentCard, frontmatter_to_claude_agent

# Agent SDK integration (optional — requires claude-agent-sdk)
try:
    from a2a.agent_sdk import (
        build_agent_options,
        run_agent_query,
        run_orchestrator_query,
        create_cybersec_mcp_server,
    )
    _HAS_AGENT_SDK = True
except ImportError:
    _HAS_AGENT_SDK = False

__all__ = [
    # Enums
    "TaskState", "MessageRole", "PartType", "AuthScheme",
    # Models
    "AgentCard", "AgentCapabilities", "AgentSkill",
    "Task", "TaskStatus", "Message", "TaskArtifact",
    "TextPart", "FilePart", "DataPart",
    "JSONRPCRequest", "JSONRPCResponse", "JSONRPCError",
    "A2AErrorCodes",
    # Core
    "TaskStore", "BaseA2AAgent",
    # Server / Client
    "A2AServer", "A2AClient", "A2AClientError",
    # Registry & Orchestration
    "AgentRegistry", "RemoteAgent",
    "OrchestratorAgent",
    # Specialized agent implementations (for running as A2A servers)
    "CybersecA2AAgent",
    "PythonDeveloperAgent",
    "CppDeveloperAgent",
    "create_default_registry",
    # .claude agent loader
    "ClaudeAgentCard", "frontmatter_to_claude_agent",
    # Agent SDK (optional)
    "build_agent_options", "run_agent_query",
    "run_orchestrator_query", "create_cybersec_mcp_server",
]
