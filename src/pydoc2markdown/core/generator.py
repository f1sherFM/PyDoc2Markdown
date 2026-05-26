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
{% if attr.type_hint %}`{{ attr.type_hint | format_type_hint }}`{% else %}-{% endif %} |
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
{% if param.type_hint %}`{{ param.type_hint | format_type_hint }}`{% else %}-{% endif %} |
{% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if method.returns %}
**Returns:**
{% if method.returns.type_hint %} `{{ method.returns.type_hint | format_type_hint }}`{% endif %}

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
{% if param.type_hint %}`{{ param.type_hint | format_type_hint }}`{% else %}-{% endif %} |
{% if param.description %}{{ param.description }}{% else %}-{% endif %} |
{% endfor %}
{% endif %}

{% if func.returns %}
**Returns:**
{% if func.returns.type_hint %} `{{ func.returns.type_hint | format_type_hint }}`{% endif %}

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

    def __init__(
        self,
        template_path: Path | None = None,
        theme: str = "default",
    ) -> None:
        """Initialize the generator with an optional custom template or theme."""
        self._template_path = template_path
        self._theme = theme
        self._env = self._create_environment()

    def _create_environment(self) -> Environment:
        """Create and configure the Jinja2 environment."""
        from pydoc2markdown.core.type_hints import format_type_hint

        if self._template_path and self._template_path.exists():
            env = Environment(
                loader=FileSystemLoader(str(self._template_path.parent)),
                autoescape=select_autoescape(),
            )
        else:
            env = Environment(
                loader=PackageLoader("pydoc2markdown", "templates"),
                autoescape=select_autoescape(),
            )
        from pydoc2markdown.core.crossref import link_type_filter

        env.filters["format_type_hint"] = format_type_hint
        env.filters["link_type"] = link_type_filter
        return env

    def _resolve_template_name(self) -> str:
        """Resolve the template file name based on theme or custom path."""
        if self._template_path:
            return self._template_path.name
        if self._theme == "default":
            return "module.md"
        return f"{self._theme}.md"

    def generate(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
    ) -> list[Path]:
        """Generate Markdown files for the given modules."""
        from pydoc2markdown.core.crossref import TypeIndex

        output_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        template_name = self._resolve_template_name()
        logger.debug("Using template: %s", template_name)
        template = self._env.get_template(template_name)
        type_index = TypeIndex.from_modules(modules)

        for module in modules:
            if module.package:
                module_dir = output_dir / module.package.replace(".", "/")
                module_dir.mkdir(parents=True, exist_ok=True)
                output_path = module_dir / f"{module.name}.md"
            else:
                output_path = output_dir / f"{module.name}.md"
            logger.debug("Generating %s", output_path)
            content = template.render(module=module, type_index=type_index)
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
        """Generate an index.md with links to all module docs, grouped by package."""
        if not modules:
            return None

        from collections import OrderedDict

        groups: OrderedDict[str, list[ModuleDoc]] = OrderedDict()
        for module in sorted(modules, key=lambda m: (m.package, m.name)):
            groups.setdefault(module.package, []).append(module)

        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) for m in modules)

        lines = ["# Documentation Index", ""]
        lines.append(
            f"**Overview:** {len(modules)} modules, "
            f"{total_classes} classes, "
            f"{total_functions} functions."
        )
        lines.append("")

        for package, mods in groups.items():
            if package:
                lines.append(f"## Package `{package}`")
                # Try to find __init__ module for package description
                init_mod = next((m for m in mods if m.name == "__init__"), None)
                if init_mod and init_mod.docstring:
                    first_line = init_mod.docstring.strip().split("\n")[0]
                    lines.append(f"\n{first_line}\n")
            else:
                lines.append("## Modules")
                lines.append("")

            for module in mods:
                if module.name == "__init__":
                    continue
                rel_path = (
                    f"{module.package.replace('.', '/')}/{module.name}.md"
                    if module.package
                    else f"{module.name}.md"
                )
                stats_parts: list[str] = []
                if module.classes:
                    stats_parts.append(f"{len(module.classes)} class(es)")
                if module.functions:
                    stats_parts.append(f"{len(module.functions)} function(s)")
                stats = f" — {', '.join(stats_parts)}" if stats_parts else ""
                lines.append(f"- [{module.name}]({rel_path}){stats}")
                if module.docstring:
                    first_line = module.docstring.strip().split("\n")[0]
                    lines.append(f"  > {first_line}")
            lines.append("")

        index_path = output_dir / "index.md"
        logger.debug("Generating %s", index_path)
        index_path.write_text("\n".join(lines), encoding="utf-8")
        return index_path

    def generate_single_file(
        self,
        modules: list[ModuleDoc],
        output_path: Path,
    ) -> Path:
        """Generate a single combined Markdown file for all modules.

        Args:
            modules: List of parsed modules.
            output_path: File path for the combined Markdown output.

        Returns:
            Path to the generated file.
        """
        from pydoc2markdown.core.crossref import TypeIndex

        output_path.parent.mkdir(parents=True, exist_ok=True)

        template_name = self._resolve_template_name()
        template = self._env.get_template(template_name)
        type_index = TypeIndex.from_modules(modules)

        lines: list[str] = ["# Documentation", ""]

        # Table of contents for all modules
        if modules:
            lines.append("## Modules")
            for module in sorted(modules, key=lambda m: (m.package, m.name)):
                lines.append(f"- {module.name}")
            lines.append("")

        # Render each module and concatenate
        for module in sorted(modules, key=lambda m: (m.package, m.name)):
            content = template.render(module=module, type_index=type_index)
            lines.append(content)
            lines.append("---")
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("Generated single file: %s", output_path)
        return output_path

    def generate_string(self, module: ModuleDoc) -> str:
        """Generate Markdown content as a string for a single module."""
        from jinja2 import Environment

        from pydoc2markdown.core.crossref import TypeIndex
        from pydoc2markdown.core.type_hints import format_type_hint

        env = Environment()
        from pydoc2markdown.core.crossref import link_type_filter

        env.filters["format_type_hint"] = format_type_hint
        env.filters["link_type"] = link_type_filter
        template = env.from_string(self.DEFAULT_TEMPLATE)
        type_index = TypeIndex.from_modules([module])
        return template.render(module=module, type_index=type_index)
