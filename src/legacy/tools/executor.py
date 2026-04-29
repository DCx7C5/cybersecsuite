import asyncio
import json
from core.tools.registry import tool_registry


async def tool_executor_loop():
    """
    Runs in the Manager process.
    Listens for tool execution requests and executes them.
    """
    redis = tool_registry.redis

    print("[TOOL_EXECUTOR] Started - listening for tool requests...")

    while True:
        try:
            # Wait for execution request
            result = await redis.brpop("tools:execution_queue", timeout=5)
            if not result:
                continue

            request = json.loads(result[1])
            tool_name = request["tool"]
            args = request.get("args", [])
            kwargs = request.get("kwargs", {})

            print(f"[TOOL_EXECUTOR] Executing: {tool_name}")

            # Get the actual tool
            tool = await tool_registry.get(tool_name)
            if not tool:
                error = {"error": f"Tool not found: {tool_name}"}
                await redis.lpush(f"tools:result:{tool_name}", json.dumps(error))
                continue

            # Execute the tool
            try:
                if hasattr(tool, 'arun'):
                    result = await tool.arun(*args, **kwargs)
                else:
                    result = tool.run(*args, **kwargs)

                # Push result back
                await redis.lpush(f"tools:result:{tool_name}", json.dumps(result))

            except Exception as exc:
                error = {"error": str(exc)}
                await redis.lpush(f"tools:result:{tool_name}", json.dumps(error))

        except Exception as exc:
            print(f"[TOOL_EXECUTOR] Error: {exc}")
            await asyncio.sleep(1)

# Start this in the Manager process
# asyncio.create_task(tool_executor_loop())