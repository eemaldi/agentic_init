# Review

## Inputs
- A diff: `git diff <base>...HEAD`, a PR number, or staged changes.

## Procedure
1. Read the intent (story, PR description, commit messages) before the code.
2. Read the full diff, then the surrounding code of every changed function.
3. Check:
   - Correctness: logic, edge cases, error handling, null/empty input
   - Compatibility: public APIs, persisted data, configuration, migrations
   - Concurrency and partial failure
   - Security: input validation, authz, secrets, injection
   - Tests: does a test fail if the change is reverted?
   - Simplicity: duplication, dead code, unnecessary abstraction
4. For each suspected issue, confirm it by reading code or running a check. Drop what you cannot confirm.

## Output
1. Blocking issues (with file:line and a concrete failure scenario)
2. Non-blocking improvements
3. Missing tests
4. Residual risk

Do not edit files while reviewing.
