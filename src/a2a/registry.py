"""
Agent Registry — discovers, registers, and resolves remote A2A agents by skill.
Also supports loading agents from .claude/agents/*.md frontmatter definitions.
"""


import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from a2a.client import A2AClient
from a2a.models import AgentCard


class RemoteAgent:
    """A registered remote agent with its card and client."""

    def __init__(self, base_url: str, card: AgentCard) -> None:
        self.base_url = base_url
        self.card = card
        self.claude_metadata: Dict[str, Any] = {}  # .claude agent frontmatter metadata

    @property
    def is_default(self) -> bool:
        """Whether this agent is marked as default in .claude config."""
        return bool(self.claude_metadata.get("default", False))

    @property
    def role(self) -> str:
        """Agent role from .claude config (e.g. 'orchestrator')."""
        return self.claude_metadata.get("role", "")

    @property
    def skill_ids(self) -> Set[str]:
        return {s.id for s in self.card.skills}

    @property
    def skill_tags(self) -> Set[str]:
        tags: Set[str] = set()
        for skill in self.card.skills:
            if skill.tags:
                tags.update(skill.tags)
        return tags

    def client(self, **kwargs) -> A2AClient:
        return A2AClient(self.base_url, **kwargs)

    def __repr__(self) -> str:
        return f"<RemoteAgent name={self.card.name!r} url={self.base_url!r}>"


class AgentRegistry:
    """
    Registry of known A2A agents.

    Agents are registered manually or discovered via their AgentCard URLs.
    Provides skill-based routing: find the best agent for a given task.
    """

    def __init__(self) -> None:
        self._agents: Dict[str, RemoteAgent] = {}  # base_url → RemoteAgent

    # ── Registration ──────────────────────────────────────────────────────────

    def register(self, base_url: str, card: AgentCard) -> RemoteAgent:
        """Register a remote agent with a known card."""
        agent = RemoteAgent(base_url=base_url, card=card)
        self._agents[base_url] = agent
        return agent

    async def discover(self, base_url: str, **client_kwargs) -> RemoteAgent:
        """
        Discover a remote agent by fetching its AgentCard.

        Args:
            base_url: Base URL of the remote agent
            **client_kwargs: Extra args passed to A2AClient

        Returns:
            Registered RemoteAgent
        """
        async with A2AClient(base_url, **client_kwargs) as client:
            card = await client.get_agent_card()
        return self.register(base_url, card)

    async def discover_many(self, urls: List[str], **client_kwargs) -> List[RemoteAgent]:
        """Discover multiple agents concurrently."""
        tasks = [self.discover(url, **client_kwargs) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        agents = []
        for r in results:
            if isinstance(r, RemoteAgent):
                agents.append(r)
        return agents

    def unregister(self, base_url: str) -> None:
        """Remove an agent from the registry."""
        self._agents.pop(base_url, None)

    # ── Lookup ────────────────────────────────────────────────────────────────

    def all(self) -> List[RemoteAgent]:
        """Return all registered agents."""
        return list(self._agents.values())

    def get(self, base_url: str) -> Optional[RemoteAgent]:
        """Get agent by base URL."""
        return self._agents.get(base_url)

    def find_by_name(self, name: str) -> Optional[RemoteAgent]:
        """Find agent by card name (case-insensitive)."""
        name_lower = name.lower()
        for agent in self._agents.values():
            if agent.card.name.lower() == name_lower:
                return agent
            # Also match .claude alias
            alias = agent.claude_metadata.get("alias", "")
            if alias and alias.lower() == name_lower:
                return agent
        return None

    def find_default(self) -> Optional[RemoteAgent]:
        """Find the agent marked as default in .claude config."""
        for agent in self._agents.values():
            if agent.is_default:
                return agent
        return None

    def find_orchestrator(self) -> Optional[RemoteAgent]:
        """Find the orchestrator agent from .claude config."""
        for agent in self._agents.values():
            if agent.role == "orchestrator":
                return agent
        return None

    def find_by_skill_id(self, skill_id: str) -> List[RemoteAgent]:
        """Find all agents that expose a given skill ID."""
        return [a for a in self._agents.values() if skill_id in a.skill_ids]

    def find_by_tag(self, tag: str) -> List[RemoteAgent]:
        """Find all agents whose skills include a given tag."""
        return [a for a in self._agents.values() if tag in a.skill_tags]

    def find_by_tags(self, tags: List[str], match_all: bool = False) -> List[RemoteAgent]:
        """
        Find agents matching skill tags.

        Args:
            tags: Tags to match
            match_all: If True, agent must have ALL tags; if False, ANY tag.

        Returns:
            Matching agents sorted by number of matching tags (best first)
        """
        tag_set = set(tags)
        scored: List[tuple[int, RemoteAgent]] = []
        for agent in self._agents.values():
            overlap = len(agent.skill_tags & tag_set)
            if match_all and overlap < len(tag_set):
                continue
            if overlap > 0:
                scored.append((overlap, agent))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in scored]

    def best_for(self, keywords: List[str]) -> Optional[RemoteAgent]:
        """
        Find the single best agent for a set of keywords.
        Matches against skill IDs, tags, names, and descriptions.
        """
        kw_lower = {k.lower() for k in keywords}
        scored: List[tuple[int, RemoteAgent]] = []

        for agent in self._agents.values():
            score = 0
            # Name match
            if any(kw in agent.card.name.lower() for kw in kw_lower):
                score += 10
            # Skill ID match
            for skill in agent.card.skills:
                if any(kw in skill.id.lower() for kw in kw_lower):
                    score += 5
                if skill.tags:
                    score += sum(1 for t in skill.tags if t.lower() in kw_lower)
                if skill.description and any(kw in skill.description.lower() for kw in kw_lower):
                    score += 2
            if score > 0:
                scored.append((score, agent))

        if not scored:
            return None
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    @classmethod
    def from_agents_dir(
        cls,
        agents_dir: Path,
        base_url: str = "http://localhost:8000",
        recurse: bool = False,
    ) -> "AgentRegistry":
        """
        Create a registry pre-populated from .claude/agents/*.md files.

        Args:
            agents_dir: Path to .claude/agents/ directory
            base_url: Base URL used for all local agent cards
            recurse: Also load teams/ subdirectory

        Returns:
            Populated AgentRegistry
        """
        from a2a.agent_loader import load_agents_from_dir
        registry = cls()
        load_agents_from_dir(agents_dir, registry, base_url, recurse)
        return registry

    @classmethod
    def from_cybersecsuite(
        cls,
        project_root: Optional[Path] = None,
        base_url: str = "http://localhost:8000",
    ) -> "AgentRegistry":
        """
        Create a registry from cybersecsuite's .claude/agents/ directory.

        Args:
            project_root: Project root (auto-detected if None)
            base_url: Base URL for local agents

        Returns:
            Populated AgentRegistry
        """
        from a2a.agent_loader import load_cybersecsuite_agents
        registry = cls()
        load_cybersecsuite_agents(registry, project_root, base_url)
        return registry

    def summary(self) -> List[Dict]:
        """Return a summary of all registered agents."""
        from typing import Dict as D
        result: List[D[str, Any]] = []
        for agent in self._agents.values():
            entry: D[str, Any] = {
                "name": agent.card.name,
                "url": agent.base_url,
                "description": agent.card.description,
                "skills": [
                    {"id": s.id, "name": s.name, "tags": s.tags}
                    for s in agent.card.skills
                ],
            }
            if agent.claude_metadata:
                entry["claude_metadata"] = agent.claude_metadata
            result.append(entry)
        return result

