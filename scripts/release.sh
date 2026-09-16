#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
uv run ruff check .
uv run pytest -q
rm -rf dist
uv build
wheel="$(realpath dist/*.whl)"
unzip -l "$wheel" | grep -q "agentinit/catalog/skills/" || { echo "catalog missing from wheel" >&2; exit 1; }
smoke="$(mktemp -d)"
(cd "$smoke" && uvx --isolated --from "$wheel" agentic-init --help >/dev/null && uvx --isolated --from "$wheel" agentic-init init --help >/dev/null)
rm -rf "$smoke"
[ "${1:-}" = "--dry-run" ] && { echo "dry run: skipping publish"; exit 0; }
uv publish "$@"
