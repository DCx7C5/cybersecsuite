from __future__ import annotations

from dataclasses import dataclass

from core.entities.base import BaseRole
from core.types import BaseRoleHeader


@dataclass
class Role(BaseRole):
    """Concrete role entity with display metadata and a permission set.

    Extends ``BaseRole`` (capability flags, allowed_tool_types) with a
    human-readable ``display_name`` that is auto-derived from ``role_id``
    when not provided.

    Built-in singletons (``ORCHESTRATOR``, ``TEAM_MODE``, ``WORKER``) cover
    the common cases. Use ``get(role_id)`` to look up by string or receive a
    default zero-capability role for unknown IDs.
    """

    def __post_init__(self) -> None:
        if self.header is None:
            self.header = BaseRoleHeader(
                name=self.role_id,
                description="",
            )
        if not self.id:
            self.id = self.role_id
        # Auto-title the header name if it matches the bare role_id
        if self.header.name == self.role_id:
            self.header.name = self.role_id.replace("-", " ").replace("_", " ").title()

    @property
    def display_name(self) -> str:
        return self.header.name if self.header else self.role_id


# ── Built-in role singletons ──────────────────────────────────────────────────

ORCHESTRATOR = Role(
    role_id="orchestrator",
    header=BaseRoleHeader(
        name="Orchestrator",
        description="Top-level coordinator — spawns sub-agents and synthesises results.",
        permissions=["tool:write", "agent:spawn", "broadcast:global"],
    ),
    can_orchestrate=True,
    can_broadcast=True,
    can_spawn_subagents=True,
)

TEAM_MODE = Role(
    role_id="team-mode",
    header=BaseRoleHeader(
        name="Team Lead",
        description="Leads a team of agents; can delegate within the team.",
        permissions=["tool:write", "agent:spawn", "broadcast:team"],
    ),
    can_orchestrate=True,
    can_broadcast=True,
    can_spawn_subagents=True,
)

WORKER = Role(
    role_id="worker",
    header=BaseRoleHeader(
        name="Worker",
        description="Executes tasks assigned by an orchestrator; no spawn rights.",
        permissions=["tool:read"],
    ),
    can_orchestrate=False,
    can_broadcast=False,
    can_spawn_subagents=False,
)

#: Maps role_id → Role for quick lookup
REGISTRY: dict[str, Role] = {r.role_id: r for r in (ORCHESTRATOR, TEAM_MODE, WORKER)}


def get(role_id: str) -> Role:
    """Return a built-in Role by ID, or a default zero-capability Role for unknown IDs."""
    return REGISTRY.get(role_id, Role(role_id=role_id))
