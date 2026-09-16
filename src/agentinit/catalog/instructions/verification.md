## Definition of done

1. Run targeted tests{% if commands.test %}, then the suite: `{{ commands.test }}`{% endif %}.
{% if commands.lint or commands.typecheck %}
2. Run static checks: {% for key in ["lint", "typecheck"] if commands[key] %}`{{ commands[key] }}`{{ ", " if not loop.last }}{% endfor %}.
{% else %}
2. Run the project's static checks.
{% endif %}
3. Review your own diff (`git diff`) for scope creep and leftovers.
4. Report: what changed, evidence (commands run and results), residual risk, follow-ups.
{% if "verify-completion" in selected.hooks %}

A Stop hook re-runs lint, typecheck and tests on any unverified commit or change and blocks completion while they fail.
{% endif %}
{% if modules.aidlc %}

Work is complete only with evidence: run `/evidence-gate` before declaring a story done.
{% endif %}
{% if level >= 4 %}

Enterprise controls are on: Bash runs in a mandatory OS sandbox that cannot read protected paths, and MCP is limited to the servers in `.mcp.json` (binding only when managed settings set `allowManagedMcpServersOnly`).{% if "audit-log" in selected.hooks %} Every tool call is logged to `.claude/state/audit.jsonl`.{% endif %} If the sandbox blocks something you need, stop and ask the human instead of working around it.
{% elif level >= 2 %}

Bash runs in an OS sandbox that cannot read protected paths. If a command fails inside it, ask the human before running it unsandboxed; never work around it.
{% endif %}
