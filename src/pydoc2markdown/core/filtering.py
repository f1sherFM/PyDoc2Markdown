"""Helpers for filtering documented module members before rendering or reporting."""

from dataclasses import replace
from typing import Any

from pydoc2markdown.core.parser import ClassDoc, ModuleDoc


def filter_modules(
    modules: list[ModuleDoc],
    options: object | None = None,
) -> list[ModuleDoc]:
    """Return module docs filtered by the configured member-visibility options."""
    return [_filter_module(module, options) for module in modules]


def _filter_module(module: ModuleDoc, options: object | None) -> ModuleDoc:
    exported_names = set(module.public_api)
    restrict_to_public_api = bool(module.public_api) and _option(options, "public_only", False)

    filtered_classes = [
        _filter_class(class_doc, options)
        for class_doc in module.classes
        if _keep_top_level_name(
            class_doc.name,
            exported_names=exported_names,
            restrict_to_public_api=restrict_to_public_api,
            options=options,
        )
    ]
    filtered_functions = [
        function_doc
        for function_doc in module.functions
        if _keep_top_level_name(
            function_doc.name,
            exported_names=exported_names,
            restrict_to_public_api=restrict_to_public_api,
            options=options,
        )
    ]

    return replace(
        module,
        classes=filtered_classes,
        functions=filtered_functions,
        public_api=list(module.public_api),
    )


def _filter_class(class_doc: ClassDoc, options: object | None) -> ClassDoc:
    filtered_methods = [
        method for method in class_doc.methods if _keep_member_name(method.name, options)
    ]
    return replace(class_doc, methods=filtered_methods)


def _keep_top_level_name(
    name: str,
    *,
    exported_names: set[str],
    restrict_to_public_api: bool,
    options: object | None,
) -> bool:
    if name in exported_names:
        return True
    if restrict_to_public_api:
        return False
    return _keep_member_name(name, options)


def _keep_member_name(name: str, options: object | None) -> bool:
    if name == "__init__":
        return True
    if _is_dunder_name(name):
        return _option(options, "show_dunder_members", False)
    if _is_private_name(name):
        return _option(options, "show_private_members", False)
    return True


def _is_dunder_name(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _is_private_name(name: str) -> bool:
    return name.startswith("_") and not _is_dunder_name(name)


def _option(options: object | None, name: str, default: bool) -> bool:
    value: Any = getattr(options, name, default)
    return value if isinstance(value, bool) else default
