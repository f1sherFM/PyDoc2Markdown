# {{ module.name }}

{% if module.docstring %}
{{ module.docstring }}
{% endif %}

{% if module.classes %}
## Classes

{% for class in module.classes %}
### `{{ class.name }}`

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
| `{{ attr.name }}` | {% if attr.type_hint %}`{{ attr.type_hint }}`{% else %}-{% endif %} | {% if attr.description %}{{ attr.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if class.methods %}
#### Methods

{% for method in class.methods %}
##### `{{ method.name }}`

{% if method.docstring %}
{{ method.docstring }}
{% endif %}

{% if method.params %}
**Parameters:**

| Name | Type | Description |
|------|------|-------------|
{% for param in method.params %}
| `{{ param.name }}` | {% if param.type_hint %}`{{ param.type_hint }}`{% else %}-{% endif %} | {% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if method.returns %}
**Returns:**{% if method.returns.type_hint %} `{{ method.returns.type_hint }}`{% endif %}

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
| `{{ param.name }}` | {% if param.type_hint %}`{{ param.type_hint }}`{% else %}-{% endif %} | {% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if func.returns %}
**Returns:**{% if func.returns.type_hint %} `{{ func.returns.type_hint }}`{% endif %}

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
