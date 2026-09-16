# Testing rules

- Every behavior change comes with a test that fails without it.
- Test through public interfaces; mock only at system boundaries (network, clock, filesystem, third-party APIs).
- One behavior per test; name tests after the behavior, not the method.
- No sleeps or real network calls in unit tests. Flaky tests are bugs.
- Never weaken or delete an assertion to make a test pass without explaining why in the report.
