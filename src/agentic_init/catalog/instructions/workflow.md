## Working agreement

Autonomy: **A{{ autonomy }} ({{ autonomy_name }})**
{% if autonomy == 0 %}
- Propose plans and diffs. Do not edit files or run state-changing commands unless asked.
{% elif autonomy == 1 %}
- Implement the requested change; the human approves each edit. Do not commit.
{% elif autonomy == 2 %}
- Research, plan, implement and test on your own. Do not commit, push or open PRs unless asked.
{% elif autonomy == 3 %}
- Own the task through a pull request: branch, commit, open a PR with evidence. Never merge.
{% elif autonomy == 4 %}
- Merge low-risk changes once CI and review pass. Never deploy.
{% else %}
- Deploy only through the approved release workflow; monitor and roll back on regression.
{% endif %}
{% if autonomy > 2 %}
- Drop to A2 for schema migrations, auth, security and payment logic.
{% endif %}
{% if autonomy > 1 %}
- Drop to A1 for production infrastructure.
{% endif %}
- Escalate instead of deciding: conflicting requirements, unclear architecture or business rules, destructive or irreversible actions, security trade-offs, production incidents.
{% if selected.skills %}
- Skills: {% for name in selected.skills %}`/{{ name }}`{{ ", " if not loop.last }}{% endfor %}. Use the matching skill instead of improvising a procedure.
{% endif %}
{% if selected.agents %}
- Agents: {% for name in selected.agents %}`{{ name }}`{{ ", " if not loop.last }}{% endfor %}. The agent that writes a change never approves it; delegate review to a read-only agent.
{% endif %}
{% if level >= 2 %}

### Autonomy by change
Autonomy is per change, not per project. Raise it when verification is strong, lower it when the blast radius grows:

| Change | Autonomy |
| --- | --- |
| Formatting, docs | A{{ [autonomy + 1, 5] | min }} |
| Test cleanup, isolated bug fix | A{{ autonomy }} |
| Normal feature | A{{ autonomy }} |
| Schema or data migration | A2 |
| Auth, security or payment logic | A1–A2 |
| Production infrastructure | A0–A1 |
| Destructive production action | A0 (ask, never act) |
{% endif %}
{% if mode == "brownfield" %}

### Existing codebase
Understand before improving. Read `docs/brownfield/` first{% if "brownfield-change" in selected.skills %} and follow `/brownfield-change` for any behavior change{% endif %}. Prefer small, reversible changes.
{% endif %}
{% if modules.bmad %}

### Planning
Non-trivial features go through BMAD: brief → PRD → architecture → stories. Implement from a story, not from a chat message.
{% endif %}
{% if level >= 3 %}

### Parallel work
Use subagents for research and review: they keep exploration out of this context. Use `claude --worktree <name>` whenever more than one session edits code, so parallel work never shares a working tree.
{% endif %}
{% if workspaces %}

### Workspaces
{% for path in workspaces %}
- `{{ path }}`
{% endfor %}
Work in one workspace at a time. Keep workspace-specific conventions in `<workspace>/.claude/rules/`, not in this file, and run that workspace's tests before the full suite.
{% endif %}

### Learning loop
When a mistake repeats, fix the system, not just the instance: update this file, a rule, a skill, a hook or a test.
