"""User communication — ask users for decisions, confirmations, and choices.

Supports multiple backends (CLI stdin/stdout, future Telegram, etc.)
and question types: confirm, single-choice, multi-select, free-text.
"""

from css.core.user_dialogue.adapters.cli import CliUserInputCollector
from css.core.user_dialogue.base import UserInputCollector
from css.core.user_dialogue.enums import ConfirmDefault, QuestionType
