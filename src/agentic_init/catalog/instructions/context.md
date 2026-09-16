{% set has_docs = selected.docs or selected.rules %}
{% if has_docs %}
## Where to look

{% if selected.rules %}
- `.claude/rules/`: {{ selected.rules | join(", ") }} rules, loaded when relevant.
{% endif %}
{% if "architecture" in selected.docs %}
- `docs/architecture/`: system overview, boundaries, data flow.
{% endif %}
{% if "decisions" in selected.docs %}
- `docs/decisions/`: ADRs. Record every significant architectural decision.
{% endif %}
{% if "stories" in selected.docs %}
- `docs/stories/`: specs with acceptance criteria.
{% endif %}
{% if "operations" in selected.docs %}
- `docs/operations/`: runbooks.
{% endif %}
{% if "brownfield" in selected.docs %}
- `docs/brownfield/`: system map, critical paths, invariants, hotspots, test gaps.
{% endif %}
{% if "evidence" in selected.docs %}
- `docs/evidence/`: verification evidence per story.
{% endif %}

Keep this file short and stable. Procedures belong in skills, details in docs.
{% endif %}
