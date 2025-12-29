#!/bin/bash

set -euo pipefail

print_status() {
    echo -e "\033[0;34m➡\033[0m $1"
}

print_success() {
    echo -e "\033[0;32m✔\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m⚠\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m✖\033[0m $1"
}

DEFAULT_PYTHON="python3"
if [[ -x ".venv/bin/python" ]]; then
    DEFAULT_PYTHON=".venv/bin/python"
fi
PYTHON_BIN=${PYTHON_BIN:-$DEFAULT_PYTHON}

load_env_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        print_warning "Environment file ${file} not found. Continuing with current shell variables."
        return
    fi
    print_status "Loading environment from ${file}"
    eval "$(
${PYTHON_BIN} - "$file" <<'PY'
import shlex
import sys
from dotenv import dotenv_values

path = sys.argv[1]
for key, value in (dotenv_values(path) or {}).items():
    if value is None:
        continue
    print(f'export {key}={shlex.quote(value)}')
PY
)"
}

ENV_FILE="${ENV_FILE:-.env}"
GH_BRANCH="${GITHUB_PAGES_BRANCH:-gh-pages}"

load_env_file "$ENV_FILE"

print_status "Generating static site with freeze.py…"
${PYTHON_BIN} freeze.py
print_success "Static site generated into ./build"

WORKTREE_DIR=$(mktemp -d)
CLEANUP() {
    if git worktree list | grep -q "$WORKTREE_DIR"; then
        git worktree remove "$WORKTREE_DIR"
    fi
    rm -rf "$WORKTREE_DIR"
}
trap CLEANUP EXIT

if git show-ref --verify --quiet "refs/heads/${GH_BRANCH}"; then
    git fetch origin "${GH_BRANCH}" || true
    git worktree add "$WORKTREE_DIR" "${GH_BRANCH}"
else
    print_warning "Branch ${GH_BRANCH} not found locally. Initializing from origin (if present)."
    if git ls-remote --exit-code --heads origin "${GH_BRANCH}" >/dev/null 2>&1; then
        git fetch origin "${GH_BRANCH}"
        git worktree add "$WORKTREE_DIR" "${GH_BRANCH}"
    else
        print_status "Creating new orphan branch ${GH_BRANCH}."
        git worktree add "$WORKTREE_DIR" --detach
        (
            cd "$WORKTREE_DIR"
            git checkout --orphan "${GH_BRANCH}"
            git reset --hard
        )
    fi
fi

print_status "Syncing build/ into ${GH_BRANCH} worktree…"
rsync -a --delete --exclude '.git' build/ "${WORKTREE_DIR}/"

pushd "$WORKTREE_DIR" >/dev/null
if git status --porcelain | grep -q .; then
    git add --all
    COMMIT_MSG=${GITHUB_PAGES_MESSAGE:-"deploy: update GitHub Pages"}
    git commit -m "$COMMIT_MSG"
    print_success "Committed Pages update."
    git push origin "${GH_BRANCH}"
    print_success "Pushed to origin/${GH_BRANCH}."
else
    print_warning "No changes detected for GitHub Pages; skipping commit."
fi
popd >/dev/null

print_success "GitHub Pages deployment complete."
