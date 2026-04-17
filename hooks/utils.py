import os
from pathlib import Path
from datetime import datetime

def get_data_dir():
    """Returns persistent ${CLAUDE_PLUGIN_DATA}/cybersec-mem"""
    return Path(os.environ["CLAUDE_PLUGIN_DATA"]) / "cybersec-mem"

def get_system_dir():
    """System Layer (highest level)"""
    return Path.home() / ".claude" / "cybersec"

def get_project_dir():
    """Project Layer"""
    data_dir, project_dir = ensure_structure()
    return project_dir

def get_session_dir():
    """Session Layer (set by artefact-logger)"""
    return Path(os.environ.get("CYBERSEC_SESSION_DIR")) if os.environ.get("CYBERSEC_SESSION_DIR") else None

def ensure_structure():
    """Create folders + copy templates"""
    data_dir = get_data_dir()
    project_dir = data_dir / "project"
    session_dir = data_dir / "session"

    project_dir.mkdir(parents=True, exist_ok=True)
    session_dir.mkdir(parents=True, exist_ok=True)

    # Copy templates
    template_dir = Path(os.environ["CLAUDE_PLUGIN_ROOT"]) / "templates" / "project"
    for template in template_dir.glob("*.md"):
        dest = project_dir / template.name
        if not dest.exists():
            dest.write_text(template.read_text(), encoding="utf-8")

    # Ensure layer directories
    get_system_dir().mkdir(parents=True, exist_ok=True)
    (project_dir / "sessions").mkdir(exist_ok=True)

    return data_dir, project_dir