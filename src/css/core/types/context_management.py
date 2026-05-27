"""Context management configuration model."""

import msgspec


class ContextManagementConfig(msgspec.Struct, frozen=True, kw_only=True):
    """Configuration for automatic context window management.

    Controls when and how the context is compacted during long conversations.
    Provider-specific default summary prompts are selected in adapter
    translation, not here.
    """

    auto_compact_at_tokens: int = 8192
    clear_thinking_on_compact: bool = True
    custom_summary_prompt: str | None = None

    def __post_init__(self) -> None:
        if self.auto_compact_at_tokens < 1:
            raise ValueError(
                f"auto_compact_at_tokens must be positive, got {self.auto_compact_at_tokens}"
            )
