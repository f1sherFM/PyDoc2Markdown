"""pytest fixtures and shared utilities."""

from pathlib import Path

import pytest


@pytest.fixture
def sample_module(tmp_path: Path) -> Path:
    """Create a temporary Python module with docstrings for testing."""
    module = tmp_path / "sample_module.py"
    module.write_text(
        '''"""A sample module for testing."""

class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Sum of a and b.

        Raises:
            ValueError: If a or b is negative.
        """
        if a < 0 or b < 0:
            raise ValueError("Negative numbers not allowed")
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b

def greet(name: str) -> str:
    """Greet a person.

    Args:
        name: Name of the person.

    Returns:
        Greeting message.
    """
    return f"Hello, {name}!"
''',
        encoding="utf-8",
    )
    return module


@pytest.fixture
def sample_package(tmp_path: Path) -> Path:
    """Create a temporary Python package for testing."""
    pkg = tmp_path / "sample_package"
    pkg.mkdir()
    init = pkg / "__init__.py"
    init.write_text('"""A sample package."""\n', encoding="utf-8")

    module = pkg / "math_utils.py"
    module.write_text(
        '''"""Math utilities."""

def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y
''',
        encoding="utf-8",
    )
    return pkg


@pytest.fixture
def typed_module(tmp_path: Path) -> Path:
    """Create a module with typing constructs for testing type hint formatting."""
    module = tmp_path / "typed_module.py"
    module.write_text(
        '''"""Module with typing constructs."""

from typing import Optional, Union, List

def process(value: Optional[str]) -> Union[int, str]:
    """Process a value."""
    return value if value else 0

def items(data: List[int]) -> List[str]:
    """Convert ints to strings."""
    return [str(x) for x in data]
''',
        encoding="utf-8",
    )
    return module


@pytest.fixture
def crossref_module(tmp_path: Path) -> Path:
    """Create a module with types referencing each other."""
    module = tmp_path / "crossref_module.py"
    module.write_text(
        '''"""Module with cross-referencing types."""

class User:
    """A user."""

    def get_profile(self) -> UserProfile:
        """Get the user profile."""
        return UserProfile()

class UserProfile:
    """A user profile."""

    def get_user(self) -> User:
        """Get the associated user."""
        return User()

def create_user() -> User:
    """Create a new user."""
    return User()
''',
        encoding="utf-8",
    )
    return module


@pytest.fixture
def advanced_module(tmp_path: Path) -> Path:
    """Create a temporary module with advanced Python constructs."""
    module = tmp_path / "advanced_module.py"
    module.write_text(
        '''"""Advanced module for testing extended parsing."""

__all__ = ["MyDataclass", "MyEnum", "MyTypedDict", "utility"]

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict


@dataclass
class MyDataclass:
    """A sample dataclass."""

    value: int


class MyEnum(Enum):
    """A sample enum."""

    A = 1
    B = 2


class MyTypedDict(TypedDict):
    """A sample typed dict."""

    name: str
    age: int


class Greeter:
    """A class with various method types."""

    def __init__(self, greeting: str) -> None:
        self._greeting = greeting

    @property
    def greeting(self) -> str:
        """The greeting message."""
        return self._greeting

    @classmethod
    def from_language(cls, lang: str) -> "Greeter":
        """Create from language."""
        return cls(f"Hello in {lang}")

    @staticmethod
    def default_greeting() -> str:
        """Return default greeting."""
        return "Hello"


def utility() -> None:
    """A utility function."""
    pass
''',
        encoding="utf-8",
    )
    return module


@pytest.fixture
def protocol_abc_module(tmp_path: Path) -> Path:
    """Create a module with Protocol and ABC classes."""
    module = tmp_path / "protocol_abc_module.py"
    module.write_text(
        '''"""Module with Protocol and ABC classes."""

from abc import ABC, abstractmethod
from typing import Protocol

class Drawable(Protocol):
    """A drawable protocol."""

    def draw(self) -> None:
        """Draw something."""
        ...

class Shape(ABC):
    """An abstract shape."""

    @abstractmethod
    def area(self) -> float:
        """Calculate area."""
        ...

class Rectangle(Shape):
    """A concrete rectangle."""

    def area(self) -> float:
        """Calculate rectangle area."""
        return 0.0
''',
        encoding="utf-8",
    )
    return module
