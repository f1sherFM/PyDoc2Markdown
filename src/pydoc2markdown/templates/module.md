# {{ module.name }}

{% if module.docstring %}
{{ module.docstring }}
{% endif %}

{% if module.classes or module.functions %}
## Table of Contents

{% if module.classes %}
- [Classes](#classes)
{% for class in module.classes %}
  - [`{{ class.name }}`](#{{ class.name | lower | replace(' ', '-') }})
{% if class.methods %}
{% for method in class.methods %}
    - [
{% if method.is_property %}@property {% elif method.is_classmethod %}@classmethod
{% elif method.is_staticmethod %}@staticmethod {% endif %}
`{{ method.name }}`](#{{ method.name | lower | replace(' ', '-') }})
{% endfor %}
{% endif %}
{% endfor %}
{% endif %}
{% if module.functions %}
- [Functions](#functions)
{% for func in module.functions %}
  - [`{{ func.name }}`](#{{ func.name | lower | replace(' ', '-') }})
{% endfor %}
{% endif %}
{% endif %}

{% if module.public_api %}
**Public API:**
{% for name in module.public_api %}
- `{{ name }}`
{% endfor %}
{% endif %}

{% if module.classes %}
## Classes

{% for class in module.classes %}
### `{{ class.name }}`{% if class.class_type != "class" %} ({{ class.class_type }}){% endif %}

{% if class.bases %}
**Bases:** `{{ class.bases | join(", ") }}`
{% endif %}

{% if class.docstring %}
{{ class.docstring }}
{% endif %}

{% if class.attributes %}
#### Attributes

| Name | Type | Description |
|------|------|-------------|
{% for attr in class.attributes %}
| `{{ attr.name }}` | {% if attr.type_hint %}`{{ attr.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if attr.description %}{{ attr.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if class.methods %}
#### Methods

{% for method in class.methods %}
##### {% if method.is_property %}@property {% elif method.is_classmethod %}@classmethod {% elif method.is_staticmethod %}@staticmethod {% endif %}`{{ method.name }}`

{% if method.docstring %}
{{ method.docstring }}
{% endif %}

{% if method.params %}
**Parameters:**

| Name | Type | Description |
|------|------|-------------|
{% for param in method.params %}
| `{{ param.name }}` | {% if param.type_hint %}`{{ param.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if method.returns %}
**Returns:**{% if method.returns.type_hint %} `{{ method.returns.type_hint | format_type_hint | link_type }}`{% endif %}

{% if method.returns.description %}{{ method.returns.description }}{% endif %}
{% endif %}

{% if method.raises %}
**Raises:**
{% for raise in method.raises %}
- {% if raise.type_name %}`{{ raise.type_name }}`{% endif %}{% if raise.description %}: {{ raise.description }}{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

---
{% endfor %}
{% endif %}

{% if module.functions %}
## Functions

{% for func in module.functions %}
### `{{ func.name }}`

{% if func.docstring %}
{{ func.docstring }}
{% endif %}

{% if func.params %}
**Parameters:**

| Name | Type | Description |
|------|------|-------------|
{% for param in func.params %}
| `{{ param.name }}` | {% if param.type_hint %}`{{ param.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if func.returns %}
**Returns:**{% if func.returns.type_hint %} `{{ func.returns.type_hint | format_type_hint | link_type }}`{% endif %}

{% if func.returns.description %}{{ func.returns.description }}{% endif %}
{% endif %}

{% if func.raises %}
**Raises:**
{% for raise in func.raises %}
- {% if raise.type_name %}`{{ raise.type_name }}`{% endif %}{% if raise.description %}: {{ raise.description }}{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}
