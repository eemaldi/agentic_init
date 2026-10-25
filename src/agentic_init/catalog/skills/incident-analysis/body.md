# Incident analysis

Production incidents are escalation territory: gather and propose, let the human decide on mitigations that change production.

## Inputs
- The symptom, when it started, the affected users or endpoints, and access to logs, traces and the deploy history.

## Procedure
1. Write down the symptom and the impact, with timestamps and a timezone.
2. Build the timeline: deploys, config and feature-flag changes, infrastructure events, traffic shifts around the start time.
3. Correlate with telemetry: error rates, latency, saturation, and the first occurrence of the error signature.
4. Form the smallest hypothesis that explains the timeline, then look for evidence that would falsify it.
5. Identify the contributing causes, not one culprit: the trigger, what let it through, and what delayed detection.
6. Propose mitigation (stop the bleeding) and remediation (fix the cause) separately, with the risk of each.
7. Record the findings in `docs/operations/` and add a regression test that would have caught it.

## Never
- Change production state, roll back or flip a flag on your own; propose it and wait for a human.
- Declare a root cause you cannot show evidence for.
- Close an incident without a durable follow-up: a test, an alert, a runbook entry or a guardrail.

## Report
- Timeline, impact, contributing causes
- Evidence: the specific logs, traces and commits that support each conclusion
- Proposed mitigation and remediation, with risks and follow-ups
