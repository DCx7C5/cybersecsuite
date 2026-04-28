"""Anthropic Agents Beta API — management tools for remote agents, sessions, environments, vaults.

Based on examples/agents.py and examples/agents_comprehensive.py from the Anthropic SDK.

Wraps the beta.agents, beta.sessions, beta.environments, beta.vaults, beta.skills APIs
so forensic agents can be created and managed programmatically via MCP tools.
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..sdk_compat import tool
from ..helpers import JsonDict, sdk_result, sdk_error


def _get_client():
    """Return a synchronous Anthropic client for beta API calls."""
    import anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    # Agents beta API must go to the real Anthropic endpoint, not our local asgi
    return anthropic.Anthropic(api_key=api_key, base_url="https://api.anthropic.com")


# ── Environments ──────────────────────────────────────────────────────────────


@tool(
    "agent_env_create",
    "Create an Anthropic agent environment (isolated execution context).",
    {
        "name": {"type": "string", "description": "Environment name (e.g. 'forensics-env-prod')"},
    },
)
async def agent_env_create(args: dict[str, Any]) -> JsonDict:
    name = str(args.get("name", "cybersec-environment")).strip()
    try:
        client = _get_client()
        env = client.beta.environments.create(name=name)
        return sdk_result({"environment_id": env.id, "name": name})
    except Exception as exc:
        return sdk_error(f"agent_env_create failed: {exc}")


# ── Vaults + Credentials ──────────────────────────────────────────────────────


@tool(
    "agent_vault_create",
    "Create an Anthropic vault for storing MCP server credentials.",
    {
        "display_name": {"type": "string", "description": "Human-readable vault name"},
    },
)
async def agent_vault_create(args: dict[str, Any]) -> JsonDict:
    display_name = str(args.get("display_name", "cybersec-vault")).strip()
    try:
        client = _get_client()
        vault = client.beta.vaults.create(display_name=display_name)
        return sdk_result({"vault_id": vault.id, "display_name": display_name})
    except Exception as exc:
        return sdk_error(f"agent_vault_create failed: {exc}")


@tool(
    "agent_vault_add_credential",
    "Store an MCP server credential (static bearer token) in an existing vault.",
    {
        "vault_id": {"type": "string", "description": "Vault ID from agent_vault_create"},
        "display_name": {"type": "string", "description": "Credential label"},
        "mcp_server_url": {"type": "string", "description": "The MCP server URL"},
        "token": {"type": "string", "description": "Bearer token for the MCP server"},
        "auth_type": {
            "type": "string",
            "description": "Authentication type (default: static_bearer)",
            "default": "static_bearer",
        },
    },
)
async def agent_vault_add_credential(args: dict[str, Any]) -> JsonDict:
    vault_id = str(args.get("vault_id", "")).strip()
    display_name = str(args.get("display_name", "mcp-credential")).strip()
    mcp_server_url = str(args.get("mcp_server_url", "")).strip()
    token = str(args.get("token", "")).strip()

    if not vault_id:
        return sdk_error("vault_id is required")
    if not mcp_server_url:
        return sdk_error("mcp_server_url is required")
    if not token:
        return sdk_error("token is required")

    try:
        client = _get_client()
        cred = client.beta.vaults.credentials.create(
            vault_id,
            display_name=display_name,
            auth={"type": "static_bearer", "mcp_server_url": mcp_server_url, "token": token},
        )
        return sdk_result({"credential_id": cred.id, "vault_id": vault_id, "display_name": display_name})
    except Exception as exc:
        return sdk_error(f"agent_vault_add_credential failed: {exc}")


# ── Skills ────────────────────────────────────────────────────────────────────


@tool(
    "agent_skill_upload",
    "Upload a SKILL.md file to Anthropic as a custom agent skill.",
    {
        "skill_path": {
            "type": "string",
            "description": "Absolute path to a SKILL.md file to upload",
        },
        "display_title": {
            "type": "string",
            "description": "Display title for the skill (must be unique; auto-generated if omitted)",
        },
    },
)
async def agent_skill_upload(args: dict[str, Any]) -> JsonDict:
    from pathlib import Path
    import time

    skill_path = str(args.get("skill_path", "")).strip()
    if not skill_path:
        return sdk_error("skill_path is required")

    path = Path(skill_path)
    if not path.exists():
        return sdk_error(f"File not found: {skill_path}")
    if not path.name.endswith(".md"):
        return sdk_error("skill_path must point to a .md file")

    display_title = str(args.get("display_title", f"cybersec-skill-{int(time.time() * 1000)}"))

    try:
        client = _get_client()
        with path.open("rb") as fh:
            skill = client.beta.skills.create(
                display_title=display_title,
                files=[(path.name, fh, "text/markdown")],
            )
        return sdk_result({"skill_id": skill.id, "display_title": display_title, "file": path.name})
    except Exception as exc:
        return sdk_error(f"agent_skill_upload failed: {exc}")


# ── Agents ────────────────────────────────────────────────────────────────────


@tool(
    "agent_remote_create",
    "Create a remote Anthropic agent with tools, MCP servers, and skills.",
    {
        "name": {"type": "string", "description": "Agent name (e.g. 'forensics-analyst')"},
        "model": {"type": "string", "description": "Model ID", "default": "claude-sonnet-4-6"},
        "system": {"type": "string", "description": "System prompt"},
        "tools_config": {
            "type": "string",
            "description": (
                "JSON array of tool configs. Examples: "
                '[{"type":"agent_toolset_20260401"}], '
                '[{"type":"mcp_toolset","mcp_server_name":"github"}], '
                '[{"type":"custom","name":"get_iocs","description":"...","input_schema":{...}}]'
            ),
        },
        "mcp_servers": {
            "type": "string",
            "description": 'JSON array of MCP server configs, e.g. [{"type":"url","name":"github","url":"https://..."}]',
        },
    },
)
async def agent_remote_create(args: dict[str, Any]) -> JsonDict:
    name = str(args.get("name", "cybersec-agent")).strip()
    model = str(args.get("model", "claude-sonnet-4-6"))
    system = args.get("system")

    tools_raw = args.get("tools_config")
    mcp_servers_raw = args.get("mcp_servers")

    try:
        tools_config = json.loads(tools_raw) if tools_raw else [{"type": "agent_toolset_20260401"}]
    except json.JSONDecodeError:
        return sdk_error("tools_config must be valid JSON")

    try:
        mcp_servers = json.loads(mcp_servers_raw) if mcp_servers_raw else []
    except json.JSONDecodeError:
        return sdk_error("mcp_servers must be valid JSON")

    try:
        client = _get_client()
        create_kwargs: dict[str, Any] = {
            "name": name,
            "model": model,
            "tools": tools_config,
        }
        if system:
            create_kwargs["system"] = system
        if mcp_servers:
            create_kwargs["mcp_servers"] = mcp_servers

        agent = client.beta.agents.create(**create_kwargs)
        return sdk_result({
            "agent_id": agent.id,
            "version": agent.version,
            "name": name,
            "model": model,
        })
    except Exception as exc:
        return sdk_error(f"agent_remote_create failed: {exc}")


@tool(
    "agent_remote_add_skills",
    "Add custom or Anthropic built-in skills to an existing remote agent (bumps version).",
    {
        "agent_id": {"type": "string", "description": "Agent ID from agent_remote_create"},
        "version": {"type": "integer", "description": "Current agent version"},
        "custom_skill_ids": {
            "type": "string",
            "description": "JSON array of custom skill IDs from agent_skill_upload",
        },
        "anthropic_skill_ids": {
            "type": "string",
            "description": 'JSON array of Anthropic built-in skill IDs, e.g. ["xlsx","pdf"]',
        },
    },
)
async def agent_remote_add_skills(args: dict[str, Any]) -> JsonDict:
    agent_id = str(args.get("agent_id", "")).strip()
    version = int(args.get("version", 1))
    custom_ids_raw = args.get("custom_skill_ids", "[]")
    anthropic_ids_raw = args.get("anthropic_skill_ids", "[]")

    if not agent_id:
        return sdk_error("agent_id is required")

    try:
        custom_ids = json.loads(custom_ids_raw) if custom_ids_raw else []
        anthropic_ids = json.loads(anthropic_ids_raw) if anthropic_ids_raw else []
    except json.JSONDecodeError:
        return sdk_error("skill IDs must be valid JSON arrays")

    skills: list[dict] = []
    for sid in custom_ids:
        skills.append({"type": "custom", "skill_id": sid})
    for sid in anthropic_ids:
        skills.append({"type": "anthropic", "skill_id": sid})

    if not skills:
        return sdk_error("At least one skill ID must be provided")

    try:
        client = _get_client()
        updated = client.beta.agents.update(agent_id, version=version, skills=skills)
        return sdk_result({
            "agent_id": updated.id,
            "new_version": updated.version,
            "skills_added": len(skills),
        })
    except Exception as exc:
        return sdk_error(f"agent_remote_add_skills failed: {exc}")


@tool(
    "agent_versions_list",
    "List all versions of a remote Anthropic agent.",
    {
        "agent_id": {"type": "string", "description": "Agent ID"},
    },
)
async def agent_versions_list(args: dict[str, Any]) -> JsonDict:
    agent_id = str(args.get("agent_id", "")).strip()
    if not agent_id:
        return sdk_error("agent_id is required")
    try:
        client = _get_client()
        versions = client.beta.agents.versions.list(agent_id)
        return sdk_result({
            "agent_id": agent_id,
            "versions": [{"version": v.version, "created_at": str(v.created_at)} for v in versions.data],
        })
    except Exception as exc:
        return sdk_error(f"agent_versions_list failed: {exc}")


# ── Sessions ──────────────────────────────────────────────────────────────────


@tool(
    "agent_session_create",
    "Create a session for a remote agent pinned to a specific version.",
    {
        "environment_id": {"type": "string", "description": "Environment ID from agent_env_create"},
        "agent_id": {"type": "string", "description": "Agent ID"},
        "agent_version": {"type": "integer", "description": "Agent version to pin to"},
        "vault_ids": {
            "type": "string",
            "description": "JSON array of vault IDs to make available to the session",
        },
        "file_resources": {
            "type": "string",
            "description": (
                "JSON array of file resources to mount: "
                '[{"file_id":"file_abc","mount_path":"evidence.pcap"}]'
            ),
        },
    },
)
async def agent_session_create(args: dict[str, Any]) -> JsonDict:
    env_id = str(args.get("environment_id", "")).strip()
    agent_id = str(args.get("agent_id", "")).strip()
    agent_version = int(args.get("agent_version", 1))

    if not env_id:
        return sdk_error("environment_id is required")
    if not agent_id:
        return sdk_error("agent_id is required")

    vault_ids_raw = args.get("vault_ids", "[]")
    file_resources_raw = args.get("file_resources", "[]")

    try:
        vault_ids = json.loads(vault_ids_raw) if vault_ids_raw else []
        file_resources = json.loads(file_resources_raw) if file_resources_raw else []
    except json.JSONDecodeError:
        return sdk_error("vault_ids and file_resources must be valid JSON arrays")

    resources = [{"type": "file", **r} for r in file_resources]

    try:
        client = _get_client()
        create_kwargs: dict[str, Any] = {
            "environment_id": env_id,
            "agent": {"type": "agent", "id": agent_id, "version": agent_version},
        }
        if vault_ids:
            create_kwargs["vault_ids"] = vault_ids
        if resources:
            create_kwargs["resources"] = resources

        session = client.beta.sessions.create(**create_kwargs)
        return sdk_result({
            "session_id": session.id,
            "agent_id": agent_id,
            "environment_id": env_id,
        })
    except Exception as exc:
        return sdk_error(f"agent_session_create failed: {exc}")


@tool(
    "agent_session_run",
    "Send a prompt to a remote agent session and stream/collect the response.",
    {
        "session_id": {"type": "string", "description": "Session ID from agent_session_create"},
        "prompt": {"type": "string", "description": "User message to send"},
        "custom_tool_results": {
            "type": "string",
            "description": (
                "JSON map of pending custom tool results: "
                '{"custom_tool_use_id": "result_text"}'
            ),
        },
    },
)
async def agent_session_run(args: dict[str, Any]) -> JsonDict:
    session_id = str(args.get("session_id", "")).strip()
    prompt = str(args.get("prompt", "")).strip()
    custom_results_raw = args.get("custom_tool_results", "{}")

    if not session_id:
        return sdk_error("session_id is required")
    if not prompt:
        return sdk_error("prompt is required")

    try:
        custom_results: dict[str, str] = json.loads(custom_results_raw) if custom_results_raw else {}
    except json.JSONDecodeError:
        return sdk_error("custom_tool_results must be valid JSON")

    try:
        client = _get_client()

        client.beta.sessions.events.send(
            session_id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": prompt}]}],
        )

        collected_text: list[str] = []
        custom_tool_calls: list[dict] = []
        stop_reason: str | None = None

        with client.beta.sessions.events.stream(session_id) as stream:
            for event in stream:
                if event.type == "agent.text_delta":
                    collected_text.append(getattr(event, "text", ""))
                elif event.type == "agent.custom_tool_use":
                    custom_tool_calls.append({
                        "tool_use_id": event.id,
                        "name": event.name,
                        "input": getattr(event, "input", {}),
                    })
                    # Answer any pre-provided results
                    if event.id in custom_results:
                        client.beta.sessions.events.send(
                            session_id,
                            events=[{
                                "type": "user.custom_tool_result",
                                "custom_tool_use_id": event.id,
                                "content": [{"type": "text", "text": custom_results[event.id]}],
                            }],
                        )
                elif event.type == "session.status_idle":
                    reason = getattr(event, "stop_reason", None)
                    stop_reason = getattr(reason, "type", "end_turn") if reason else "end_turn"
                    break

        return sdk_result({
            "session_id": session_id,
            "response": "".join(collected_text),
            "stop_reason": stop_reason,
            "pending_tool_calls": [tc for tc in custom_tool_calls if tc["tool_use_id"] not in custom_results],
        })
    except Exception as exc:
        return sdk_error(f"agent_session_run failed: {exc}")


@tool(
    "agent_file_upload",
    "Upload a file to Anthropic beta Files API for use as a session resource.",
    {
        "file_path": {"type": "string", "description": "Absolute path to the file to upload"},
    },
)
async def agent_file_upload(args: dict[str, Any]) -> JsonDict:
    from pathlib import Path

    file_path = str(args.get("file_path", "")).strip()
    if not file_path:
        return sdk_error("file_path is required")

    path = Path(file_path)
    if not path.exists():
        return sdk_error(f"File not found: {file_path}")

    try:
        client = _get_client()
        uploaded = client.beta.files.upload(file=path)
        return sdk_result({
            "file_id": uploaded.id,
            "file_name": path.name,
            "size_bytes": path.stat().st_size,
        })
    except Exception as exc:
        return sdk_error(f"agent_file_upload failed: {exc}")


ALL_TOOLS = [
    agent_env_create,
    agent_vault_create,
    agent_vault_add_credential,
    agent_skill_upload,
    agent_remote_create,
    agent_remote_add_skills,
    agent_versions_list,
    agent_session_create,
    agent_session_run,
    agent_file_upload,
]
