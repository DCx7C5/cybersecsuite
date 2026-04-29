#!/usr/bin/env bash
# commit-msg hook — Worktree session: @@SID@@
# Enforces Conventional Commits format:
#   type(scope): description
#   where type ∈ feat|fix|legacy_docs|style|refactor|perf|test|build|ci|chore|revert
set -euo pipefail

SID="@@SID@@"
MSG_FILE="$1"

if [ ! -f "$MSG_FILE" ]; then
  echo "[WSM] commit-msg: message file not found: $MSG_FILE" >&2
  exit 1
fi

# Strip comments and blank lines for validation
MSG="$(sed '/^#/d' "$MSG_FILE" | head -1)"

PATTERN='^(feat|fix|legacy_docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .{1,100}'

if ! echo "$MSG" | grep -qE "$PATTERN"; then
  echo "" >&2
  echo "[WSM] commit-msg: message does not match Conventional Commits format" >&2
  echo "  Received : $MSG" >&2
  echo "  Expected : type(scope): description" >&2
  echo "  Types    : feat fix docs style refactor perf test build ci chore revert" >&2
  echo "  Example  : feat(auth): add JWT refresh token support" >&2
  echo "" >&2
  exit 1
fi

exit 0
