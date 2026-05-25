# {{ module.name }}

{% if module.docstring %}
{{ module.docstring }}
{% endif %}

{% if module.classes %}
## Classes

{% for class in module.classes %}
### `{{ class.name }}`{% if class.class_type != "class" %} ({{ class.class_type }}){% endif %}

{% if class.docstring %}
{{ class.docstring }}
{% endif %}

{% endfor %}
{% endif %}

{% if module.functions %}
## Functions

{% for func in module.functions %}
### `{{ func.name }}`

{% if func.docstring %}
{{ func.docstring }}
{% endif %}

{% endfor %}
{% endif %}
