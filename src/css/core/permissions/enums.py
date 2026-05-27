"""Permission module enums."""

from enum import Flag, auto


class PathOp(Flag):
    """Filesystem operation flags used by path grants."""

    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    ALL = READ | WRITE | EXECUTE

