"""agents.sessions — Session lifecycle management wrapping claude_agent_sdk.

Bridges claude_agent_sdk session functions to the forensic investigation
workflow: maps session IDs to cases, agents, and modes.
"""


from legacy.logger import getLogger
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = getLogger("agents.sessions")


@dataclass
class SessionRecord:
    """In-memory record of a Claude SDK session."""
    session_id: str
    agent_name: str
    mode: str = "blue"
    case_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)


class SessionManager:
    """Manages Claude SDK sessions for forensic investigations.

    Wraps claude_agent_sdk session functions (list_sessions, get_session_info,
    delete_session, rename_session, tag_session, fork_session) and maintains
    an in-memory index mapping session_id → SessionRecord.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    def register(
        self,
        session_id: str,
        agent_name: str,
        mode: str = "blue",
        case_id: str | None = None,
        tags: list[str] | None = None,
    ) -> SessionRecord:
        """Register a new session in the local index."""
        record = SessionRecord(
            session_id=session_id,
            agent_name=agent_name,
            mode=mode,
            case_id=case_id,
            tags=tags or [],
        )
        self._sessions[session_id] = record
        logger.info("registered session %s agents=%s mode=%s", session_id, agent_name, mode)
        return record

    def get(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    def list_local(self, case_id: str | None = None) -> list[SessionRecord]:
        """List locally registered sessions, optionally filtered by case."""
        records = list(self._sessions.values())
        if case_id:
            records = [r for r in records if r.case_id == case_id]
        return sorted(records, key=lambda r: r.created_at, reverse=True)

    async def list_sdk(self) -> list[dict[str, Any]]:
        """List all sessions from claude_agent_sdk."""
        try:
            from claude_agent_sdk import list_sessions
            sessions = await list_sessions()
            return [s.__dict__ if hasattr(s, "__dict__") else dict(s) for s in (sessions or [])]
        except Exception as exc:
            logger.warning("list_sdk failed: %s", exc)
            return []

    async def get_sdk_info(self, session_id: str) -> dict[str, Any] | None:
        """Get session info from claude_agent_sdk."""
        try:
            from claude_agent_sdk import get_session_info
            info = await get_session_info(session_id)
            return info.__dict__ if hasattr(info, "__dict__") else dict(info)
        except Exception as exc:
            logger.warning("get_sdk_info(%s) failed: %s", session_id, exc)
            return None

    async def delete(self, session_id: str) -> bool:
        """Delete session from SDK and local index."""
        self._sessions.pop(session_id, None)
        try:
            from claude_agent_sdk import delete_session
            await delete_session(session_id)
            return True
        except Exception as exc:
            logger.warning("delete_session(%s) failed: %s", session_id, exc)
            return False

    async def rename(self, session_id: str, new_name: str) -> bool:
        """Rename a session in the SDK."""
        try:
            from claude_agent_sdk import rename_session
            await rename_session(session_id, new_name)
            return True
        except Exception as exc:
            logger.warning("rename_session(%s) failed: %s", session_id, exc)
            return False

    async def tag(self, session_id: str, tags: list[str]) -> bool:
        """Tag a session in the SDK and update local record."""
        record = self._sessions.get(session_id)
        if record:
            record.tags = list(set(record.tags + tags))
        try:
            from claude_agent_sdk import tag_session
            await tag_session(session_id, tags)
            return True
        except Exception as exc:
            logger.warning("tag_session(%s) failed: %s", session_id, exc)
            return False

    async def fork(self, session_id: str, new_agent: str | None = None) -> str | None:
        """Fork a session; register the forked session in local index."""
        try:
            from claude_agent_sdk import fork_session
            result = await fork_session(session_id)
            forked_id = result.session_id if hasattr(result, "session_id") else str(result)
            parent = self._sessions.get(session_id)
            self.register(
                session_id=forked_id,
                agent_name=new_agent or (parent.agent_name if parent else "unknown"),
                mode=parent.mode if parent else "blue",
                case_id=parent.case_id if parent else None,
                tags=(parent.tags if parent else []) + ["forked"],
            )
            return forked_id
        except Exception as exc:
            logger.warning("fork_session(%s) failed: %s", session_id, exc)
            return None


# Global singleton — shared across AgentRunner instances
default_session_manager = SessionManager()
