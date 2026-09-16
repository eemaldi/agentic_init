# {{ project.name }}
{% if project.description %}

{{ project.description }}
{% endif %}
{% if stack.languages or stack.frameworks %}

## Stack
{% if stack.languages %}
- Languages: {{ stack.languages | join(", ") }}
{% endif %}
{% if stack.frameworks %}
- Frameworks: {{ stack.frameworks | join(", ") }}
{% endif %}
{% if stack.package_managers %}
- Package managers: {{ stack.package_managers | join(", ") }}
{% endif %}
{% endif %}
