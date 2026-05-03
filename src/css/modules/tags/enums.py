"""Enums for the tags module."""

from enum import Enum


class TagColor(str, Enum):
    """Color options for tags."""

    RED = "red"
    ORANGE = "orange"
    YELLOW = "yellow"
    GREEN = "green"
    BLUE = "blue"
    PURPLE = "purple"
    GRAY = "gray"
    BLACK = "black"
