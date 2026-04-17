"""
Orchestrator Agent — routes and delegates tasks to specialized sub-agents.

Supports:
- Keyword-based routing to the best registered agent
- Explicit delegation by agent name or skill ID
- Fan-out: send the same task to multiple agents and merge results
- Sequential pipelines: chain agents where one's output feeds the next
"""
from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any, List, Optional, Tuple

from a2a.agent import BaseA2AAgent
from a2a.enums import TaskState, PartType, AuthScheme
from a2a.models import (
    AgentCard, AgentCapabilities, AgentAuthentication, AgentSkill,
    Task, Message, TextPart, DataPart, TaskArtifact,
)
from a2a.registry import AgentRegistry, RemoteAgent
from a2a.task_store import TaskStore


def build_orchestrator_card(base_url: str = "http://localhost:9000") -> AgentCard:
    return AgentCard(
        name="OrchestratorAgent",
        description=(
            "Multi-agent orchestrator — routes tasks to specialized agents "
            "(Python Developer, C++ Developer, CybersecAgent, etc.) "
            "and merges their results."
        ),
        url=base_url,
        version="1.0.0",
        capabilities=AgentCapabilities(
            streaming=True,
            push_notifications=False,
            state_transition_history=True,
        ),
        authentication=AgentAuthentication(schemes=[AuthScheme.ED25519]),
        default_input_modes=["text/plain", "application/json"],
        default_output_modes=["text/plain", "application/json"],
        skills=[
            AgentSkill(
                id="delegate",
                name="Task Delegation",
                description="Route task to the best available specialized agent.",
                tags=["orchestrate", "delegate", "route"],
                examples=["Write a Python script to parse CVEs", "Implement this in C++"],
            ),
            AgentSkill(
                id="fanout",
                name="Fan-out",
                description="Send a task to multiple agents and merge results.",
                tags=["fanout", "parallel", "multi-agent"],
                examples=["Get Python and C++ implementations of this algorithm"],
            ),
            AgentSkill(
                id="pipeline",
                name="Pipeline",
                description="Chain agents sequentially — pass output of one as input to next.",
                tags=["pipeline", "chain", "sequential"],
                examples=["Analyze this CVE then write a C++ exploit PoC"],
            ),
            AgentSkill(
                id="list-agents",
                name="List Agents",
                description="List all registered agents and their skills.",
                tags=["agents", "registry", "list"],
                examples=["What agents are available?"],
            ),
        ],
        provider={"name": "cybersecsuite-orchestrator", "url": base_url},
    )


class OrchestratorAgent(BaseA2AAgent):
    """
    Orchestrator that delegates tasks to specialized sub-agents.

    Automatically loads agents from .claude/agents/*.md on startup.

    Usage:
        # Auto-load from .claude/agents/:
        orchestrator = OrchestratorAgent.from_agents_dir(project_root=Path("."))

        # Or build manually:
        registry = AgentRegistry()
        await registry.discover("http://python-agent:8001")
        orchestrator = OrchestratorAgent(registry=registry)
    """

    def __init__(
        self,
        registry: AgentRegistry,
        base_url: str = "http://localhost:9000",
        store: Optional[TaskStore] = None,
    ) -> None:
        card = build_orchestrator_card(base_url)
        super().__init__(card=card, store=store)
        self.registry = registry

    @classmethod
    def from_agents_dir(
        cls,
        project_root: Optional["Path"] = None,  # type: ignore[name-defined]
        base_url: str = "http://localhost:9000",
        store: Optional[TaskStore] = None,
    ) -> "OrchestratorAgent":
        """
        Create an OrchestratorAgent pre-populated from .claude/agents/*.md files.

        Args:
            project_root: Root of the cybersecsuite project (auto-detected if None)
            base_url: URL for the orchestrator itself
            store: Optional task store

        Returns:
            OrchestratorAgent with all local agents registered
        """
        from a2a.agent_loader import load_cybersecsuite_agents
        registry = AgentRegistry()
        load_cybersecsuite_agents(registry, project_root, base_url)
        return cls(registry=registry, base_url=base_url, store=store)

    # ── Main dispatch ─────────────────────────────────────────────────────────

    async def execute(self, task: Task, message: Message) -> None:
        """Parse intent and delegate to the appropriate sub-agent(s)."""
        text = self._extract_text(message).strip()
        lower = text.lower()

        try:
            # Explicit commands
            if lower.startswith("@fanout "):
                await self._fanout(task, text[8:], message)

            elif lower.startswith("@pipeline "):
                steps = [s.strip() for s in text[10:].split("->")]
                await self._pipeline(task, steps, message)

            elif lower.startswith("@agent "):
                # "@agent PythonDeveloper: write a parser"
                rest = text[7:]
                agent_name, _, prompt = rest.partition(":")
                await self._delegate_to_named(task, agent_name.strip(), prompt.strip(), message)

            elif lower.startswith("@skill "):
                # "@skill python-dev: write a parser"
                rest = text[7:]
                skill_id, _, prompt = rest.partition(":")
                await self._delegate_to_skill(task, skill_id.strip(), prompt.strip(), message)

            elif any(kw in lower for kw in ("list agents", "what agents", "available agents")):
                await self._list_agents(task)

            else:
                # Auto-route based on keywords
                await self._auto_route(task, text, message)

        except Exception as e:
            self._fail(task.id, f"Orchestrator error: {e}")

    # ── Delegation strategies ─────────────────────────────────────────────────

    async def _auto_route(self, task: Task, text: str, message: Message) -> None:
        """Auto-detect best agent from message keywords, fallback to SDK query."""
        keywords = text.lower().split()
        agent = self.registry.best_for(keywords)

        if agent:
            result = await self._call_agent(agent, text)
            self._deliver_result(task.id, agent.card.name, result)
            return

        # No registry match — fall back to SDK orchestrator query
        try:
            from a2a.agent_sdk import run_orchestrator_query
            sdk_result = await run_orchestrator_query(text)
            result_text = sdk_result.get("result") or "No response from orchestrator."
            self.store.add_artifact(task.id, TaskArtifact(
                name="orchestrator-result",
                parts=[TextPart(type=PartType.TEXT, text=result_text)],
            ))
            self._reply(task.id, result_text[:500] if len(result_text) > 500 else result_text)
        except Exception as exc:
            self._reply(
                task.id,
                f"No suitable agent found for: {text!r}\n\n"
                f"Registered agents:\n{self._agents_summary()}\n\n"
                f"SDK fallback error: {exc}",
            )

    async def _delegate_to_named(
        self, task: Task, name: str, prompt: str, message: Message
    ) -> None:
        """Delegate to a specific agent by name."""
        agent = self.registry.find_by_name(name)
        if not agent:
            self._fail(task.id, f"Agent not found: {name!r}. Available: {self._agent_names()}")
            return
        result = await self._call_agent(agent, prompt or self._extract_text(message))
        self._deliver_result(task.id, agent.card.name, result)

    async def _delegate_to_skill(
        self, task: Task, skill_id: str, prompt: str, message: Message
    ) -> None:
        """Delegate to agents that provide a specific skill ID."""
        agents = self.registry.find_by_skill_id(skill_id)
        if not agents:
            self._fail(task.id, f"No agent found with skill: {skill_id!r}")
            return
        result = await self._call_agent(agents[0], prompt or self._extract_text(message))
        self._deliver_result(task.id, agents[0].card.name, result)

    async def _fanout(self, task: Task, prompt: str, message: Message) -> None:
        """Send task to ALL registered agents in parallel and merge results."""
        agents = self.registry.all()
        if not agents:
            self._fail(task.id, "No agents registered.")
            return

        self.store.update_status(task.id, TaskState.WORKING)

        calls = [self._call_agent(a, prompt) for a in agents]
        results: List[Tuple[str, Any]] = list(zip(
            [a.card.name for a in agents],
            await asyncio.gather(*calls, return_exceptions=True),
        ))

        # Add one artifact per agent
        for agent_name, result in results:
            if isinstance(result, Exception):
                text = f"[ERROR from {agent_name}]: {result}"
            else:
                text = self._result_text(result)
            self.store.add_artifact(task.id, TaskArtifact(
                name=f"result-{agent_name.lower().replace(' ', '-')}",
                parts=[TextPart(type=PartType.TEXT, text=text)],
            ))

        self._reply(task.id, f"Fan-out complete. Got {len(results)} responses.")

    async def _pipeline(
        self, task: Task, steps: List[str], message: Message
    ) -> None:
        """
        Chain agents sequentially.

        Each step is: "AgentName: optional override prompt"
        The output of step N is fed as input to step N+1.
        """
        if not steps:
            self._fail(task.id, "Pipeline has no steps.")
            return

        self.store.update_status(task.id, TaskState.WORKING)

        current_input = self._extract_text(message)

        for i, step in enumerate(steps):
            agent_name, _, override = step.partition(":")
            agent_name = agent_name.strip()
            prompt = override.strip() if override.strip() else current_input

            agent = self.registry.find_by_name(agent_name)
            if not agent:
                # Try tag/keyword match
                agent = self.registry.best_for(agent_name.lower().split())
            if not agent:
                self._fail(task.id, f"Pipeline step {i+1}: agent {agent_name!r} not found.")
                return

            result = await self._call_agent(agent, prompt)
            current_input = self._result_text(result)

            self.store.add_artifact(task.id, TaskArtifact(
                name=f"step-{i+1}-{agent.card.name.lower().replace(' ', '-')}",
                parts=[TextPart(type=PartType.TEXT, text=current_input)],
            ))

        self._reply(task.id, f"Pipeline complete ({len(steps)} steps). Final output in last artifact.")

    async def _list_agents(self, task: Task) -> None:
        """Return a formatted list of all registered agents."""
        agents = self.registry.all()
        if not agents:
            self._reply(task.id, "No agents registered.")
            return

        lines = ["## Registered Agents\n"]
        for agent in agents:
            lines.append(f"### {agent.card.name}")
            lines.append(f"URL: {agent.base_url}")
            if agent.card.description:
                lines.append(f"{agent.card.description}")
            for skill in agent.card.skills:
                tags = ", ".join(skill.tags or [])
                lines.append(f"  - **{skill.name}** (`{skill.id}`) — {tags}")
            lines.append("")

        self.store.add_artifact(task.id, TaskArtifact(
            name="agent-registry",
            parts=[TextPart(type=PartType.TEXT, text="\n".join(lines))],
        ))
        self._reply(task.id, f"{len(agents)} agent(s) available. See artifact for details.")

    # ── Remote call helper ────────────────────────────────────────────────────

    async def _call_agent(self, agent: RemoteAgent, prompt: str) -> Task:
        """Call a remote agent and return the completed Task."""
        async with agent.client() as client:
            return await client.send_task(prompt, task_id=str(uuid.uuid4()))

    def _deliver_result(self, task_id: str, agent_name: str, result: Task) -> None:
        """Push remote agent artifacts into this task and complete."""
        if result.artifacts:
            for artifact in result.artifacts:
                artifact.name = f"{agent_name}: {artifact.name or 'result'}"
                self.store.add_artifact(task_id, artifact)
        status_text = self._result_text(result)
        self._reply(task_id, f"[{agent_name}] {status_text}")

    @staticmethod
    def _result_text(result: Any) -> str:
        """Extract readable text from a remote Task result."""
        if isinstance(result, Exception):
            return f"[ERROR]: {result}"
        if not isinstance(result, Task):
            return str(result)
        if result.status.message:
            for part in result.status.message.parts:
                if isinstance(part, TextPart):
                    return part.text
        if result.artifacts:
            texts = []
            for artifact in result.artifacts:
                for part in artifact.parts:
                    if isinstance(part, TextPart):
                        texts.append(part.text)
            if texts:
                return "\n\n".join(texts)
        return f"Task {result.id} — {result.status.state}"

    @staticmethod
    def _extract_text(message: Message) -> str:
        parts = []
        for part in message.parts:
            if isinstance(part, TextPart):
                parts.append(part.text)
            elif isinstance(part, DataPart):
                import json
                parts.append(json.dumps(part.data))
        return " ".join(parts)

    def _agents_summary(self) -> str:
        lines = []
        for a in self.registry.all():
            lines.append(f"  - **{a.card.name}** ({a.base_url}): {', '.join(a.skill_ids)}")
        return "\n".join(lines) or "  (none)"

    def _agent_names(self) -> str:
        return ", ".join(a.card.name for a in self.registry.all()) or "(none)"

