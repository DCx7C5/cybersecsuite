#!/usr/bin/env bash
# post-checkout hook — Worktree session: @@SID@@
# Args: $1=prev HEAD  $2=new HEAD  $3=branch-checkout-flag (1) or file-checkout (0)
set -euo pipefail

SID="@@SID@@"
PREV_HEAD="$1"
NEW_HEAD="$2"
IS_BRANCH_CHECKOUT="$3"

BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'detached')"
echo "[WSM] post-checkout: session=$SID branch=$BRANCH head=$NEW_HEAD" >&2

# Only log branch switches, not file-level checkouts
if [ "$IS_BRANCH_CHECKOUT" = "1" ] && [ "$PREV_HEAD" != "$NEW_HEAD" ]; then
  echo "[WSM] post-checkout: switched from $PREV_HEAD → $NEW_HEAD (branch=$BRANCH)" >&2
fi

exit 0
