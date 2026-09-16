# Security rules

- Never read, print, log or commit secrets. Configuration comes from the environment.
- Validate and bound all external input at the boundary.
- Use parameterized queries and argument arrays; never build SQL or shell commands by string concatenation.
- Enforce authorization server-side on every request, per resource.
- Do not disable TLS verification, CSRF protection or security headers.
- Changes to auth, crypto, permissions or payment flows require human approval.
