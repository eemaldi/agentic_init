# Security review

## Procedure
1. Map the attack surface of the change: entry points, trust boundaries, data stores, external calls.
2. For each entry point, ask:
   - Who can reach this, and is that verified server-side?
   - What happens with malformed, oversized or malicious input?
   - Can this leak data across tenants or users?
   - Are secrets read, logged or returned?
   - Is there injection risk (SQL, shell, template, path, SSRF, deserialization)?
3. Check new or updated dependencies for known vulnerabilities and maintenance status.
4. Confirm findings with a concrete exploit scenario or a failing test. Drop speculation.

## Output
| Severity | Location | Issue | Exploit scenario | Fix |
|---|---|---|---|---|

Read-only: never modify code during the review. Escalate critical findings to the human immediately.
