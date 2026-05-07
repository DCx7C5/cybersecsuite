"""Enumerations for permissions module."""

from enum import Enum


class Role(str, Enum):
    """Orchestration roles in CSS."""

    ORCHESTRATOR = "orchestrator"
    TEAM_LEADER = "team_leader"
    WORKER = "worker"
    PLANNER = "planner"
    TRIAGE = "triage"
    TEAM_MEMBER = "team_member"


class ScopeLevel(str, Enum):
    """Scope hierarchy levels."""

    GLOBAL = "global"
    APP = "app"
    PROJECT = "project"
    RUNTIME = "runtime"
    SESSION = "session"


class Permission(str, Enum):
    """Path-based permissions."""

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
