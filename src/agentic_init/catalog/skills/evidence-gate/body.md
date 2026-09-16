# Evidence gate

A task is done when evidence says so, not when the implementation looks finished.

## Procedure
1. Load the acceptance criteria{% if "stories" in selected.docs %} from `docs/stories/`{% endif %}.
2. Map each criterion to objective evidence:
   | Claim | Evidence |
   |---|---|
   | Builds | successful build output |
   | Behavior implemented | passing acceptance or integration test |
   | UI works | e2e/browser test or screenshot |
   | Migration works | migration run against a fresh database |
   | No regressions | full test suite |
   | Secure | security review with no open blocking findings |
3. Produce missing evidence by running the checks. Never infer evidence from reading code.
4. Read `.claude/state/verification.json` for the latest automated check results.
5. Write `docs/evidence/<story-slug>.md` using `docs/evidence/_template.md`.
6. Any criterion without evidence: the task is **not done**. Report the gap instead.
