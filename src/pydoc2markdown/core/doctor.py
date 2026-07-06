"""Project diagnostics for PyDoc2Markdown onboarding."""

from dataclasses import dataclass
from pathlib import Path

from pydoc2markdown.core.parser import ModuleDoc
from pydoc2markdown.core.report import CoverageReport, analyze_modules


@dataclass(frozen=True)
class DoctorOptions:
    """Context used to render a project diagnostics report."""

    source: Path
    recursive: bool
    output: Path
    readme_path: Path
    cwd: Path
    filter_options: object | None = None


def format_doctor_report(modules: list[ModuleDoc], options: DoctorOptions) -> str:
    """Return a human-readable diagnostics report for a Python documentation surface."""
    report = analyze_modules(modules, filter_options=options.filter_options)
    lines = [
        "PyDoc2Markdown Doctor",
        "",
        "Scanned:",
        f"- Source: {options.source}",
        f"- Recursive: {_yes_no(options.recursive)}",
        f"- Modules: {report.module_count}",
        f"- Classes: {report.class_count}",
        f"- Functions: {report.function_count}",
        f"- __all__ exports: {report.public_api_count}",
        "",
        "Docs readiness:",
        _coverage_line("Module docstrings", report, "modules"),
        _coverage_line("Class docstrings", report, "classes"),
        _coverage_line("Function docstrings", report, "functions"),
        _coverage_line("Public API exports", report, "public_api"),
        _coverage_line("Parameter descriptions", report, "params"),
        f"- Overall: {report.overall_percentage():.1f}%",
        "",
        "Project signals:",
        f"- README target: {_path_status(options.readme_path)}",
        f"- pyproject config: {_config_status(options.cwd)}",
        f"- Generated docs target: {options.output}",
        "",
        "Recommended commands:",
    ]
    lines.extend(_recommended_commands(options))
    notes = _doctor_notes(report, modules, options)
    if notes:
        lines.extend(["", "Notes:", *notes])
    return "\n".join(lines) + "\n"


def _coverage_line(label: str, report: CoverageReport, key: str) -> str:
    """Return one documented/total coverage line for a report category."""
    totals = report.category_totals()
    documented = report.category_documented()
    percentages = report.category_percentages()
    return f"- {label}: {documented[key]}/{totals[key]} ({percentages[key]:.1f}%)"


def _recommended_commands(options: DoctorOptions) -> list[str]:
    """Return useful next-step commands for the scanned source."""
    source = _command_path(options.source)
    output = _command_path(options.output)
    readme = _command_path(options.readme_path)
    recursive = " --recursive" if options.source.is_dir() else ""
    return [
        "- Generate navigation docs:",
        f"  pydoc2markdown {source}{recursive} --nav -o {output}",
        "- Keep README API section in sync:",
        f"  pydoc2markdown {source}{recursive} --readme --readme-path {readme}",
        "- Check generated docs in CI:",
        f"  pydoc2markdown {source}{recursive} --nav --readme --check -o {output}",
        "- Inspect documentation coverage:",
        f"  pydoc2markdown {source}{recursive} --report",
    ]


def _doctor_notes(
    report: CoverageReport,
    modules: list[ModuleDoc],
    options: DoctorOptions,
) -> list[str]:
    """Return short contextual notes for the diagnostics report."""
    notes: list[str] = []
    if not modules:
        notes.append("- No Python modules were parsed. Check the source path or include filters.")
        if options.source.is_dir() and not options.recursive:
            notes.append("- For package directories, try adding --recursive.")
        return notes
    if options.source.is_dir() and not options.recursive:
        notes.append(
            "- Directory scan is not recursive. Add --recursive to inspect nested packages."
        )
    if report.total_findings() == 0:
        notes.append("- No documentation coverage gaps found in the scanned surface.")
    else:
        counts = report.category_counts()
        largest = max(counts, key=lambda key: counts[key])
        if counts[largest] > 0:
            labels = {
                "modules": "module docstrings",
                "classes": "class docstrings",
                "functions": "function docstrings",
                "public_api": "__all__ exports",
                "params": "parameter descriptions",
            }
            notes.append(f"- Largest documentation gap: {labels[largest]} ({counts[largest]}).")
    if not options.readme_path.exists():
        notes.append("- README target is missing. --readme can create it.")
    if not _has_pydoc2markdown_config(options.cwd):
        notes.append(
            "- No [tool.pydoc2markdown] config found. Run pydoc2markdown --init to add defaults."
        )
    return notes


def _path_status(path: Path) -> str:
    """Return a compact found/missing status for a path."""
    status = "found" if path.exists() else "missing"
    return f"{path} ({status})"


def _config_status(cwd: Path) -> str:
    """Return whether pyproject.toml contains the PyDoc2Markdown config section."""
    pyproject = cwd / "pyproject.toml"
    if not pyproject.exists():
        return "missing pyproject.toml"
    if _has_pydoc2markdown_config(cwd):
        return f"{pyproject} ([tool.pydoc2markdown] found)"
    return f"{pyproject} ([tool.pydoc2markdown] missing)"


def _has_pydoc2markdown_config(cwd: Path) -> bool:
    """Return whether cwd/pyproject.toml contains [tool.pydoc2markdown]."""
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    pyproject = cwd / "pyproject.toml"
    if not pyproject.exists():
        return False
    try:
        with pyproject.open("rb") as file:
            data = tomllib.load(file)
    except Exception:
        return False
    tool = data.get("tool", {})
    return isinstance(tool, dict) and isinstance(tool.get("pydoc2markdown"), dict)


def _command_path(path: Path) -> str:
    """Return a shell-friendly path token for displayed example commands."""
    text = path.as_posix()
    if any(ch.isspace() for ch in text):
        return f'"{text}"'
    return text


def _yes_no(value: bool) -> str:
    """Return yes/no for terminal output."""
    return "yes" if value else "no"
