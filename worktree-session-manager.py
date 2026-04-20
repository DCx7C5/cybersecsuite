#!/usr/bin/env python3
"""
worktree-session-manager.py — Git Worktree + Session-ID + Isolated Hooks Manager

Each agent session gets an isolated git worktree named  worktree-<sid>  where
<sid> is a 12-character lowercase hex string.  Per-worktree core.hooksPath
via extensions.worktreeConfig provides complete hook isolation.

Usage:
    worktree-session-manager.py create [--sid SID] [--branch BRANCH] [--hooks-template DIR]
    worktree-session-manager.py teardown <sid> [--force]
    worktree-session-manager.py list
    worktree-session-manager.py sid
    worktree-session-manager.py install-hooks <sid> [--template DIR]
    worktree-session-manager.py remove-hooks <sid>
"""
from __future__ import annotations

import argparse
import logging
import os
import re
import shutil
import stat
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SID_PATTERN = re.compile(r"^[0-9a-f]{12}$")
MARKER_FILE = ".worktree-session"
DEFAULT_HOOKS_TEMPLATE_DIR = Path(__file__).parent / "scripts" / "hooks"
LOG_PREFIX = "[WSM]"

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter(f"{LOG_PREFIX} %(levelname)s %(message)s"))
log = logging.getLogger("wsm")
log.addHandler(_handler)
log.setLevel(logging.INFO)


# ---------------------------------------------------------------------------
# SID helpers
# ---------------------------------------------------------------------------

def generate_sid() -> str:
    """Return a fresh 12-char lowercase hex session ID."""
    return uuid.uuid4().hex[:12]


def validate_sid(sid: str) -> None:
    """Raise ValueError if sid does not match [0-9a-f]{12}."""
    if not SID_PATTERN.match(sid):
        raise ValueError(
            f"Invalid session ID {sid!r}. Must be exactly 12 lowercase hex chars."
        )


# ---------------------------------------------------------------------------
# Git / repo helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess, log failures, and optionally raise on non-zero exit."""
    log.debug("$ %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if check and result.returncode != 0:
        log.error("Command failed: %s", " ".join(cmd))
        if result.stderr.strip():
            log.error("stderr: %s", result.stderr.strip())
        raise RuntimeError(f"Command failed (exit {result.returncode}): {' '.join(cmd)}")
    return result


def get_repo_root() -> Path:
    """Return the absolute path to the main (non-worktree) repository root."""
    result = _run(["git", "rev-parse", "--git-common-dir"])
    git_common = Path(result.stdout.strip())
    # --git-common-dir returns the path to the shared .git dir
    # For main worktree: .git  → parent is repo root
    # For linked worktree: /abs/path/to/main/.git  → parent is repo root
    if not git_common.is_absolute():
        git_common = Path.cwd() / git_common
    return git_common.parent.resolve()


def get_worktree_root(sid: str, repo_root: Optional[Path] = None) -> Path:
    """Return the expected absolute path for worktree-<sid> (sibling of repo root)."""
    if repo_root is None:
        repo_root = get_repo_root()
    return repo_root.parent / f"worktree-{sid}"


def enable_worktree_config(repo_root: Path) -> None:
    """Idempotently set extensions.worktreeConfig = true in the main repo config."""
    result = _run(
        ["git", "config", "--local", "--get", "extensions.worktreeConfig"],
        cwd=repo_root, check=False,
    )
    if result.stdout.strip().lower() == "true":
        log.debug("extensions.worktreeConfig already true")
        return
    # Retry up to 3 times to handle concurrent git config lock contention
    for attempt in range(3):
        r = _run(
            ["git", "config", "--local", "extensions.worktreeConfig", "true"],
            cwd=repo_root, check=False,
        )
        if r.returncode == 0:
            log.info("Enabled extensions.worktreeConfig = true")
            return
        # Another process may have already set it
        check = _run(
            ["git", "config", "--local", "--get", "extensions.worktreeConfig"],
            cwd=repo_root, check=False,
        )
        if check.stdout.strip().lower() == "true":
            log.debug("extensions.worktreeConfig set by concurrent process")
            return
        if attempt < 2:
            import time as _time
            _time.sleep(0.05 * (attempt + 1))
    raise RuntimeError(f"Failed to set extensions.worktreeConfig after retries: {r.stderr.strip()}")


def worktree_exists(sid: str, repo_root: Optional[Path] = None) -> bool:
    """Return True if git knows about a worktree named worktree-<sid>."""
    if repo_root is None:
        repo_root = get_repo_root()
    result = _run(["git", "worktree", "list", "--porcelain"], cwd=repo_root, check=False)
    target = f"worktree-{sid}"
    for line in result.stdout.splitlines():
        if line.startswith("worktree ") and line.endswith(target):
            return True
        if line.startswith("worktree ") and f"/{target}" in line:
            return True
    return False


def list_worktrees(repo_root: Optional[Path] = None) -> list[dict]:
    """
    Return a list of dicts describing each registered worktree.
    Keys: name, sid, path, branch, HEAD, locked.
    """
    if repo_root is None:
        repo_root = get_repo_root()
    result = _run(["git", "worktree", "list", "--porcelain"], cwd=repo_root)
    worktrees: list[dict] = []
    current: dict = {}
    for raw_line in result.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                worktrees.append(current)
            current = {}
        elif line.startswith("worktree "):
            path = line[len("worktree "):]
            name = Path(path).name
            sid_match = re.match(r"^worktree-([0-9a-f]{12})$", name)
            current = {
                "path": path,
                "name": name,
                "sid": sid_match.group(1) if sid_match else None,
                "branch": "",
                "HEAD": "",
                "locked": False,
            }
        elif line.startswith("HEAD "):
            current["HEAD"] = line[len("HEAD "):]
        elif line.startswith("branch "):
            current["branch"] = line[len("branch refs/heads/"):]
        elif line == "locked" or line.startswith("locked "):
            current["locked"] = True
        elif line == "bare":
            current["bare"] = True
    if current:
        worktrees.append(current)
    return worktrees


# ---------------------------------------------------------------------------
# Hooks helpers
# ---------------------------------------------------------------------------

def resolve_worktree_git_hooks_dir(worktree_path: Path) -> Path:
    """
    Resolve the private hooks directory for a linked worktree.

    A linked worktree's .git is a *file* containing 'gitdir: <path>'.
    We follow that pointer to the per-worktree admin dir and append /hooks.
    """
    dot_git = worktree_path / ".git"
    if dot_git.is_file():
        # Linked worktree: .git is a file with content "gitdir: <admin_dir>"
        content = dot_git.read_text().strip()
        if content.startswith("gitdir:"):
            admin_dir = Path(content[len("gitdir:"):].strip())
            if not admin_dir.is_absolute():
                admin_dir = (worktree_path / admin_dir).resolve()
            return admin_dir / "hooks"
        raise RuntimeError(f"Unexpected .git file content in {worktree_path}: {content!r}")
    elif dot_git.is_dir():
        # Main worktree
        return dot_git / "hooks"
    raise RuntimeError(f".git not found in {worktree_path}")


def install_hooks(
    sid: str,
    worktree_path: Path,
    template_dir: Optional[Path] = None,
) -> None:
    """
    Install hook templates into the worktree's private hooks directory.
    Replaces @@SID@@ with the actual sid. Sets +x on each hook.
    Aborts if any installed hook still contains @@SID@@ after substitution.
    Lints each bash hook with 'bash -n' before finalising.
    """
    if template_dir is None:
        template_dir = DEFAULT_HOOKS_TEMPLATE_DIR

    hooks_dir = resolve_worktree_git_hooks_dir(worktree_path)
    hooks_dir.mkdir(parents=True, exist_ok=True)

    templates = list(template_dir.glob("*.tpl"))
    if not templates:
        log.warning("No hook templates found in %s — skipping hook installation", template_dir)
        return

    installed: list[Path] = []
    for tpl in templates:
        hook_name = tpl.stem  # e.g. pre-commit.tpl → pre-commit
        content = tpl.read_text()
        content = content.replace("@@SID@@", sid)

        dest = hooks_dir / hook_name

        # Write atomically via tmp file
        tmp = dest.with_suffix(".tmp")
        tmp.write_text(content)

        # Lint bash scripts
        if content.startswith("#!/usr/bin/env bash") or content.startswith("#!/bin/bash"):
            lint = subprocess.run(["bash", "-n", str(tmp)], capture_output=True, text=True)
            if lint.returncode != 0:
                tmp.unlink(missing_ok=True)
                raise RuntimeError(
                    f"Hook template {tpl.name} failed bash -n lint:\n{lint.stderr}"
                )

        tmp.rename(dest)
        dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Verify no unreplaced tokens
        final = dest.read_text()
        if "@@SID@@" in final:
            dest.unlink(missing_ok=True)
            raise RuntimeError(
                f"Hook {hook_name} still contains @@SID@@ after substitution — aborting."
            )

        installed.append(dest)
        log.info("Installed %s → %s", hook_name, dest)

    log.info("Hook verification passed (%d hooks installed)", len(installed))


def remove_hooks(sid: str, worktree_path: Path) -> None:
    """Remove all hook scripts from the worktree's private hooks directory."""
    hooks_dir = resolve_worktree_git_hooks_dir(worktree_path)
    if not hooks_dir.exists():
        log.debug("No hooks dir found at %s — nothing to remove", hooks_dir)
        return
    removed = 0
    for hook in hooks_dir.iterdir():
        if hook.is_file() and not hook.name.endswith(".sample"):
            hook.unlink()
            log.info("Removed hook %s", hook.name)
            removed += 1
    log.info("Removed %d hooks from %s", removed, hooks_dir)


# ---------------------------------------------------------------------------
# Worktree config helpers
# ---------------------------------------------------------------------------

def set_hooks_path(sid: str, worktree_path: Path, repo_root: Path) -> None:
    """
    Set core.hooksPath in the worktree-specific config file so that Git
    resolves hooks from the worktree's private .git/hooks/ directory only.

    Uses --worktree flag which writes to
      <repo_root>/.git/worktrees/<name>/config.worktree
    """
    hooks_dir = resolve_worktree_git_hooks_dir(worktree_path)
    hooks_dir.mkdir(parents=True, exist_ok=True)

    _run(
        [
            "git",
            "-C", str(worktree_path),
            "config",
            "--worktree",
            "core.hooksPath",
            str(hooks_dir),
        ],
        cwd=repo_root,
    )
    log.info("Set core.hooksPath = %s", hooks_dir)


def write_marker_file(worktree_path: Path, sid: str) -> None:
    """Atomically write sid to <worktree>/.worktree-session."""
    marker = worktree_path / MARKER_FILE
    tmp = marker.with_suffix(".tmp")
    tmp.write_text(sid + "\n")
    tmp.rename(marker)
    log.info("Written marker file %s", marker)


# ---------------------------------------------------------------------------
# Main lifecycle
# ---------------------------------------------------------------------------

def create_worktree(
    sid: str,
    branch: str,
    repo_root: Optional[Path] = None,
    hooks_template_dir: Optional[Path] = None,
    new_branch: bool = True,
) -> Path:
    """
    Create and configure an isolated worktree for session <sid>.

    By default (new_branch=True) a new branch ``wt-<sid>`` is created from
    ``branch`` so the worktree gets its own isolated branch — required for
    multi-agent workflows where the base branch is already checked out.
    Pass new_branch=False to check out an existing branch directly (the branch
    must not be checked out in any other worktree).

    Idempotent: if the worktree already exists, returns its path immediately.
    """
    validate_sid(sid)
    if repo_root is None:
        repo_root = get_repo_root()

    enable_worktree_config(repo_root)

    worktree_path = get_worktree_root(sid, repo_root)

    if worktree_exists(sid, repo_root):
        log.info("Worktree worktree-%s already exists at %s — skipping create", sid, worktree_path)
        return worktree_path

    if new_branch:
        session_branch = f"wt-{sid}"
        log.info("Creating worktree worktree-%s on new branch %s from %s", sid, session_branch, branch)
        cmd = [
            "git", "worktree", "add",
            "--lock",
            f"--reason=session-{sid}",
            "-b", session_branch,
            str(worktree_path),
            branch,
        ]
    else:
        log.info("Creating worktree worktree-%s on existing branch %s", sid, branch)
        cmd = [
            "git", "worktree", "add",
            "--lock",
            f"--reason=session-{sid}",
            str(worktree_path),
            branch,
        ]

    _run(cmd, cwd=repo_root)
    log.info("Worktree created at %s", worktree_path)

    write_marker_file(worktree_path, sid)
    set_hooks_path(sid, worktree_path, repo_root)
    install_hooks(sid, worktree_path, hooks_template_dir)

    return worktree_path


def teardown_worktree(
    sid: str,
    repo_root: Optional[Path] = None,
    force: bool = False,
    delete_branch: bool = True,
) -> None:
    """
    Idempotent teardown: unlock, remove worktree, prune, optionally delete session branch.

    delete_branch=True (default) also deletes the ``wt-<sid>`` branch if it exists.
    """
    validate_sid(sid)
    if repo_root is None:
        repo_root = get_repo_root()

    worktree_name = f"worktree-{sid}"
    worktree_path = get_worktree_root(sid, repo_root)

    if not worktree_exists(sid, repo_root):
        log.info("Worktree %s not found — pruning and exiting", worktree_name)
        _run(["git", "worktree", "prune"], cwd=repo_root)
        return

    # Unlock (may already be unlocked — ignore error)
    unlock = _run(
        ["git", "worktree", "unlock", str(worktree_path)],
        cwd=repo_root, check=False,
    )
    if unlock.returncode != 0:
        log.debug("Unlock returned %d (may already be unlocked): %s", unlock.returncode, unlock.stderr.strip())

    # Remove our marker file before worktree remove (prevents "untracked files" error)
    marker = worktree_path / MARKER_FILE
    if marker.exists():
        marker.unlink()
        log.debug("Removed marker file before worktree remove")

    # Remove
    remove_cmd = ["git", "worktree", "remove"]
    if force:
        remove_cmd.append("--force")
    remove_cmd.append(str(worktree_path))
    _run(remove_cmd, cwd=repo_root)
    log.info("Removed worktree %s", worktree_name)

    # Prune
    _run(["git", "worktree", "prune"], cwd=repo_root)
    log.info("Pruned stale worktree entries")

    # Delete the session branch wt-<sid> if it exists
    if delete_branch:
        session_branch = f"wt-{sid}"
        branch_check = _run(
            ["git", "branch", "--list", session_branch],
            cwd=repo_root, check=False,
        )
        if session_branch in branch_check.stdout:
            _run(["git", "branch", "-D", session_branch], cwd=repo_root, check=False)
            log.info("Deleted session branch %s", session_branch)

    # Clean up any stale marker file in the directory if --force left it
    stale_marker = worktree_path / MARKER_FILE
    if stale_marker.exists():
        stale_marker.unlink()
        log.debug("Removed stale marker file %s", stale_marker)


def get_current_worktree_sid(cwd: Optional[Path] = None) -> Optional[str]:
    """
    Read .worktree-session from cwd (default: current directory).
    Returns the SID string or None if not in a managed worktree.
    Safe to call from hook scripts for conditional execution.
    """
    if cwd is None:
        # Try git work-tree first (accurate inside hooks)
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True,
        )
        cwd = Path(result.stdout.strip()) if result.returncode == 0 else Path.cwd()

    marker = cwd / MARKER_FILE
    if not marker.exists():
        return None
    sid = marker.read_text().strip()
    if SID_PATTERN.match(sid):
        return sid
    return None


# ---------------------------------------------------------------------------
# CLI command handlers
# ---------------------------------------------------------------------------

def cmd_create(args: argparse.Namespace) -> int:
    sid = args.sid if args.sid else generate_sid()
    try:
        validate_sid(sid)
    except ValueError as exc:
        log.error("%s", exc)
        return 1

    template_dir = Path(args.hooks_template) if args.hooks_template else None

    try:
        repo_root = get_repo_root()
        path = create_worktree(
            sid, args.branch, repo_root, template_dir,
            new_branch=not args.no_new_branch,
        )
        print(sid)  # stdout only: consumed by shell aliases via $()
        log.info("Worktree ready at %s", path)
        return 0
    except Exception as exc:
        log.error("%s", exc)
        return 1


def cmd_teardown(args: argparse.Namespace) -> int:
    try:
        teardown_worktree(args.sid, force=args.force)
        return 0
    except Exception as exc:
        log.error("%s", exc)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    try:
        worktrees = list_worktrees()
    except Exception as exc:
        log.error("%s", exc)
        return 1

    fmt = "{:<14}  {:<28}  {:<6}  {}"
    print(fmt.format("SID", "BRANCH", "LOCKED", "PATH"))
    print("-" * 80)
    for wt in worktrees:
        sid = wt.get("sid") or "(main)"
        branch = wt.get("branch") or "(detached)"
        locked = "yes" if wt.get("locked") else "no"
        print(fmt.format(sid, branch[:28], locked, wt.get("path", "")))
    return 0


def cmd_sid(args: argparse.Namespace) -> int:
    sid = get_current_worktree_sid()
    if sid:
        print(sid)
        return 0
    log.error("Not inside a managed worktree (no %s found)", MARKER_FILE)
    return 1


def cmd_install_hooks(args: argparse.Namespace) -> int:
    try:
        validate_sid(args.sid)
        repo_root = get_repo_root()
        worktree_path = get_worktree_root(args.sid, repo_root)
        if not worktree_path.exists():
            log.error("Worktree directory not found: %s", worktree_path)
            return 1
        template_dir = Path(args.template) if args.template else None
        remove_hooks(args.sid, worktree_path)
        install_hooks(args.sid, worktree_path, template_dir)
        return 0
    except Exception as exc:
        log.error("%s", exc)
        return 1


def cmd_remove_hooks(args: argparse.Namespace) -> int:
    try:
        validate_sid(args.sid)
        repo_root = get_repo_root()
        worktree_path = get_worktree_root(args.sid, repo_root)
        if not worktree_path.exists():
            log.error("Worktree directory not found: %s", worktree_path)
            return 1
        remove_hooks(args.sid, worktree_path)
        return 0
    except Exception as exc:
        log.error("%s", exc)
        return 1


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="worktree-session-manager.py",
        description="Git worktree + session-ID + isolated hooks manager",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable debug logging")
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="Create a new isolated worktree session")
    p_create.add_argument("--sid", default=None, help="12-char hex session ID (auto-generated if omitted)")
    p_create.add_argument("--branch", default="HEAD", help="Branch or commit to base the session on (default: HEAD)")
    p_create.add_argument("--no-new-branch", action="store_true",
                          help="Check out the branch directly instead of creating a new wt-<sid> branch")
    p_create.add_argument("--hooks-template", default=None, metavar="DIR",
                          help="Directory containing *.tpl hook templates")
    p_create.set_defaults(func=cmd_create)

    # teardown
    p_td = sub.add_parser("teardown", help="Remove a worktree session")
    p_td.add_argument("sid", help="12-char hex session ID")
    p_td.add_argument("--force", action="store_true", help="Remove even if there are uncommitted changes")
    p_td.set_defaults(func=cmd_teardown)

    # list
    p_list = sub.add_parser("list", help="List all registered worktrees")
    p_list.set_defaults(func=cmd_list)

    # sid
    p_sid = sub.add_parser("sid", help="Print the session ID of the current directory")
    p_sid.set_defaults(func=cmd_sid)

    # install-hooks
    p_ih = sub.add_parser("install-hooks", help="(Re-)install hooks for a session")
    p_ih.add_argument("sid", help="12-char hex session ID")
    p_ih.add_argument("--template", default=None, metavar="DIR",
                      help="Hook template directory (default: ./scripts/hooks/)")
    p_ih.set_defaults(func=cmd_install_hooks)

    # remove-hooks
    p_rh = sub.add_parser("remove-hooks", help="Remove all hooks for a session")
    p_rh.add_argument("sid", help="12-char hex session ID")
    p_rh.set_defaults(func=cmd_remove_hooks)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
