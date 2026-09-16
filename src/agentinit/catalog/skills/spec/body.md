# Spec

## Procedure
1. Restate the intent in one sentence: who needs what, and why.
2. Research the relevant code and docs. List what exists and what must change.
3. Surface ambiguities as explicit questions. Ask them; do not assume business rules.
4. Write the story using the template below{% if "stories" in selected.docs %} in `docs/stories/<slug>.md`{% endif %}.
5. Every acceptance criterion must be verifiable by a test or a command.

## Template
```md
# <Title>

## Goal
## Context
## Constraints
## Acceptance criteria
- [ ] ...
## Verification
## Authority
- May modify: ...
- Must not modify: ...
## Out of scope
```
