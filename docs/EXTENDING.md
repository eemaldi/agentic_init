# Extending agentic_init

There are two repo-provided skills for this (`.claude/skills/add-catalog-
component/`, `.claude/skills/add-target/` — hand-authored, not part of the
generated catalog itself). This doc mirrors their content for readers
without Claude Code, plus the surrounding context.

## Adding a catalog component (skill, agent, hook, rule, MCP server, or doc)

1. Create `src/agentic_init/catalog/<kind>/<name>/component.yaml` with a
   `description` of **at least 8 words** stating what it does and when to
   use it (`doctor.py::_descriptions` flags anything shorter as "too vague
   for reliable delegation" — this is enforced by a real check, not just a
   convention). Kind-specific metadata:
   - **agents**: `tools: [...]`, optional `model`
   - **skills**: optional `user_only: true` for side-effecting procedures
     (rendered as `disable-model-invocation: true`, so it's only invoked
     explicitly by name — e.g. `agentic_init-enrich`, `release`)
   - **hooks**: `event` (a Claude Code hook event name), optional
     `matcher`; the script goes in `files/hook.py`, stdlib-only, exit 2 to
     block the tool call (see `docs/CATALOG.md` for two verified examples)
   - **rules**: optional `paths: [globs]` to scope the rule to matching
     files
   - **mcp**: a `server:` block exactly as it should appear under
     `.mcp.json`'s `mcpServers`, plus `env: [VARS]` it needs (surfaced as a
     "Next steps" export reminder and checked by `doctor`)
   - **docs**: seed files under `files/<project-relative path>` — written
     once, never touched again after creation
2. Write `body.md` (skills/agents/rules only) — Jinja, rendered with
   `commands`, `selected`, `stack`, `modules`, `level`, `mode`, `autonomy`
   in scope (see `resolver.py::resolve`'s `context` dict for the exact
   keys). Keep it procedural — steps an agent follows — not a persona
   description.
3. If it should be part of a level/mode preset, add it to
   `src/agentic_init/presets.py::_CUMULATIVE` (or `_BROWNFIELD`) at the
   lowest level that needs it; if it's part of an optional module, add it
   to `src/agentic_init/modules/__init__.py`. Components not in any preset
   are still usable via `agentic_init.yaml`'s `include`.
4. Hooks with actual blocking/allowing behavior need a test in
   `tests/test_hooks.py` (see the existing tests there for the pattern —
   they invoke the hook script as a subprocess with a JSON payload on
   stdin, exactly as Claude Code does, and assert on the exit code —
   the same approach used to verify `block-dangerous-commands` and
   `protect-secrets` for this documentation).
5. Run `scripts/snapshot-update.sh` to regenerate `tests/snapshots/`,
   review the diff (`git diff tests/snapshots`) to confirm only the
   intended output changed, then `uv run pytest && uv run ruff check .`.

## Adding a new target (a different agentic tool, e.g. Cursor, Copilot)

1. Read `src/agentic_init/targets/claude_code.py` and
   `src/agentic_init/blueprint.py` first. Targets only *translate* a
   `Blueprint` into that tool's file format — resolver/catalog logic must
   stay tool-agnostic; never branch on target name outside `targets/`.
2. Create `src/agentic_init/targets/<tool>.py` with a class exposing a
   `name: str` class attribute and `render(self, blueprint: Blueprint) ->
   list[FileOp]` (matches the `Target` protocol in `targets/base.py`).
   Choose a `Strategy` per file (`targets/base.py::Strategy`):
   - `blueprint.sections` (the CLAUDE.md-equivalent instructions) →
     `Strategy.BLOCKS`, so the human can add their own content around it
   - structured config the user may also hand-edit → `Strategy.JSON`
     (merged, reversible via `merge.py`)
   - fully generated files (skills, agents, hook scripts) →
     `Strategy.OWNED`
   Map `blueprint.policy` to the target tool's permission model as best you
   can; if the tool can't express something (e.g. no sandbox concept),
   drop it rather than forcing a bad approximation, and say so explicitly
   if the CLI output needs it.
3. Register the class in `TARGETS` in `src/agentic_init/targets/__init__.py`
   — this is also what `Config.known_targets` validates `targets:` entries
   against, so an unregistered name fails config validation with a clear
   error rather than being silently ignored.
4. Add snapshot cases with `targets: [<tool>]` in
   `tests/test_snapshots.py`, run `scripts/snapshot-update.sh`, and review
   the generated output.
5. `uv run pytest && uv run ruff check .`.

## General conventions (from `CLAUDE.md`)

- Package manager: `uv`. Lint/format: `ruff` (`ruff check .` / `ruff format
  .`, 120-char lines, `src/agentic_init/catalog` and `.claude/hooks` are
  excluded from linting since they're templates/generated scripts).
- Tests: `uv run pytest` (whole suite) or `uv run pytest
  path/to/test_file.py::test_name` (single test).
- When a mistake repeats, fix the system, not just the instance: update
  `CLAUDE.md`, a rule, a skill, or a test.
