"""
A2A package — Google Agent-to-Agent protocol implementation.

Usage:
    # Single agent server (default — .claude/agents/ as source of truth)
    from google_a2a import CybersecA2AAgent, A2AServer
    agent = CybersecA2AAgent(base_url="http://localhost:8000")
    server = A2AServer(agent)

    # Client
    from google_a2a import A2AClient
    async with A2AClient("http://localhost:8000") as client:
        task = await client.send_task("CVE-2024-1234 analysis")
        task = await client.send_task("analyze IOC: 192.168.1.100")

All agent routing is handled by the Agent SDK which reads .claude/agents/*.md directly.
Routing to 60 providers (DeepSeek, Gemini, Groq, …) is done via the AI asgi at
ANTHROPIC_BASE_URL=http://localhost:8000/v1 using each agent's declared model.

All top-level names are lazy-loaded to prevent import-time crashes from optional
dependencies (hooks, crypto, agent SDK, DB models).
"""

from __future__ import annotations

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

_MODULE_MAP: dict[str, tuple[str, str]] = {
    # Enums
    "TaskState":        ("google_a2a.enums", "TaskState"),
    "MessageRole":      ("google_a2a.enums", "MessageRole"),
    "PartType":         ("google_a2a.enums", "PartType"),
    "AuthScheme":       ("google_a2a.enums", "AuthScheme"),
    # Models
    "AgentCard":        ("google_a2a.models", "AgentCard"),
    "AgentCapabilities":("google_a2a.models", "AgentCapabilities"),
    "AgentSkill":       ("google_a2a.models", "AgentSkill"),
    "Task":             ("google_a2a.models", "Task"),
    "TaskStatus":       ("google_a2a.models", "TaskStatus"),
    "Message":          ("google_a2a.models", "Message"),
    "TaskArtifact":     ("google_a2a.models", "TaskArtifact"),
    "TextPart":         ("google_a2a.models", "TextPart"),
    "FilePart":         ("google_a2a.models", "FilePart"),
    "DataPart":         ("google_a2a.models", "DataPart"),
    "JSONRPCRequest":   ("google_a2a.models", "JSONRPCRequest"),
    "JSONRPCResponse":  ("google_a2a.models", "JSONRPCResponse"),
    "JSONRPCError":     ("google_a2a.models", "JSONRPCError"),
    "A2AErrorCodes":    ("google_a2a.models", "A2AErrorCodes"),
    # Core
    "TaskStore":        ("google_a2a.task_store", "TaskStore"),
    "BaseA2AAgent":     ("google_a2a.agent", "BaseA2AAgent"),
    # Server / Client
    "A2AServer":        ("google_a2a.server", "A2AServer"),
    "A2AClient":        ("google_a2a.client", "A2AClient"),
    "A2AClientError":   ("google_a2a.client", "A2AClientError"),
    # Registry (lazy to break circular import with registries.agents)
    "AgentRegistry":    ("core.registries.agents", "AgentRegistry"),
    "RemoteAgent":      ("core.registries.agents", "RemoteAgent"),
    # Agent implementation (imports crypto + db — lazy)
    "CybersecA2AAgent": ("google_a2a.cybersec_agent", "CybersecA2AAgent"),
    # .claude agent loader (imports hooks — lazy)
    "ClaudeAgentCard":          ("google_a2a.agent_loader", "ClaudeAgentCard"),
    "frontmatter_to_claude_agent": ("google_a2a.agent_loader", "frontmatter_to_claude_agent"),
    # Agent SDK (optional — requires claude-agent-sdk)
    "build_agent_options":       ("google_a2a.agent_sdk", "build_agent_options"),
    "build_agent_definitions":   ("google_a2a.agent_sdk", "build_agent_definitions"),
    "clear_caches":              ("google_a2a.agent_sdk", "clear_caches"),
    "run_agent_query":           ("google_a2a.agent_sdk", "run_agent_query"),
    "run_orchestrator_query":    ("google_a2a.agent_sdk", "run_orchestrator_query"),
    "run_agent_stream":          ("google_a2a.agent_sdk", "run_agent_stream"),
    "run_agent_stream_with_memory": ("google_a2a.agent_sdk", "run_agent_stream_with_memory"),
}


def __getattr__(name: str) -> object:
    if name in _MODULE_MAP:
        import importlib
        mod_path, attr = _MODULE_MAP[name]
        try:
            mod = importlib.import_module(mod_path)
            return getattr(mod, attr)
        except (ImportError, AttributeError) as exc:
            raise ImportError(
                f"google_a2a.{name} could not be imported from {mod_path}: {exc}"
            ) from exc
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
