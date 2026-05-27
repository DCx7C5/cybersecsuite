"""Prompt module enums."""

from enum import Enum


class PromptCategory(str, Enum):
    SYSTEM = "system"
    USER = "user"
    INSTRUCTION = "instruction"
    CUSTOM = "custom"


class PromptStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DISABLED = "disabled"


class PromptVariableType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    SELECT = "select"
    CONTEXT = "context"


__all__ = ["PromptCategory", "PromptStatus", "PromptVariableType"]
