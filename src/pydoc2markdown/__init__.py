"""PyDoc2Markdown - Convert Python docstrings to Markdown documentation."""

__version__ = "0.1.0"
__author__ = "f1sherFM"

from pydoc2markdown.core.generator import MarkdownGenerator
from pydoc2markdown.core.parser import DocstringParser

__all__ = ["DocstringParser", "MarkdownGenerator"]
