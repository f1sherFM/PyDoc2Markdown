"""Tests for MarkdownGenerator."""

from pathlib import Path

from pydoc2markdown.core.generator import MarkdownGenerator
from pydoc2markdown.core.parser import DocstringParser


def test_generate_single_module(sample_module: Path, tmp_path: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "docs"
    paths = generator.generate(modules, output_dir)

    assert len(paths) == 1
    assert paths[0].exists()
    content = paths[0].read_text()
    assert "Calculator" in content
    assert "greet" in content


def test_generate_string(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    generator = MarkdownGenerator()
    content = generator.generate_string(modules[0])

    assert "# sample_module" in content
    assert "## Classes" in content
    assert "## Functions" in content


def test_generate_creates_output_dir(tmp_path: Path) -> None:
    parser = DocstringParser()
    module = tmp_path / "empty.py"
    module.write_text('"""Empty module."""\n', encoding="utf-8")
    modules = parser.parse(module)

    generator = MarkdownGenerator()
    output_dir = tmp_path / "nested" / "docs"
    paths = generator.generate(modules, output_dir)

    assert output_dir.exists()
    assert paths[0].exists()
