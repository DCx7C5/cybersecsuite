from enum import Enum


class AgentStatus(str, Enum):
    """Status of an agent."""

    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


class AgentType(str, Enum):
    """Type of agent."""

    LLM = "llm"
    HYBRID = "hybrid"
    LOCAL = "local"
    EXTERNAL = "external"
