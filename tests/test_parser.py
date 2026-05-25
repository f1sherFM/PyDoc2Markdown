"""Tests for DocstringParser."""

from pathlib import Path

import pytest

from pydoc2markdown.core.parser import (
    ClassDoc,
    DocstringParser,
    FunctionDoc,
    ModuleDoc,
    RaisesInfo,
    ReturnsInfo,
)


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


def test_parse_function_params(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    func = modules[0].functions[0]

    assert len(func.params) == 1
    assert func.params[0].name == "name"
    assert func.params[0].type_hint == "str"
    assert func.params[0].description == "Name of the person."


def test_parse_function_returns(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    func = modules[0].functions[0]

    assert isinstance(func.returns, ReturnsInfo)
    assert func.returns.type_hint == "str"
    assert func.returns.description == "Greeting message."


def test_parse_method_params_and_raises(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    add_method = next(m for m in modules[0].classes[0].methods if m.name == "add")

    assert len(add_method.params) == 2
    param_names = {p.name for p in add_method.params}
    assert param_names == {"a", "b"}

    assert isinstance(add_method.returns, ReturnsInfo)
    assert add_method.returns.description == "Sum of a and b."

    assert len(add_method.raises) == 1
    assert isinstance(add_method.raises[0], RaisesInfo)
    assert add_method.raises[0].type_name == "ValueError"
    assert add_method.raises[0].description == "If a or b is negative."


def test_parse_property(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    greeter = next(c for c in modules[0].classes if c.name == "Greeter")
    prop = next(m for m in greeter.methods if m.name == "greeting")
    assert prop.is_property is True
    assert prop.is_classmethod is False
    assert prop.is_staticmethod is False


def test_parse_classmethod(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    greeter = next(c for c in modules[0].classes if c.name == "Greeter")
    cm = next(m for m in greeter.methods if m.name == "from_language")
    assert cm.is_classmethod is True
    assert cm.is_property is False
    assert cm.is_staticmethod is False


def test_parse_staticmethod(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    greeter = next(c for c in modules[0].classes if c.name == "Greeter")
    sm = next(m for m in greeter.methods if m.name == "default_greeting")
    assert sm.is_staticmethod is True
    assert sm.is_property is False
    assert sm.is_classmethod is False


def test_parse_dataclass(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    dc = next(c for c in modules[0].classes if c.name == "MyDataclass")
    assert dc.class_type == "dataclass"


def test_parse_enum(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    en = next(c for c in modules[0].classes if c.name == "MyEnum")
    assert en.class_type == "enum"


def test_parse_typeddict(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    td = next(c for c in modules[0].classes if c.name == "MyTypedDict")
    assert td.class_type == "typeddict"


def test_parse_public_api(advanced_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(advanced_module)
    assert modules[0].public_api == [
        "MyDataclass",
        "MyEnum",
        "MyTypedDict",
        "utility",
    ]
