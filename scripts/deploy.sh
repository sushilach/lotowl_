#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-$(pwd)}"

cd "$APP_DIR"

if [ ! -d .git ]; then
  echo "This deploy script must run inside the git repo."
  exit 1
fi

if [ -n "$(git status --porcelain)" ]; then
  echo "Refusing to deploy with uncommitted changes in $APP_DIR."
  git status --short
  exit 1
fi

git fetch origin "$BRANCH"
git checkout "$BRANCH"
git pull --ff-only origin "$BRANCH"
docker compose up -d --build
