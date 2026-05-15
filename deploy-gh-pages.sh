#!/bin/sh
set -eu

BUILD_DIR="build"
BRANCH="${GH_PAGES_BRANCH:-gh-pages}"
REPO_URL=$(git config --get remote.origin.url || true)

if [ -z "$REPO_URL" ]; then
  echo "No remote origin URL found. Please set remote origin." >&2
  exit 1
fi

if [ ! -d "$BUILD_DIR" ]; then
  echo "Build directory '$BUILD_DIR' not found. Run 'make freeze' first." >&2
  exit 1
fi

cd "$BUILD_DIR"

# Initialize a git repo in the build dir and push to the gh-pages branch
# This will overwrite the remote branch with the current build contents.
if [ -d .git ]; then
  # reuse existing repo
  git reset --hard
else
  git init >/dev/null
fi

# Make sure user config exists for committing
GIT_NAME=$(git config user.name || true)
GIT_EMAIL=$(git config user.email || true)
if [ -z "$GIT_NAME" ]; then
  git config user.name "GitHub Actions"
fi
if [ -z "$GIT_EMAIL" ]; then
  git config user.email "actions@github.com"
fi

# Create or switch to branch
if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  git checkout "$BRANCH" >/dev/null 2>&1 || git checkout -b "$BRANCH"
else
  git checkout -b "$BRANCH"
fi

# Add all files and commit (if any changes)
git add --all

if git diff --cached --quiet; then
  echo "No changes to deploy. Skipping commit."
else
  git commit -m "chore(deploy): publish site $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
fi

# Push to remote
# Use the remote URL rather than 'origin' to avoid requiring remotes in this repo
REMOTE="$REPO_URL"

echo "Pushing to $REMOTE $BRANCH"
git push --force "$REMOTE" "$BRANCH"

echo "Deployed to branch '$BRANCH'"
