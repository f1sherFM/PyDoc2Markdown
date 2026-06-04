# {{ module.name }}
{% if module.docstring %}

{{ module.docstring }}
{% endif %}
{% if render_options.show_toc and (module.classes or module.functions) %}

## Table of Contents
{% if module.classes %}

- [Classes](#classes)
{% for class in module.classes %}
  - [`{{ class.name }}`](#{{ anchorize(class.name) }})
{% for method in class.methods %}
    - [{% if method.is_property %}@property {% elif method.is_classmethod %}@classmethod {% elif method.is_staticmethod %}@staticmethod {% endif %}`{{ method.name }}`](#{{ method_anchor(class.name, method.name) }})
{% endfor %}
{% endfor %}
{% endif %}
{% if module.functions %}

- [Functions](#functions)
{% for func in module.functions %}
  - [`{{ func.name }}`](#{{ anchorize(func.name) }})
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

### `{{ class.name }}`{% if render_options.show_class_metadata and class.class_type != "class" %} ({{ class.class_type }}){% endif %}{% if render_options.show_class_metadata and class.is_protocol %} *(Protocol)*{% endif %}{% if render_options.show_class_metadata and class.is_abstract %} *(Abstract)*{% endif %}{% if render_options.show_class_metadata and class.is_pydantic_model %} *(Pydantic)*{% endif %}{% set class_source = source_url(class.source_path, class.line_number) %}{% if class_source %} [source]({{ class_source }}){% endif %}
{% if render_options.show_class_metadata and class.bases %}

**Bases:** `{{ class.bases | join(", ") }}`
{% endif %}
{% if class.docstring %}

{{ class.docstring }}
{% endif %}
{% if class.attributes %}

{% if render_options.compact_sections %}**Attributes:**{% else %}#### Attributes{% endif %}

| Name | Type | Description |
|------|------|-------------|
{% for attr in class.attributes %}
| `{{ attr.name }}` | {% if attr.type_hint %}`{{ attr.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if attr.description %}{{ attr.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}
{% if class.pydantic_fields %}

{% if render_options.compact_sections %}**Pydantic Fields:**{% else %}#### Pydantic Fields{% endif %}

| Name | Type | Default | Description |
|------|------|---------|-------------|
{% for field in class.pydantic_fields %}
| `{{ field.name }}` | {% if field.type_hint %}`{{ field.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if field.default %}`{{ field.default }}`{% elif field.required %}*required*{% else %}-{% endif %} | {% if field.description %}{{ field.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}
{% if class.methods %}

{% if render_options.compact_sections %}**Methods:**{% else %}#### Methods{% endif %}
{% for method in class.methods %}

<a id="{{ method_anchor(class.name, method.name) }}"></a>

##### {% if method.is_property %}@property {% elif method.is_classmethod %}@classmethod {% elif method.is_staticmethod %}@staticmethod {% endif %}`{{ method.name }}`{% set method_source = source_url(method.source_path, method.line_number) %}{% if method_source %} [source]({{ method_source }}){% endif %}
{% if method.docstring %}

{{ method.docstring }}
{% endif %}
{% if method.params %}

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
{% for param in method.params %}
| `{{ param.name }}` | {% if param.type_hint %}`{{ param.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if param.default %}`{{ param.default }}`{% else %}*required*{% endif %} | {% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}
{% if method.returns %}

**Returns:**{% if method.returns.type_hint %} `{{ method.returns.type_hint | format_type_hint | link_type }}`{% endif %}
{% if method.returns.description %}

{{ method.returns.description }}
{% endif %}
{% endif %}
{% if method.raises %}

**Raises:**
{% for raise in method.raises %}
- {% if raise.type_name %}`{{ raise.type_name }}`{% endif %}{% if raise.description %}: {{ raise.description }}{% endif %}
{% endfor %}

{% endif %}
{% endfor %}
{% endif %}

{% if not render_options.compact_sections %}---{% endif %}
{% endfor %}
{% endif %}
{% if module.functions %}

## Functions
{% for func in module.functions %}

### `{{ func.name }}`{% set func_source = source_url(func.source_path, func.line_number) %}{% if func_source %} [source]({{ func_source }}){% endif %}
{% if func.docstring %}

{{ func.docstring }}
{% endif %}
{% if func.params %}

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
{% for param in func.params %}
| `{{ param.name }}` | {% if param.type_hint %}`{{ param.type_hint | format_type_hint | link_type }}`{% else %}-{% endif %} | {% if param.default %}`{{ param.default }}`{% else %}*required*{% endif %} | {% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}
{% if func.returns %}

**Returns:**{% if func.returns.type_hint %} `{{ func.returns.type_hint | format_type_hint | link_type }}`{% endif %}
{% if func.returns.description %}

{{ func.returns.description }}
{% endif %}
{% endif %}
{% if func.raises %}

**Raises:**
{% for raise in func.raises %}
- {% if raise.type_name %}`{{ raise.type_name }}`{% endif %}{% if raise.description %}: {{ raise.description }}{% endif %}
{% endfor %}

{% endif %}
{% endfor %}
{% endif %}
