#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
AGENTIC_DIR="${REPO_ROOT}/agentic"
CLAUDE_DIR="${REPO_ROOT}/.claude"

for target in "${AGENTIC_DIR}"/*/; do
    name="$(basename "${target}")"
    link="${CLAUDE_DIR}/${name}"
    ln -sfn "../agentic/${name}" "${link}"
    git -C "${REPO_ROOT}" add -f "${link}"
done
