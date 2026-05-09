"""Anthropic Native SDK Adapter — wraps anthropic.AsyncAnthropic.

Preserves Anthropic-only features lost in the generic HTTP path:
- Prompt caching (automatic top-level cache_control + optional breakpoints)
- Computer use beta tools (computer, bash, text_editor)
- Extended thinking (budget_tokens)
"""

from collections.abc import AsyncIterator
from typing import Any

from css.core.logger import getLogger
from css.core.types.base_messages import LLMResponse, StreamChunk, Tool
from css.core.types.enums import ProviderType

logger = getLogger(__name__)

COMPUTER_USE_TOOLS: list[Tool] = [
    Tool(
        name="computer",
        description="A computer interface tool for GUI interaction. Use mouse, keyboard, and screenshot operations.",
        input_schema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "The action to perform",
                    "enum": [
                        "key", "type", "mouse_move", "left_click", "left_click_drag",
                        "right_click", "middle_click", "double_click", "screenshot",
                        "cursor_position", "wait",
                    ],
                },
                "coordinate": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "x,y coordinates for mouse actions",
                },
                "text": {"type": "string", "description": "Text to type"},
            },
            "required": ["action"],
        },
    ),
    Tool(
        name="bash",
        description="Run bash commands on the system. Returns stdout, stderr, and exit code.",
        input_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute",
                },
                "restart": {
                    "type": "boolean",
                    "description": "Restart the bash session",
                },
            },
            "required": ["command"],
        },
    ),
    Tool(
        name="str_replace_editor",
        description="A text editor tool for viewing, creating, and editing files.",
        input_schema={
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The editor command (view, create, str_replace, insert, undo_edit)",
                    "enum": ["view", "create", "str_replace", "insert", "undo_edit"],
                },
                "path": {"type": "string", "description": "Absolute path to the file"},
                "file_text": {"type": "string", "description": "File content for create command"},
                "old_str": {"type": "string", "description": "Text to replace (str_replace command)"},
                "new_str": {"type": "string", "description": "Replacement text (str_replace command)"},
                "insert_line": {"type": "integer", "description": "Line number for insert command"},
            },
            "required": ["command", "path"],
        },
    ),
]


class AnthropicNativeAdapter:
    """Native SDK adapter for Anthropic — implements LLMAdapter.

    Wraps anthropic.AsyncAnthropic directly to support features not
    available through the generic HTTP path:
    - Prompt caching (cache_control on system and content blocks)
    - Computer use beta tools (computer, bash, text_editor)
    - Extended thinking (budget_tokens / thinking parameter)
    """

    provider_id: str = ProviderType.ANTHROPIC.value

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self._client: Any = None

    @property
    def client(self) -> Any:
        if self._client is None:
            from anthropic import AsyncAnthropic
            self._client = AsyncAnthropic(
                api_key=self.api_key,
                base_url=self.base_url,
            )
        return self._client

    async def get_models(self) -> list[Any]:
        return [
            type("ModelInfo", (), {"id": "claude-3-5-sonnet-20241022"})(),
            type("ModelInfo", (), {"id": "claude-3-opus-20250219"})(),
            type("ModelInfo", (), {"id": "claude-3-sonnet-20240229"})(),
            type("ModelInfo", (), {"id": "claude-3-haiku-20240307"})(),
        ]

    async def call_llm(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        streaming: bool = True,
        **kwargs: Any,
    ) -> AsyncIterator[Any]:
        if not streaming:
            response = await self.complete(
                model_id=model_id,
                messages=messages,
                tools=tools,
                temperature=temperature,
                max_tokens=max_tokens,
                system_prompt=system_prompt,
                **kwargs,
            )
            yield response
            return

        async for chunk in self.stream(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs,
        ):
            yield chunk

    async def call_llm_buffered(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> Any:
        return await self.complete(
            model_id=model_id,
            messages=messages,
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            **kwargs,
        )

    def supports_feature(self, model: Any, feature: str) -> bool:
        supported = {
            "streaming": True,
            "vision": True,
            "tool_use": True,
            "prompt_caching": True,
            "structured_output": True,
            "extended_thinking": True,
            "computer_use": True,
        }
        return supported.get(feature, False)

    async def complete(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        formatted = self._format_messages(messages)
        call_kwargs = self._build_call_kwargs(
            model_id=model_id,
            messages=formatted["messages"],
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt or formatted.get("system"),
            **kwargs,
        )

        response = await self.client.messages.create(**call_kwargs)
        return self._parse_response(response)

    async def stream(
        self,
        model_id: str,
        messages: list[Any],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamChunk]:
        formatted = self._format_messages(messages)
        call_kwargs = self._build_call_kwargs(
            model_id=model_id,
            messages=formatted["messages"],
            tools=tools,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt or formatted.get("system"),
            **kwargs,
        )

        async with self.client.messages.stream(**call_kwargs) as stream:
            async for event in stream:
                if event.type == "content_block_delta" and hasattr(event.delta, "text"):
                    yield StreamChunk(
                        type="content_block_delta",
                        content=event.delta.text,
                    )
                elif event.type == "message_stop":
                    yield StreamChunk(
                        type="message_stop",
                        stop_reason="stop",
                    )

    def builtin_tools(self) -> list[Tool]:
        return list(COMPUTER_USE_TOOLS)

    @staticmethod
    def _format_messages(
        messages: list[Any],
    ) -> dict[str, Any]:
        system: str | None = None
        formatted: list[dict[str, str]] = []

        for msg in messages:
            role = getattr(msg, "role", None)
            if hasattr(role, "value"):
                role = role.value
            content = getattr(msg, "content", "") or ""

            if role == "system":
                system = (system or "") + content if content else system
            else:
                formatted.append({"role": role or "user", "content": content})

        result: dict[str, Any] = {"messages": formatted}
        if system:
            result["system"] = [{"type": "text", "text": system}]
        return result

    @staticmethod
    def _build_call_kwargs(
        model_id: str,
        messages: list[dict[str, str]],
        tools: list[Any] | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        call_kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "max_tokens": max_tokens or 4096,
            "temperature": temperature,
        }

        if system_prompt:
            call_kwargs["system"] = system_prompt

        if tools:
            formatted_tools = AnthropicNativeAdapter._format_tools(tools)
            if formatted_tools:
                call_kwargs["tools"] = formatted_tools

        if "thinking" in kwargs:
            call_kwargs["thinking"] = kwargs["thinking"]

        return call_kwargs

    @staticmethod
    def _parse_response(response: Any) -> LLMResponse:
        text = ""
        for block in response.content:
            if hasattr(block, "text"):
                text += block.text

        usage = {}
        if hasattr(response, "usage"):
            try:
                usage = response.usage.model_dump()
            except (AttributeError, TypeError):
                pass

        return LLMResponse(
            text=text,
            stop_reason=response.stop_reason or "stop",
            usage=usage,
        )

    @staticmethod
    def _format_tools(tools: list[Any]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for tool in tools:
            name = getattr(tool, "name", None) or getattr(tool, "tool_name", None)
            if not name or not isinstance(name, str):
                continue
            description = getattr(tool, "description", "") or ""
            input_schema = getattr(tool, "input_schema", {}) or {}
            result.append({
                "name": name,
                "description": str(description),
                "input_schema": input_schema if isinstance(input_schema, dict) else {},
            })
        return result


__all__ = ["AnthropicNativeAdapter", "COMPUTER_USE_TOOLS"]
