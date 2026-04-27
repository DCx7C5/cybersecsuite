#!/usr/bin/env python3
"""
Agent Hooks: Lifecycle management for A2A agents with ruff scoping and dry-run mode.

Features:
  - Snapshot baseline on agent start
  - Detect file changes on agent stop
  - Scope ruff fixes to only changed files
  - Dry-run mode by default
  - Comprehensive logging
"""
import asyncio
import hashlib
import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _utils import (
    ensure_structure,
    get_project_dir,
    get_session_dir,
    audit,
    append_file,
    emit,
    hook_context,
    read_stdin,
)

logger = logging.getLogger(__name__)

# Baseline snapshots per session/agent
BASELINE_DIR = Path(os.environ.get("CYBERSECSUITE_HOME", Path.home() / ".cybersecsuite")) / "hooks" / "baselines"


def get_logger():
    """Set up logger with both file and console handlers."""
    if logger.hasHandlers():
        return logger
    logger.setLevel(logging.DEBUG)
    
    # File handler
    log_dir = Path(os.environ.get("CYBERSECSUITE_HOME", Path.home() / ".cybersecsuite")) / "hooks" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    fh = logging.FileHandler(log_dir / "agent_hooks.log")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler(sys.stderr)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(ch)
    
    return logger


def compute_file_hash(path: Path) -> str:
    """Compute SHA256 hash of a file for change detection."""
    if not path.exists():
        return "NOTFOUND"
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception as e:
        get_logger().warning(f"Failed to hash {path}: {e}")
        return "ERROR"


def get_baseline_file(agent_name: str, session_id: str) -> Path:
    """Get baseline snapshot file for an agent."""
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    sanitized_name = agent_name.replace("/", "_").replace(":", "_")
    return BASELINE_DIR / f"{session_id}_{sanitized_name}.json"


def snapshot_baseline(agent_name: str, session_id: str, target_files: List[str]) -> Dict[str, str]:
    """
    Create baseline snapshot of target files.
    
    Args:
        agent_name: Name of the agent
        session_id: Session ID
        target_files: List of file paths to snapshot (relative to project root)
    
    Returns:
        Dict mapping file path -> hash
    """
    log = get_logger()
    project_dir = get_project_dir()
    baseline = {}
    
    for rel_path in target_files:
        abs_path = project_dir / rel_path
        baseline[rel_path] = compute_file_hash(abs_path)
        log.debug(f"Baseline snapshot: {rel_path} -> {baseline[rel_path][:8]}...")
    
    # Store baseline
    baseline_file = get_baseline_file(agent_name, session_id)
    baseline_file.write_text(json.dumps(baseline, indent=2))
    log.info(f"Baseline snapshot created: {len(baseline)} files -> {baseline_file}")
    
    return baseline


def get_changed_files(agent_name: str, session_id: str, target_files: List[str]) -> List[str]:
    """
    Detect which files have actually changed since baseline snapshot.
    
    Uses git diff if available, falls back to hash comparison.
    
    Args:
        agent_name: Name of the agent
        session_id: Session ID
        target_files: List of file paths to check (relative to project root)
    
    Returns:
        List of changed file paths
    """
    log = get_logger()
    project_dir = get_project_dir()
    baseline_file = get_baseline_file(agent_name, session_id)
    
    if not baseline_file.exists():
        log.warning(f"No baseline found for {agent_name}. Using all target files.")
        return target_files
    
    baseline = json.loads(baseline_file.read_text())
    changed = []
    
    # Try git diff first
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            git_changed = set(result.stdout.strip().split("\n")) if result.stdout.strip() else set()
            for rel_path in target_files:
                if rel_path in git_changed or rel_path in baseline:
                    changed.append(rel_path)
            log.info(f"Git diff detected {len(changed)} changed files")
            return changed
    except Exception as e:
        log.debug(f"Git diff failed: {e}. Falling back to hash comparison.")
    
    # Fallback: hash comparison
    for rel_path in target_files:
        abs_path = project_dir / rel_path
        current_hash = compute_file_hash(abs_path)
        baseline_hash = baseline.get(rel_path, "NOTFOUND")
        
        if current_hash != baseline_hash:
            changed.append(rel_path)
            log.debug(f"Change detected: {rel_path} (hash {baseline_hash[:8]}... -> {current_hash[:8]}...)")
    
    log.info(f"Hash comparison detected {len(changed)} changed files")
    return changed


def run_ruff_dry_run(files: List[str]) -> Tuple[str, int]:
    """
    Run ruff in dry-run mode (--diff) on specified files.
    
    Args:
        files: List of file paths relative to project root
    
    Returns:
        Tuple of (diff_output, file_count)
    """
    if not files:
        return "", 0
    
    log = get_logger()
    project_dir = get_project_dir()
    
    try:
        cmd = ["ruff", "check", "--diff"] + files
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        output = result.stdout + result.stderr
        # ruff check returns non-zero if issues found, which is expected in dry-run
        log.debug(f"Ruff dry-run completed with code {result.returncode}")
        return output, len(files)
    except subprocess.TimeoutExpired:
        log.error("Ruff dry-run timed out")
        return "", 0
    except Exception as e:
        log.error(f"Ruff dry-run failed: {e}")
        return "", 0


def run_ruff_fix(files: List[str]) -> Tuple[int, str]:
    """
    Run ruff with --fix on specified files.
    
    Args:
        files: List of file paths relative to project root
    
    Returns:
        Tuple of (files_modified_count, summary)
    """
    if not files:
        return 0, ""
    
    log = get_logger()
    project_dir = get_project_dir()
    
    try:
        cmd = ["ruff", "check", "--fix"] + files
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        output = result.stdout + result.stderr
        log.debug(f"Ruff fix completed with code {result.returncode}")
        
        # Parse output for file count
        fixed_count = output.count("fixed")
        return len(files), output
    except subprocess.TimeoutExpired:
        log.error("Ruff fix timed out")
        return 0, "Timeout"
    except Exception as e:
        log.error(f"Ruff fix failed: {e}")
        return 0, str(e)


async def on_agent_start(
    agent_name: str,
    session_id: str,
    target_files: Optional[List[str]] = None,
) -> None:
    """
    Hook fired when agent starts. Snapshots baseline of target files.
    
    Args:
        agent_name: Name of the agent
        session_id: Session ID
        target_files: List of file paths agent will modify (optional)
    """
    log = get_logger()
    log.info(f"on_agent_start: {agent_name} (session={session_id})")
    
    ensure_structure()
    project_dir = get_project_dir()
    session_dir = get_session_dir()
    start_time = datetime.now(timezone.utc)
    
    loop = asyncio.get_running_loop()
    
    # Timeline entry
    if session_dir:
        timeline = session_dir / "timeline.md"
        entry = f"| {start_time.strftime('%H:%M:%S')} | agent_start | **{agent_name}** | — |\n"
        await loop.run_in_executor(None, append_file, timeline, entry)
    
    # Agent active state
    state_file = project_dir / ".agent_active.json"
    payload = {
        "agent_name": agent_name,
        "started_at": start_time.isoformat(),
        "session_id": session_id,
        "target_files": target_files or [],
    }
    await loop.run_in_executor(None, state_file.write_text, json.dumps(payload, indent=2), "utf-8")
    
    # Changelog
    changelog = project_dir / "session_changes.log"
    await loop.run_in_executor(
        None,
        append_file,
        changelog,
        f"[{start_time.isoformat(timespec='seconds')}] agent_start: {agent_name}\n",
    )
    
    # Snapshot baseline if target files provided
    if target_files:
        def _snapshot():
            return snapshot_baseline(agent_name, session_id, target_files)
        
        await loop.run_in_executor(None, _snapshot)
        log.info(f"Agent {agent_name}: baseline snapshot created for {len(target_files)} files")
    
    audit({"event": "AgentStart", "agent": agent_name, "session_id": session_id, "target_files": len(target_files or [])})
    
    profile = f"Agent: {agent_name}"
    emit(hook_context(f"""🕵️ **AGENT STARTED: {agent_name}**
⏱  {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
🎯 Target files: {len(target_files or [])}

**Agent `{agent_name}` is now active.**"""))


async def on_agent_stop(
    agent_name: str,
    session_id: str,
    target_files: Optional[List[str]] = None,
    dry_run: bool = True,
) -> None:
    """
    Hook fired when agent stops. Detects changes and runs scoped ruff with optional fix.
    
    Args:
        agent_name: Name of the agent
        session_id: Session ID
        target_files: List of file paths agent was supposed to modify (optional)
        dry_run: If True, show diffs without applying fixes. Default: True
    """
    log = get_logger()
    log.info(f"on_agent_stop: {agent_name} (session={session_id}, dry_run={dry_run})")
    
    ensure_structure()
    project_dir = get_project_dir()
    session_dir = get_session_dir()
    end_time = datetime.now(timezone.utc)
    
    loop = asyncio.get_running_loop()
    
    # Timeline
    if session_dir:
        timeline = session_dir / "timeline.md"
        entry = f"| {end_time.strftime('%H:%M:%S')} | agent_end | **{agent_name}** | — |\n"
        await loop.run_in_executor(None, append_file, timeline, entry)
    
    # Changelog
    changelog = project_dir / "session_changes.log"
    await loop.run_in_executor(
        None,
        append_file,
        changelog,
        f"[{end_time.isoformat(timespec='seconds')}] agent_end: {agent_name}\n",
    )
    
    # Cleanup state
    state_file = project_dir / ".agent_active.json"
    if state_file.exists():
        await loop.run_in_executor(None, state_file.unlink)
    
    # Detect changed files if target_files provided
    changed_files = []
    if target_files:
        def _get_changed():
            return get_changed_files(agent_name, session_id, target_files)
        
        changed_files = await loop.run_in_executor(None, _get_changed)
        log.info(f"Agent {agent_name} modified {len(changed_files)} files: {changed_files}")
    
    # Run ruff on changed files
    ruff_summary = ""
    if changed_files:
        if dry_run:
            def _dry_run():
                return run_ruff_dry_run(changed_files)
            
            diff_output, file_count = await loop.run_in_executor(None, _dry_run)
            if diff_output:
                ruff_summary = f"Ruff dry-run on {file_count} files:\n{diff_output[:500]}..."
                log.info(f"Ruff dry-run output ({len(diff_output)} chars): {diff_output[:200]}...")
            else:
                ruff_summary = f"Ruff dry-run: no issues found in {file_count} files"
                log.info(ruff_summary)
        else:
            def _fix():
                return run_ruff_fix(changed_files)
            
            file_count, output = await loop.run_in_executor(None, _fix)
            ruff_summary = f"Ruff applied fixes to {file_count} files"
            log.info(ruff_summary)
            if "error" in output.lower():
                log.error(f"Ruff fix output: {output[:500]}")
    else:
        ruff_summary = "No files changed. Ruff not invoked."
        log.info(ruff_summary)
    
    audit({
        "event": "AgentEnd",
        "agent": agent_name,
        "session_id": session_id,
        "target_files": len(target_files or []),
        "changed_files": len(changed_files),
        "ruff_dry_run": dry_run,
    })
    
    emit(hook_context(f"""✅ **AGENT STOPPED: {agent_name}**
⏱  {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
📝 Modified: {len(changed_files)}/{len(target_files or [])} target files
🔧 {ruff_summary}

**Agent `{agent_name}` finished.**"""))


# CLI entry points for standalone hook invocation

async def main_start():
    """CLI entry point for on_agent_start hook."""
    data = read_stdin()
    agent_name = data.get("agent_name") or data.get("agent") or os.environ.get("CYBERSEC_AGENT_NAME") or "unknown"
    session_id = data.get("session_id") or os.environ.get("CYBERSEC_SESSION_ID") or ""
    target_files = data.get("target_files") or []
    
    await on_agent_start(agent_name, session_id, target_files)


async def main_stop():
    """CLI entry point for on_agent_stop hook."""
    data = read_stdin()
    agent_name = data.get("agent_name") or data.get("agent") or os.environ.get("CYBERSEC_AGENT_NAME") or "unknown"
    session_id = data.get("session_id") or os.environ.get("CYBERSEC_SESSION_ID") or ""
    target_files = data.get("target_files") or []
    dry_run = data.get("dry_run", True)
    
    await on_agent_stop(agent_name, session_id, target_files, dry_run)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        asyncio.run(main_stop())
    else:
        asyncio.run(main_start())
