---
name: implement
description: Implement a well-defined change from acceptance criteria through tests and verified evidence. Use for any feature or fix with clear requirements.
---

# Implement

## Inputs
- The task, story or issue with acceptance criteria. Missing criteria: write them down and confirm before coding.

## Procedure
1. Read the acceptance criteria and restate them as a checklist.
2. Locate the affected code, its callers and its tests. Reuse existing utilities before writing new ones.
3. List the files you expect to change. More than expected mid-task: stop and re-plan.
4. Write or update a failing test that captures the requirement.
5. Implement the smallest coherent change that makes it pass.
6. Run targeted tests: `uv run pytest path/to/test_file.py::test_name`.
7. Run `uv run ruff check .`, `uv run pytest`.
8. Review the full diff. Remove debug output, dead code and unrelated edits.
9. Delegate review to the `reviewer` agent; resolve blocking findings.

## Never
- Add a dependency without checking for an existing equivalent.
- Change public APIs, schemas or configuration beyond the task scope without asking.
- Declare done without running the checks above.

## Report
- Changes (files and why)
- Evidence: commands run and their results
- Unresolved risks and follow-ups
