"""Shared helpers for generated documentation outputs."""

import json
import os
from pathlib import Path

from pydoc2markdown.core.parser import ModuleDoc

MANIFEST_VERSION = 1


def manifest_path(output: Path, *, single_file: bool) -> Path:
    """Return the manifest path for generated Markdown files."""
    if single_file:
        return output.parent / f".{output.name}.pydoc2markdown.json"
    return output / ".pydoc2markdown.json"


def write_manifest(output: Path, *, single_file: bool, generated_paths: list[Path]) -> None:
    """Persist generated Markdown paths for future prune operations."""
    path = manifest_path(output, single_file=single_file)
    base_dir = output.parent if single_file else output
    payload = {
        "version": MANIFEST_VERSION,
        "single_file": single_file,
        "files": sorted(
            str(generated.relative_to(base_dir).as_posix()) for generated in generated_paths
        ),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def readme_module_links(
    modules: list[ModuleDoc],
    *,
    output: Path,
    readme_path: Path,
    single_file: bool,
    navigation: bool,
    api_dir: Path,
) -> dict[str, str]:
    """Build README links to generated module docs for the current run."""
    if single_file:
        return {}

    links: dict[str, str] = {}
    readme_dir = readme_path.resolve().parent
    docs_root = output / api_dir if navigation else output
    for module in modules:
        if module.name == "__init__":
            continue
        module_name = f"{module.package}.{module.name}" if module.package else module.name
        module_path = (
            docs_root / module.package.replace(".", "/") / f"{module.name}.md"
            if module.package
            else docs_root / f"{module.name}.md"
        )
        links[module_name] = Path(
            os.path.relpath(module_path.resolve(), start=readme_dir)
        ).as_posix()
    return links
