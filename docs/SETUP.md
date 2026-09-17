# Setup Guide

## Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) for dependency management (the project
  uses `[tool.uv]` and ships a `uv.lock`)
- `git` (used for brownfield/greenfield detection and by generated
  permissions); optional: `claude` on `PATH` for `agentic_init enrich`,
  `npx` for the optional BMAD module

## Install for development

```sh
git clone https://github.com/eemaldi/agentic_init.git
cd agentic_init
uv sync                       # installs the package + dev deps (pytest, ruff) into .venv
uv run agentic_init version   # 0.1.0 — confirms the CLI entry point resolves
```

`uv sync` was run against this exact repository as part of writing this
guide; it completed cleanly and `agentic_init version` printed `0.1.0`.

## Install as a tool (what end users do)

```sh
uvx agentic_init init        # run once, ephemeral — no venv to manage
# or
pip install agentic_init && agentic_init init
```

`agentic_init` is registered as a console script
(`[project.scripts] agentic_init = "agentic_init.cli:app"` in
`pyproject.toml`), so once installed the `agentic_init` command is on `PATH`.

## Bootstrapping a project

From inside the target repository:

```sh
agentic_init init            # detect the repo, ask a few questions, write agentic_init.yaml, apply it
agentic_init init --yes      # skip the questions, accept detected defaults (wizard.defaults())
agentic_init init --dry-run  # ask the questions but don't write anything
```

`init` refuses to run if `agentic_init.yaml` already exists — it asks
"Reconfigure?" interactively, or exits with an error under `--yes` (verified:
`init --yes` against a directory with an existing `agentic_init.yaml` exits 1
with `agentic_init.yaml exists; run \`agentic_init apply\`, or delete it to
start over.`). Re-running the whole setup after the config already exists is
`agentic_init apply`.

Detection (`agentic_init/detect/`) looks for:

- **Stack**: language/package-manager markers (`pyproject.toml`,
  `package.json`, `Cargo.toml`, `go.mod`, …), lockfiles, and framework hints
  in dependency manifests.
- **Commands**: `Makefile`/`justfile` targets, `package.json` scripts, and
  per-language conventions (pytest/ruff/mypy for Python, cargo for Rust, go
  for Go, …) — matched against a fixed set of task names (install, dev,
  build, test, lint, format, typecheck, e2e).
- **Git history / mode**: ≥20 commits or ≥30 source files ⇒ suggests
  `brownfield`, else `greenfield`; project size (`level`) is suggested from
  source file count (<50 files ⇒ L1, else L2).

Everything detection finds is editable in the wizard (or via
`agentic_init.yaml` afterwards) — it's a starting point, not a hard rule.

## What gets written

Running `init`/`apply` in a project writes (paths vary with your
level/mode/module selection — see `docs/CONFIGURATION.md` and
`docs/CATALOG.md`):

```
agentic_init.yaml            your configuration (source of truth for regeneration)
.agentic_init.lock           ownership tracking — do not hand-edit
CLAUDE.md                    generated instruction sections (partially yours — see below)
.claude/settings.json        permissions, hooks, sandbox (merged JSON — partially yours)
.claude/skills/*/SKILL.md
.claude/agents/*.md
.claude/rules/*.md
.claude/hooks/*.py
.mcp.json                    MCP server config (merged JSON)
.gitignore                   adds .claude/settings.local.json, .claude/state/ (merged block)
docs/**                      seed docs at L2+ (architecture, decisions, stories, operations, …)
```

`CLAUDE.md`, `.claude/settings.json`, `.mcp.json` and `.gitignore` accept
your own edits alongside the generated content (see "write strategies" in
`docs/ARCHITECTURE.md`); everything under `.claude/skills`, `.claude/agents`,
`.claude/rules`, `.claude/hooks` is fully owned by agentic_init — edit
`agentic_init.yaml` instead, or accept that a hand-edit will be skipped (and
flagged by `doctor`) until you run `apply --force`.

**Verified**: all of the above was exercised against a scratch Python project
(uv + pytest + ruff) — `init --yes` produced exactly this file set;
`agentic_init diff` immediately after reported "Everything is up to date."
(idempotent); editing a generated agent file by hand made `doctor` report
`! .claude/agents/reviewer.md modified locally` and `apply` (without
`--force`) print `skip … modified locally`; `apply --force` then restored it.

## Registering the GitHub MCP server

The `github` MCP server (included by default at L1+) needs a token in your
environment — `init`/`apply` print this as a "Next" step, and `doctor` warns
if it's missing:

```sh
export GITHUB_PERSONAL_ACCESS_TOKEN=ghp_...
```

## Everyday commands

```sh
agentic_init apply          # regenerate after editing agentic_init.yaml (safe to re-run — see ARCHITECTURE.md)
agentic_init diff           # preview pending changes as a unified diff, without writing
agentic_init doctor         # check the current setup against best practices; exit 1 if any ERROR
agentic_init enrich         # run `claude -p /agentic_init-enrich` to fill generated docs with real project knowledge
agentic_init catalog        # list every skill/agent/hook/rule/mcp/docs component with its description
agentic_init schema         # print agentic_init.yaml's JSON Schema (pydantic model_json_schema())
```

Full flag-by-flag reference: `docs/CLI.md`.

## Running the test suite (agentic_init's own)

```sh
uv run pytest          # 86 tests, ~5s
uv run ruff check .    # lint
uv run ruff format .   # format
```

Both were run against this repository while writing this documentation:
`uv run pytest` → `86 passed`, `uv run ruff check .` → `All checks passed!`.

Golden-file (snapshot) tests live in `tests/test_snapshots.py` /
`tests/snapshots/`; regenerate them with `scripts/snapshot-update.sh` after
changing what the catalog renders (see `docs/EXTENDING.md`).
