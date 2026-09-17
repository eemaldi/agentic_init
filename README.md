# agentic_init

Bootstrap any repository for agentic development with Claude Code: `CLAUDE.md`, skills, agents, hooks, rules, permissions, MCP and docs, sized to your project and autonomy level.

```sh
uvx agentic_init init       # detect, answer a few questions, generate
agentic_init apply            # regenerate from agentic_init.yaml (safe to re-run)
agentic_init diff             # preview pending changes
agentic_init doctor           # check the setup against best practices
agentic_init catalog          # list available components
agentic_init schema > agentic_init.schema.json
```

## Documentation

- [Setup Guide](docs/SETUP.md) — install, bootstrap a project, what gets written
- [Architecture](docs/ARCHITECTURE.md) — the generation pipeline and every module's role
- [CLI Reference](docs/CLI.md) — every command and flag
- [Configuration Reference](docs/CONFIGURATION.md) — the full `agentic_init.yaml` schema
- [Catalog Reference](docs/CATALOG.md) — every skill, agent, hook, rule, MCP server and doc seed
- [Extending agentic_init](docs/EXTENDING.md) — add a catalog component or a new target tool
- [Verification Log](docs/VERIFICATION.md) — what was actually run to confirm this documentation, and what wasn't
