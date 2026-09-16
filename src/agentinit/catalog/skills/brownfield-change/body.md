# Brownfield change

## Before editing
1. Locate the affected subsystem in `docs/brownfield/system-map.md`. Missing: run `/discover` for it first.
2. List invariants and critical paths the change touches (`docs/brownfield/invariants.md`, `critical-paths.md`).
3. Find the tests that exercise the code. None: write characterization tests that pin current behavior.
4. Identify external dependents: APIs, persisted data, events, other services, scheduled jobs.
5. Identify backward-compatibility constraints.
6. Write the blast radius: what could break, how you would notice, how to roll back.
7. Blast radius crosses a critical path or invariant: stop and get human approval.

## Editing
- Change behavior in small, separately verifiable steps.
- Keep old and new paths side by side (flag, adapter) when the change is not trivially reversible.

## After
- Run characterization and targeted tests, then the suite.
- Update `docs/brownfield/` with anything learned.
