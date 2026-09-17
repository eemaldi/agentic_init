# Architecture

## Purpose

agentic_init generates the setup an AI coding agent needs to work safely and
usefully in a repository: `CLAUDE.md`, skills, subagents, hooks, permission
policy, MCP servers and seed docs. It never runs on its own initiative — a
human runs `agentic_init init` or `agentic_init apply`, reviews the diff (git
tracks the output), and commits it like any other change.

## Pipeline

```
agentic_init.yaml            what to generate (project, level, mode, autonomy, modules, overrides)
     │
     ▼
detect()                     read the repo: languages, package managers, frameworks,
(detect/*.py)                 commands (Makefile/justfile/package.json/pyproject.toml),
                               git history, GitHub remote
     │
     ▼
resolve()                    presets(level, mode) + module_selections(config) + config.include,
(resolver.py)                 minus config.exclude, resolved per Kind (skills/agents/hooks/rules/mcp/docs)
     │                        → catalog.load() each item → render its Jinja templates with a
     │                          shared context (project, level, mode, autonomy, stack, commands, selected)
     ▼
Blueprint                    tool-agnostic: Config + Detection + Commands + autonomy + CLAUDE.md
(blueprint.py)                 sections + rendered Component list + Policy (permissions/sandbox)
     │
     ▼
targets/*.render()           turn the Blueprint into FileOps (owned file / merged block /
                               merged JSON / one-shot seed), one target per output tool
     │                        (today: claude-code; targets/shared.py adds .gitignore + doc seeds
     │                          for every target)
     ▼
writer.plan()                diff each FileOp against disk and against .agentic_init.lock to
(writer.py)                   decide create/update/delete/skip, tracking per-file ownership
     │
     ▼
writer.apply()                write the pending changes, update .agentic_init.lock
```

`agentic_init diff` and `agentic_init doctor` run the same pipeline up to
`writer.plan()` without calling `apply()`, so they're always looking at a real
plan rather than a description of one.

## Core modules

| Module | Responsibility |
|---|---|
| `config.py` | `Config` (the `agentic_init.yaml` schema, pydantic, `extra="forbid"`), load/save, validation |
| `detect/` | Read the target repo: `stack.py` (languages/package managers/frameworks from manifests and lockfiles), `commands.py` (install/dev/build/test/lint/format/typecheck/e2e from Makefile, justfile, `package.json` scripts, Python/Rust/Go conventions), `git.py` (repo age, GitHub remote) |
| `presets.py` | Level × mode → cumulative catalog selection (`preset()`), and level/mode → default autonomy (`default_autonomy()`) |
| `catalog.py` | Loads a catalog item's `component.yaml` metadata and enumerates its template files |
| `resolver.py` | `select()` merges preset + module selections + include/exclude into a final `Kind → [name]` map; `resolve()` renders every selected item's Jinja templates and the `CLAUDE.md` instruction sections into a `Blueprint` |
| `blueprint.py` | Tool-agnostic output: `Blueprint`, `Component`, `Section`, `Policy` — dataclasses, no file-format knowledge |
| `policy.py` | Turns `(autonomy, level, commands)` into a `Policy`: allowed/ask/denied shell commands, protected paths, edit mode, sandbox level |
| `targets/` | Render a `Blueprint` into `FileOp`s for one tool. `base.py` defines `FileOp`/`Strategy`/`Block`; `claude_code.py` is the only target today (`CLAUDE.md`, `.claude/settings.json`, skills, agents, rules, hooks, `.mcp.json`); `shared.py` adds `.gitignore` and doc seeds for every target |
| `writer.py` | Turns `FileOp`s into a `Plan` of `Change`s against disk state and `.agentic_init.lock`, then applies pending changes |
| `merge.py` | The merge primitives: recursive dict/list `merge`/`unmerge` for JSON files, marker-delimited `upsert_blocks` for `CLAUDE.md`/`.gitignore` |
| `lock.py` | `.agentic_init.lock`: per-file strategy + content hash (owned files) or owned JSON subtree/block ids, so re-runs and hand-edits are distinguishable |
| `engine.py` | `build()` ties `resolve()` → target rendering → `writer.plan()` into one call used by every CLI command |
| `doctor.py` | Independent checks against the built plan and the files on disk: `CLAUDE.md` size, skill/agent description quality, hook script presence, command runnability, MCP env vars, drift |
| `wizard.py` | The interactive `questionary` prompts behind `agentic_init init` (skipped by `--yes`, which uses `wizard.defaults()`) |
| `enrich.py` | Shells out to `claude -p /agentic_init-enrich` to run a Claude Code pass that fills the generated docs with real project knowledge |
| `modules/bmad.py` | Detects/installs the optional BMAD planning workflow via `npx bmad-method@latest install` |
| `cli.py` | Typer app wiring all of the above to `init`, `apply`, `diff`, `doctor`, `enrich`, `catalog`, `schema`, `version` |

## The four write strategies (`targets/base.py::Strategy`)

Every generated file is written under exactly one strategy, chosen per
`FileOp` by whichever target created it:

- **`owned`** — agentic_init owns the whole file (skills, agents, rules, hook
  scripts). A local edit is detected by content hash; `apply` skips it (prints
  `skip … modified locally`) unless `--force`, which overwrites it. Verified:
  editing `.claude/agents/reviewer.md` by hand makes `doctor` flag it and
  `apply` skip it; `apply --force` restores the generated content.
- **`blocks`** — agentic_init owns only the content between
  `<!-- agentic_init:begin ID --> … <!-- agentic_init:end ID -->` (or `#`
  equivalents for non-Markdown files) markers; everything else in the file is
  the human's. Used for `CLAUDE.md` (one block per instruction section) and
  `.gitignore`. Verified: freeform text appended outside the managed blocks
  in `CLAUDE.md` survives `apply --force` untouched — by design, `--force`
  only ever applies to `owned` files.
- **`json`** — agentic_init owns a declared subtree of a JSON file
  (`.claude/settings.json`, `.mcp.json`); `merge()`/`unmerge()` let the human
  add unrelated keys (or extend arrays) that survive regeneration, while keys
  agentic_init previously owned and no longer generates are cleanly removed.
- **`seed`** — write once if the file doesn't exist yet, never touch it
  again (`docs/**` templates: stories, ADRs, runbooks — meant to be edited by
  humans/agents immediately after creation).

## Ownership tracking (`.agentic_init.lock`)

For every generated path, the lock records its strategy and either a content
hash (`owned`), the list of block ids it owns (`blocks`), or the owned JSON
subtree (`json`). On the next run, `writer.plan()`:

1. Re-renders the desired content for every currently-selected `FileOp`.
2. Compares it to what's on disk and what the lock last wrote, deciding
   create / update / skip (locally modified) / unchanged.
3. For paths that were previously generated but are no longer selected
   (e.g. a skill was removed from `agentic_init.yaml`), retires them:
   deletes `owned` files, strips the relevant blocks, or removes the owned
   JSON subtree — never touching anything the human added.

This is what makes `agentic_init apply` safe to re-run after every config
change, and what lets it coexist with hand-authored content in the same
files.

## Permission policy (`policy.py` → `targets/claude_code.py`)

`autonomy` (A0–A5) and `level` (L0–L4) are compiled into a `Policy`:

- `edits`: `propose` (A0) / `ask` (A1) / `auto` (A2+) → Claude Code's
  `permissions.defaultMode` (`plan` / `default` / `acceptEdits`).
- `allowed_commands`: read-only git always; project commands (test/lint/
  typecheck/format/build) always; commit/PR-creation git at A3+; `git push`
  and `gh pr merge` only at A4+ (otherwise moved to `ask`).
- `denied_commands`: `rm -rf`, `sudo`, force-push always; `curl`/`wget`/`ssh`/
  `scp` added at L4 (enterprise).
- `protected_paths`: `.env*`, `secrets/**`, `*.pem`, `*.key`,
  `credentials.json` — denied for `Read`/`Edit` in `settings.json`, and (at
  L2+) filesystem-denied in the sandbox.
- `sandbox`: `off` (L0–1) / `soft` (L2–3) / `strict` (L4, with
  `failIfUnavailable` and no unsandboxed commands).
- At L4, MCP servers are also allowlisted explicitly
  (`enabledMcpjsonServers`/`allowedMcpServers`).

Verified end-to-end: generating a `level: 4, mode: brownfield` project
produces exactly this — `defaultMode: "default"` (autonomy resolves to A1
under the brownfield penalty), `curl`/`wget`/`ssh`/`scp` in `deny`, a `strict`
sandbox, and the GitHub MCP server allowlisted.

## Catalog layout

Every generated skill/agent/hook/rule/doc lives under
`src/agentic_init/catalog/<kind>/<name>/`:

- `component.yaml` — `description` (and kind-specific metadata: hook
  `event`/`matcher`, agent `tools`/`model`, rule `paths`, MCP server config).
- `body.md` — Jinja-templated body (skills, agents, rules).
- `files/**` — Jinja-templated file tree, written verbatim under the
  component's output directory (hook scripts, multi-file skills, doc seeds).

`CLAUDE.md` itself is composed from `src/agentic_init/catalog/instructions/
{project,commands,workflow,verification,context}.md`, one block per section,
each included only if it renders non-empty for the current config.

See `docs/EXTENDING.md` for how to add to the catalog or add a new target.
