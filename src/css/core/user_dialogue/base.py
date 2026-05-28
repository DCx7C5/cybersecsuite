"""Abstract base for collecting user input through various channels."""

from abc import ABC, abstractmethod

from css.core.user_dialogue.enums import QuestionType


class UserInputCollector(ABC):
    @abstractmethod
    async def ask(
        self,
        question: str,
        *,
        timeout: float | None = None,
    ) -> str:
        ...

    async def confirm(
        self,
        question: str,
        *,
        default: bool | None = True,
        timeout: float | None = None,
    ) -> bool:
        answer = await self._ask_typed(
            QuestionType.CONFIRM,
            question,
            choices=["yes", "no"] if default is None else [],
            timeout=timeout,
        )
        answer = answer.strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        if default is not None:
            return default
        return await self.confirm(question=question, default=None, timeout=timeout)

    async def choose(
        self,
        question: str,
        choices: list[str],
        *,
        timeout: float | None = None,
    ) -> int:
        answer = await self._ask_typed(
            QuestionType.CHOICE,
            question,
            choices=choices,
            timeout=timeout,
        )
        stripped = answer.strip()
        if stripped.isdigit():
            idx = int(stripped) - 1
            if 0 <= idx < len(choices):
                return idx
        try:
            return choices.index(stripped)
        except ValueError:
            ...

        return await self.choose(question, choices, timeout=timeout)

    async def multi_select(
        self,
        question: str,
        choices: list[str],
        *,
        timeout: float | None = None,
    ) -> list[int]:
        answer = await self._ask_typed(
            QuestionType.MULTI_SELECT,
            question,
            choices=choices,
            timeout=timeout,
        )
        indices: list[int] = []
        for part in answer.replace(",", " ").split():
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(choices) and idx not in indices:
                    indices.append(idx)
        return indices

    @abstractmethod
    async def _ask_typed(
        self,
        qtype: QuestionType,
        question: str,
        *,
        choices: list[str] | None = None,
        timeout: float | None = None,
    ) -> str:
        ...


__all__ = [
    "UserInputCollector",
]
