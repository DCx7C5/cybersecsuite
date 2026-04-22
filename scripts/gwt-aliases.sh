#!/usr/bin/env bash
# gwt-aliases.sh — Git Worktree Session Manager shell aliases
#
# Source this file in your ~/.bashrc or ~/.zshrc:
#   source /path/to/repo/scripts/gwt-aliases.sh
#
# The aliases export GWT_SID after creation and auto-detect the repo root.

# ─── Resolve manager script ────────────────────────────────────────────────
_gwt_manager() {
  local root
  root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "[gwt] ERROR: Not inside a git repository" >&2
    return 1
  }
  echo "$root/scripts/worktree-session-manager.py"
}

# ─── gwt-create [branch] ───────────────────────────────────────────────────
# Create a new worktree session. Exports GWT_SID on success.
# Optionally accepts a --sid flag to specify an exact session ID.
gwt-create() {
  local branch="HEAD"
  local extra_args=()
  local sid

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --sid) extra_args+=(--sid "$2"); shift 2 ;;
      --with-llm) extra_args+=(--with-llm); shift ;;
      *)     branch="$1"; shift ;;
    esac
  done

  local manager
  manager="$(_gwt_manager)" || return 1

  sid="$(python3 "$manager" create --branch "$branch" "${extra_args[@]}")" || return 1
  export GWT_SID="$sid"
  echo "[gwt] ✓ Created worktree-$sid  branch=$branch"
  echo "[gwt]   cd $(git rev-parse --show-toplevel 2>/dev/null)/../worktree-$sid"
}

# ─── gwt-teardown [sid] ────────────────────────────────────────────────────
# Remove a worktree session. Uses GWT_SID if no argument given.
gwt-teardown() {
  local sid=""
  local extra_args=()

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --force|--with-llm) extra_args+=("$1"); shift ;;
      *)
        if [ -z "$sid" ]; then
          sid="$1"
          shift
        else
          echo "[gwt] ERROR: Unexpected argument: $1" >&2
          return 1
        fi
        ;;
    esac
  done

  sid="${sid:-${GWT_SID:-}}"

  if [ -z "$sid" ]; then
    echo "[gwt] ERROR: No session ID. Pass one or set GWT_SID." >&2
    return 1
  fi

  local manager
  manager="$(_gwt_manager)" || return 1

  python3 "$manager" teardown "$sid" "${extra_args[@]}" || return 1

  if [ "${GWT_SID:-}" = "$sid" ]; then
    unset GWT_SID
    echo "[gwt] GWT_SID unset"
  fi
}

# ─── gwt-sid ───────────────────────────────────────────────────────────────
# Print the session ID for the current directory.
gwt-sid() {
  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" sid
}

# ─── gwt-list ──────────────────────────────────────────────────────────────
# List all registered worktrees.
gwt-list() {
  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" list
}

# ─── gwt-hooks-install [sid] ───────────────────────────────────────────────
# (Re-)install hooks for a session. Uses GWT_SID if no argument given.
gwt-hooks-install() {
  local sid="${1:-${GWT_SID:-}}"
  if [ -z "$sid" ]; then
    echo "[gwt] ERROR: No session ID. Pass one or set GWT_SID." >&2
    return 1
  fi

  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" install-hooks "$sid"
}

# ─── gwt-hooks-remove [sid] ────────────────────────────────────────────────
# Remove all hooks for a session.
gwt-hooks-remove() {
  local sid="${1:-${GWT_SID:-}}"
  if [ -z "$sid" ]; then
    echo "[gwt] ERROR: No session ID. Pass one or set GWT_SID." >&2
    return 1
  fi

  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" remove-hooks "$sid"
}

# ─── gwt-llm-open [sid] ────────────────────────────────────────────────────
gwt-llm-open() {
  local sid="${1:-${GWT_SID:-}}"
  if [ -z "$sid" ]; then
    echo "[gwt] ERROR: No session ID. Pass one or set GWT_SID." >&2
    return 1
  fi
  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" llm-session-open "$sid"
}

# ─── gwt-llm-close [sid] ───────────────────────────────────────────────────
gwt-llm-close() {
  local sid="${1:-${GWT_SID:-}}"
  if [ -z "$sid" ]; then
    echo "[gwt] ERROR: No session ID. Pass one or set GWT_SID." >&2
    return 1
  fi
  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" llm-session-close "$sid"
}

# ─── gwt-llm-cost [sid] ────────────────────────────────────────────────────
gwt-llm-cost() {
  local sid="${1:-${GWT_SID:-}}"
  if [ -z "$sid" ]; then
    echo "[gwt] ERROR: No session ID. Pass one or set GWT_SID." >&2
    return 1
  fi
  local manager
  manager="$(_gwt_manager)" || return 1
  python3 "$manager" llm-cost "$sid"
}

# ─── Auto-detect SID on directory change (opt-in) ──────────────────────────
# Uncomment the appropriate block for your shell to auto-export GWT_SID
# whenever you cd into a managed worktree.

# zsh:
# autoload -Uz add-zsh-hook
# _gwt_chpwd() {
#   local marker=".worktree-session"
#   if [ -f "$marker" ]; then
#     export GWT_SID="$(cat "$marker" | tr -d '[:space:]')"
#     echo "[gwt] Session: $GWT_SID"
#   elif [ -n "${GWT_SID:-}" ]; then
#     unset GWT_SID
#   fi
# }
# add-zsh-hook chpwd _gwt_chpwd

# bash:
# PROMPT_COMMAND='
#   if [ -f ".worktree-session" ]; then
#     export GWT_SID="$(cat .worktree-session | tr -d "[:space:]")"
#   fi
# '

echo "[gwt] aliases loaded: gwt-create gwt-teardown gwt-sid gwt-list gwt-hooks-install gwt-hooks-remove gwt-llm-open gwt-llm-close gwt-llm-cost"
