# Operating-model coverage

`Guideline.md`'s 61 sections are the specification for what agentic_init generates. This file maps each
one to the thing in the generated repository that manifests it, so the mapping can be checked rather than
assumed. "Guidance" means the section states a principle that shapes the generator's design but produces
no file of its own.

| # | Section | Where it shows up |
| --- | --- | --- |
| 1 | Mental model / layer separation | The `Blueprint` layers: instructions, rules, skills, agents, MCP, hooks, CI (`src/agentic_init/blueprint.py`) |
| 2 | `CLAUDE.md` as persistent memory | `CLAUDE.md`, generated in managed blocks from `catalog/instructions/*.md` |
| 3 | Scoped rules | `.claude/rules/*.md` from level 2, with `paths:` frontmatter for scoping |
| 4 | Skills as procedures | `.claude/skills/*/SKILL.md`, procedural bodies with Inputs / Procedure / Never / Report |
| 5 | Agents as specialized workers | `.claude/agents/*.md` with `tools:` and `model:` frontmatter |
| 6 | Subagents vs worktrees vs teams | Worktree instruction in the workflow section at level 3+; `explorer` agent for research |
| 7 | MCP as capability layer | `.mcp.json` from the `mcp` catalog (github, linear, sentry, playwright, postgres) |
| 8 | MCP / tool security classes | `permissions.allow / ask / deny` in `.claude/settings.json` (`src/agentic_init/policy.py`) |
| 9 | Hooks as deterministic control | `.claude/hooks/*.py` wired into `settings.json` events |
| 10 | Task framing, not prompts | `/spec` and `/implement` skills: acceptance criteria, constraints, verification, authority |
| 11 | Context engineering | Level presets: only the components a project of that size needs |
| 12 | BMAD | `modules.bmad`: planning section in `CLAUDE.md` plus `npx bmad-method install` |
| 13 | AIDLC lifecycle | `modules.aidlc`: `/evidence-gate` skill, `verify-completion` Stop hook, `docs/evidence/` |
| 14 | Evidence gates | `verify-completion` hook re-runs lint/typecheck/tests and blocks on failure; CI repeats them |
| 15 | Task lifecycle | Skill set per level: `/spec` → `/implement` → `/test` → `/review` → `/release` |
| 16 | Greenfield | `mode: greenfield`: defaults, golden path, no brownfield mapping overhead |
| 17 | Brownfield first phase | `mode: brownfield`: `docs/brownfield/`, `/discover`, `/brownfield-change` |
| 18 | Golden path | Detected commands in the `commands` block of `CLAUDE.md`, reused by skills, hooks and CI |
| 19 | Repository structure | The generated tree: `CLAUDE.md`, `.claude/`, `docs/`, `.mcp.json`, `.github/` |
| 20 | Do not over-engineer | Level 0 generates `CLAUDE.md` only; components are added by level, not by default |
| 21 | Level 0 | `level: 0` → instructions only |
| 22 | Level 1 | `level: 1` → 3 skills, `reviewer`, 2 guardrail hooks, github MCP, CI |
| 23 | Level 2 | `level: 2` → +rules, docs, `test-engineer`/`security-reviewer`, formatter hook, tracker + observability MCP, e2e and security CI jobs, sandbox |
| 24 | Level 3 | `level: 3` → +`explorer`/`architect`, `verify-completion`, browser MCP, worktree instruction, migration/performance/incident skills |
| 25 | Level 4 | `level: 4` → +`audit-log`, strict sandbox, MCP allowlist, `disableBypassPermissionsMode` |
| 26 | Autonomy levels A0–A5 | `autonomy:` drives the working agreement, edit mode and command policy |
| 27 | Risk-based autonomy | The "Autonomy by change" table in `CLAUDE.md` at level 2+ |
| 28 | Small agent team | Five agents at most: reviewer, test-engineer, security-reviewer, explorer, architect |
| 29 | No persona agents | Agent bodies define purpose, inputs, authority, procedure, output — no personas |
| 30 | Agent contract | Same: every agent body follows the contract layout |
| 31 | Generation ≠ verification | "The agent that writes a change never approves it" in the working agreement; read-only reviewers |
| 32 | Adversarial reviewers | `security-reviewer` agent and `/security-review` skill |
| 33 | Explicit repository knowledge | `docs/architecture/`, `docs/decisions/`, `docs/stories/`, `docs/operations/`, `docs/brownfield/` |
| 34 | Context budget | `doctor` warns past 300 lines of `CLAUDE.md`; procedures live in skills |
| 35 | Executable procedures | Skills cite the project's real commands; guardrails are scripts, not instructions |
| 36 | MCP vs skills vs hooks vs agents | The catalog kinds map one-to-one onto this split |
| 37 | Permission architecture | Deny rules, protected paths, sandbox, MCP allowlist at level 4 |
| 38 | Deployment as a capability | `/release` is explicit-invocation only; `git push` / `gh pr merge` need autonomy 4+ |
| 39 | Tools designed for agents | Hooks emit JSON decisions; `verification.json` records machine-readable evidence |
| 40 | CI pipeline | `.github/workflows/agentic-checks.yml`: lint → typecheck → test → build, plus e2e and dependency review |
| 41 | Evaluation beyond unit tests | `/test` covers behaviour, edge cases and failure modes; e2e job at level 2+ |
| 42 | Autonomous loop | "Learning loop" section: fix the system, not the instance |
| 43 | Agent boot sequence | Context-loading order in the "Where to look" section at level 2+ |
| 44 | Greenfield setup | `level >= 2, mode: greenfield` with `aidlc` / `bmad` modules |
| 45 | Brownfield setup | `docs/brownfield/`: system map, critical paths, invariants, hotspots, test gaps, migration plan |
| 46 | Monorepo | Workspace detection: workspace list in `CLAUDE.md`, scoped-rules instruction, level 3 suggestion |
| 47 | Agentic PR | `.github/pull_request_template.md` with architecture, migration, evidence, security, risk |
| 48 | Escalate ambiguity | Escalation list in the working agreement; every skill has an escalation path |
| 49 | Model strategy | `model:` per agent: opus for architecture and security, sonnet for review and tests, haiku for search |
| 50 | Cost optimization | Same mechanism as context engineering: durable docs, scoped rules, subagent research |
| 51 | Skill library | 16 skills in the catalog, selected by level; `/release` and `/migrate-db` are explicit-invocation only |
| 52 | Agent library | 5 agents in the catalog, selected by level |
| 53 | MCP stack | github, linear, sentry, playwright, postgres |
| 54 | Hooks stack | PreToolUse guardrails, PostToolUse formatting and audit, Stop verification |
| 55 | AI-native stack | The end-to-end generated setup: instructions → skills/agents → MCP → hooks → CI → evidence |
| 56 | Four autonomy dimensions | Reasoning/execution are set by `autonomy`; integration and operations by the command policy |
| 57 | Setup by project level | The level presets (`src/agentic_init/presets.py`) |
| 58 | Greenfield matrix | `level` × `mode: greenfield` → autonomy default (`default_autonomy`) |
| 59 | Brownfield matrix | `mode: brownfield` lowers the default autonomy by one level |
| 60 | Best default for a serious project | `level: 2` output: rules, four skills, reviewer + test-engineer, docs, MCP, CI |
| 61 | Final rule set | Enforced by construction: stable facts in `CLAUDE.md`, procedures in skills, guardrails in hooks, evidence in CI |

## Deliberately not generated

- Agent teams (§6): experimental and disabled by default; subagents and worktrees cover the same ground.
- Cloud, deployment and feature-flag MCP servers (§53): project-specific credentials and blast radius.
- Golden datasets and LLM-as-judge evals (§41): they belong to the product being built, not to the scaffold.
- Managed enterprise policy files (§25, §37): they live in organization settings, not in a repository.
