"""Iterative tool-call execution loop for provider function-calling responses."""

import json
from collections.abc import Awaitable, Callable
from typing import Any

from css.core.tools.executor import get_executor


class ToolCallLoop:
    """Executes provider-returned tool calls until the model stops requesting them."""

    def __init__(self, max_iterations: int = 5):
        self.max_iterations = max_iterations
        self._tool_executor = get_executor()

    @staticmethod
    def _extract_tool_call(call: dict[str, Any]) -> tuple[str, dict[str, Any], str | None]:
        if "function" in call and isinstance(call["function"], dict):
            fn = call["function"]
            tool_id = str(fn.get("name", ""))
            raw_args = fn.get("arguments", {})
            call_id = str(call.get("id")) if call.get("id") is not None else None
        else:
            tool_id = str(call.get("name", ""))
            raw_args = call.get("arguments", {})
            call_id = str(call.get("id")) if call.get("id") is not None else None

        if isinstance(raw_args, str):
            try:
                args = json.loads(raw_args) if raw_args.strip() else {}
            except json.JSONDecodeError:
                args = {}
        elif isinstance(raw_args, dict):
            args = raw_args
        else:
            args = {}

        return tool_id, args, call_id

    async def run(
        self,
        *,
        initial_response: dict[str, Any],
        llm_caller: Callable[[str], Awaitable[dict[str, Any]]],
        base_prompt: str,
        agent_id: str,
        scope: object | None = None,
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Execute tool-call loop and return final response plus tool messages."""

        response = initial_response
        tool_messages: list[dict[str, Any]] = []

        for _ in range(self.max_iterations):
            tool_calls = response.get("tool_calls", []) or []
            if not tool_calls:
                break

            for call in tool_calls:
                tool_id, params, call_id = self._extract_tool_call(call)
                if not tool_id:
                    continue
                result = await self._tool_executor.execute(
                    agent_id=agent_id,
                    tool_id=tool_id,
                    params=params,
                    scope=scope,
                )
                tool_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call_id,
                        "name": tool_id,
                        "content": json.dumps(result, default=str),
                    }
                )

            prompt_with_results = (
                f"{base_prompt}\n\n"
                "Tool results (JSON):\n"
                + "\n".join(
                    f"- {message['name']}: {message['content']}"
                    for message in tool_messages
                )
        )
            response = await llm_caller(prompt_with_results)

        return response, tool_messages
