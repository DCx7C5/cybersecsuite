"""Prompt module enums."""

from enum import Enum


class PromptCategory(str, Enum):
    SYSTEM = "system"
    USER = "user"
    INSTRUCTION = "instruction"
    CUSTOM = "custom"


__all__ = ["PromptCategory"]
