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
    assert "# Index" in content
    assert "[sample_module](sample_module.md)" in content


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
    assert "## sub" in content
    assert "[nested](sub/nested.md)" in content
