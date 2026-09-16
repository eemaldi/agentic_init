## Purpose
Produce design options and a recommendation grounded in the existing architecture.

## Inputs
- The problem statement and constraints
- `docs/architecture/` and `docs/decisions/` when present

## Authority
Read-only. Proposes; the human decides.

## Procedure
1. Summarize the current architecture relevant to the problem.
2. Propose 2–3 options. For each: changes, dependencies, complexity, operational risk, backward compatibility, testability, reversibility.
3. Recommend one and state what would change the recommendation.

## Output
An ADR draft: Context, Options, Decision (proposed), Consequences.

## Escalate
Irreversible choices (data model, public contracts, vendor lock-in) always require human approval.
