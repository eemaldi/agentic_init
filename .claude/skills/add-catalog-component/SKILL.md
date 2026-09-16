---
name: add-catalog-component
description: Add a new skill, agent, hook, rule, MCP server or docs seed to the agentic_init catalog, wire it into presets and refresh snapshots. Use when extending what agentic_init generates.
---

# Add a catalog component

1. Create `src/agentic_init/catalog/<kind>/<name>/component.yaml` with a `description` of at least 8 words stating what it does and when to use it.
   - agents: `tools: [...]`, optional `model`
   - skills: optional `user_only: true` for side-effecting procedures
   - hooks: `event`, optional `matcher`; script in `files/hook.py` (stdlib only, exit 2 to block)
   - rules: optional `paths: [globs]`
   - mcp: `server:` block exactly as in `.mcp.json`, `env: [VARS]` it needs
   - docs: seed files under `files/<project-relative path>`
2. Write `body.md` (Jinja: `commands`, `selected`, `stack`, `modules`, `level`, `mode`, `autonomy`). Procedural, no personas.
3. If it belongs in a preset, add it to `src/agentic_init/presets.py` at the lowest level that needs it, or to a module in `src/agentic_init/modules/__init__.py`.
4. Behavioral hooks need a test in `tests/test_hooks.py`.
5. Run `scripts/snapshot-update.sh`, review the snapshot diff, then `uv run pytest` and `uv run ruff check`.
