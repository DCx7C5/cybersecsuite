"""Events module exports."""

from .store import EventStore
from .types import (
    DomainEvent,
    event_permission_granted,
    event_task_completed,
    event_task_delegated,
    event_task_failed,
    event_team_shutdown,
    event_team_spawned,
)
# Phase 6 T6.3: Command pattern for event sourcing
from .command_bus import (
    Command,
    CommandBus,
    CommandHandler,
    CreateTeamCommand,
    CreateTaskCommand,
    CompleteTaskCommand,
    SpawnAgentCommand,
)

__all__ = [
    "DomainEvent",
    "EventStore",
    "event_team_spawned",
    "event_team_shutdown",
    "event_task_delegated",
    "event_task_completed",
    "event_task_failed",
    "event_permission_granted",
    # Command pattern
    "Command",
    "CommandBus",
    "CommandHandler",
    "CreateTeamCommand",
    "CreateTaskCommand",
    "CompleteTaskCommand",
    "SpawnAgentCommand",
]
