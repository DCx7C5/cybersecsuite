#!/usr/bin/env bash
# pre-commit hook — Worktree session: @@SID@@
# Installed by worktree-session-manager.py.  Fires ONLY in worktree-@@SID@@.
set -euo pipefail

SID="@@SID@@"

# Guard: skip silently if we are somehow running in the wrong worktree
MARKER="$(git rev-parse --show-toplevel 2>/dev/null)/.worktree-session"
if [ -f "$MARKER" ]; then
  MARKER_SID="$(cat "$MARKER" | tr -d '[:space:]')"
  if [ "$MARKER_SID" != "$SID" ]; then
    echo "[WSM] pre-commit: SID mismatch (expected=$SID actual=$MARKER_SID) — skipping" >&2
    exit 0
  fi
fi

echo "[WSM] pre-commit: running for session=$SID" >&2

# ─── Project-specific checks ───────────────────────────────────────────────
# Uncomment / extend as needed:

# 1. Ensure no debug/TODO markers in staged Python files
# STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$' || true)
# if [ -n "$STAGED" ]; then
#   if grep -rn 'import pdb\|pdb\.set_trace\|breakpoint()' $STAGED; then
#     echo "[WSM] pre-commit: debug breakpoint found — aborting" >&2
#     exit 1
#   fi
# fi

# 2. Python syntax check on staged files
# if command -v python3 &>/dev/null; then
#   git diff --cached --name-only --diff-filter=ACM | grep '\.py$' | while read -r f; do
#     python3 -m py_compile "$f" || { echo "[WSM] Syntax error in $f" >&2; exit 1; }
#   done
# fi

exit 0
