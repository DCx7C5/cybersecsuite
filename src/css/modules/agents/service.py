"""Service-layer operations for agent lifecycle management."""

from css.modules.agents.manager import AgentRegistry
from css.modules.agents.models import AgentConfig

_agent_registry = AgentRegistry()


def get_agent_registry() -> AgentRegistry:
    """Return the shared in-process agent registry."""
    return _agent_registry


def create_agent(config: AgentConfig) -> object:
    """Create/register an agent state."""
    return _agent_registry.register(config)


def get_agent(agent_id: str) -> object | None:
    """Fetch one agent state by identifier."""
    return _agent_registry.get(agent_id)


def list_agents() -> list[object]:
    """List all known agents."""
    return _agent_registry.list_all()


def delete_agent(agent_id: str) -> bool:
    """Remove one agent from the shared registry."""
    return _agent_registry.deregister(agent_id)
