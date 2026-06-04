"""Documentation coverage analysis and terminal reporting."""

from dataclasses import dataclass, field

from pydoc2markdown.core.parser import FunctionDoc, ModuleDoc


@dataclass
class CoverageReport:
    """Structured documentation coverage findings."""

    module_count: int = 0
    class_count: int = 0
    function_count: int = 0
    undocumented_modules: list[str] = field(default_factory=list)
    undocumented_classes: list[str] = field(default_factory=list)
    undocumented_functions: list[str] = field(default_factory=list)
    undocumented_public_api: list[str] = field(default_factory=list)
    params_missing_descriptions: list[str] = field(default_factory=list)


def analyze_modules(modules: list[ModuleDoc]) -> CoverageReport:
    """Inspect parsed modules and return coverage findings."""
    report = CoverageReport(
        module_count=len(modules),
        class_count=sum(len(module.classes) for module in modules),
        function_count=sum(len(module.functions) for module in modules),
    )

    for module in modules:
        module_name = f"{module.package}.{module.name}" if module.package else module.name
        if not module.docstring:
            report.undocumented_modules.append(module_name)

        documented_top_level: dict[str, bool] = {}

        for class_doc in module.classes:
            documented_top_level[class_doc.name] = bool(class_doc.docstring)
            if not class_doc.docstring:
                report.undocumented_classes.append(f"{module_name}.{class_doc.name}")
            _collect_missing_param_descriptions(
                report,
                module_name=module_name,
                owner=class_doc.name,
                functions=class_doc.methods,
            )

        for function_doc in module.functions:
            documented_top_level[function_doc.name] = bool(function_doc.docstring)
            if not function_doc.docstring:
                report.undocumented_functions.append(f"{module_name}.{function_doc.name}")
            _collect_missing_param_descriptions(
                report,
                module_name=module_name,
                owner=None,
                functions=[function_doc],
            )

        for export_name in module.public_api:
            if not documented_top_level.get(export_name, False):
                report.undocumented_public_api.append(f"{module_name}.{export_name}")

    return report


def _collect_missing_param_descriptions(
    report: CoverageReport,
    *,
    module_name: str,
    owner: str | None,
    functions: list[FunctionDoc],
) -> None:
    """Collect missing parameter descriptions for documented functions/methods."""
    for function_doc in functions:
        if not function_doc.docstring:
            continue
        for param in function_doc.params:
            if param.description:
                continue
            qualified_name = f"{module_name}.{function_doc.name}"
            if owner:
                qualified_name = f"{module_name}.{owner}.{function_doc.name}"
            report.params_missing_descriptions.append(f"{qualified_name}({param.name})")


def format_report(report: CoverageReport) -> str:
    """Format a human-readable terminal report."""
    lines = [
        "Documentation Coverage Report",
        "",
        (
            f"Scanned {report.module_count} module(s), "
            f"{report.class_count} class(es), "
            f"and {report.function_count} function(s)."
        ),
    ]
    _append_section(lines, "Modules without docstrings", report.undocumented_modules)
    _append_section(lines, "Classes without docstrings", report.undocumented_classes)
    _append_section(lines, "Functions without docstrings", report.undocumented_functions)
    _append_section(lines, "Undocumented public API exports", report.undocumented_public_api)
    _append_section(
        lines,
        "Parameters missing descriptions",
        report.params_missing_descriptions,
    )
    return "\n".join(lines) + "\n"


def _append_section(lines: list[str], title: str, values: list[str]) -> None:
    """Append a findings section to the terminal report."""
    lines.extend(["", f"{title}: {len(values)}"])
    for value in values:
        lines.append(f"- {value}")
