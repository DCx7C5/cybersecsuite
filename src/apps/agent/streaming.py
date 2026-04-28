"""agent.streaming — SSE adapter for streaming agent query results.

Converts the claude_agent_sdk async generator (query() with partial messages)
into SSE-ready dicts consumed by dashboard /api/agent-query endpoint.
"""


from logger import getLogger
from collections.abc import AsyncGenerator
from typing import Any

logger = getLogger("agent.streaming")


async def stream_query(
    prompt: str,
    agent_name: str | None = None,
    mode: str = "blue",
    session_id: str | None = None,
    extra_tools: list[str] | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """Stream a query through the agent SDK, yielding SSE-ready dicts.

    Yield types:
        {"type": "text", "text": str}             — partial text output
        {"type": "tool_use", "name": str, "input": dict}  — tool invocation
        {"type": "tool_result", "name": str, "content": str} — tool output
        {"type": "result", "text": str, "cost": float, "session_id": str}
        {"type": "error", "message": str}
    """
    from claude_agent_sdk import (
        query,
        ResultMessage,
        SystemMessage,
        AssistantMessage,
        TextBlock,
        ToolUseBlock,
        ToolResultBlock,
    )
    from a2a.agent_sdk import build_agent_options

    options = build_agent_options(extra_tools=extra_tools)
    if session_id:
        options.resume = session_id

    mode_prefix = f"[MODE: {mode.upper()}] " if mode != "blue" else ""
    agent_prefix = f"Delegate to {agent_name}: " if agent_name else ""
    full_prompt = f"{mode_prefix}{agent_prefix}{prompt}"

    try:
        async for message in query(prompt=full_prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        yield {"type": "text", "text": block.text}
                    elif isinstance(block, ToolUseBlock):
                        yield {
                            "type": "tool_use",
                            "name": block.name,
                            "input": block.input if isinstance(block.input, dict) else {},
                        }
                    elif isinstance(block, ToolResultBlock):
                        content = ""
                        if isinstance(block.content, list):
                            for c in block.content:
                                if hasattr(c, "text"):
                                    content += c.text
                        elif isinstance(block.content, str):
                            content = block.content
                        yield {"type": "tool_result", "name": block.tool_use_id, "content": content}

            elif isinstance(message, SystemMessage) and message.subtype == "init":
                session_id = message.data.get("session_id", session_id)

            elif isinstance(message, ResultMessage) and message.subtype == "success":
                yield {
                    "type": "result",
                    "text": message.result or "",
                    "cost": getattr(message, "cost_usd", 0.0) or 0.0,
                    "session_id": session_id or "",
                }

    except Exception as exc:
        logger.error("stream_query error: %s", exc)
        yield {"type": "error", "message": str(exc)}
