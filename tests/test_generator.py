"""Tests for MarkdownGenerator."""

from pathlib import Path

import pytest

from pydoc2markdown.core.generator import README_END_MARKER, README_START_MARKER, MarkdownGenerator
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

    package_content = (output_dir / "sub.md").read_text(encoding="utf-8")
    assert "# sub" in package_content
    assert "[`sub.nested`](api/sub/nested.md)" in package_content


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
