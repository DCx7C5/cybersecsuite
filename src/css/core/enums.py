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



class MessageRole(str, Enum):
    """Message roles in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MarketplaceStatus(str, Enum):
    """Lifecycle status of a marketplace item."""

    active = "active"
    updates_available = "updates_available"



class MarketplaceItemStatus(str, Enum):
    """Lifecycle status of a marketplace item."""

    installed = "installed"
    update_available = "update_available"
    enabled = "enabled"
    disabled = "disabled"


class MarketplaceItemType(str, Enum):
    """Type of marketplace item."""

    agent = "agent"
    skill = "skill"
    mcp = "mcp"
    template = "template"
    workflow = "workflow"
    prompt = "prompt"


class RoleType(str, Enum):
    """Available orchestration roles."""
    ORCHESTRATOR = "orchestrator"
    TEAM_LEADER = "team-leader"
    TEAM_MEMBER = "team-member"


class Permission(str, Enum):
    """Available permissions in the system."""
    # Orchestrator permissions
    ORCHESTRATOR_SPAWN = "orchestrator:spawn"
    ORCHESTRATOR_KILL = "orchestrator:kill"

    # Team permissions
    TEAM_MONITOR = "team:monitor"
    TEAM_PAUSE = "team:pause"
    TEAM_RESUME = "team:resume"

    # Heartbeat permissions
    HEARTBEAT_CHECK = "heartbeat:check"

    # Crash recovery
    CRASH_RECOVER = "crash:recover"

    # Task permissions
    TASK_DELEGATE = "task:delegate"
    TASK_RETRY = "task:retry"
    TASK_CANCEL = "task:cancel"
    TASK_EXECUTE = "task:execute"

    # Member permissions
    MEMBER_ASSIGN = "member:assign"
    MEMBER_REASSIGN = "member:reassign"

    # Tool permissions
    TOOL_USE = "tool:use"

    # Result permissions
    RESULT_AGGREGATE = "result:aggregate"
    RESULT_REPORT = "result:report"

    # Timeout permissions
    TIMEOUT_ENFORCE = "timeout:enforce"

    # Error handling
    ERROR_CATCH = "error:catch"
