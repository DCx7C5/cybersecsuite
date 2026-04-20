"""
Seed helpers for ToolRegistry and ProviderModel tables.

seed_tool_registry()  — populate ToolRegistry from live MCP tools + known SDK builtins
seed_provider_models() — populate ProviderModel from provider registry / pricing data
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("db.seeds.tools")

# ── Known Anthropic SDK builtin tools ────────────────────────────────────────
# Format: (sdk_type_string, display_name, required_beta, description, min_tier)
_SDK_BUILTIN_TOOLS: list[tuple[str, str, str | None, str, str]] = [
    (
        "computer_use_20250124",
        "Computer Use",
        "computer-use-2025-01-24",
        "Control a computer: mouse, keyboard, screenshot, bash commands.",
        "standard",
    ),
    (
        "web_search_20250305",
        "Web Search",
        "web-search-2025-03-05",
        "Search the web and return relevant results.",
        "standard",
    ),
    (
        "text_editor_20250124",
        "Text Editor",
        "computer-use-2025-01-24",
        "View and edit text files with str_replace, view, create operations.",
        "standard",
    ),
    (
        "bash_20250124",
        "Bash",
        "computer-use-2025-01-24",
        "Execute bash commands in a persistent shell session.",
        "standard",
    ),
]

# ── Known Anthropic SDK beta tools ────────────────────────────────────────────
_SDK_BETA_TOOLS: list[tuple[str, str, str, str, str]] = [
    (
        "memory_20250818",
        "Memory Tool",
        "memory-2025-08-18",
        "Persistent memory across conversations via /memories/* file operations.",
        "standard",
    ),
    (
        "skills_20250515",
        "Skills",
        "skills-2025-05-15",
        "Reusable parameterized prompt templates registered as beta tools.",
        "standard",
    ),
]

_AGENT_SDK_BUILTINS: list[tuple[str, str, str]] = [
    ("Agent", "Agent Delegation", "Delegate work to a specialist sub-agent."),
    ("Bash", "Bash", "Run shell commands in a persistent session."),
    ("Edit", "Edit", "Edit an existing file in-place."),
    ("Glob", "Glob", "Find files by glob pattern."),
    ("Grep", "Grep", "Search code and text content."),
    ("Monitor", "Monitor", "Observe long-running task or session output."),
    ("Read", "Read", "Read file contents."),
    ("WebFetch", "Web Fetch", "Fetch and inspect a web page."),
    ("WebSearch", "Web Search", "Search the web for current information."),
    ("Write", "Write", "Create or overwrite files."),
]


async def seed_tool_registry() -> dict[str, Any]:
    """
    Populate ToolRegistry with:
    1. All live MCP tools from cybersec + dystopian servers
    2. Known Anthropic SDK builtin tools
    3. Known Anthropic SDK beta tools
    4. Agent SDK builtin + discovered custom agent tools
    """
    from db.models.tool_registry import ToolRegistry
    from db.models.enums import ToolType, ModelTier

    created = 0
    updated = 0
    errors: list[str] = []

    # ── 1. MCP tools from live servers ───────────────────────────────────────
    try:
        from csmcp.cybersec import _ALL_CYBERSEC_TOOLS
        for tool_fn in _ALL_CYBERSEC_TOOLS:
            name = getattr(tool_fn, "_sdk_tool_name", None) or getattr(tool_fn, "__name__", None)
            if not name:
                continue
            desc = getattr(tool_fn, "_sdk_tool_description", "") or ""
            schema = getattr(tool_fn, "_sdk_tool_input_schema", {}) or {}

            tags = _infer_tags(name, "mcp_cybersec")
            _, was_created = await ToolRegistry.update_or_create(
                tool_name=name,
                defaults={
                    "display_name": name.replace("_", " ").title(),
                    "description": desc[:500],
                    "tool_type": ToolType.MCP_CYBERSEC,
                    "mcp_server": "cybersec",
                    "input_schema": schema,
                    "min_tier": ModelTier.FREE,
                    "enabled_by_default": True,
                    "tags": tags,
                },
            )
            created += int(was_created)
            updated += int(not was_created)
    except Exception as e:
        errors.append(f"cybersec tools: {e}")
        logger.warning("Could not load cybersec tools: %s", e)

    try:
        from csmcp.dystopian import _ALL_DYSTOPIAN_TOOLS
        for tool_fn in _ALL_DYSTOPIAN_TOOLS:
            name = getattr(tool_fn, "_sdk_tool_name", None) or getattr(tool_fn, "__name__", None)
            if not name:
                continue
            desc = getattr(tool_fn, "_sdk_tool_description", "") or ""
            schema = getattr(tool_fn, "_sdk_tool_input_schema", {}) or {}

            _, was_created = await ToolRegistry.update_or_create(
                tool_name=name,
                defaults={
                    "display_name": name.replace("_", " ").title(),
                    "description": desc[:500],
                    "tool_type": ToolType.MCP_DYSTOPIAN,
                    "mcp_server": "dystopian",
                    "input_schema": schema,
                    "min_tier": ModelTier.FREE,
                    "enabled_by_default": True,
                    "tags": ["crypto", "signing"],
                },
            )
            created += int(was_created)
            updated += int(not was_created)
    except Exception as e:
        errors.append(f"dystopian tools: {e}")
        logger.warning("Could not load dystopian tools: %s", e)

    # ── 2. SDK builtin tools ─────────────────────────────────────────────────
    for sdk_type, display, beta, desc, tier_str in _SDK_BUILTIN_TOOLS:
        tier = ModelTier(tier_str)
        name = sdk_type  # tool_name == sdk_type_string for builtins
        try:
            _, was_created = await ToolRegistry.update_or_create(
                tool_name=name,
                defaults={
                    "display_name": display,
                    "description": desc,
                    "tool_type": ToolType.SDK_BUILTIN,
                    "sdk_type_string": sdk_type,
                    "required_beta": beta,
                    "required_provider": "anthropic",
                    "min_tier": tier,
                    "enabled_by_default": True,
                    "tags": ["sdk", "builtin", "anthropic"],
                },
            )
            created += int(was_created)
            updated += int(not was_created)
        except Exception as e:
            errors.append(f"sdk_builtin {sdk_type}: {e}")

    # ── 3. SDK beta tools ────────────────────────────────────────────────────
    for sdk_type, display, beta, desc, tier_str in _SDK_BETA_TOOLS:
        tier = ModelTier(tier_str)
        name = sdk_type
        try:
            _, was_created = await ToolRegistry.update_or_create(
                tool_name=name,
                defaults={
                    "display_name": display,
                    "description": desc,
                    "tool_type": ToolType.SDK_BETA,
                    "sdk_type_string": sdk_type,
                    "required_beta": beta,
                    "required_provider": "anthropic",
                    "min_tier": tier,
                    "enabled_by_default": True,
                    "tags": ["sdk", "beta", "anthropic"],
                },
            )
            created += int(was_created)
            updated += int(not was_created)
        except Exception as e:
            errors.append(f"sdk_beta {sdk_type}: {e}")

    # ── 4. Agent SDK builtin + discovered custom tools ──────────────────────
    for tool_name, display_name, desc in _AGENT_SDK_BUILTINS:
        try:
            _, was_created = await ToolRegistry.update_or_create(
                tool_name=tool_name,
                defaults={
                    "display_name": display_name,
                    "description": desc,
                    "tool_type": ToolType.AGENT_SDK,
                    "agent_source": "builtin",
                    "input_schema": {},
                    "min_tier": ModelTier.FREE,
                    "enabled_by_default": True,
                    "tags": ["agent-sdk", "builtin"],
                },
            )
            created += int(was_created)
            updated += int(not was_created)
        except Exception as e:
            errors.append(f"agent_sdk builtin {tool_name}: {e}")

    try:
        from pathlib import Path
        from a2a.agent_loader import frontmatter_to_claude_agent, iter_agent_markdown_files

        project_root = Path(__file__).resolve().parents[3]
        agents_dir = project_root / ".claude" / "agents"
        seen_custom: set[str] = set()
        builtin_names = {name for name, _, _ in _AGENT_SDK_BUILTINS}
        for md_path in iter_agent_markdown_files(agents_dir, recurse=True, include_sub_agents=True):
            card = frontmatter_to_claude_agent(md_path)
            if not card:
                continue
            agent_name = card.card.name
            source = str(card.metadata.get("source") or "")
            source_kind = str(card.metadata.get("source_kind") or "agent")
            for tool_name in card.tools:
                if tool_name in builtin_names or tool_name in seen_custom:
                    continue
                seen_custom.add(tool_name)
                _, was_created = await ToolRegistry.update_or_create(
                    tool_name=tool_name,
                    defaults={
                        "display_name": tool_name.replace("_", " ").replace("-", " ").title(),
                        "description": f"Custom tool discovered from agent '{agent_name}'.",
                        "tool_type": ToolType.EXTERNAL,
                        "agent_source": source,
                        "input_schema": {},
                        "min_tier": ModelTier.FREE,
                        "enabled_by_default": True,
                        "tags": ["agent-sdk", "custom", source_kind],
                    },
                )
                created += int(was_created)
                updated += int(not was_created)
    except Exception as e:
        errors.append(f"agent_sdk custom tools: {e}")

    total = created + updated
    logger.info("ToolRegistry seed: %d created, %d updated (%d total)", created, updated, total)
    return {
        "status": "ok" if not errors else "partial",
        "created": created,
        "updated": updated,
        "total": total,
        "errors": errors,
    }


async def seed_provider_models(provider_id: str | None = None) -> dict[str, Any]:
    """
    Sync ProviderModel rows from the live provider registry / pricing catalog.

    If provider_id is given, only syncs that provider. Otherwise syncs all.
    """
    from db.models.provider_model import ProviderModel
    from db.models.provider import Provider
    from db.models.enums import ModelTier, ModelStatus

    created = 0
    updated = 0
    errors: list[str] = []

    try:
        from ai_proxy.providers.registry import get_provider_registry
        registry = get_provider_registry()
        providers = registry.list_providers()
    except Exception as e:
        errors.append(f"Could not load provider registry: {e}")
        return {"status": "error", "errors": errors}

    for prov_cfg in providers:
        pid = prov_cfg.get("id") or prov_cfg.get("provider_id", "")
        if provider_id and pid != provider_id:
            continue

        # Ensure provider row exists
        try:
            db_provider = await Provider.filter(id=pid).first()
            if not db_provider:
                logger.debug("Provider %s not in DB — skipping model sync", pid)
                continue
        except Exception:
            continue

        for m in prov_cfg.get("models", []):
            model_id = m.get("id") or m.get("model_id", "")
            if not model_id:
                continue
            try:
                tier_str = m.get("tier", "standard")
                try:
                    tier = ModelTier(tier_str)
                except ValueError:
                    tier = ModelTier.STANDARD

                defaults: dict[str, Any] = {
                    "display_name": m.get("name") or model_id,
                    "description": m.get("description", ""),
                    "context_window": m.get("context_length") or m.get("context_window"),
                    "max_output_tokens": m.get("max_output_tokens") or m.get("max_tokens"),
                    "input_cost_per_mtok": m.get("input_cost_per_mtok") or m.get("input_price"),
                    "output_cost_per_mtok": m.get("output_cost_per_mtok") or m.get("output_price"),
                    "supports_vision": bool(m.get("supports_vision") or m.get("vision", False)),
                    "supports_tools": bool(m.get("supports_tools", True)),
                    "supports_streaming": bool(m.get("supports_streaming", True)),
                    "supports_thinking": bool(m.get("supports_thinking") or m.get("extended_thinking", False)),
                    "supports_prompt_cache": bool(m.get("supports_prompt_cache") or m.get("prompt_caching", False)),
                    "supports_batches": bool(m.get("supports_batches") or m.get("batch_processing", False)),
                    "supports_computer_use": bool(m.get("supports_computer_use", False)),
                    "supports_memory_tool": bool(m.get("supports_memory_tool", False)),
                    "modalities": m.get("modalities", ["text"]),
                    "required_betas": m.get("required_betas", []),
                    "tier": tier,
                    "status": ModelStatus.ACTIVE,
                    "enabled": True,
                    "extra": {k: v for k, v in m.items() if k not in (
                        "id", "model_id", "name", "description", "context_length",
                        "context_window", "max_output_tokens", "max_tokens",
                    )},
                }
                _, was_created = await ProviderModel.update_or_create(
                    provider=db_provider, model_id=model_id, defaults=defaults
                )
                created += int(was_created)
                updated += int(not was_created)
            except Exception as e:
                errors.append(f"{pid}/{model_id}: {e}")
                logger.warning("Error syncing model %s/%s: %s", pid, model_id, e)

    total = created + updated
    logger.info("ProviderModel seed: %d created, %d updated", created, updated)
    return {
        "status": "ok" if not errors else "partial",
        "created": created,
        "updated": updated,
        "total": total,
        "errors": errors,
    }


def _infer_tags(tool_name: str, tool_type: str) -> list[str]:
    """Infer tag list from tool name."""
    tags = [tool_type.replace("mcp_", "").replace("_", "-")]
    mappings = {
        "vault": ["vault", "memory", "forensics"],
        "canvas": ["canvas", "visual"],
        "memory": ["memory"],
        "finding": ["findings", "forensics"],
        "ioc": ["ioc", "forensics"],
        "case": ["cases"],
        "proxy": ["proxy", "routing"],
        "cache": ["cache"],
        "route": ["routing"],
        "combo": ["routing"],
        "crypto": ["crypto"],
        "toggle": ["toggle", "config"],
        "skill": ["skills"],
        "health": ["health"],
        "session": ["session"],
    }
    for key, extra_tags in mappings.items():
        if key in tool_name:
            tags.extend(t for t in extra_tags if t not in tags)
    return tags
