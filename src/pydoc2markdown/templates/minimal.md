# {{ module.name }}
{% if module.docstring %}

{{ module.docstring }}
{% endif %}
{% if module.attributes %}

## Attributes
{% for attr in module.attributes %}

### `{{ attr.name }}`
{% if attr.description %}

{{ attr.description }}
{% endif %}
{% endfor %}
{% endif %}
{% if module.classes %}

## Classes
{% for class in module.classes %}

### `{{ class.name }}`{% if class.class_type != "class" %} ({{ class.class_type }}){% endif %}{% set class_source = source_url(class.source_path, class.line_number) %}{% if class_source %} [source]({{ class_source }}){% endif %}
{% if class.docstring %}

{{ class.docstring }}
{% endif %}
{% endfor %}
{% endif %}
{% if module.functions %}

## Functions
{% for func in module.functions %}

### `{{ func.name }}`{% set func_source = source_url(func.source_path, func.line_number) %}{% if func_source %} [source]({{ func_source }}){% endif %}
{% if func.docstring %}

{{ func.docstring }}
{% endif %}
{% endfor %}
{% endif %}
