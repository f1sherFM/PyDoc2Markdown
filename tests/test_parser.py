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
    assert cls.source_path == "sample_module.py"
    assert cls.line_number is not None


def test_parse_module_functions(sample_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(sample_module)
    module = modules[0]

    assert len(module.functions) == 1
    func = module.functions[0]
    assert isinstance(func, FunctionDoc)
    assert func.name == "greet"
    assert func.source_path == "sample_module.py"
    assert func.line_number is not None


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


def test_parse_recursive_excludes_matching_files(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    internal = pkg / "internal"
    tests_dir = pkg / "tests"
    internal.mkdir(parents=True)
    tests_dir.mkdir()
    (pkg / "public.py").write_text('"""Public module."""\n', encoding="utf-8")
    (internal / "secret.py").write_text('"""Internal module."""\n', encoding="utf-8")
    (tests_dir / "test_public.py").write_text('"""Test module."""\n', encoding="utf-8")

    modules = DocstringParser().parse(
        pkg,
        recursive=True,
        exclude=["internal/*", "test_*.py"],
    )

    assert [module.name for module in modules] == ["public"]


def test_parse_recursive_includes_matching_files(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    api = pkg / "api"
    core = pkg / "core"
    api.mkdir(parents=True)
    core.mkdir()
    (api / "users.py").write_text('"""Users API."""\n', encoding="utf-8")
    (core / "utils.py").write_text('"""Core utils."""\n', encoding="utf-8")

    modules = DocstringParser().parse(pkg, recursive=True, include=["api/*"])

    assert [module.name for module in modules] == ["users"]


def test_parse_recursive_applies_include_then_exclude(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    api = pkg / "api"
    api.mkdir(parents=True)
    (api / "public.py").write_text('"""Public API."""\n', encoding="utf-8")
    (api / "generated.py").write_text('"""Generated API."""\n', encoding="utf-8")

    modules = DocstringParser().parse(
        pkg,
        recursive=True,
        include=["api/*"],
        exclude=["*/generated.py"],
    )

    assert [module.name for module in modules] == ["public"]


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


def test_parse_function_parameter_defaults(tmp_path: Path) -> None:
    module = tmp_path / "defaults.py"
    module.write_text(
        '''"""Defaults module."""

def connect(host: str, port: int = 8080, *, timeout: float = 30.0, secure: bool):
    """Connect to a service."""
    return None
''',
        encoding="utf-8",
    )

    func = DocstringParser().parse(module)[0].functions[0]

    defaults = {param.name: param.default for param in func.params}
    assert defaults == {
        "host": None,
        "port": "8080",
        "timeout": "30.0",
        "secure": None,
    }


def test_parse_method_parameter_defaults_skip_self(tmp_path: Path) -> None:
    module = tmp_path / "defaults.py"
    module.write_text(
        '''"""Defaults module."""

class Client:
    """Client."""

    def request(self, path: str, retries: int = 3) -> None:
        """Send a request."""
''',
        encoding="utf-8",
    )

    method = DocstringParser().parse(module)[0].classes[0].methods[0]

    assert [param.name for param in method.params] == ["path", "retries"]
    assert [param.default for param in method.params] == [None, "3"]


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


def test_parse_protocol(protocol_abc_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(protocol_abc_module)
    drawable = next(c for c in modules[0].classes if c.name == "Drawable")
    assert drawable.is_protocol is True
    assert drawable.is_abstract is False


def test_parse_abc(protocol_abc_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(protocol_abc_module)
    shape = next(c for c in modules[0].classes if c.name == "Shape")
    assert shape.is_protocol is False
    assert shape.is_abstract is True


def test_parse_concrete_subclass(protocol_abc_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(protocol_abc_module)
    rect = next(c for c in modules[0].classes if c.name == "Rectangle")
    assert rect.is_protocol is False
    assert rect.is_abstract is False


def test_parse_pydantic_model(pydantic_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(pydantic_module)
    user = next(c for c in modules[0].classes if c.name == "User")
    assert user.is_pydantic_model is True
    assert len(user.pydantic_fields) == 4

    id_field = next(f for f in user.pydantic_fields if f.name == "id")
    assert id_field.type_hint == "int"
    assert id_field.required is True
    assert id_field.default is None

    name_field = next(f for f in user.pydantic_fields if f.name == "name")
    assert name_field.type_hint == "str"
    assert name_field.required is False
    assert name_field.default == "'Anonymous'"

    email_field = next(f for f in user.pydantic_fields if f.name == "email")
    assert email_field.description == "User email address"
    assert email_field.required is False

    age_field = next(f for f in user.pydantic_fields if f.name == "age")
    assert age_field.type_hint == "int | None"
    assert age_field.description == "User age in years"


def test_parse_pydantic_config(pydantic_module: Path) -> None:
    parser = DocstringParser()
    modules = parser.parse(pydantic_module)
    config = next(c for c in modules[0].classes if c.name == "Config")
    assert config.is_pydantic_model is True
    assert len(config.pydantic_fields) == 2

    debug_field = next(f for f in config.pydantic_fields if f.name == "debug")
    assert debug_field.type_hint == "bool"
    assert debug_field.default == "False"

    timeout_field = next(f for f in config.pydantic_fields if f.name == "timeout")
    assert timeout_field.description == "Request timeout in seconds"
