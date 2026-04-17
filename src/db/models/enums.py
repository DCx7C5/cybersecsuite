"""Minimal enums for csdb-mcp initial tables."""
from enum import Enum


class RedBlueMode(str, Enum):
    BLUE = "blue"
    RED = "red"
    PURPLE = "purple"


class AuditAction(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    START = "start"
    STOP = "stop"
    MODE_SWITCH = "mode_switch"
    READ = "read"
    SCHEMA_CREATE = "schema_create"
    SCHEMA_DROP = "schema_drop"
    SEED = "seed"
    HEALTH_CHECK = "health_check"

