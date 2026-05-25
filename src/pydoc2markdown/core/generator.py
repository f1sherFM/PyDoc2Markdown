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
| `{{ attr.name }}` |
{% if attr.type_hint %}`{{ attr.type_hint }}`{% else %}-{% endif %} |
{% if attr.description %}{{ attr.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if class.methods %}
#### Methods

{% for method in class.methods %}
{% if method.is_property %}##### @property `{{ method.name }}`
{% elif method.is_classmethod %}##### @classmethod `{{ method.name }}`
{% elif method.is_staticmethod %}##### @staticmethod `{{ method.name }}`
{% else %}##### `{{ method.name }}`
{% endif %}

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

        index_path = self._generate_index(modules, output_dir)
        if index_path:
            generated.append(index_path)

        return generated

    def _generate_index(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
    ) -> Path | None:
        """Generate an index.md with links to all module docs."""
        if not modules:
            return None

        lines = ["# Index", ""]
        for module in modules:
            filename = f"{module.name}.md"
            lines.append(f"- [{module.name}]({filename})")
            if module.docstring:
                first_line = module.docstring.split("\n")[0]
                lines.append(f"  - {first_line}")
        lines.append("")

        index_path = output_dir / "index.md"
        logger.debug("Generating %s", index_path)
        index_path.write_text("\n".join(lines), encoding="utf-8")
        return index_path

    def generate_string(self, module: ModuleDoc) -> str:
        """Generate Markdown content as a string for a single module."""
        from jinja2 import Template

        template = Template(self.DEFAULT_TEMPLATE)
        return template.render(module=module)
