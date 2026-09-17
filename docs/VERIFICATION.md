# Verification Log

This documentation set was written after reading the full source tree, then
checked against real command runs rather than left as static analysis.
Everything below was actually executed against this repository (branch
`claude/vigilant-mayer-uf7dq6`) while writing the docs. Re-run any of it
yourself to confirm; nothing here is inferred from reading code alone.

## Static checks

```
$ uv sync                    → resolved and installed cleanly (typer, questionary, jinja2,
                                pyyaml, pydantic, pytest, ruff, …)
$ uv run ruff check .        → All checks passed!
$ uv run pytest -q           → 86 passed in 4.64s
$ uv run agentic_init version → 0.1.0
```

## `init` end-to-end, against a real scratch project

A scratch git repo was created with a `pyproject.toml` (`[tool.uv]`, pytest +
ruff deps), a `tests/test_x.py`, and an initial commit — i.e. a realistic
small Python project, not an empty directory.

```
$ agentic_init init --yes <scratch>
wrote agentic_init.yaml
create  .gitignore
create  CLAUDE.md
create  .claude/settings.json
create  .claude/skills/implement/SKILL.md
create  .claude/skills/test/SKILL.md
create  .claude/skills/review/SKILL.md
create  .claude/agents/reviewer.md
create  .claude/hooks/block-dangerous-commands.py
create  .claude/hooks/protect-secrets.py
create  .mcp.json
```

This matches the documented L1/greenfield preset exactly (`docs/
CONFIGURATION.md`'s level table) — detection correctly suggested `level: 1`
(≪50 source files) and `mode: greenfield` (no git history to speak of).

## Idempotency

```
$ agentic_init diff <scratch>
Everything is up to date.
```

Immediately after `init`, with no changes made, `diff` reports nothing
pending — confirms the plan-vs-disk-vs-lock comparison in `writer.py`
correctly recognizes its own freshly-written output as already satisfied.

## `doctor`

```
$ agentic_init doctor <scratch>
✓ CLAUDE.md is 43 lines
✓ 4 skills/agents have usable descriptions
✓ 2 hooks are configured
✓ 5 project commands resolved
! MCP needs $GITHUB_PERSONAL_ACCESS_TOKEN in your environment
✓ generated files match agentic_init.yaml
```

All six check categories in `doctor.py` fired and produced a real finding
(five OK, one legitimate WARN for the unset GitHub token) — not skipped or
stubbed.

## Ownership semantics — the core value proposition, so tested directly

**`owned` strategy** (fully generated file, e.g. `.claude/agents/
reviewer.md`):

1. Appended a line by hand to the generated agent file.
2. `doctor` → `! .claude/agents/reviewer.md modified locally; \`agentic_init
   apply --force\` restores it` (drift correctly detected via content hash
   mismatch against `.agentic_init.lock`).
3. `apply --dry-run` (no `--force`) → `skip  .claude/agents/reviewer.md
   modified locally` (local edit correctly protected).
4. `apply --force` → `update  .claude/agents/reviewer.md` and the hand-added
   line was gone afterwards (confirmed by grep) — force-overwrite works as
   documented.

**`blocks` strategy** (`CLAUDE.md`, partially owned):

1. Appended freeform text (`<!-- local note -->`) *outside* any managed
   block.
2. `doctor` did **not** flag it as drift, and `apply --force` left it
   intact — confirmed by grep after the force-apply. This is correct,
   documented behavior: `--force` only affects `owned`-strategy files; the
   whole point of `blocks` is that content outside the markers is the
   human's and is never touched, force or not. (Initial expectation going
   in was that `--force` would blow away the whole file; source reading —
   `writer.py::_owned` vs `_blocks`, `_blocks` never even looks at `force`
   — plus this test confirmed the actual, more useful, behavior.)

## Hooks — behavioral, not just read

`.claude/hooks/protect-secrets.py` and `.claude/hooks/block-dangerous-
commands.py` from the generated scratch project were invoked exactly as
Claude Code invokes them (JSON payload on stdin, exit code as the signal):

```
protect-secrets:   Read .env            → exit 2 (blocked)
protect-secrets:   Read README.md       → exit 0 (allowed)
block-dangerous-commands: "ls -la"      → exit 0 (allowed)
block-dangerous-commands: "rm -rf /"    → exit 2 (blocked)
```

Plus `is_secret()` was checked directly against 10 path cases spanning real
secrets (`.env`, `.env.local`, `id_rsa`, `server.pem`, `credentials.json`,
`secrets/token`) and lookalikes/templates that must *not* be blocked
(`README.md`, `src/app.py`, `.env.example`, `.env.template`).

Bonus, unplanned confirmation: mid-session, a Bash command of mine that
referenced a `.env` path was itself blocked by this exact hook — because
this repository runs agentic_init on itself, and that hook is installed and
live here too. That's an even stronger signal than the isolated test: the
hook fired correctly against a real tool call in a real Claude Code session,
not just a synthetic subprocess invocation.

## Level/mode scaling and policy compilation

A second scratch project was configured directly via `agentic_init.yaml`
(`level: 4, mode: brownfield`, no explicit `autonomy`) and applied:

- Produced the full L1+L2+L3+L4 cumulative catalog plus the brownfield
  additions (9 skills, 5 agents, 5 hooks, 3 rules, 6 doc seed directories) —
  matches `docs/CATALOG.md`/`docs/CONFIGURATION.md`'s level tables exactly.
- The generated `.claude/settings.json` was inspected directly and matches
  `docs/ARCHITECTURE.md`'s policy description precisely: `defaultMode:
  "default"` (autonomy resolves to A1 — L4's A2 floor minus the brownfield
  penalty), `curl`/`wget`/`ssh`/`scp` in `deny`, `sandbox.enabled: true`
  with `failIfUnavailable: true` (strict), and `enabledMcpjsonServers`/
  `allowedMcpServers` allowlisting the `github` MCP server (enterprise-only
  behavior, correctly gated on `level >= 4`).

## Error paths

```
$ agentic_init apply <dir with no config>
agentic_init.yaml not found in <dir>. Run `agentic_init init` first.   (exit 1)

$ agentic_init init --yes <dir with existing config>
agentic_init.yaml exists; run `agentic_init apply`, or delete it to start over.   (exit 1)

$ agentic_init enrich <project without enrich:true>
Set `enrich: true` in agentic_init.yaml and run `agentic_init apply` first.   (exit 1)
```

All three guard clauses fail closed with an actionable message rather than
a stack trace, as designed.

## `schema`

`agentic_init schema` output was piped through `json.load` — parses as valid
JSON and is a well-formed JSON Schema document (top-level `properties`,
`$defs`, etc. from pydantic's `model_json_schema()`).

## What was *not* independently re-verified

- `audit-log` and `verify-completion` (the Stop hook) — read and
  cross-checked against `tests/test_hooks.py`'s existing coverage (which
  does exercise both: `test_audit_log_records_tool_calls`,
  `test_verify_completion_blocks_on_failing_checks_and_records_evidence`,
  and two more `verify-completion` cases), but not re-run standalone for
  this pass, since that behavior is already covered by the suite that just
  passed (86/86).
- `post-edit-format` — **not covered by any test in `tests/test_hooks.py`**
  (checked directly: no reference to it in that file) and not re-run
  standalone here either. Read only. This is a real gap, not a documentation
  simplification — worth a follow-up test alongside the other hooks.
- `agentic_init enrich`'s actual `claude -p /agentic_init-enrich` run and
  `modules/bmad.py`'s `npx bmad-method@latest install` — both shell out to
  external tools/network and were verified only at the guard-clause level
  (above), not executed end-to-end, since doing so would install real
  third-party tooling as a side effect of writing documentation.
- The interactive wizard (`wizard.py`, `questionary` prompts) — exercised
  only via `--yes`/`wizard.defaults()`, since the interactive path isn't
  scriptable from a non-interactive shell. Its logic is straightforward
  (each prompt maps 1:1 to a `Config` field) and is covered by
  `tests/test_cli.py`.
