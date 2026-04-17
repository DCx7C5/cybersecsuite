#!/usr/bin/env python3
"""
UserPromptSubmit Hook — fires before Claude processes a user prompt.
Injects current investigation phase, active mode (blue/red/purple), and session context.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import get_session_dir, audit


def main():
    data = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    session_dir = get_session_dir()

    context_parts = []

    if session_dir:
        # Inject active mode
        mode_file = session_dir / "mode.json"
        if mode_file.exists():
            try:
                mode_data = json.loads(mode_file.read_text())
                context_parts.append(f"[Mode: {mode_data.get('mode', 'blue')}]")
            except (json.JSONDecodeError, OSError):
                pass

        # Inject active phase
        phase_file = session_dir / "phase.json"
        if phase_file.exists():
            try:
                phase_data = json.loads(phase_file.read_text())
                context_parts.append(f"[Phase: {phase_data.get('phase', 'unknown')}]")
            except (json.JSONDecodeError, OSError):
                pass

    audit("user_prompt_submit", {
        "prompt_length": len(data.get("prompt", "")),
        "context_injected": context_parts,
    })


if __name__ == "__main__":
    main()
