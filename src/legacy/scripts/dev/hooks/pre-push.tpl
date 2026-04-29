#!/usr/bin/env bash
# pre-push hook — Worktree session: @@SID@@
# Stdin: "<local-ref> <local-sha> <remote-ref> <remote-sha>" per line
set -euo pipefail

SID="@@SID@@"

MARKER="$(git rev-parse --show-toplevel 2>/dev/null)/.worktree-session"
if [ -f "$MARKER" ]; then
  MARKER_SID="$(cat "$MARKER" | tr -d '[:space:]')"
  if [ "$MARKER_SID" != "$SID" ]; then
    exit 0
  fi
fi

REMOTE="$1"
URL="$2"
echo "[WSM] pre-push: session=$SID remote=$REMOTE url=$URL" >&2

# Skip hooks when pushing from CI (set SKIP_HOOKS=1 in CI env)
if [ "${SKIP_HOOKS:-0}" = "1" ]; then
  echo "[WSM] pre-push: SKIP_HOOKS=1 — bypassing checks" >&2
  exit 0
fi

# ─── Pre-push checks ───────────────────────────────────────────────────────
# Uncomment to run your test suite before any push:
# echo "[WSM] pre-push: running tests..." >&2
# if ! python3 -m pytest --tb=short -q; then
#   echo "[WSM] pre-push: tests failed — push aborted" >&2
#   exit 1
# fi

exit 0
