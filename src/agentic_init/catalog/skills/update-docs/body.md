# Update docs

Stale project docs are worse than missing ones: every future session reads them as fact.

## Inputs
- The change that made something out of date (a diff, a release, a new subsystem).

## Procedure
1. List what the change invalidated: commands, architecture, invariants, runbooks, ADRs, acceptance criteria.
2. Check each claim against the code before rewriting it. Verify commands by running them.
3. Update the smallest correct place:
   - `CLAUDE.md`: stable, project-wide facts and commands only
   - `.claude/rules/`: constraints that apply to a scope
   - `docs/architecture/`: structure and data flow
   - `docs/decisions/`: a new ADR when a decision changed; never rewrite history in an old one
   - `docs/operations/`: runbooks
4. Delete what is no longer true instead of appending a correction next to it.
5. Keep `CLAUDE.md` short; move procedures into skills and detail into docs.
6. If commands changed, update them in `agentic_init.yaml` under `commands:` and run `agentic_init apply` so generated files follow.

## Never
- Document intended behaviour as if it exists.
- Copy the same fact into two files; link to the one that owns it.

## Report
- Files updated and what each claim now reflects
- Evidence: commands re-run, code read
- Anything you found stale but left alone, and why
