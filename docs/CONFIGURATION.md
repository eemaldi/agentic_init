# Configuration Reference (`agentic_init.yaml`)

The full schema is always available from the code itself:
`agentic_init schema` (or `Config.model_json_schema()` in `config.py`). This
is a human-readable walkthrough of the same model; all field names, types
and defaults below were read directly from `Config` in `config.py` and
double-checked against `agentic_init schema` output.

`Config` uses `extra="forbid"` — an unknown top-level key, or an unknown key
under `commands`/`include`/`exclude`/`modules`, fails validation with a
clear pydantic error (`load_config` wraps `ValidationError` into
`ConfigError`, printed and exit 1 by the CLI).

## Fields

```yaml
version: 1                    # literal 1 — the only supported schema version today

project:
  name: my-project            # required
  description: ""             # optional one-liner, used in generated CLAUDE.md

level: 1                      # 0-4, required — see "Levels" below
mode: greenfield               # "greenfield" | "brownfield", required
autonomy: null                 # 0-5, optional — omit to use default_autonomy(level, mode)

targets: [claude-code]         # which targets/*.py to render for; only "claude-code" exists today

modules:
  aidlc: false                  # evidence-gated delivery: adds evidence-gate skill + verify-completion hook + evidence docs
  bmad: false                   # BMAD planning workflow, installed separately via `npx bmad-method@latest install`

include:                        # add components beyond the level/mode preset, per kind
  skills: []
  agents: []
  hooks: []
  rules: []
  mcp: []
  docs: []

exclude:                        # remove components the preset would otherwise include, per kind
  skills: []
  agents: []
  hooks: []
  rules: []
  mcp: []
  docs: []

commands:                       # override/disable detected commands; set a value to null to disable it
  install: null
  dev: null
  build: null
  test: null
  test_one: null
  lint: null
  format: null
  typecheck: null
  e2e: null

enrich: false                   # generate the agentic_init-enrich skill (`agentic_init enrich` then runs it)
```

`save_config` (`config.py`) omits empty/default sections when writing —
that's why a freshly generated `agentic_init.yaml` is short (see this
repo's own `agentic_init.yaml`, which only sets `project`, `level`, `mode`,
`targets`, and a small `include`).

## Levels (`level`, 0–4)

| Level | Meaning | Default autonomy (greenfield) |
|---|---|---|
| 0 | Tiny script / one-off | A4 |
| 1 | Small application | A3 |
| 2 | Production application | A3 |
| 3 | Large system / monorepo | A3 |
| 4 | Enterprise / regulated | A2 |

Each level *adds* to the catalog selection cumulatively (`presets.py`,
`_CUMULATIVE`) — L2 includes everything L1 does, plus more:

- **L1**: skills `implement`, `test`, `review`; agent `reviewer`; hooks
  `block-dangerous-commands`, `protect-secrets`; MCP `github`.
- **L2** (+L1): skills `debug`, `spec`, `security-review`; agents
  `test-engineer`, `security-reviewer`; hook `post-edit-format`; rules
  `architecture`, `testing`, `security`; docs `architecture`, `decisions`,
  `stories`, `operations`.
- **L3** (+L2): skills `discover`, `release`; agents `explorer`,
  `architect`; hook `verify-completion`.
- **L4** (+L3): hook `audit-log`. Also raises `Policy.enterprise`
  (MCP allowlisting) and `Policy.sandbox` to `"strict"`, and denies
  `curl`/`wget`/`ssh`/`scp`.
- **L0** selects nothing from the cumulative table (an empty preset, just
  autonomy A4 — "propose, don't scaffold").

## Mode (`greenfield` | `brownfield`)

`brownfield` adds skills `discover`, `brownfield-change` and docs
`brownfield` (system map, hotspots, critical paths, invariants, test gaps)
on top of whatever the level preset selects, and lowers `default_autonomy`
by one step (floor A1) — the idea being an agent should understand existing
code before it's trusted to act on it as autonomously as it would in a
greenfield project.

`agentic_init init`'s detection suggests `brownfield` when the repo has
≥20 commits or ≥30 source files (`detect/__init__.py::Detection.mode`).

## Autonomy (`autonomy`, 0–5, optional)

Leave unset to use `default_autonomy(level, mode)`; set explicitly to
override it. Autonomy drives `policy.py::build_policy`, which becomes
`.claude/settings.json`'s `permissions` (and `sandbox` at L2+):

| Autonomy | Scope | `permissions.defaultMode` |
|---|---|---|
| A0 | Claude proposes, the human executes | `plan` |
| A1 | Claude implements, the human approves each change | `default` |
| A2 | Claude plans, implements and tests; the human merges | `acceptEdits` |
| A3 | Claude owns the task through a pull request | `acceptEdits` |
| A4 | Claude merges after automated verification | `acceptEdits` |
| A5 | Claude deploys, monitors and rolls back | `acceptEdits` |

Commit/PR-creation git commands (`git add`, `git commit`, `git switch -c`,
`gh pr create`, …) move from `ask` to `allow` at A3+; `git push` and
`gh pr merge` move from `ask` to `allow` only at A4+. This repository's own
`CLAUDE.md` documents its working agreement at **A3** (own the task through
a PR, never merge) — consistent with what `agentic_init.yaml`
(`level: 1, mode: greenfield`, no explicit `autonomy`) would generate.

## Modules

- **`aidlc`**: adds the `evidence-gate` skill, the `verify-completion` Stop
  hook (re-runs lint/typecheck/test when the tree is unverified and blocks
  completion on failure), and the `docs/evidence` seed — for teams that want
  every "done" claim backed by recorded evidence.
- **`bmad`**: adds nothing to the catalog directly; the CLI's "Next steps"
  suggest running `npx bmad-method@latest install` if it isn't already
  present and `npx` is available (`cli.py::_apply`, `modules/bmad.py`).

`enrich: true` similarly adds the `agentic_init-enrich` skill
(`modules/__init__.py`) so `agentic_init enrich` has something to invoke.

## `include` / `exclude`

Both are applied *after* the level/mode preset and module selections, in
that order (`resolver.py::select`): `include` adds names the preset didn't
select; `exclude` removes names by name regardless of which layer added
them. Referencing an unknown component name raises a `ConfigError` naming
the available options for that kind (`catalog.py::load`).

## `commands`

Detected automatically (`detect/commands.py`) but always overridable.
Setting a command to an explicit string replaces the detected value; setting
it to `null`/empty disables it for that key (`Commands.blank_is_none`
validator strips blank strings to `None`). Disabled commands are omitted
from generated instructions and from `doctor`'s "commands resolved" count —
useful for e.g. disabling `e2e` in a repo where the detector guesses wrong.

## Example: this repository's own config

```yaml
version: 1
project:
  name: agentic_init
  description: Config-based CLI that bootstraps repositories with a lean, best-practice agentic development setup.
level: 1
mode: greenfield
targets:
- claude-code
include:
  skills: [debug]
  hooks: [post-edit-format]
```
