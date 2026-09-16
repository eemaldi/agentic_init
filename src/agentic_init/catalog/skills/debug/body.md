# Debug

## Procedure
1. Reproduce. Capture the exact command, input and output. Cannot reproduce: gather logs and stop to ask.
2. Write a failing test that reproduces the bug.
3. Form hypotheses ranked by likelihood. For each, name the observation that would confirm or refute it.
4. Test the cheapest hypothesis first: read code paths, add temporary logging, bisect with `git log`/`git bisect`.
5. Identify the root cause, not the first symptom. Ask "why" until the answer is a code or data defect.
6. Fix the root cause with the smallest change. Remove temporary logging.
7. Confirm the failing test now passes and the suite is green{% if commands.test %} (`{{ commands.test }}`){% endif %}.
8. Search for the same defect pattern elsewhere.

## Report
- Root cause (one paragraph)
- Fix and regression test
- Other places with the same pattern
- What would have caught this earlier (rule, hook, test), as a follow-up
