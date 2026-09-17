# agentic_init

Bootstrap any repository for agentic development with Claude Code: `CLAUDE.md`, skills, agents, hooks,
rules, permissions, MCP, docs and CI, sized to your project and autonomy level.

Everything is generated from the commands and stack it detects in your repository, so the agent's
instructions, its guardrails and your CI all run the same checks. Re-running is safe: generated files are
tracked in `.agentic_init.lock`, local edits are never overwritten silently.

```sh
uvx agentic_init init       # detect, answer a few questions, generate
agentic_init apply            # regenerate from agentic_init.yaml (safe to re-run)
agentic_init diff             # preview pending changes
agentic_init doctor           # check the setup against best practices
agentic_init catalog          # list available components
agentic_init schema > agentic_init.schema.json
```

## What you get

| Level | Generated |
| --- | --- |
| 0 | `CLAUDE.md` with the detected stack, commands and working agreement |
| 1 | + `/implement` `/test` `/review`, a read-only `reviewer` agent, secret and dangerous-command hooks, GitHub MCP, a CI workflow and a PR template |
| 2 | + scoped rules, `docs/` (architecture, decisions, stories, operations), `test-engineer` and `security-reviewer`, formatter hook, tracker and observability MCP, e2e and dependency-review CI jobs, sandboxed Bash |
| 3 | + `explorer` and `architect`, migration/performance/incident skills, browser MCP, a Stop hook that re-runs the checks before the agent may finish |
| 4 | + audit logging, a strict sandbox and an MCP allowlist |

Brownfield repositories additionally get `docs/brownfield/` (system map, critical paths, invariants,
hotspots, test gaps, migration plan) and a `/brownfield-change` procedure; `agentic_init enrich` runs Claude
Code once to fill those documents from the actual code.

`docs/guideline-coverage.md` maps the operating model this generates onto the files it produces.
