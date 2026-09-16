---
name: add-target
description: Add a new output target (for example Cursor or Copilot) that renders the tool-agnostic Blueprint into that tool's files. Use when supporting another agentic coding tool.
---

# Add a target

1. Read `src/agentinit/targets/claude_code.py` and `src/agentinit/blueprint.py`. Targets only translate; never add tool-specific logic to the resolver or catalog.
2. Create `src/agentinit/targets/<tool>.py` with a class exposing `name` and `render(blueprint) -> list[FileOp]`.
   - Instructions: `blueprint.sections` as `Strategy.BLOCKS`
   - Structured config the user may also edit: `Strategy.JSON` (merged, reversible)
   - Fully generated files: `Strategy.OWNED`
   - Map `blueprint.policy` to the tool's permission model; drop what it cannot express and say so in a comment-free, explicit summary in the CLI output if needed.
3. Register it in `TARGETS` in `src/agentinit/targets/__init__.py`.
4. Add snapshot cases with `targets: [<tool>]` in `tests/test_snapshots.py`, run `scripts/snapshot-update.sh`, review.
5. `uv run pytest && uv run ruff check`.
