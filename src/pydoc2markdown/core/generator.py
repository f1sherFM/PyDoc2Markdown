"""Markdown documentation generator."""

import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from pydoc2markdown.core.parser import ModuleDoc

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Generate Markdown files from parsed Python documentation."""

    DEFAULT_TEMPLATE = """# {{ module.name }}

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
| `{{ attr.name }}` |
{% if attr.type_hint %}`{{ attr.type_hint }}`{% else %}-{% endif %} |
{% if attr.description %}{{ attr.description }}{% else %}-{% endif %} |
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
| `{{ param.name }}` |
{% if param.type_hint %}`{{ param.type_hint }}`{% else %}-{% endif %} |
{% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if method.returns %}
**Returns:**{% if method.returns.type_hint %} `{{ method.returns.type_hint }}`{% endif %}

{% if method.returns.description %}{{ method.returns.description }}{% endif %}
{% endif %}

{% if method.raises %}
**Raises:**
{% for raise in method.raises %}
- {% if raise.type_name %}`{{ raise.type_name }}`{% endif %}
{% if raise.description %}: {{ raise.description }}{% endif %}
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
| `{{ param.name }}` |
{% if param.type_hint %}`{{ param.type_hint }}`{% else %}-{% endif %} |
{% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if func.returns %}
**Returns:**{% if func.returns.type_hint %} `{{ func.returns.type_hint }}`{% endif %}

{% if func.returns.description %}{{ func.returns.description }}{% endif %}
{% endif %}

{% if func.raises %}
**Raises:**
{% for raise in func.raises %}
- {% if raise.type_name %}`{{ raise.type_name }}`{% endif %}
{% if raise.description %}: {{ raise.description }}{% endif %}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}
"""

    def __init__(self, template_path: Path | None = None) -> None:
        """Initialize the generator with an optional custom template."""
        self._template_path = template_path
        self._env = self._create_environment()

    def _create_environment(self) -> Environment:
        """Create and configure the Jinja2 environment."""
        if self._template_path and self._template_path.exists():
            return Environment(
                loader=FileSystemLoader(str(self._template_path.parent)),
                autoescape=select_autoescape(),
            )
        return Environment(
            loader=PackageLoader("pydoc2markdown", "templates"),
            autoescape=select_autoescape(),
        )

    def generate(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
    ) -> list[Path]:
        """Generate Markdown files for the given modules."""
        output_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        template_name = self._template_path.name if self._template_path else "module.md"
        logger.debug("Using template: %s", template_name)
        template = self._env.get_template(template_name)

        for module in modules:
            output_path = output_dir / f"{module.name}.md"
            logger.debug("Generating %s", output_path)
            content = template.render(module=module)
            output_path.write_text(content, encoding="utf-8")
            generated.append(output_path)

        return generated

    def generate_string(self, module: ModuleDoc) -> str:
        """Generate Markdown content as a string for a single module."""
        from jinja2 import Template

        template = Template(self.DEFAULT_TEMPLATE)
        return template.render(module=module)
