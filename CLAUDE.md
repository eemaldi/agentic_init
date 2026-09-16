This is agentic_init
Configurable, runnable, makes you kickstart you agentic development in minutes 🚀

## Architecture
`agentic_init.yaml` → `resolver.py` (presets + modules + detection + Jinja catalog) → tool-agnostic `Blueprint` → `targets/*` render `FileOp`s → `writer.py` plans and applies them (owned files, managed blocks, JSON merge, seeds), tracking ownership in `.agentic_init.lock`.
`Guideline.md` is the source of truth for what gets generated. Extend via `/add-catalog-component` and `/add-target`; regenerate golden files with `scripts/snapshot-update.sh`.

<!-- agentic_init:begin project -->
# agentic_init

Config-based CLI that bootstraps repositories with a lean, best-practice agentic development setup.

## Stack
- Languages: python
- Package managers: uv
<!-- agentic_init:end project -->

<!-- agentic_init:begin commands -->
## Commands

- Install: `uv sync`
- Test (all): `uv run pytest`
- Test (single): `uv run pytest path/to/test_file.py::test_name`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`

Use these commands instead of guessing. If a command you need is missing, ask, then record it here.
<!-- agentic_init:end commands -->

<!-- agentic_init:begin workflow -->
## Working agreement

Autonomy: **A3 (Feature delivery)**
- Own the task through a pull request: branch, commit, open a PR with evidence. Never merge.
- Drop to A2 for schema migrations, auth, security and payment logic.
- Drop to A1 for production infrastructure.
- Escalate instead of deciding: conflicting requirements, unclear architecture or business rules, destructive or irreversible actions, security trade-offs, production incidents.
- Skills: `/implement`, `/test`, `/review`, `/debug`. Use the matching skill instead of improvising a procedure.
- Agents: `reviewer`. The agent that writes a change never approves it; delegate review to a read-only agent.

### Learning loop
When a mistake repeats, fix the system, not just the instance: update this file, a rule, a skill, a hook or a test.
<!-- agentic_init:end workflow -->

<!-- agentic_init:begin verification -->
## Definition of done

1. Run targeted tests, then the suite: `uv run pytest`.
2. Run static checks: `uv run ruff check .`.
3. Review your own diff (`git diff`) for scope creep and leftovers.
4. Report: what changed, evidence (commands run and results), residual risk, follow-ups.
<!-- agentic_init:end verification -->
