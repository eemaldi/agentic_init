---
name: test
description: Design and run tests for a change, filling coverage gaps for behavior, edge cases and failure modes. Use when adding tests or when verification is missing.
---

# Test

## Procedure
1. Identify the behavior under test and its contract (inputs, outputs, side effects, errors).
2. Find the existing test style, fixtures and helpers; follow them.
3. Cover, in order: the happy path, boundaries, invalid input, failure of dependencies, concurrency or ordering where relevant.
4. Test behavior through public interfaces, not implementation details. Mock only at system boundaries.
5. Run the new tests and confirm they fail without the change (or would have caught the bug).
6. Run the suite: `uv run pytest`.

## Report
- Tests added or changed, and what behavior each proves
- Commands run with pass/fail counts
- Remaining untested risk
