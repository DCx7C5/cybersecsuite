"""Session linking - connects DB Session model to Claude SDK session IDs."""


from css.core.logger import getLogger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = getLogger("agents.session_linking")


async def link_to_sdk(db_session_id: int, sdk_session_id: str) -> bool:
    """Link a DB Session to a Claude SDK session ID."""
    try:
        from db.models import Session

        session = await Session.get(id=db_session_id)
        if not session:
            logger.warning("session %s not found", db_session_id)
            return False

        # Store SDK session ID - may need to add field to model first
        if hasattr(session, "sdk_session_id"):
            session.sdk_session_id = sdk_session_id
            await session.save()
            logger.info("linked db_session=%s -> sdk_session=%s", db_session_id, sdk_session_id)
            return True
        else:
            # Fallback: store in description or extra field
            logger.warning("Session model missing sdk_session_id field")
            return False
    except Exception as exc:
        logger.error("link_to_sdk failed: %s", exc)
        return False


async def resolve_sdk_id(db_session_id: int) -> str | None:
    """Resolve DB session ID to Claude SDK session ID."""
    try:
        from db.models import Session

        session = await Session.get(id=db_session_id)
        if not session:
            return None

        if hasattr(session, "sdk_session_id"):
            return session.sdk_session_id
        return None
    except Exception:
        return None


async def resolve_db_id(sdk_session_id: str) -> int | None:
    """Resolve Claude SDK session ID to DB session ID."""
    try:
        from db.models import Session

        session = await Session.filter(sdk_session_id=sdk_session_id).first()
        return session.id if session else None
    except Exception:
        return None


async def create_linked_session(
    project_id: int,
    name: str,
    sdk_session_id: str,
    agent: str = "cybersec-agents",
    mode: str = "blue",
) -> int | None:
    """Create a new DB Session linked to an SDK session."""
    try:
        from db.models import Session, Project
        from db.models.enums import RedBlueMode

        project = await Project.get(id=project_id)
        if not project:
            logger.warning("project %s not found", project_id)
            return None

        session = await Session.create(
            project=project,
            session_id=sdk_session_id,
            name=name,
            agent=agent,
            mode=RedBlueMode[mode.upper()],
            sdk_session_id=sdk_session_id,
        )
        logger.info("created linked session: db_id=%s sdk_id=%s", session.id, sdk_session_id)
        return session.id
    except Exception as exc:
        logger.error("create_linked_session failed: %s", exc)
        return None