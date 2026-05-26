"""PyDoc2Markdown - Convert Python docstrings to Markdown documentation."""

__version__ = "0.2.0"
__author__ = "f1sherFM"

from pydoc2markdown.core.generator import MarkdownGenerator
from pydoc2markdown.core.parser import (
    ClassDoc,
    DocstringParser,
    FunctionDoc,
    ModuleDoc,
    Parameter,
    RaisesInfo,
    ReturnsInfo,
)

__all__ = [
    "ClassDoc",
    "DocstringParser",
    "FunctionDoc",
    "MarkdownGenerator",
    "ModuleDoc",
    "Parameter",
    "RaisesInfo",
    "ReturnsInfo",
]
