# Discover

## Procedure
1. Read the entry points: manifests, main modules, routing, CLI or job definitions.
2. Identify components and their boundaries, data stores, external integrations, and deployment units.
3. Trace one representative request or job end to end.
4. Map tests: where they live, what they cover, how to run them, notable gaps.
5. Record invariants: rules the code relies on that are not enforced by types or tests.
6. Record hotspots: complex, frequently changed or fragile areas.
{% if "brownfield" in selected.docs %}
7. Write findings to `docs/brownfield/` (system-map, critical-paths, invariants, hotspots, test-gaps). Update, never duplicate.
{% elif "architecture" in selected.docs %}
7. Write findings to `docs/architecture/`. Update, never duplicate.
{% else %}
7. Summarize findings; propose where to store them durably.
{% endif %}

State uncertainty explicitly: mark unverified claims with `(unverified)`.
