#!/usr/bin/env python3
"""
SessionStart Hook – loads 3-tier memory and prepares session.
Now respects AgentRootPermission for any privileged operations.
"""
import asyncio
import json
from pathlib import Path

from utils import ensure_structure, get_system_dir, get_project_dir, get_session_dir
from uvloop_integration import run_with_uvloop, get_event_loop_info
from utils.permission_checker import check_agent_permission  # NEW

async def main_async():
    ensure_structure()

    agent_name = "SessionStart"  # special system agent
    memory_parts = []

    # === HIERARCHICAL LOADING: System → Project → Session ===
    layers = [
        ("System Layer", get_system_dir()),
        ("Project Layer", get_project_dir()),
        ("Session Layer", get_session_dir())
    ]

    tasks = []
    for layer_name, layer_dir in layers:
        if layer_dir and layer_dir.exists():
            tasks.append(load_layer_content_async(layer_name, layer_dir))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, list):
            memory_parts.extend(result)

    combined = "\n\n".join(memory_parts) or "No prior memory yet."
    loop_info = get_event_loop_info()

    # Permission check for any future privileged operations in this session
    allowed, reason, needs_approval = await check_agent_permission(
        agent_name=agent_name,
        action="read",
        path=str(get_project_dir())
    )

    output = {
        "hookSpecificOutput": {
            "additionalContext": f"""🔐 **CYBERSEC SESSION STARTED** (uvloop {loop_info['performance']})

{combined}

**Permission status**: {agent_name} → {reason} (allowed={allowed})
**Active Layers**: System → Project → Session
**Event Loop**: {loop_info['class']}
Ready for Hunter / specialists."""
        }
    }

    print(json.dumps(output))

async def load_layer_content_async(layer_name, layer_dir):
    parts = []
    filenames = ["scope.md", "threat_model.md", "risk_register.md", "mitre-attack.md"]
    for filename in filenames:
        p = layer_dir / filename
        if p.exists():
            try:
                loop = asyncio.get_event_loop()
                content = await loop.run_in_executor(None, p.read_text, "utf-8")
                if content.strip():
                    parts.append(f"### {layer_name.upper()} — {filename.replace('.md','').upper()}\n{content.strip()[:1000]}")
            except Exception:
                pass
    return parts

def main():
    run_with_uvloop(main_async())

if __name__ == "__main__":
    main()