"""Tests for MarkdownGenerator."""

from pathlib import Path

import pytest

from pydoc2markdown.core.generator import (
    README_END_MARKER,
    README_START_MARKER,
    MarkdownGenerator,
    OutputOptions,
)
from pydoc2markdown.core.parser import DocstringParser


def test_generate_single_module(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    paths = generator.generate(modules, output_dir)

    assert len(paths) == 2  # module + index.md
    module_path = output_dir / "sample_module.md"
    assert module_path.exists()
    content = module_path.read_text()
    assert "Calculator" in content
    assert "greet" in content


def test_generate_string(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    content = generator.generate_string(modules[0])

    assert "# sample_module" in content
    assert "## Table of Contents" in content
    assert "## Classes" in content
    assert "## Functions" in content


def test_generate_string_formats_type_hints_and_crossrefs(
    typed_module: Path,
    crossref_module: Path,
) -> None:
    parser = DocstringParser()
    generator = MarkdownGenerator()

    typed_content = generator.generate_string(parser.parse(typed_module)[0])
    assert "str | None" in typed_content
    assert "list[int]" in typed_content

    crossref_content = generator.generate_string(parser.parse(crossref_module)[0])
    assert "[UserProfile](#userprofile)" in crossref_content
    assert "[User](#user)" in crossref_content


def test_generate_string_uses_configured_theme(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator(theme="minimal")
    content = generator.generate_string(modules[0])

    assert "# sample_module" in content
    assert "## Classes" in content
    assert "## Table of Contents" not in content


def test_generate_creates_output_dir(tmp_path: Path) -> None:
    parser = DocstringParser()
    module = tmp_path / "empty.py"
    module.write_text('"""Empty module."""\n', encoding="utf-8")
    modules = parser.parse(module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "nested" / "docs"
    paths = generator.generate(modules, output_dir)

    assert output_dir.exists()
    assert len(paths) == 2  # module + index.md


def test_generate_index(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    index_path = output_dir / "index.md"
    assert index_path.exists()
    content = index_path.read_text()
    assert "# Documentation Index" in content
    assert "**Overview:**" in content
    assert "[sample_module](sample_module.md)" in content
    assert "1 class(es)" in content
    assert "1 function(s)" in content


def test_generate_toc_in_module(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    module_path = output_dir / "sample_module.md"
    content = module_path.read_text()
    assert "## Table of Contents" in content
    assert "[Classes](#classes)" in content
    assert "[Functions](#functions)" in content


def test_generate_string_normalizes_toc_links_and_spacing(tmp_path: Path) -> None:
    module = tmp_path / "formatted.py"
    module.write_text(
        '''"""Formatting sample."""

class Example:
    """Example class."""

    def run(self, value: int) -> None:
        """Run the example.

        Args:
            value: Input value.
        """
''',
        encoding="utf-8",
    )

    parsed = DocstringParser().parse(module)
    content = MarkdownGenerator().generate_string(parsed[0])

    assert "- [`run`](#example-run)" in content
    assert "[\n" not in content
    assert "\n\n\n" not in content
    assert "| `value` | `int` | *required* | Input value. |" in content


def test_generate_package_grouping(tmp_path: Path) -> None:
    pkg = tmp_path / "my_pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)
    (pkg / "top.py").write_text('"""Top module."""\n', encoding="utf-8")
    (sub / "nested.py").write_text('"""Nested module."""\n', encoding="utf-8")

    parser = DocstringParser()
    modules = parser.parse(pkg, recursive=True)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    assert (output_dir / "top.md").exists()
    assert (output_dir / "sub" / "nested.md").exists()

    index = output_dir / "index.md"
    assert index.exists()
    content = index.read_text()
    assert "## Package `sub`" in content
    assert "[nested](sub/nested.md)" in content
    assert "**Overview:**" in content


def test_generate_navigation_layout(tmp_path: Path) -> None:
    pkg = tmp_path / "my_pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)
    (pkg / "top.py").write_text('"""Top module."""\n', encoding="utf-8")
    (sub / "nested.py").write_text(
        '''"""Nested module."""

def helper() -> None:
    """Help with something."""
''',
        encoding="utf-8",
    )

    parser = DocstringParser()
    modules = parser.parse(pkg, recursive=True)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    paths = generator.generate_navigation(modules, output_dir)

    assert output_dir.exists()
    assert (output_dir / "api" / "top.md").exists()
    assert (output_dir / "api" / "sub" / "nested.md").exists()
    assert (output_dir / "index.md").exists()
    assert (output_dir / "modules.md").exists()
    assert (output_dir / "sub.md").exists()
    assert len(paths) == 5

    index_content = (output_dir / "index.md").read_text(encoding="utf-8")
    assert "# Documentation" in index_content
    assert "[Modules](modules.md)" in index_content
    assert "[sub](sub.md)" in index_content
    assert "[`top`](api/top.md)" in index_content
    assert "[`sub.nested`](api/sub/nested.md)" in index_content
    assert " - 1 function(s)" in index_content

    package_content = (output_dir / "sub.md").read_text(encoding="utf-8")
    assert "# sub" in package_content
    assert "[`sub.nested`](api/sub/nested.md)" in package_content
    assert " — " not in package_content


def test_generate_navigation_uses_custom_api_dir(
    sample_module: Path,
    tmp_path: Path,
) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    output_dir = tmp_path / "docs"
    MarkdownGenerator().generate_navigation(modules, output_dir, api_dir=Path("reference"))

    assert (output_dir / "reference" / "sample_module.md").exists()
    content = (output_dir / "index.md").read_text(encoding="utf-8")
    assert "[`sample_module`](reference/sample_module.md)" in content


def test_generate_minimal_theme(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator(theme="minimal")
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    module_path = output_dir / "sample_module.md"
    content = module_path.read_text()
    assert "# sample_module" in content
    assert "## Classes" in content
    assert "## Table of Contents" not in content


def test_generate_type_hint_formatting(typed_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(typed_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    module_path = output_dir / "typed_module.md"
    content = module_path.read_text()
    assert "str | None" in content
    assert "int | str" in content
    assert "list[int]" in content
    assert "list[str]" in content


def test_generate_parameter_defaults(tmp_path: Path) -> None:
    module = tmp_path / "defaults.py"
    module.write_text(
        '''"""Defaults module."""

def connect(host: str, port: int = 8080, *, timeout: float = 30.0) -> None:
    """Connect to a service.

    Args:
        host: Host name.
        port: Port number.
        timeout: Timeout in seconds.
    """
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    output_dir = tmp_path / "docs"
    MarkdownGenerator().generate(modules, output_dir)

    content = (output_dir / "defaults.md").read_text(encoding="utf-8")
    assert "| Name | Type | Default | Description |" in content
    assert "| `host` | `str` | *required* | Host name. |" in content
    assert "| `port` | `int` | `8080` | Port number. |" in content
    assert "| `timeout` | `float` | `30.0` | Timeout in seconds. |" in content


def test_generate_source_links(sample_module: Path, tmp_path: Path) -> None:
    modules = DocstringParser().parse(sample_module)
    output_dir = tmp_path / "docs"
    generator = MarkdownGenerator(
        source_link_template="https://github.com/acme/app/blob/main/{path}#L{line}"
    )

    generator.generate(modules, output_dir)

    content = (output_dir / "sample_module.md").read_text(encoding="utf-8")
    assert "[source](https://github.com/acme/app/blob/main/sample_module.py#L" in content


def test_generate_respects_output_toggles(sample_module: Path, tmp_path: Path) -> None:
    modules = DocstringParser().parse(sample_module)
    output_dir = tmp_path / "docs"
    generator = MarkdownGenerator(
        source_link_template="https://github.com/acme/app/blob/main/{path}#L{line}",
        output_options=OutputOptions(
            show_toc=False,
            show_source_links=False,
            compact_sections=True,
            show_class_metadata=False,
        ),
    )

    generator.generate(modules, output_dir)

    content = (output_dir / "sample_module.md").read_text(encoding="utf-8")
    assert "## Table of Contents" not in content
    assert "[source](" not in content
    assert "**Bases:**" not in content
    assert "#### Methods" not in content
    assert "**Methods:**" in content


def test_generate_hides_class_metadata(
    protocol_abc_module: Path,
    tmp_path: Path,
) -> None:
    modules = DocstringParser().parse(protocol_abc_module)
    output_dir = tmp_path / "docs"

    MarkdownGenerator(
        output_options=OutputOptions(show_class_metadata=False),
    ).generate(modules, output_dir)

    content = (output_dir / "protocol_abc_module.md").read_text(encoding="utf-8")
    assert "*(Protocol)*" not in content
    assert "*(Abstract)*" not in content


def test_generate_hides_public_api_attributes_returns_and_raises(tmp_path: Path) -> None:
    module = tmp_path / "toggle_sections.py"
    module.write_text(
        '''"""Module for section toggles."""

__all__ = ["Widget", "helper"]

class Widget:
    """Example widget."""

    def __init__(self, name: str) -> None:
        """Create a widget.

        Args:
            name: Widget name.
        """
        self.name: str = name

    def run(self, value: int) -> int:
        """Run the widget.

        Args:
            value: Input value.

        Returns:
            Processed value.

        Raises:
            ValueError: If the input is invalid.
        """
        if value < 0:
            raise ValueError("invalid")
        return value

def helper() -> int:
    """Help the widget.

    Returns:
        Static result.

    Raises:
        RuntimeError: Never raised in practice.
    """
    return 1
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    output_dir = tmp_path / "docs"
    MarkdownGenerator(
        output_options=OutputOptions(
            show_public_api=False,
            show_attributes=False,
            show_returns=False,
            show_raises=False,
        )
    ).generate(modules, output_dir)

    content = (output_dir / "toggle_sections.md").read_text(encoding="utf-8")
    assert "**Public API:**" not in content
    assert "#### Attributes" not in content
    assert "**Attributes:**" not in content
    assert "**Returns:**" not in content
    assert "**Raises:**" not in content


def test_generate_filters_private_dunder_and_public_only_members(tmp_path: Path) -> None:
    module = tmp_path / "filtered_members.py"
    module.write_text(
        '''"""Module for member filtering."""

__all__ = ["Widget", "exported_helper"]

class Widget:
    """Public widget."""

    def run(self) -> None:
        """Run the widget."""

    def _debug(self) -> None:
        """Debug helper."""

    def __repr__(self) -> str:
        """Render the widget."""
        return "Widget()"

class _InternalWidget:
    """Internal widget."""

def exported_helper() -> None:
    """Exported helper."""

def public_helper() -> None:
    """Non-exported helper."""

def _private_helper() -> None:
    """Private helper."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    output_dir = tmp_path / "docs"
    MarkdownGenerator(
        output_options=OutputOptions(public_only=True),
    ).generate(modules, output_dir)

    content = (output_dir / "filtered_members.md").read_text(encoding="utf-8")
    assert "### `Widget`" in content
    assert "### `exported_helper`" in content
    assert "`run`" in content
    assert "_debug" not in content
    assert "__repr__" not in content
    assert "_InternalWidget" not in content
    assert "public_helper" not in content
    assert "_private_helper" not in content


def test_update_readme_summary_respects_member_filtering(tmp_path: Path) -> None:
    module = tmp_path / "readme_filtering.py"
    module.write_text(
        '''"""README filtering sample."""

__all__ = ["Widget"]

class Widget:
    """Public widget."""

class _InternalWidget:
    """Internal widget."""

def public_helper() -> None:
    """Non-exported helper."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    readme_path = tmp_path / "README.md"

    MarkdownGenerator(
        output_options=OutputOptions(public_only=True),
    ).update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert "- `Widget`: Public widget." in content
    assert "_InternalWidget" not in content
    assert "public_helper" not in content


def test_generate_can_show_private_and_dunder_members_when_enabled(tmp_path: Path) -> None:
    module = tmp_path / "visible_members.py"
    module.write_text(
        '''"""Module for visible member filtering."""

class Widget:
    """Public widget."""

    def _debug(self) -> None:
        """Debug helper."""

    def __repr__(self) -> str:
        """Render the widget."""
        return "Widget()"

def _private_helper() -> None:
    """Private helper."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    content = MarkdownGenerator(
        output_options=OutputOptions(
            show_private_members=True,
            show_dunder_members=True,
        )
    ).generate_string(modules[0])

    assert "`_debug`" in content
    assert "`__repr__`" in content
    assert "### `_private_helper`" in content


def test_generate_filters_members_by_name_patterns(tmp_path: Path) -> None:
    module = tmp_path / "pattern_members.py"
    module.write_text(
        '''"""Module for pattern filtering."""

class Widget:
    """Public widget."""

    def run(self) -> None:
        """Run the widget."""

    def helper(self) -> None:
        """Helper method."""

class Service:
    """Background service."""

    def run(self) -> None:
        """Run the service."""

def public_helper() -> None:
    """Public helper."""

def backup() -> None:
    """Backup helper."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    content = MarkdownGenerator(
        output_options=OutputOptions(
            member_include=("Widget", "Service.run", "public_*"),
            member_exclude=("Widget.helper",),
        )
    ).generate_string(modules[0])

    assert "### `Widget`" in content
    assert "`run`" in content
    assert "`helper`" not in content
    assert "### `Service`" in content
    assert "Run the service." in content
    assert "### `public_helper`" in content
    assert "### `backup`" not in content


def test_generate_filters_class_attributes_and_pydantic_fields(tmp_path: Path) -> None:
    module = tmp_path / "field_filtering.py"
    module.write_text(
        '''"""Module for field filtering."""

from pydantic import BaseModel, Field

class Widget:
    """Widget with internal state."""

    def __init__(self, name: str, secret: str) -> None:
        """Create widget.

        Args:
            name: Public name.
            secret: Internal secret.
        """
        self.name: str = name
        self._secret: str = secret

class Config(BaseModel):
    """Pydantic config."""

    debug: bool = False
    _token: str = Field(default="", description="Internal token")
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    content = MarkdownGenerator(
        output_options=OutputOptions(
            show_private_members=False,
            member_exclude=("Config.debug",),
        )
    ).generate_string(modules[0])

    assert "| `name` | `str` | Public name. |" in content
    assert "_secret" not in content
    assert "#### Pydantic Fields" not in content
    assert "`debug`" not in content
    assert "_token" not in content


def test_generate_can_show_private_attributes_and_fields_when_enabled(tmp_path: Path) -> None:
    module = tmp_path / "field_visibility.py"
    module.write_text(
        '''"""Module for visible fields."""

from pydantic import BaseModel, Field

class Widget:
    """Widget with internal state."""

    def __init__(self, secret: str) -> None:
        """Create widget.

        Args:
            secret: Internal secret.
        """
        self._secret: str = secret

class Config(BaseModel):
    """Pydantic config."""

    _token: str = Field(default="", description="Internal token")
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    content = MarkdownGenerator(
        output_options=OutputOptions(show_private_members=True),
    ).generate_string(modules[0])

    assert "_secret" in content
    assert "_token" in content


def test_generate_skips_empty_returns_block(tmp_path: Path) -> None:
    module = tmp_path / "no_returns.py"
    module.write_text(
        '''"""Module without return details."""

def log(message: str) -> None:
    """Log a message."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    output_dir = tmp_path / "docs"
    MarkdownGenerator().generate(modules, output_dir)

    content = (output_dir / "no_returns.md").read_text(encoding="utf-8")
    assert "**Returns:**" not in content


def test_generate_unique_method_anchors(tmp_path: Path) -> None:
    module = tmp_path / "duplicate_methods.py"
    module.write_text(
        '''"""Module with duplicate method names."""

class A:
    """First class."""

    def run(self) -> None:
        """Run A."""

class B:
    """Second class."""

    def run(self) -> None:
        """Run B."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    output_dir = tmp_path / "docs"
    MarkdownGenerator().generate(modules, output_dir)

    content = (output_dir / "duplicate_methods.md").read_text(encoding="utf-8")
    assert "(#a-run)" in content
    assert "(#b-run)" in content
    assert '<a id="a-run"></a>' in content
    assert '<a id="b-run"></a>' in content


def test_generate_cross_references(crossref_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(crossref_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    module_path = output_dir / "crossref_module.md"
    content = module_path.read_text()
    # UserProfile referenced as return type in User.get_profile
    assert "[UserProfile](#userprofile)" in content
    # User referenced as return type in UserProfile.get_user
    assert "[User](#user)" in content
    # create_user returns User
    assert "[User](#user)" in content


def test_generate_single_file(sample_package: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_package, recursive=True)

    generator = MarkdownGenerator()
    output_path = tmp_path / "combined.md"
    result = generator.generate_single_file(modules, output_path)

    assert result == output_path
    assert output_path.exists()
    content = output_path.read_text()
    assert "# Documentation" in content
    assert "## Modules" in content
    assert "math_utils" in content
    assert "multiply" in content


def test_generate_protocol_abc(protocol_abc_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(protocol_abc_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    content = (output_dir / "protocol_abc_module.md").read_text()
    assert "*(Protocol)*" in content
    assert "*(Abstract)*" in content


def test_generate_pydantic_model(pydantic_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(pydantic_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    generator.generate(modules, output_dir)

    content = (output_dir / "pydantic_module.md").read_text()
    assert "*(Pydantic)*" in content
    assert "#### Pydantic Fields" in content
    assert "User email address" in content
    assert "User age in years" in content
    assert "Request timeout in seconds" in content


def test_update_readme_creates_file(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    readme_path = tmp_path / "README.md"
    result = generator.update_readme(modules, readme_path)

    assert result == readme_path
    content = readme_path.read_text(encoding="utf-8")
    assert "# API Reference" in content
    assert README_START_MARKER in content
    assert README_END_MARKER in content
    assert "Calculator" in content
    assert "greet" in content


def test_update_readme_summary_includes_stats_and_item_summaries(
    sample_module: Path,
    tmp_path: Path,
) -> None:
    modules = DocstringParser().parse(sample_module)
    readme_path = tmp_path / "README.md"

    MarkdownGenerator().update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert "**Overview:** 1 modules, 1 classes, 1 functions." in content
    assert "**Quick links:**" in content
    assert "- [`sample_module`](#readme-sample_module)" in content
    assert '<a id="readme-sample_module"></a>' in content
    assert "_Includes: 1 class(es), 1 function(s)._" in content
    assert "- `Calculator`: A simple calculator class." in content
    assert "- `greet`: Greet a person." in content


def test_update_readme_summary_prioritizes_public_api_order(tmp_path: Path) -> None:
    module = tmp_path / "public_api_module.py"
    module.write_text(
        '''"""Public API module."""

__all__ = ["helper", "Widget", "missing_export"]

class Widget:
    """Primary widget."""

class InternalThing:
    """Internal helper."""

def helper() -> None:
    """Helpful entrypoint."""

def internal_helper() -> None:
    """Internal function."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(module)
    readme_path = tmp_path / "README.md"

    MarkdownGenerator().update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    public_api_index = content.index("**Public API:**")
    helper_index = content.index("- `helper`: Helpful entrypoint.")
    widget_index = content.index("- `Widget`: Primary widget.")
    additional_exports_index = content.index("**Additional exports:**")
    other_classes_index = content.index("**Other classes:**")
    other_functions_index = content.index("**Other functions:**")

    assert public_api_index < helper_index < widget_index
    assert widget_index < additional_exports_index < other_classes_index < other_functions_index
    assert "- `missing_export`" in content
    assert "- `InternalThing`: Internal helper." in content
    assert "- `internal_helper`: Internal function." in content


def test_update_readme_summary_groups_modules_by_package(tmp_path: Path) -> None:
    pkg = tmp_path / "my_pkg"
    sub = pkg / "sub"
    sub.mkdir(parents=True)
    (pkg / "__init__.py").write_text('"""Top-level package."""\n', encoding="utf-8")
    (pkg / "top.py").write_text('"""Top module."""\n', encoding="utf-8")
    (sub / "__init__.py").write_text('"""Subpackage docs."""\n', encoding="utf-8")
    (sub / "nested.py").write_text(
        '''"""Nested module."""

def helper() -> None:
    """Help from nested."""
''',
        encoding="utf-8",
    )

    modules = DocstringParser().parse(pkg, recursive=True)
    readme_path = tmp_path / "README.md"

    MarkdownGenerator().update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert "**Overview:** 2 modules, 0 classes, 1 functions." in content
    assert "**Packages:**" in content
    assert "- [`Modules`](#readme-package-modules) (1 module(s))" in content
    assert "- [`sub`](#readme-package-sub) (1 module(s))" in content
    assert "**Quick links:**" in content
    assert "- [`top`](#readme-top)" in content
    assert (
        "- [`sub.nested`](sub/nested.md)" in content
        or "- [`sub.nested`](#readme-sub-nested)" in content
    )
    assert '<a id="readme-package-sub"></a>' in content
    assert "### Modules" in content
    assert "### Package `sub`" in content
    assert "Subpackage docs." in content
    assert "#### `top`" in content
    assert "#### [`sub.nested`](sub/nested.md)" in content or "#### `sub.nested`" in content


def test_update_readme_replaces_marked_section(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        "# Project\n\n"
        "Before\n\n"
        f"{README_START_MARKER}\nold content\n{README_END_MARKER}\n\n"
        "After\n",
        encoding="utf-8",
    )

    MarkdownGenerator().update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert "Before" in content
    assert "After" in content
    assert "old content" not in content
    assert "Calculator" in content


def test_update_readme_detailed_mode_uses_rendered_module_content(
    sample_module: Path,
    tmp_path: Path,
) -> None:
    modules = DocstringParser().parse(sample_module)
    readme_path = tmp_path / "README.md"

    MarkdownGenerator(readme_mode="detailed").update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert "### sample_module" in content
    assert "#### Classes" in content
    assert "##### `Calculator`" in content
    assert "## Table of Contents" not in content


def test_update_readme_uses_custom_title(sample_module: Path, tmp_path: Path) -> None:
    modules = DocstringParser().parse(sample_module)
    readme_path = tmp_path / "README.md"

    MarkdownGenerator(readme_title="Developer API").update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert "# Developer API" in content
    assert "# API Reference" not in content


def test_update_readme_appends_section_when_markers_missing(
    sample_module: Path,
    tmp_path: Path,
) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    readme_path = tmp_path / "README.md"
    readme_path.write_text("# Project\n\nIntro.\n", encoding="utf-8")

    MarkdownGenerator().update_readme(modules, readme_path)

    content = readme_path.read_text(encoding="utf-8")
    assert content.startswith("# Project")
    assert "## API Reference" in content
    assert README_START_MARKER in content
    assert "Calculator" in content


def test_update_readme_rejects_partial_marker_block(
    sample_module: Path,
    tmp_path: Path,
) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    readme_path = tmp_path / "README.md"
    readme_path.write_text(
        f"# Project\n\n{README_START_MARKER}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="only one PyDoc2Markdown marker"):
        MarkdownGenerator().update_readme(modules, readme_path)
