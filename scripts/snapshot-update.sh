#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
UPDATE_SNAPSHOTS=1 uv run pytest tests/test_snapshots.py -q
git diff --stat -- tests/snapshots 2>/dev/null || true
