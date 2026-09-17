# CLI Reference

All commands accept a `root` positional argument (a project directory,
default `.`) except `catalog`, `schema` and `version`. Source: `cli.py`.

## `agentic_init init [root] [--yes/-y] [--dry-run] [--force]`

Detect the project, run the interactive wizard (or accept defaults with
`--yes`), write `agentic_init.yaml`, then apply it.

- Refuses to run if `agentic_init.yaml` already exists: prompts
  "Reconfigure?" interactively, or (with `--yes`) exits 1 pointing at
  `apply`.
- `--dry-run`: still writes `agentic_init.yaml`? **No** — under `--dry-run`
  the config is not saved either (only `_apply(..., dry_run=True)` is
  skipped from writing files; verify against `cli.py:init` — `if not
  dry_run: save_config(...)`). Use it to preview the wizard's effect without
  touching the filesystem.
- `--force`: overwrite files that exist but aren't tracked by
  `.agentic_init.lock`, or were modified locally since the last generation.

## `agentic_init apply [root] [--dry-run] [--force]`

Regenerate the setup from the existing `agentic_init.yaml`. This is what you
run after hand-editing `agentic_init.yaml` (selection, level, mode, autonomy,
modules, command overrides). Errors with a friendly message (exit 1) if
`agentic_init.yaml` is missing or invalid, instead of a traceback — verified:
running `apply` in a directory with no config prints `agentic_init.yaml not
found in <dir>. Run \`agentic_init init\` first.` and exits 1.

## `agentic_init diff [root]`

Builds the same plan `apply` would, and prints it as a unified diff (one hunk
per pending file) followed by the summary table — without writing anything.
Verified idempotent: running `diff` immediately after `apply` on an unchanged
config prints only "Everything is up to date."

## `agentic_init doctor [root]`

Runs independent checks against the current repo state and the plan the
config would produce (`doctor.diagnose()`):

1. `CLAUDE.md` exists and is ≤300 lines (else WARN to move detail into
   skills/docs).
2. Every skill/agent frontmatter `description` is ≥8 words (WARN if too
   vague for reliable delegation).
3. Every hook script referenced in `.claude/settings.json` exists on disk,
   and `python3` is on `PATH` if any hook is configured.
4. Every resolved project command's executable is runnable (`shutil.which`);
   WARN if there's no `test` command at all.
5. Every `${VAR}` referenced in `.mcp.json` is set in the environment.
6. No generated `owned` file differs from what's in `.agentic_init.lock`
   (drift), and no pending changes remain (config and generated files agree).

Exits 1 if any finding is `ERROR` (currently only "no config" / "no
CLAUDE.md" reach that level); `WARN` findings don't fail the exit code.

## `agentic_init enrich [root]`

Runs `claude -p /agentic_init-enrich --permission-mode acceptEdits` in
`root`, which is a Claude Code pass that fills the generated docs and
`CLAUDE.md` placeholders with real project knowledge. Requires:

- `claude` on `PATH` (`enrich.available()`), else exit with `\`claude\` is
  not on PATH. Install Claude Code first.`
- `enrich: true` set in `agentic_init.yaml` **and** `apply` already run
  (i.e. the `agentic_init-enrich` skill file actually exists), else exit
  with `Set \`enrich: true\` in agentic_init.yaml and run \`agentic_init
  apply\` first.`

Verified: both guard clauses were exercised against a project without
`enrich: true` set — the command exited 1 with the second message above,
without attempting to shell out to `claude`.

## `agentic_init catalog`

Lists every available skill, agent, hook, rule, MCP server and docs
component with its description, grouped by kind — a live view of
`src/agentic_init/catalog/`, independent of any project's config. Run it to
see everything `include`/`exclude` in `agentic_init.yaml` can reference; the
full current listing is in `docs/CATALOG.md`.

## `agentic_init schema`

Prints `Config.model_json_schema()` (pydantic) as JSON — the authoritative,
always-current schema for `agentic_init.yaml`. Useful for editor validation:

```sh
agentic_init schema > agentic_init.schema.json
```

Verified valid JSON and a well-formed JSON Schema document (piped through
`json.load`).

## `agentic_init version`

Prints the installed package version (`importlib.metadata.version` via
`agentic_init.__version__`; falls back to `0.0.0` if the package isn't
installed, e.g. running from a raw checkout without `pip install -e .`).
