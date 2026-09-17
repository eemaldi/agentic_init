{% set has_docs = selected.docs or selected.rules or ci %}
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
- `docs/brownfield/`: system map, critical paths, invariants, hotspots, test gaps, migration plan.
{% endif %}
{% if "evidence" in selected.docs %}
- `docs/evidence/`: verification evidence per story.
{% endif %}
{% if ci %}
- `.github/`: CI checks and the pull request template.
{% endif %}
{% if level >= 2 %}

Start a task by loading context in this order: this file, the rules for the area you are touching, the story or issue, the docs above for that subsystem, then the code. Pick the matching skill before improvising, and delegate research to a subagent instead of filling this context with it.
{% endif %}

Keep this file short and stable. Procedures belong in skills, details in docs.
{% endif %}
