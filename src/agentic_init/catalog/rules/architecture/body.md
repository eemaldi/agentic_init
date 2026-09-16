# Architecture rules

- Follow existing module boundaries; do not import across them in new directions without an ADR.
- Keep domain logic independent of frameworks, transport and persistence.
- Prefer extending an existing abstraction over creating a parallel one.
- Do not introduce new dependencies, services or datastores without checking for existing equivalents and asking.
- Generated files are never edited by hand; change the generator.
{% if "decisions" in selected.docs %}
- Record significant decisions as ADRs in `docs/decisions/`.
{% endif %}
