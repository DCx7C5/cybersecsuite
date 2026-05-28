"""CLI adapter — reads user input from stdin, prompts on stderr."""

import asyncio
import sys
from typing import override

from css.core.logger import getLogger
from css.core.user_dialogue.base import UserInputCollector
from css.core.user_dialogue.enums import QuestionType

logger = getLogger(__name__)


class CliUserInputCollector(UserInputCollector):
    @override
    async def _ask_typed(
        self,
        qtype: QuestionType,
        question: str,
        *,
        choices: list[str] | None = None,
        timeout: float | None = None,
    ) -> str:
        self._render_prompt(question, qtype, choices)
        loop = asyncio.get_event_loop()
        try:
            raw = await asyncio.wait_for(
                loop.run_in_executor(None, sys.stdin.readline),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logger.warning("User input timed out after %s seconds", timeout)
            raise
        return raw.rstrip("\n\r")

    @staticmethod
    def _render_prompt(question: str, qtype: QuestionType, choices: list[str] | None) -> None:
        parts: list[str] = [question]
        if choices:
            parts.append("")
            for i, c in enumerate(choices, 1):
                parts.append(f"  {i}. {c}")
        if qtype is QuestionType.CONFIRM:
            parts.append("")
            parts.append("(y/n) ")
        elif qtype in (QuestionType.CHOICE, QuestionType.MULTI_SELECT) and choices:
            parts.append("")
            parts.append(f"(enter 1\u2013{len(choices)}{' comma-separated' if qtype is QuestionType.MULTI_SELECT else ''}) ")
        hint = "\n".join(parts)
        print(hint, end=" ", file=sys.stderr, flush=True)


