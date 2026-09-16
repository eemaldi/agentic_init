# Implement

## Inputs
- The task, story or issue with acceptance criteria. Missing criteria: write them down and confirm before coding.

## Procedure
1. Read the acceptance criteria and restate them as a checklist.
2. Locate the affected code, its callers and its tests. Reuse existing utilities before writing new ones.
3. List the files you expect to change. More than expected mid-task: stop and re-plan.
4. Write or update a failing test that captures the requirement.
5. Implement the smallest coherent change that makes it pass.
{% if commands.test_one %}
6. Run targeted tests: `{{ commands.test_one }}`.
{% else %}
6. Run the targeted tests for the changed code.
{% endif %}
7. Run {% for key in ["lint", "typecheck", "test"] if commands[key] %}`{{ commands[key] }}`{{ ", " if not loop.last }}{% else %}the project's lint, typecheck and test commands{% endfor %}.
8. Review the full diff. Remove debug output, dead code and unrelated edits.
{% if "reviewer" in selected.agents %}
9. Delegate review to the `reviewer` agent; resolve blocking findings.
{% endif %}

## Never
- Add a dependency without checking for an existing equivalent.
- Change public APIs, schemas or configuration beyond the task scope without asking.
- Declare done without running the checks above.

## Report
- Changes (files and why)
- Evidence: commands run and their results
- Unresolved risks and follow-ups
