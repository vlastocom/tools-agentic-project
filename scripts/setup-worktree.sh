#!/usr/bin/env bash
# setup-worktree.sh — bootstrap a freshly-created git worktree with the
# local-only state it needs to build, test, or run the project.
#
# Run from inside the worktree. Idempotent. No-op when invoked from the
# main worktree itself.
#
# This is the project-agnostic template. **Tailor the link_if_missing
# and link_file_if_missing calls below to the items your project
# actually keeps gitignored** — a backend-only project drops
# node_modules, a non-Gradle project drops gradle.properties.local, etc.
#
# See the SDLC workflow guide §8.5 for the full pattern, including the
# orchestrator's first-action contract and the dep-manifest concurrency
# rule.

set -euo pipefail

WORKTREE="$(pwd)"
# `git worktree list --porcelain | awk '... exit'` (or `| head -n 1`)
# triggers SIGPIPE (141) on git under `set -o pipefail` because the
# consumer closes the pipe after the first match. Capture into a
# variable first, then extract the first match in pure bash to avoid
# the pipe entirely.
WORKTREE_LIST="$(git worktree list --porcelain)"
MAIN="$(awk '/^worktree / { print $2; exit }' <<<"$WORKTREE_LIST")"

if [[ "$WORKTREE" == "$MAIN" ]]; then
    echo "in main worktree; nothing to bootstrap"
    exit 0
fi

# link_if_missing — for top-level paths (directories OR files) that the
# worktree does not own at all because they are entirely gitignored
# (e.g. node_modules/, .env, options.txt).
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

# link_file_if_missing — for files that live inside a directory the
# worktree already owns via tracked content (e.g. .secrets/README.md is
# tracked, but .secrets/db-*.txt are gitignored data that needs to come
# from main). `link_if_missing` cannot link the parent dir because it
# already exists in the worktree, so each gitignored sibling has to be
# linked individually.
link_file_if_missing() {
    local rel="$1"
    if [[ ! -f "$MAIN/$rel" ]]; then
        return 0
    fi
    if [[ -L "$WORKTREE/$rel" || -e "$WORKTREE/$rel" ]]; then
        return 0
    fi
    mkdir -p "$(dirname "$WORKTREE/$rel")"
    ln -s "$MAIN/$rel" "$WORKTREE/$rel"
    echo "linked: $rel"
}

# ----- adjust this list to your project's actual gitignored state -----

# .secrets/ — directory exists in the worktree (tracked README +
# .example placeholders), but the actual secret data files are
# gitignored. Link each one individually from main so the worktree has
# working credentials without the main worktree leaking actual values
# into the repo.
link_file_if_missing .secrets/db-api.txt
link_file_if_missing .secrets/db-creator.txt
link_file_if_missing .secrets/db-root.txt

link_if_missing .env
link_if_missing options.txt
link_if_missing gradle.properties.local
link_if_missing node_modules

# ---------------------------------------------------------------------

# Verify the minimum: a load-bearing secret must be reachable for any
# test or build that needs DB credentials, API keys, etc. We probe a
# specific file rather than just the directory so a malformed / empty
# secrets/ tree is caught at bootstrap time.
if [[ ! -e "$WORKTREE/.secrets/db-api.txt" ]]; then
    echo "BOOTSTRAP FAIL: .secrets/db-api.txt not present (main worktree missing it?)" >&2
    exit 1
fi

echo "worktree ready: $WORKTREE"
