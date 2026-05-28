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

from typing import override
from css.core.events.instrument import instrument
from css.core.logger import getLogger
from datetime import datetime, UTC
import uuid

import msgspec

log = getLogger(__name__)

class Command(msgspec.Struct, tag=True):
    """Base command struct.

    All commands should inherit from this to enable type-safe dispatch.
    """

    command_id: str = msgspec.field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = msgspec.field(default_factory=lambda: datetime.now(UTC))
    user_id: str | None = None


class TeamCommand(Command):
    """Base for team domain commands."""

    team_id: str | None = None


class CreateTeamCommand(TeamCommand):
    """Create a new team."""

    name: str = ""
    description: str = ""


class TaskCommand(Command):
    """Base for task domain commands."""

    task_id: str | None = None


class CreateTaskCommand(TaskCommand):
    """Create a new task."""

    title: str = ""
    description: str = ""
    team_id: str | None = None


class CompleteTaskCommand(TaskCommand):
    """Mark a task as complete."""

    result: str = ""


class AgentCommand(Command):
    """Base for agent domain commands."""

    agent_id: str | None = None


class SpawnAgentCommand(AgentCommand):
    """Spawn a new agent."""

    name: str = ""
    role: str = ""
    team_id: str | None = None


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

    @override
    async def handle(self, command: Command) -> list:
        """Process team commands."""
        from .domain_event import DomainEvent

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
                    metadata={"user_id": command.user_id} if command.user_id else {},
                )
            ]
        return []


class TaskCommandHandler(CommandHandler):
    """Handler for task domain commands."""

    @override
    async def handle(self, command: Command) -> list:
        """Process task commands."""
        from .domain_event import DomainEvent

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
                    metadata={"user_id": command.user_id} if command.user_id else {},
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
                    metadata={"user_id": command.user_id} if command.user_id else {},
                )
            ]
        return []


class AgentCommandHandler(CommandHandler):
    """Handler for agent domain commands."""

    @override
    async def handle(self, command: Command) -> list:
        """Process agent commands."""
        from .domain_event import DomainEvent

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
                    metadata={"user_id": command.user_id} if command.user_id else {},
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
        handlers: dict[type[Command], CommandHandler] | None = None,
    ):
        """Initialize command bus.

        Args:
            event_store: EventStore instance for persisting events
            handlers: Dict mapping command types to handlers
        """
        self.event_store = event_store
        self.handlers: dict[type[Command], CommandHandler] = handlers or {
            CreateTeamCommand: TeamCommandHandler(),
            TaskCommand: TaskCommandHandler(),
            CreateTaskCommand: TaskCommandHandler(),
            CompleteTaskCommand: TaskCommandHandler(),
            SpawnAgentCommand: AgentCommandHandler(),
        }

    def register_handler(
        self, command_type: type[Command], handler: CommandHandler
    ) -> None:
        """Register a command handler.

        Args:
            command_type: Command class this handler processes
            handler: CommandHandler instance
        """
        self.handlers[command_type] = handler

    @instrument("command.dispatch")
    async def dispatch(self, command: Command) -> list:
        """Public entrypoint for command dispatch — instrumented.

        Delegates to execute() for handler resolution and event emission.
        """
        return await self.execute(command)

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
                self.event_store.append(event)
            log.info(f"Command {command.command_id} emitted {len(events)} events")

        return events
