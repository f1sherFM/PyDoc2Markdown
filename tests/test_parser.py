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

    assert func.docstring == "Greet a person."
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


def test_parse_function_without_return_info_has_no_returns(tmp_path: Path) -> None:
    module = tmp_path / "no_returns.py"
    module.write_text(
        '''"""Module without return details."""

def log(message: str) -> None:
    """Log a message."""
''',
        encoding="utf-8",
    )

    func = DocstringParser().parse(module)[0].functions[0]

    assert func.returns is None


def test_parse_does_not_inherit_docstrings_by_default(tmp_path: Path) -> None:
    module = tmp_path / "models.py"
    module.write_text(
        '''"""Models."""

class Base:
    """Base model."""

    def save(self, force: bool) -> bool:
        """Persist the model.

        Args:
            force: Persist even when unchanged.

        Returns:
            Whether a write happened.
        """
        return True

class User(Base):
    def save(self, force: bool) -> bool:
        return False
''',
        encoding="utf-8",
    )

    user = DocstringParser().parse(module)[0].classes[1]

    assert user.docstring is None
    assert user.methods[0].docstring is None
    assert user.methods[0].params[0].description is None


def test_parse_can_inherit_class_and_method_docstrings(tmp_path: Path) -> None:
    module = tmp_path / "models.py"
    module.write_text(
        '''"""Models."""

class Base:
    """Base model."""

    def save(self, force: bool) -> bool:
        """Persist the model.

        Args:
            force: Persist even when unchanged.

        Returns:
            Whether a write happened.
        """
        return True

class User(Base):
    def save(self, force: bool) -> bool:
        return False
''',
        encoding="utf-8",
    )

    user = DocstringParser(inherit_docstrings=True).parse(module)[0].classes[1]
    save = user.methods[0]

    assert user.docstring == "Base model."
    assert save.docstring == "Persist the model."
    assert save.params[0].description == "Persist even when unchanged."
    assert isinstance(save.returns, ReturnsInfo)
    assert save.returns.description == "Whether a write happened."


def test_parse_inherits_docstrings_across_modules(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "base.py").write_text(
        '''"""Base module."""

class Service:
    """Reusable service."""
''',
        encoding="utf-8",
    )
    (package / "users.py").write_text(
        '''"""Users module."""

from .base import Service

class UserService(Service):
    pass
''',
        encoding="utf-8",
    )

    users = DocstringParser(inherit_docstrings=True).parse(package, recursive=True)[1]

    assert users.classes[0].docstring == "Reusable service."


def test_parse_inherits_docstrings_from_aliased_base_import(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "base.py").write_text(
        '''"""Base module."""

class Service:
    """Reusable service."""
''',
        encoding="utf-8",
    )
    (package / "other.py").write_text(
        '''"""Other module."""

class Service:
    """Different service."""
''',
        encoding="utf-8",
    )
    (package / "users.py").write_text(
        '''"""Users module."""

from .base import Service as BaseService

class UserService(BaseService):
    pass
''',
        encoding="utf-8",
    )

    modules = DocstringParser(inherit_docstrings=True).parse(package, recursive=True)
    users = next(module for module in modules if module.name == "users")

    assert users.classes[0].bases == ["BaseService"]
    assert users.classes[0].resolved_bases == [".base.Service"]
    assert users.classes[0].docstring == "Reusable service."


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


def test_parse_dataclass_fields_from_class_body(tmp_path: Path) -> None:
    module = tmp_path / "models.py"
    module.write_text(
        '''"""Models."""

from dataclasses import dataclass

@dataclass
class Product:
    """A product.

    Args:
        sku: Stable product identifier.
        price: Unit price.
    """

    sku: str
    price: float
''',
        encoding="utf-8",
    )

    product = DocstringParser().parse(module)[0].classes[0]

    assert product.docstring == "A product."
    assert [(attr.name, attr.type_hint, attr.description) for attr in product.attributes] == [
        ("sku", "str", "Stable product identifier."),
        ("price", "float", "Unit price."),
    ]


def test_parse_attrs_fields_from_class_body(tmp_path: Path) -> None:
    module = tmp_path / "models.py"
    module.write_text(
        '''"""Models."""

import attrs

@attrs.define
class Product:
    """A product.

    Args:
        sku: Stable product identifier.
        price: Unit price.
    """

    sku: str
    price: float = attrs.field(default=0.0)
''',
        encoding="utf-8",
    )

    product = DocstringParser().parse(module)[0].classes[0]

    assert product.class_type == "attrs"
    assert product.docstring == "A product."
    assert [
        (attr.name, attr.type_hint, attr.default, attr.description) for attr in product.attributes
    ] == [
        ("sku", "str", None, "Stable product identifier."),
        ("price", "float", "attrs.field(default=0.0)", "Unit price."),
    ]


def test_parse_attrs_alias_decorators(tmp_path: Path) -> None:
    module = tmp_path / "aliases.py"
    module.write_text(
        '''"""Attrs aliases."""

import attr as attr_lib
from attrs import frozen as frozen_class

@attr_lib.s
class LegacyModel:
    """Legacy attrs model."""

    name: str

@frozen_class
class FrozenModel:
    """Frozen attrs model."""

    name: str
''',
        encoding="utf-8",
    )

    classes = {
        class_doc.name: class_doc for class_doc in DocstringParser().parse(module)[0].classes
    }

    assert classes["LegacyModel"].class_type == "attrs"
    assert classes["FrozenModel"].class_type == "attrs"


def test_parse_constructor_params_from_class_docstring(tmp_path: Path) -> None:
    module = tmp_path / "inventory.py"
    module.write_text(
        '''"""Inventory module."""

class Inventory:
    """In-memory inventory.

    Args:
        products: Initial products keyed by SKU.
    """

    def __init__(self, products: dict[str, str] | None = None) -> None:
        self._products = products or {}
''',
        encoding="utf-8",
    )

    inventory = DocstringParser().parse(module)[0].classes[0]

    assert inventory.docstring == "In-memory inventory."
    assert [
        (param.name, param.type_hint, param.default, param.description)
        for param in inventory.constructor_params
    ] == [
        (
            "products",
            "dict[str, str] | None",
            "None",
            "Initial products keyed by SKU.",
        )
    ]


def test_parse_documented_module_attribute(tmp_path: Path) -> None:
    module = tmp_path / "settings.py"
    module.write_text(
        '''"""Settings."""

DEFAULT_TIMEOUT: float = 30.0
"""Default request timeout in seconds."""
''',
        encoding="utf-8",
    )

    parsed = DocstringParser().parse(module)[0]

    assert [
        (attr.name, attr.type_hint, attr.default, attr.description) for attr in parsed.attributes
    ] == [
        (
            "DEFAULT_TIMEOUT",
            "float",
            "30.0",
            "Default request timeout in seconds.",
        )
    ]


def test_parse_documented_class_and_instance_attributes(tmp_path: Path) -> None:
    module = tmp_path / "client.py"
    module.write_text(
        '''"""Client module."""

class Client:
    """HTTP client."""

    default_retries: int = 3
    """Default retry count."""

    def __init__(self, token: str) -> None:
        self.token: str = token
        """Authentication token."""
''',
        encoding="utf-8",
    )

    client = DocstringParser().parse(module)[0].classes[0]

    assert [(attr.name, attr.type_hint, attr.description) for attr in client.attributes] == [
        ("default_retries", "int", "Default retry count."),
        ("token", "str", "Authentication token."),
    ]


def test_parse_pydantic_field_description_from_adjacent_docstring(tmp_path: Path) -> None:
    module = tmp_path / "settings.py"
    module.write_text(
        '''"""Settings."""

from pydantic import BaseModel

class Settings(BaseModel):
    """Application settings."""

    timeout: float = 30.0
    """Request timeout in seconds."""
''',
        encoding="utf-8",
    )

    settings = DocstringParser().parse(module)[0].classes[0]

    timeout = settings.pydantic_fields[0]
    assert timeout.name == "timeout"
    assert timeout.description == "Request timeout in seconds."


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


def test_parse_common_import_aliases_for_class_metadata(tmp_path: Path) -> None:
    module = tmp_path / "aliases.py"
    module.write_text(
        '''"""Alias-heavy module."""

import dataclasses as dc
import enum as enum_mod
from abc import ABC as BaseABC
from pydantic import BaseModel as Model, Field as PydanticField
from typing import Protocol as Proto, TypedDict as TD

@dc.dataclass
class Product:
    """A product."""

    sku: str

class OrderStatus(enum_mod.Enum):
    """Order status."""

    PAID = "paid"

class Payload(TD):
    """Typed payload."""

    value: str

class Drawable(Proto):
    """Drawable contract."""

class Shape(BaseABC):
    """Abstract shape."""

class Settings(Model):
    """Application settings."""

    timeout: float = PydanticField(default=30.0, description="Request timeout.")
''',
        encoding="utf-8",
    )

    classes = {
        class_doc.name: class_doc for class_doc in DocstringParser().parse(module)[0].classes
    }

    assert classes["Product"].class_type == "dataclass"
    assert classes["OrderStatus"].class_type == "enum"
    assert classes["Payload"].class_type == "typeddict"
    assert classes["Drawable"].is_protocol is True
    assert classes["Shape"].is_abstract is True
    assert classes["Settings"].is_pydantic_model is True
    assert classes["Settings"].bases == ["Model"]
    timeout = classes["Settings"].pydantic_fields[0]
    assert timeout.name == "timeout"
    assert timeout.description == "Request timeout."
