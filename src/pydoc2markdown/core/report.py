"""Documentation coverage analysis and terminal reporting."""

import json
from dataclasses import dataclass, field

from pydoc2markdown.core.parser import FunctionDoc, ModuleDoc

REPORT_CATEGORY_TITLES = {
    "modules": "Modules without docstrings",
    "classes": "Classes without docstrings",
    "functions": "Functions without docstrings",
    "public_api": "Undocumented public API exports",
    "params": "Parameters missing descriptions",
}
REPORT_COVERAGE_LABELS = {
    "modules": "Modules",
    "classes": "Classes",
    "functions": "Functions",
    "public_api": "Public API exports",
    "params": "Parameter descriptions",
}
REPORT_CATEGORY_ORDER = ("modules", "classes", "functions", "public_api", "params")


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
    public_api_count: int = 0
    parameter_count: int = 0

    def category_counts(self) -> dict[str, int]:
        """Return finding counts keyed by report category."""
        return {
            "modules": len(self.undocumented_modules),
            "classes": len(self.undocumented_classes),
            "functions": len(self.undocumented_functions),
            "public_api": len(self.undocumented_public_api),
            "params": len(self.params_missing_descriptions),
        }

    def category_totals(self) -> dict[str, int]:
        """Return total documentable items keyed by report category."""
        return {
            "modules": self.module_count,
            "classes": self.class_count,
            "functions": self.function_count,
            "public_api": self.public_api_count,
            "params": self.parameter_count,
        }

    def category_documented(self) -> dict[str, int]:
        """Return documented counts keyed by report category."""
        totals = self.category_totals()
        findings = self.category_counts()
        return {key: max(totals.get(key, 0) - findings.get(key, 0), 0) for key in totals}

    def category_percentages(self) -> dict[str, float]:
        """Return coverage percentages keyed by report category."""
        totals = self.category_totals()
        documented = self.category_documented()
        percentages: dict[str, float] = {}
        for key, total in totals.items():
            if total == 0:
                percentages[key] = 100.0
            else:
                percentages[key] = (documented[key] / total) * 100
        return percentages

    def total_findings(self) -> int:
        """Return the total number of report findings."""
        return sum(self.category_counts().values())

    def total_checks(self) -> int:
        """Return the total number of documentable checks in the report."""
        return sum(self.category_totals().values())

    def overall_percentage(self) -> float:
        """Return overall documentation coverage as a percentage."""
        total_checks = self.total_checks()
        if total_checks == 0:
            return 100.0
        documented = total_checks - self.total_findings()
        return (documented / total_checks) * 100

    def has_findings(self, categories: set[str] | None = None) -> bool:
        """Return whether any findings exist in the selected categories."""
        counts = self.category_counts()
        keys = categories or set(counts)
        return any(counts.get(key, 0) > 0 for key in keys)

    def findings_by_category(self) -> dict[str, list[str]]:
        """Return findings keyed by report category."""
        return {
            "modules": self.undocumented_modules,
            "classes": self.undocumented_classes,
            "functions": self.undocumented_functions,
            "public_api": self.undocumented_public_api,
            "params": self.params_missing_descriptions,
        }

    def to_dict(self, categories: tuple[str, ...] | None = None) -> dict[str, object]:
        """Return a machine-readable representation of the report."""
        selected_categories = categories or REPORT_CATEGORY_ORDER
        all_counts = self.category_counts()
        all_totals = self.category_totals()
        all_documented = self.category_documented()
        all_percentages = self.category_percentages()
        all_findings = self.findings_by_category()
        return {
            "summary": {
                "module_count": self.module_count,
                "class_count": self.class_count,
                "function_count": self.function_count,
                "public_api_count": self.public_api_count,
                "parameter_count": self.parameter_count,
                "total_checks": self.total_checks(),
                "total_findings": self.total_findings(),
                "overall_percentage": self.overall_percentage(),
                "selected_categories": list(selected_categories),
            },
            "counts": {key: all_counts[key] for key in selected_categories},
            "totals": {key: all_totals[key] for key in selected_categories},
            "documented": {key: all_documented[key] for key in selected_categories},
            "percentages": {key: all_percentages[key] for key in selected_categories},
            "findings": {key: all_findings[key] for key in selected_categories},
        }


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
        report.public_api_count += len(module.public_api)

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
            report.parameter_count += 1
            if param.description:
                continue
            qualified_name = f"{module_name}.{function_doc.name}"
            if owner:
                qualified_name = f"{module_name}.{owner}.{function_doc.name}"
            report.params_missing_descriptions.append(f"{qualified_name}({param.name})")


def format_report(
    report: CoverageReport,
    *,
    categories: tuple[str, ...] | None = None,
    summary_only: bool = False,
) -> str:
    """Format a human-readable terminal report."""
    selected_categories = categories or REPORT_CATEGORY_ORDER
    passed_checks = report.total_checks() - report.total_findings()
    lines = [
        "Documentation Coverage Report",
        "",
        (
            f"Scanned {report.module_count} module(s), "
            f"{report.class_count} class(es), "
            f"and {report.function_count} function(s)."
        ),
        (
            f"Overall coverage: {report.overall_percentage():.1f}% "
            f"({passed_checks}/{report.total_checks()} checks passed)"
        ),
        "",
        "Coverage by category:",
    ]
    findings = report.findings_by_category()
    for key in selected_categories:
        _append_coverage_line(lines, REPORT_COVERAGE_LABELS[key], report, key)
    for key in selected_categories:
        _append_section(
            lines,
            REPORT_CATEGORY_TITLES[key],
            findings[key],
            summary_only=summary_only,
        )
    return "\n".join(lines) + "\n"


def format_report_json(report: CoverageReport, *, categories: tuple[str, ...] | None = None) -> str:
    """Format a machine-readable JSON coverage report."""
    return json.dumps(report.to_dict(categories=categories), indent=2) + "\n"


def _append_section(
    lines: list[str],
    title: str,
    values: list[str],
    *,
    summary_only: bool,
) -> None:
    """Append a findings section to the terminal report."""
    lines.extend(["", f"{title}: {len(values)}"])
    if summary_only:
        return
    for value in values:
        lines.append(f"- {value}")


def _append_coverage_line(
    lines: list[str],
    title: str,
    report: CoverageReport,
    key: str,
) -> None:
    """Append one coverage summary line for a report category."""
    totals = report.category_totals()
    documented = report.category_documented()
    percentages = report.category_percentages()
    lines.append(f"- {title}: {percentages[key]:.1f}% ({documented[key]}/{totals[key]})")
