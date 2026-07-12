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
        if ctx.get("link_cross_module_types"):
            return idx.link(type_str)

        module = cast("ModuleDoc | None", ctx.get("module"))
        current_module = _module_key(module) if module else None
        return idx.link(type_str, current_module=current_module)
    return type_str


def _to_anchor(name: str) -> str:
    """Convert a name to a Markdown anchor."""
    return name.lower().replace(" ", "-")


def _module_key(module: ModuleDoc) -> str:
    """Return a stable key for a module in the type index."""
    return f"{module.package}.{module.name}" if module.package else module.name


@dataclass(frozen=True)
class TypeRef:
    """A project-defined type target."""

    anchor: str
    module: str | None = None


@dataclass
class TypeIndex:
    """Index of project-defined types for cross-referencing."""

    types: dict[str, list[TypeRef] | TypeRef | str]
    """Mapping from type name to one or more Markdown targets."""

    @classmethod
    def from_modules(cls, modules: list[ModuleDoc]) -> "TypeIndex":
        """Build an index from a list of parsed modules."""
        types: dict[str, list[TypeRef] | TypeRef | str] = {}
        for module in modules:
            module_key = _module_key(module)
            for class_doc in module.classes:
                refs = types.setdefault(class_doc.name, [])
                assert isinstance(refs, list)
                refs.append(
                    TypeRef(
                        anchor=_to_anchor(class_doc.name),
                        module=module_key,
                    )
                )
            for func in module.functions:
                refs = types.setdefault(func.name, [])
                assert isinstance(refs, list)
                refs.append(
                    TypeRef(
                        anchor=_to_anchor(func.name),
                        module=module_key,
                    )
                )
        return cls(types)

    def link(self, type_str: str, *, current_module: str | None = None) -> str:
        """Replace project-defined type names with Markdown hyperlinks.

        Args:
            type_str: A type hint string (preferably already formatted).
            current_module: Module key for local-only links. When provided,
                types from other modules are left as plain text.

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
        for name, target in sorted(self.types.items(), key=lambda item: len(item[0]), reverse=True):
            ref = self._select_ref(target, current_module=current_module)
            if ref is None:
                continue
            # Match the type name as a whole word, avoiding substrings inside other words
            pattern = rf"\b{re.escape(name)}\b"
            replacement = rf"[{name}](#{ref.anchor})"
            type_str = re.sub(pattern, replacement, type_str)

        for index, link in enumerate(existing_links):
            type_str = type_str.replace(f"@@PYDOC2MARKDOWN_LINK_{index}@@", link)
        return type_str

    def _refs_for(self, target: list[TypeRef] | TypeRef | str) -> list[TypeRef]:
        """Return normalized type references for one indexed name."""
        if isinstance(target, list):
            return target
        if isinstance(target, TypeRef):
            return [target]
        return [TypeRef(anchor=target)]

    def _select_ref(
        self,
        target: list[TypeRef] | TypeRef | str,
        *,
        current_module: str | None,
    ) -> TypeRef | None:
        """Choose the safest link target for a type name."""
        refs = self._refs_for(target)
        if current_module is not None:
            return next(
                (ref for ref in refs if ref.module is None or ref.module == current_module),
                None,
            )
        if len(refs) == 1:
            return refs[0]
        return None
