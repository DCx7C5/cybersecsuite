#!/usr/bin/env bash
# post-merge hook — Worktree session: @@SID@@
# $1 = 1 if squash merge, 0 for normal merge
set -euo pipefail

SID="@@SID@@"

MARKER="$(git rev-parse --show-toplevel 2>/dev/null)/.worktree-session"
if [ -f "$MARKER" ]; then
  MARKER_SID="$(cat "$MARKER" | tr -d '[:space:]')"
  if [ "$MARKER_SID" != "$SID" ]; then
    exit 0
  fi
fi

IS_SQUASH="${1:-0}"
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'detached')"
echo "[WSM] post-merge: session=$SID branch=$BRANCH squash=$IS_SQUASH" >&2

# ─── Post-merge tasks ──────────────────────────────────────────────────────
# e.g. reinstall dependencies if lockfile changed:
# if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q 'uv.lock\|requirements'; then
#   echo "[WSM] post-merge: lockfile changed — running uv sync" >&2
#   uv sync --quiet
# fi

exit 0
