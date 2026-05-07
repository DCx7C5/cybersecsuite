"""Command pattern implementation for domain-driven event sourcing (Phase 6 T6.3).

CommandBus coordinates command handlers and event emission.
Commands are actions that can be executed; they trigger domain events.

Example flow:
  1. Client sends command: CreateTeamCommand(name="Alpha")
  2. CommandBus routes to TeamCommandHandler
  3. Handler validates and executes -> emits TeamSpawnedEvent
  4. Event is appended to EventStore and persisted to DB
  5. Projections (read models) are updated from event
"""

import logging
from typing import Any, Callable, Dict, Type, TypeVar, Optional
from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid

import msgspec

log = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class Command(msgspec.Struct):
    """Base command struct.

    All commands should inherit from this to enable type-safe dispatch.
    """

    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    user_id: Optional[str] = None


@dataclass
class TeamCommand(Command):
    """Base for team domain commands."""

    team_id: Optional[str] = None


@dataclass
class CreateTeamCommand(TeamCommand):
    """Create a new team."""

    name: str = ""
    description: str = ""


@dataclass
class TaskCommand(Command):
    """Base for task domain commands."""

    task_id: Optional[str] = None


@dataclass
class CreateTaskCommand(TaskCommand):
    """Create a new task."""

    title: str = ""
    description: str = ""
    team_id: Optional[str] = None


@dataclass
class CompleteTaskCommand(TaskCommand):
    """Mark a task as complete."""

    result: str = ""


@dataclass
class AgentCommand(Command):
    """Base for agent domain commands."""

    agent_id: Optional[str] = None


@dataclass
class SpawnAgentCommand(AgentCommand):
    """Spawn a new agent."""

    name: str = ""
    role: str = ""
    team_id: Optional[str] = None


class CommandHandler:
    """Base class for command handlers.

    Implementations should override handle() to process specific command types
    and return events to emit.
    """

    async def handle(self, command: Command) -> list:
        """Handle a command and return domain events to emit.

        Args:
            command: The command to handle

        Returns:
            List of domain events to append to event store
        """
        raise NotImplementedError


class TeamCommandHandler(CommandHandler):
    """Handler for team domain commands."""

    async def handle(self, command: Command) -> list:
        """Process team commands."""
        from .types import DomainEvent

        if isinstance(command, CreateTeamCommand):
            team_id = str(uuid.uuid4())
            return [
                DomainEvent(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(UTC),
                    aggregate_type="team",
                    aggregate_id=team_id,
                    kind="team_spawned",
                    data={
                        "name": command.name,
                        "description": command.description,
                    },
                    user_id=command.user_id,
                )
            ]
        return []


class TaskCommandHandler(CommandHandler):
    """Handler for task domain commands."""

    async def handle(self, command: Command) -> list:
        """Process task commands."""
        from .types import DomainEvent

        if isinstance(command, CreateTaskCommand):
            task_id = str(uuid.uuid4())
            return [
                DomainEvent(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(UTC),
                    aggregate_type="task",
                    aggregate_id=task_id,
                    kind="task_created",
                    data={
                        "title": command.title,
                        "description": command.description,
                        "team_id": command.team_id,
                    },
                    user_id=command.user_id,
                )
            ]
        elif isinstance(command, CompleteTaskCommand):
            return [
                DomainEvent(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(UTC),
                    aggregate_type="task",
                    aggregate_id=command.task_id,
                    kind="task_completed",
                    data={"result": command.result},
                    user_id=command.user_id,
                )
            ]
        return []


class AgentCommandHandler(CommandHandler):
    """Handler for agent domain commands."""

    async def handle(self, command: Command) -> list:
        """Process agent commands."""
        from .types import DomainEvent

        if isinstance(command, SpawnAgentCommand):
            agent_id = str(uuid.uuid4())
            return [
                DomainEvent(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now(UTC),
                    aggregate_type="agent",
                    aggregate_id=agent_id,
                    kind="agent_spawned",
                    data={
                        "name": command.name,
                        "role": command.role,
                        "team_id": command.team_id,
                    },
                    user_id=command.user_id,
                )
            ]
        return []


class CommandBus:
    """Routes commands to handlers and coordinates event emission.

    Usage:
        bus = CommandBus(event_store=store)
        await bus.execute(CreateTeamCommand(name="Alpha"))
    """

    def __init__(
        self,
        event_store=None,
        handlers: Optional[Dict[Type[Command], CommandHandler]] = None,
    ):
        """Initialize command bus.

        Args:
            event_store: EventStore instance for persisting events
            handlers: Dict mapping command types to handlers
        """
        self.event_store = event_store
        self.handlers: Dict[Type[Command], CommandHandler] = handlers or {
            CreateTeamCommand: TeamCommandHandler(),
            TaskCommand: TaskCommandHandler(),
            CreateTaskCommand: TaskCommandHandler(),
            CompleteTaskCommand: TaskCommandHandler(),
            SpawnAgentCommand: AgentCommandHandler(),
        }

    def register_handler(
        self, command_type: Type[Command], handler: CommandHandler
    ) -> None:
        """Register a command handler.

        Args:
            command_type: Command class this handler processes
            handler: CommandHandler instance
        """
        self.handlers[command_type] = handler

    async def execute(self, command: Command) -> list:
        """Execute a command and emit resulting events.

        Args:
            command: The command to execute

        Returns:
            List of domain events that were emitted

        Raises:
            KeyError: If no handler registered for command type
        """
        # Find handler
        handler_cls = type(command)
        handler = self.handlers.get(handler_cls)

        if not handler:
            # Try parent class handlers
            for cmd_type, cmd_handler in self.handlers.items():
                if isinstance(command, cmd_type):
                    handler = cmd_handler
                    break

        if not handler:
            raise KeyError(f"No handler registered for {handler_cls.__name__}")

        # Execute handler
        events = await handler.handle(command)

        # Append events to store
        if self.event_store and events:
            for event in events:
                await self.event_store.append(event)
            log.info(f"Command {command.command_id} emitted {len(events)} events")

        return events
