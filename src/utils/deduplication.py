"""
Deduplication utilities — consolidate and standardize duplicate removal logic.

This module provides reusable functions for removing duplicates from various
data structures while preserving order and type integrity.

Patterns:
  - `deduplicate_strings()` — Remove duplicate strings while preserving order
  - `deduplicate_items()` — Remove duplicate items (hashable) while preserving order
  - `deduplicate_by_key()` — Remove duplicates based on a comparison key
  - `are_messages_similar()` — Check if two messages are similar (content-based)
"""


from typing import Any, Callable, Iterable, Sequence, TypeVar

T = TypeVar("T")
K = TypeVar("K")


def deduplicate_strings(values: Iterable[Any]) -> list[str]:
    """
    Remove duplicate strings while preserving order.

    Converts values to strings, strips whitespace, filters empty, and deduplicates.
    Originally from: src/db/intel/_utils.py::_dedupe_strings()

    Args:
        values: Iterable of values to deduplicate

    Returns:
        List of unique strings in order of first appearance
    """
    items: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in items:
            items.append(text)
    return items


def deduplicate_items(values: Iterable[T]) -> list[T]:
    """
    Remove duplicate items while preserving order.

    Uses dict.fromkeys() for O(n) performance with hashable types.
    Originally from: src/db/intel/_loaders.py and src/db/intel/_utils.py

    Args:
        values: Iterable of hashable items

    Returns:
        List of unique items in order of first appearance
    """
    return list(dict.fromkeys(values))


def deduplicate_by_key(
    items: Iterable[T],
    key_func: Callable[[T], K],
) -> list[T]:
    """
    Remove duplicates based on a comparison key.

    Keeps first occurrence of each unique key value.
    Useful when items are equal by some property but not by identity.

    Args:
        items: Iterable of items to deduplicate
        key_func: Function to extract comparison key from item

    Returns:
        List of items with unique keys in order of first appearance
    """
    seen: set[K] = set()
    result: list[T] = []
    for item in items:
        k = key_func(item)
        if k not in seen:
            seen.add(k)
            result.append(item)
    return result


def are_messages_similar(
    msg1: dict[str, str],
    msg2: dict[str, str],
) -> bool:
    """
    Check if two messages are similar (simple heuristic).

    Compares role and content. Content is considered similar if:
      - Exact match (case-insensitive)
      - First 30 chars match (and content > 10 chars)

    Originally from: src/ai_proxy/validation/json_response.py::_messages_similar()

    Args:
        msg1: First message dict (must have 'role' and 'content' keys)
        msg2: Second message dict (must have 'role' and 'content' keys)

    Returns:
        True if messages are similar, False otherwise
    """
    if msg1.get("role") != msg2.get("role"):
        return False

    content1 = msg1.get("content", "").lower()
    content2 = msg2.get("content", "").lower()

    return content1 == content2 or (
        len(content1) > 10 and content1[:30] == content2[:30]
    )


def deduplicate_messages(
    messages: Sequence[dict[str, str]],
) -> list[dict[str, str]]:
    """
    Remove duplicate or similar consecutive messages.

    Keeps first message and skips any that are similar to the previous one.
    Useful for context compression in conversation histories.

    Args:
        messages: Sequence of message dicts

    Returns:
        List of messages with duplicates/similar consecutive ones removed
    """
    if len(messages) <= 1:
        return list(messages)

    result: list[dict[str, str]] = [messages[0]] if messages else []

    for i in range(1, len(messages)):
        if not are_messages_similar(messages[i], messages[i - 1]):
            result.append(messages[i])

    return result
