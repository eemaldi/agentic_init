# Test

## Procedure
1. Identify the behavior under test and its contract (inputs, outputs, side effects, errors).
2. Find the existing test style, fixtures and helpers; follow them.
3. Cover, in order: the happy path, boundaries, invalid input, failure of dependencies, concurrency or ordering where relevant.
4. Test behavior through public interfaces, not implementation details. Mock only at system boundaries.
5. Run the new tests and confirm they fail without the change (or would have caught the bug).
6. Run the suite{% if commands.test %}: `{{ commands.test }}`{% endif %}.
{% if commands.e2e %}
7. For user-facing flows, run end-to-end tests: `{{ commands.e2e }}`.
{% endif %}

## Report
- Tests added or changed, and what behavior each proves
- Commands run with pass/fail counts
- Remaining untested risk
