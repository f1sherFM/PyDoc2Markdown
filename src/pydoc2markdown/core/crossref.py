"""Cross-referencing utilities for linking project-defined types."""

import re
from dataclasses import dataclass

from jinja2 import pass_context

from pydoc2markdown.core.parser import ModuleDoc


@pass_context
def link_type_filter(ctx: dict, type_str: str) -> str:
    """Jinja2 filter that auto-links project-defined types.

    Expects ``type_index`` in the render context.
    """
    from typing import cast

    idx = cast("TypeIndex | None", ctx.get("type_index"))
    if idx:
        return idx.link(type_str)
    return type_str


def _to_anchor(name: str) -> str:
    """Convert a name to a Markdown anchor."""
    return name.lower().replace(" ", "-")


@dataclass
class TypeIndex:
    """Index of project-defined types for cross-referencing."""

    types: dict[str, str]
    """Mapping from type name to Markdown anchor."""

    @classmethod
    def from_modules(cls, modules: list[ModuleDoc]) -> "TypeIndex":
        """Build an index from a list of parsed modules."""
        types: dict[str, str] = {}
        for module in modules:
            for class_doc in module.classes:
                types[class_doc.name] = _to_anchor(class_doc.name)
                for method in class_doc.methods:
                    types[method.name] = _to_anchor(method.name)
            for func in module.functions:
                types[func.name] = _to_anchor(func.name)
        return cls(types)

    def link(self, type_str: str) -> str:
        """Replace project-defined type names with Markdown hyperlinks.

        Args:
            type_str: A type hint string (preferably already formatted).

        Returns:
            Markdown string with hyperlinks for known types.
        """
        if not type_str:
            return type_str

        existing_links: list[str] = []

        def _stash_link(match: re.Match[str]) -> str:
            existing_links.append(match.group(0))
            return f"@@PYDOC2MARKDOWN_LINK_{len(existing_links) - 1}@@"

        type_str = re.sub(r"\[[^\]]+\]\([^)]+\)", _stash_link, type_str)

        # Sort by length descending to avoid partial replacements
        # e.g. replace "MyClass" before "My"
        for name, anchor in sorted(self.types.items(), key=lambda item: len(item[0]), reverse=True):
            # Match the type name as a whole word, avoiding substrings inside other words
            pattern = rf"\b{re.escape(name)}\b"
            replacement = rf"[{name}](#{anchor})"
            type_str = re.sub(pattern, replacement, type_str)

        for index, link in enumerate(existing_links):
            type_str = type_str.replace(f"@@PYDOC2MARKDOWN_LINK_{index}@@", link)
        return type_str
