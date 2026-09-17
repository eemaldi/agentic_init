# Catalog Reference

This is the output of `agentic_init catalog` against this repository's
`src/agentic_init/catalog/` (captured while writing this documentation — run
`agentic_init catalog` yourself for the always-current version; it reads the
catalog directory live).

## Skills (`.claude/skills/<name>/SKILL.md`)

| Skill | Description |
|---|---|
| `agentic_init-enrich` | One-off pass that maps this repository and fills the agentic_init-generated docs and CLAUDE.md placeholders with verified project knowledge. Invoke explicitly only. |
| `brownfield-change` | Safely change behavior in existing code by establishing invariants, blast radius and test coverage before editing. Use for any modification of established production code. |
| `debug` | Investigate a bug or failing test systematically from reproduction to root cause and regression test. Use when behavior is wrong or a check fails. |
| `discover` | Map an unfamiliar codebase or subsystem into durable architecture notes before changing it. Use at the start of work in an area without documentation. |
| `evidence-gate` | Verify a story or task is actually complete by collecting objective evidence for every acceptance criterion. Use before declaring any story done. |
| `implement` | Implement a well-defined change from acceptance criteria through tests and verified evidence. Use for any feature or fix with clear requirements. |
| `release` | Prepare a release with changelog, version bump, verification and tagging. Invoke explicitly only. |
| `review` | Review a diff or pull request for correctness, design, security and test gaps, producing prioritized findings. Use before merging any non-trivial change. |
| `security-review` | Adversarial security review of a change or area covering authn/authz, input handling, secrets, dependencies and data exposure. Use for any change touching auth, user input, data access or infrastructure. |
| `spec` | Turn an idea or request into a story with context, constraints, acceptance criteria and verification plan. Use before implementing anything ambiguous. |
| `test` | Design and run tests for a change, filling coverage gaps for behavior, edge cases and failure modes. Use when adding tests or when verification is missing. |

## Agents (`.claude/agents/<name>.md`)

| Agent | Description |
|---|---|
| `architect` | Evaluates designs and cross-module changes for boundaries, coupling, operability and reversibility, and drafts ADRs. Use before significant structural changes or new components. |
| `explorer` | Read-only codebase research. Use proactively to locate code, trace call paths or answer "where/how does X work" without filling the main context. |
| `reviewer` | Independent read-only reviewer for diffs and pull requests. Use proactively after implementing any non-trivial change and before opening or merging a PR. |
| `security-reviewer` | Adversarial read-only security reviewer. Use proactively for changes touching authentication, authorization, user input, secrets, data access, dependencies or infrastructure. |
| `test-engineer` | Writes and repairs tests, closes coverage gaps and diagnoses flaky or failing suites. Use when a change lacks tests or a test run fails for unclear reasons. |

## Hooks (`.claude/hooks/<name>.py`)

| Hook | Description | Verified behavior |
|---|---|---|
| `audit-log` | Appends every tool call Claude makes to an audit log in `.claude/state/audit.jsonl` for review and compliance. | (static-only; see `docs/VERIFICATION.md`) |
| `block-dangerous-commands` | Blocks destructive shell commands (recursive deletes, force pushes, destructive SQL, infra mutation, remote script execution). | Exit 0 on `ls -la`, exit 2 (blocked) on `rm -rf /`, reproduced by direct subprocess invocation. |
| `post-edit-format` | Formats each edited file with the project's formatter when one is available. | (static-only) |
| `protect-secrets` | Blocks reading or editing secret files (`.env`, keys, credentials) through file tools and any shell command that names them. | Exit 2 on reading `.env`, exit 0 on `README.md`; `is_secret()` checked against 10 path cases (secrets and lookalikes/templates). Also independently confirmed live: this same hook, installed on this repository itself, blocked an actual shell command of mine that referenced a `.env` path mid-session. |
| `verify-completion` | On Stop, re-runs lint, typecheck and tests when the current commit or working tree is unverified, blocks completion on failure and records evidence. | (static-only) |

## Rules (`.claude/rules/<name>.md`)

| Rule | Description |
|---|---|
| `architecture` | Structural conventions that keep the codebase coherent. |
| `security` | Security constraints for all code. |
| `testing` | How tests are written and organized. |

## MCP servers (`.mcp.json`)

| Server | Description |
|---|---|
| `github` | GitHub repositories, issues, pull requests and Actions via the official remote MCP server. Requires `GITHUB_PERSONAL_ACCESS_TOKEN` in the environment (checked by `doctor`). |

## Docs seeds (`docs/**`, written once with `Strategy.SEED`)

| Doc | Description | Seed path(s) |
|---|---|---|
| `architecture` | System overview, boundaries and data flow. | `docs/architecture/system-overview.md` |
| `brownfield` | Machine-readable map of an existing system. | `docs/brownfield/{system-map,hotspots,critical-paths,invariants,test-gaps}.md` |
| `decisions` | Architecture decision records. | `docs/decisions/0000-template.md` |
| `evidence` | Verification evidence per story. | `docs/evidence/_template.md` |
| `operations` | Runbooks and operational knowledge. | `docs/operations/runbook.md` |
| `stories` | Stories with acceptance criteria. | `docs/stories/_template.md` |

Which of these are selected for a given project is governed by `level` and
`mode` (see `docs/CONFIGURATION.md`); any can be added or removed with
`include`/`exclude` regardless of level.
