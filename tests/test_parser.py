"""Tests for DocstringParser."""

from pathlib import Path

import pytest

from pydoc2markdown.core.parser import ClassDoc, DocstringParser, FunctionDoc, ModuleDoc


def test_parse_single_module(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)

    assert len(modules) == 1
    module = modules[0]
    assert isinstance(module, ModuleDoc)
    assert module.name == "sample_module"
    assert module.docstring == "A sample module for testing."


def test_parse_module_classes(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    module = modules[0]

    assert len(module.classes) == 1
    cls = module.classes[0]
    assert isinstance(cls, ClassDoc)
    assert cls.name == "Calculator"
    assert cls.docstring == "A simple calculator class."


def test_parse_module_functions(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    module = modules[0]

    assert len(module.functions) == 1
    func = module.functions[0]
    assert isinstance(func, FunctionDoc)
    assert func.name == "greet"


def test_parse_class_methods(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    cls = modules[0].classes[0]

    assert len(cls.methods) == 2
    method_names = {m.name for m in cls.methods}
    assert method_names == {"add", "subtract"}


def test_parse_recursive(sample_package: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_package, recursive=True)

    assert len(modules) == 2  # __init__.py and math_utils.py
    names = {m.name for m in modules}
    assert names == {"__init__", "math_utils"}


def test_parse_invalid_source() -> None:
    parser = DocstringParser()
    with pytest.raises(ValueError, match="Invalid source"):
        parser.parse(Path("nonexistent.py"))
