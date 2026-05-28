"""Enums for user communication types and defaults."""

import enum


class QuestionType(str, enum.Enum):
    CONFIRM = "confirm"
    CHOICE = "choice"
    MULTI_SELECT = "multi_select"
    INPUT = "input"


class ConfirmDefault(str, enum.Enum):
    YES = "yes"
    NO = "no"
    NONE = "none"


__all__ = [
    "ConfirmDefault",
    "QuestionType",
]
