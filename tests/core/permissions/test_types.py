from datetime import UTC, datetime

from css.core.permissions import PathOp, ToolGrant


def test_path_op_all_combines_read_write_execute() -> None:
    assert PathOp.ALL == (PathOp.READ | PathOp.WRITE | PathOp.EXECUTE)
    assert (PathOp.ALL & PathOp.READ) == PathOp.READ
    assert (PathOp.ALL & PathOp.WRITE) == PathOp.WRITE
    assert (PathOp.ALL & PathOp.EXECUTE) == PathOp.EXECUTE


def test_tool_grant_struct_contract() -> None:
    expires_at = datetime.now(UTC)
    grant = ToolGrant(
        agent_id="agent-1",
        tool_pattern="provider:*",
        allowed=False,
        session_id="sess-1",
        expires_at=expires_at,
    )

    assert grant.agent_id == "agent-1"
    assert grant.tool_pattern == "provider:*"
    assert grant.allowed is False
    assert grant.session_id == "sess-1"
    assert grant.expires_at == expires_at
