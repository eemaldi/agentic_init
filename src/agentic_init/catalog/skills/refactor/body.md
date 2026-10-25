# Refactor

## Inputs
- The code to restructure and the specific problem with it (duplication, coupling, unclear naming, dead code).

## Procedure
1. Name the problem in one sentence. No problem, no refactor.
2. Establish the safety net: find the tests that cover this behaviour. Missing or thin: write characterization tests first and commit them separately.
3. Record the current behaviour you must preserve, including error cases and side effects.
4. Refactor in small steps. After each step run {% if commands.test %}`{{ commands.test }}`{% else %}the test suite{% endif %}; keep it green.
5. Keep behaviour changes out. A bug you find becomes a separate task, not part of this diff.
6. Run {% for key in ["lint", "typecheck"] if commands[key] %}`{{ commands[key] }}`{{ ", " if not loop.last }}{% else %}the static checks{% endfor %} and re-read the diff.

## Never
- Mix a refactor with a feature or a fix in one commit.
- Change public APIs, serialized formats or database schemas under the label "refactor".
- Delete tests that became inconvenient.

## Report
- The problem, the structural change, and why it is safe
- Evidence: tests run before and after
- Behaviour deliberately left unchanged, and follow-ups
