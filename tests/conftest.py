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
        """
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
