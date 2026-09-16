## Commands

{% set labels = {"install": "Install", "dev": "Run locally", "build": "Build", "test": "Test (all)", "test_one": "Test (single)", "lint": "Lint", "format": "Format", "typecheck": "Typecheck", "e2e": "End-to-end"} %}
{% for name, label in labels.items() if commands[name] %}
- {{ label }}: `{{ commands[name] }}`
{% else %}
- No commands detected yet. Add them under `commands:` in `agentinit.yaml` and run `agentinit apply`.
{% endfor %}

Use these commands instead of guessing. If a command you need is missing, ask, then record it here.
