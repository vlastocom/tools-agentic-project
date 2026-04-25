#!/usr/bin/env bash
# setup-worktree.sh — bootstrap a freshly-created git worktree with the
# local-only state it needs to build, test, or run the project.
#
# Run from inside the worktree. Idempotent. No-op when invoked from the
# main worktree itself.
#
# This is the project-agnostic template. **Tailor the link_if_missing
# calls below to the items your project actually keeps gitignored** —
# a backend-only project drops node_modules, a non-Gradle project drops
# gradle.properties.local, etc.
#
# See the SDLC workflow guide §8.5 for the full pattern, including the
# orchestrator's first-action contract and the dep-manifest concurrency
# rule.

set -euo pipefail

WORKTREE="$(pwd)"
MAIN="$(git worktree list --porcelain | awk '/^worktree / { print $2; exit }')"

if [[ "$WORKTREE" == "$MAIN" ]]; then
    echo "in main worktree; nothing to bootstrap"
    exit 0
fi

link_if_missing() {
    local rel="$1"
    if [[ ! -e "$MAIN/$rel" ]]; then
        return 0  # main doesn't have it — nothing to link
    fi
    if [[ -L "$WORKTREE/$rel" || -e "$WORKTREE/$rel" ]]; then
        return 0  # already present in this worktree (idempotent)
    fi
    ln -s "$MAIN/$rel" "$WORKTREE/$rel"
    echo "linked: $rel"
}

# ----- adjust this list to your project's actual gitignored state -----

link_if_missing .secrets
link_if_missing .env
link_if_missing options.txt
link_if_missing gradle.properties.local
link_if_missing node_modules

# ---------------------------------------------------------------------

# Verify the minimum: secrets must be reachable for any test or build
# that needs DB credentials, API keys, etc.
if [[ ! -e "$WORKTREE/.secrets" ]]; then
    echo "BOOTSTRAP FAIL: .secrets/ not present and main worktree has no copy" >&2
    exit 1
fi

echo "worktree ready: $WORKTREE"
