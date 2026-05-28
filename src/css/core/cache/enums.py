"""Cache enums used by cache config/runtime layers."""

from enum import Enum


class CacheBackend(str, Enum):
    REDIS = "redis"
    POSTGRES = "postgres"
    DISK = "disk"

