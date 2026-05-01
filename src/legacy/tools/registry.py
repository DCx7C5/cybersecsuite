import json
import redis.asyncio as aioredis

from typing import Dict, List, Optional

from core.types.entities import BaseTool
from core.types.entities.headers.tool import ToolHeader


class ToolRegistry:
    """
    REDIS-BACKED Tool Registry for cross-process access.

    All processes (Manager, Team Leaders, Roles) share the same tool definitions via Redis.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self._local_cache: Dict[str, BaseTool] = {}  # Local cache for performance

    async def register(self, tool: BaseTool) -> None:
        """Register a tool globally (available to all processes)"""
        tool_data = {
            "name": tool.name,
            "description": tool.header.description if tool.header else "",
            "parameters": tool.header.parameters if tool.header else {},
            "return_type": tool.header.return_type if tool.header else "string",
            "tags": tool.header.tags if tool.header else [],
            "is_async": tool.is_async,
        }

        # Store in Redis (persistent across processes)
        await self.redis.hset("tools:registry", tool.name, json.dumps(tool_data))
        await self.redis.sadd("tools:all", tool.name)

        # Cache locally
        self._local_cache[tool.name] = tool

        print(f"[TOOL_REGISTRY] Registered (cross-process): {tool.name}")

    async def get(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name (from Redis + local cache)"""
        # Check local cache first
        if name in self._local_cache:
            return self._local_cache[name]

        # Load from Redis
        tool_data = await self.redis.hget("tools:registry", name)
        if not tool_data:
            return None

        data = json.loads(tool_data)

        # Reconstruct tool (without the actual function - see note below)
        header = ToolHeader(
            name=data["name"],
            description=data["description"],
            parameters=data["parameters"],
            return_type=data["return_type"],
            tags=data["tags"]
        )

        # Create a proxy tool that delegates execution
        tool = BaseTool(name, header=header, func=self._create_proxy(name))
        self._local_cache[name] = tool
        return tool

    def _create_proxy(self, tool_name: str):
        """Create a proxy function that delegates to the actual tool executor"""

        async def proxy(*args, **kwargs):
            # Send execution request to Manager via Redis
            request = {
                "tool": tool_name,
                "args": args,
                "kwargs": kwargs,
                "requester": "unknown"  # Can be set by caller
            }
            await self.redis.lpush("tools:execution_queue", json.dumps(request))

            # Wait for result (with timeout)
            result = await self.redis.brpop(f"tools:result:{tool_name}", timeout=30)
            if result:
                return json.loads(result[1])
            return {"error": "Tool execution timeout"}

        return proxy

    async def get_all(self) -> List[BaseTool]:
        """Get all registered tools"""
        tool_names = await self.redis.smembers("tools:all")
        tools = []
        for name in tool_names:
            tool = await self.get(name)
            if tool:
                tools.append(tool)
        return tools

    async def get_for_team(self, team_name: str) -> List[BaseTool]:
        """Get tools available to a specific team"""
        # For now, all teams get all tools
        # Future: Add team-specific tool permissions in Redis
        return await self.get_all()

    async def inject_into_agent(self, agent) -> None:
        """Inject all tools into an agent"""
        tools = await self.get_all()
        for tool in tools:
            if tool not in agent.tools:
                agent.add_tool(tool)
        print(f"[TOOL_REGISTRY] Injected {len(tools)} tools into {agent.name}")

    async def clear(self):
        """Clear all tools"""
        await self.redis.delete("tools:registry", "tools:all")
        self._local_cache.clear()


# Global instance (each process creates its own connection)
tool_registry = ToolRegistry()