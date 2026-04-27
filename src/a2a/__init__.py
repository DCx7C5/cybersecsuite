"""
A2A package — Google Agent-to-Agent protocol implementation.

Usage:
    # Single agent server (default — .claude/agents/ as source of truth)
    from a2a import CybersecA2AAgent, A2AServer
    agent = CybersecA2AAgent(base_url="http://localhost:8000")
    server = A2AServer(agent)

    # Client
    from a2a import A2AClient
    async with A2AClient("http://localhost:8000") as client:
        task = await client.send_task("CVE-2024-1234 analysis")
        task = await client.send_task("analyze IOC: 192.168.1.100")

All agent routing is handled by the Agent SDK which reads .claude/agents/*.md directly.
Routing to 60 providers (DeepSeek, Gemini, Groq, …) is done via the AI proxy at
ANTHROPIC_BASE_URL=http://localhost:8000/v1 using each agent's declared model.
"""
from src.logger import getLogger  # noqa: F401

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
from src.registries.agents import AgentRegistry, RemoteAgent
from a2a.cybersec_agent import CybersecA2AAgent
from a2a.agent_loader import ClaudeAgentCard, frontmatter_to_claude_agent

# Agent SDK integration (optional — requires claude-agent-sdk)
try:
    from a2a.agent_sdk import (
        build_agent_options,
        build_agent_definitions,
        clear_caches,
        run_agent_query,
        run_orchestrator_query,
        run_agent_stream,
        run_agent_stream_with_memory,
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
    # Registry
    "AgentRegistry", "RemoteAgent",
    # Agent implementation
    "CybersecA2AAgent",
    # .claude agent loader
    "ClaudeAgentCard", "frontmatter_to_claude_agent",
    # Agent SDK (optional)
    "build_agent_options", "build_agent_definitions", "clear_caches",
    "run_agent_query", "run_orchestrator_query", "run_agent_stream",
    "run_agent_stream_with_memory",
]
