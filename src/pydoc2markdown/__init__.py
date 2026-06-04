"""PyDoc2Markdown - Convert Python docstrings to Markdown documentation."""

__version__ = "0.7.2"
__author__ = "f1sherFM"

from pydoc2markdown.core.generator import MarkdownGenerator, OutputOptions
from pydoc2markdown.core.parser import (
    ClassDoc,
    DocstringParser,
    FunctionDoc,
    ModuleDoc,
    Parameter,
    PydanticField,
    RaisesInfo,
    ReturnsInfo,
)

__all__ = [
    "ClassDoc",
    "DocstringParser",
    "FunctionDoc",
    "MarkdownGenerator",
    "ModuleDoc",
    "OutputOptions",
    "Parameter",
    "PydanticField",
    "RaisesInfo",
    "ReturnsInfo",
]
