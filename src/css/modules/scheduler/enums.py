"""Scheduler enums."""

from enum import Enum


class TaskType(str, Enum):
    """Types of scheduled tasks."""

    SCAN = "scan"
    THREAT_FEED_SYNC = "threat_feed_sync"
    REPORT_GENERATION = "report_generation"
    BACKUP = "backup"
    CLEANUP = "cleanup"
    COMPLIANCE_CHECK = "compliance_check"
    RED_TEAM_DRILL = "red_team_drill"
    CUSTOM = "custom"


__all__ = ["TaskType"]
