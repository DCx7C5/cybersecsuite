"""Agent types — concrete implementation of BaseAgent with HTTP/remote capabilities."""
import aiohttp
import msgspec

from typing import Any, override

from css.core.types.base_entity import BaseAgent
from css.core.types.base_entity import BaseAgentHeader

class Agent(BaseAgent):
    """Concrete agents entity with HTTP endpoint and metadata.

    Extends BaseAgent with:
      - HTTP endpoint (base_url) for remote agents discovery
      - Metadata bag for claude_metadata (frontmatter fields, role, alias, defaults)
      - Skill tags for tag-based routing
      - Integration with marketplace/registry systems
    """

    header: BaseAgentHeader | None = None
    skill_tags: set[str] = msgspec.field(default_factory=set)
    claude_metadata: dict[str, Any] = msgspec.field(default_factory=dict)

    @property
    @override
    def is_default(self) -> bool:
        """Check if this agents is marked as default."""
        return bool(self.claude_metadata.get("default", False))

    @property
    def base_url(self) -> str | None:
        """Get the HTTP base URL (from header or metadata)."""
        if self.header:
            return self.header.base_url
        return self.metadata.get("base_url")

    def client(self):
        """Lazily create an HTTP client for remote agents communication.

        Returns aiohttp.ClientSession for making requests to base_url.
        """
        if not self.base_url:
            raise RuntimeError(f"Agent {self.id} has no base_url; cannot create client")

        return aiohttp.ClientSession(base_url=self.base_url)
