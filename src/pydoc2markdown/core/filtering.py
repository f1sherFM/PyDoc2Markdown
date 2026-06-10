"""Helpers for filtering documented module members before rendering or reporting."""

import fnmatch
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
    module_name = f"{module.package}.{module.name}" if module.package else module.name

    filtered_classes: list[ClassDoc] = []
    for class_doc in module.classes:
        filtered_class = _filter_class(class_doc, module_name=module_name, options=options)
        keep_class = _keep_top_level_name(
            class_doc.name,
            module_name=module_name,
            exported_names=exported_names,
            restrict_to_public_api=restrict_to_public_api,
            options=options,
        )
        if (
            keep_class
            or filtered_class.methods
            or filtered_class.attributes
            or filtered_class.pydantic_fields
        ):
            filtered_classes.append(filtered_class)
    filtered_functions = [
        function_doc
        for function_doc in module.functions
        if _keep_top_level_name(
            function_doc.name,
            module_name=module_name,
            exported_names=exported_names,
            restrict_to_public_api=restrict_to_public_api,
            options=options,
        )
    ]
    available_top_level_names = {
        *(class_doc.name for class_doc in filtered_classes),
        *(function_doc.name for function_doc in filtered_functions),
    }
    filtered_public_api = [
        export_name
        for export_name in module.public_api
        if _keep_export_name(
            export_name,
            module_name=module_name,
            available_top_level_names=available_top_level_names,
            options=options,
        )
    ]

    return replace(
        module,
        classes=filtered_classes,
        functions=filtered_functions,
        public_api=filtered_public_api,
    )


def _filter_class(class_doc: ClassDoc, *, module_name: str, options: object | None) -> ClassDoc:
    filtered_methods = [
        method
        for method in class_doc.methods
        if _keep_member_name(
            method.name,
            options,
            owner_name=class_doc.name,
            module_name=module_name,
        )
    ]
    filtered_attributes = [
        attribute
        for attribute in class_doc.attributes
        if _keep_member_name(
            attribute.name,
            options,
            owner_name=class_doc.name,
            module_name=module_name,
        )
    ]
    filtered_pydantic_fields = [
        field
        for field in class_doc.pydantic_fields
        if _keep_member_name(
            field.name,
            options,
            owner_name=class_doc.name,
            module_name=module_name,
        )
    ]
    return replace(
        class_doc,
        methods=filtered_methods,
        attributes=filtered_attributes,
        pydantic_fields=filtered_pydantic_fields,
    )


def _keep_top_level_name(
    name: str,
    *,
    module_name: str,
    exported_names: set[str],
    restrict_to_public_api: bool,
    options: object | None,
) -> bool:
    if name in exported_names:
        return _matches_member_patterns(name, options, module_name=module_name)
    if restrict_to_public_api:
        return False
    return _keep_member_name(name, options, module_name=module_name)


def _keep_export_name(
    name: str,
    *,
    module_name: str,
    available_top_level_names: set[str],
    options: object | None,
) -> bool:
    if name in available_top_level_names:
        return True
    return _matches_member_patterns(name, options, module_name=module_name)


def _keep_member_name(
    name: str,
    options: object | None,
    *,
    owner_name: str | None = None,
    module_name: str | None = None,
) -> bool:
    if name == "__init__":
        return True
    if _is_dunder_name(name):
        if not _option(options, "show_dunder_members", False):
            return False
        return _matches_member_patterns(
            name,
            options,
            owner_name=owner_name,
            module_name=module_name,
        )
    if _is_private_name(name):
        if not _option(options, "show_private_members", False):
            return False
        return _matches_member_patterns(
            name,
            options,
            owner_name=owner_name,
            module_name=module_name,
        )
    return _matches_member_patterns(
        name,
        options,
        owner_name=owner_name,
        module_name=module_name,
    )


def _matches_member_patterns(
    name: str,
    options: object | None,
    *,
    owner_name: str | None = None,
    module_name: str | None = None,
) -> bool:
    include_patterns = _patterns(options, "member_include")
    exclude_patterns = _patterns(options, "member_exclude")
    candidate_names = _candidate_names(name, owner_name=owner_name, module_name=module_name)

    if include_patterns and not any(
        fnmatch.fnmatch(candidate_name, pattern)
        for candidate_name in candidate_names
        for pattern in include_patterns
    ):
        return False

    return not any(
        fnmatch.fnmatch(candidate_name, pattern)
        for candidate_name in candidate_names
        for pattern in exclude_patterns
    )


def _candidate_names(
    name: str,
    *,
    owner_name: str | None,
    module_name: str | None,
) -> tuple[str, ...]:
    names = [name]
    if owner_name:
        names.append(f"{owner_name}.{name}")
    if module_name:
        names.append(f"{module_name}.{name}")
        if owner_name:
            names.append(f"{module_name}.{owner_name}.{name}")
    return tuple(dict.fromkeys(names))


def _is_dunder_name(name: str) -> bool:
    return len(name) > 4 and name.startswith("__") and name.endswith("__")


def _is_private_name(name: str) -> bool:
    return name.startswith("_") and not _is_dunder_name(name)


def _option(options: object | None, name: str, default: bool) -> bool:
    value: Any = getattr(options, name, default)
    return value if isinstance(value, bool) else default


def _patterns(options: object | None, name: str) -> tuple[str, ...]:
    value: Any = getattr(options, name, ())
    if isinstance(value, tuple):
        return tuple(pattern for pattern in value if isinstance(pattern, str) and pattern)
    if isinstance(value, list):
        return tuple(pattern for pattern in value if isinstance(pattern, str) and pattern)
    return ()
