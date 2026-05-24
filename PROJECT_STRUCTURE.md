# PyDoc2Markdown — Project Structure

## Overview

**Project name:** `PyDoc2Markdown`  
**Project type:** CLI tool / Python library  
**Core features:** docstring parsing, Markdown generation, customizable templates  

---

## Directory Tree

```
PyDoc2Markdown/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions: test, lint, type-check, release
├── src/
│   └── pydoc2markdown/
│       ├── __init__.py         # Package entry point; exports public API
│       ├── cli.py              # Argument parsing and CLI entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── parser.py       # AST-based docstring extraction
│       │   └── generator.py    # Jinja2-based Markdown generation
│       └── utils/
│           ├── __init__.py
│           └── helpers.py      # String utilities (slugify, docstring cleanup)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures and shared test utilities
│   ├── test_parser.py          # Unit tests for DocstringParser
│   ├── test_generator.py       # Unit tests for MarkdownGenerator
│   └── test_cli.py             # Unit tests for CLI argument handling
├── docs/
│   └── .gitkeep                # Documentation site / guides (placeholder)
├── examples/
│   ├── basic_usage.py          # Minimal library usage example
│   └── custom_template.md.j2   # Example Jinja2 template
├── .gitignore                  # Standard Python .gitignore
├── pyproject.toml              # Build, dependency, and tool configuration
├── README.md                   # Project overview, quick start, badges
├── CONTRIBUTING.md             # Setup, commit conventions, PR process
└── PROJECT_STRUCTURE.md        # This file
```

---

## Purpose of Each Directory / File

### `.github/workflows/ci.yml`
- **Why it exists:** Automates CI/CD on every push and PR.
- **What it does:**
  - Runs the test matrix across Python 3.10, 3.11, and 3.12.
  - Lints code with `ruff`.
  - Type-checks with `mypy`.
  - Uploads coverage to Codecov.
  - Publishes releases to PyPI when a `v*` tag is pushed.

### `src/pydoc2markdown/`
- **Why it exists:** Houses all library code. Using `src/` layout prevents accidental imports from the repository root and encourages installation before testing.

#### `src/pydoc2markdown/__init__.py`
- **Why it exists:** Declares the public API.
- **Exports:** `DocstringParser`, `MarkdownGenerator`, `__version__`.

#### `src/pydoc2markdown/cli.py`
- **Why it exists:** Provides a user-friendly command-line interface.
- **Key responsibilities:**
  - Parse `argparse` arguments (`source`, `--output`, `--recursive`, `--template`).
  - Validate source paths.
  - Orchestrate `DocstringParser` → `MarkdownGenerator`.
  - Return standard exit codes (`0` for success, `1` for error).

### `src/pydoc2markdown/core/`
- **Why it exists:** Separates core business logic from CLI and utilities.

#### `src/pydoc2markdown/core/parser.py`
- **Why it exists:** Extracts structured documentation from Python source files.
- **Key classes:**
  - `ModuleDoc` — top-level module info (classes, functions, docstring).
  - `ClassDoc` — class info (methods, attributes, bases).
  - `FunctionDoc` — function/method info (params, returns, raises).
  - `Parameter` — typed parameter representation.
  - `DocstringParser` — orchestrates AST traversal and populates the above models.

#### `src/pydoc2markdown/core/generator.py`
- **Why it exists:** Converts parsed models into Markdown text.
- **Key classes:**
  - `MarkdownGenerator` — loads Jinja2 templates and renders `ModuleDoc` objects into `.md` files.
- **Features:**
  - Default built-in template (no external files required).
  - Optional custom Jinja2 template via `--template`.

### `src/pydoc2markdown/utils/`
- **Why it exists:** Holds pure, stateless helper functions reused across the core.

#### `src/pydoc2markdown/utils/helpers.py`
- **Why it exists:** Shared formatting utilities.
- **Functions:**
  - `clean_docstring()` — normalizes indentation and trims whitespace.
  - `slugify()` — converts headings into URL-friendly anchors.

### `tests/`
- **Why it exists:** Comprehensive pytest-based test suite.
- **Files:**
  - `conftest.py` — shared fixtures (e.g., sample Python source files).
  - `test_parser.py` — verifies AST extraction accuracy.
  - `test_generator.py` — verifies Markdown output correctness.
  - `test_cli.py` — verifies argument parsing and exit codes.

### `docs/`
- **Why it exists:** Reserved for Sphinx / MkDocs documentation site (future expansion).

### `examples/`
- **Why it exists:** Demonstrates real-world usage for new users.
- **Files:**
  - `basic_usage.py` — programmatic API usage.
  - `custom_template.md.j2` — example Jinja2 template override.

### `pyproject.toml`
- **Why it exists:** Single source of truth for project metadata, dependencies, and tool configuration.
- **Sections:**
  - `[project]` — name, version, description, authors, classifiers.
  - `[project.optional-dependencies]` — `dev` extras (pytest, ruff, mypy).
  - `[project.scripts]` — CLI entry point `pydoc2markdown`.
  - `[tool.ruff]` — linting and formatting rules.
  - `[tool.mypy]` — strict type-checking configuration.
  - `[tool.pytest.ini_options]` — test discovery and coverage settings.

---

## Example Code Snippets

### `cli.py` — CLI Entry Point

```python
import argparse
import sys
from pathlib import Path

from pydoc2markdown.core.parser import DocstringParser
from pydoc2markdown.core.generator import MarkdownGenerator


def main(args: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pydoc2markdown",
        description="Convert Python docstrings to Markdown documentation.",
    )
    parser.add_argument("source", type=Path, help="Path to a Python file or directory.")
    parser.add_argument("-o", "--output", type=Path, default=Path("docs"))
    parser.add_argument("--recursive", action="store_true")
    parser.add_argument("--template", type=Path, default=None)
    parsed = parser.parse_args(args)

    modules = DocstringParser().parse(parsed.source, recursive=parsed.recursive)
    MarkdownGenerator(template_path=parsed.template).generate(modules, parsed.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### `parser.py` — Core Extraction Logic

```python
import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class ModuleDoc:
    name: str
    path: Path
    docstring: str | None = None
    classes: list = field(default_factory=list)
    functions: list = field(default_factory=list)


class DocstringParser:
    def parse(self, source: Path, recursive: bool = False) -> List[ModuleDoc]:
        modules = []
        pattern = "**/*.py" if recursive else "*.py"
        for file_path in source.glob(pattern):
            tree = ast.parse(file_path.read_text())
            modules.append(self._extract_module(file_path, tree))
        return modules

    def _extract_module(self, path: Path, tree: ast.AST) -> ModuleDoc:
        module = ModuleDoc(name=path.stem, path=path, docstring=ast.get_docstring(tree))
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                module.classes.append(self._extract_class(node))
            elif isinstance(node, ast.FunctionDef):
                module.functions.append(self._extract_function(node))
        return module
```

### `generator.py` — Markdown Rendering

```python
from pathlib import Path
from typing import List

from jinja2 import Environment, PackageLoader

from pydoc2markdown.core.parser import ModuleDoc


class MarkdownGenerator:
    def __init__(self, template_path: Path | None = None):
        self._env = Environment(loader=PackageLoader("pydoc2markdown", "templates"))

    def generate(self, modules: List[ModuleDoc], output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        template = self._env.get_template("module.md")
        generated = []
        for module in modules:
            out = output_dir / f"{module.name}.md"
            out.write_text(template.render(module=module))
            generated.append(out)
        return generated
```

---

## Key Requirements

| Requirement        | Tool / Standard                                   |
|--------------------|---------------------------------------------------|
| Commit style       | [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`) |
| Testing framework  | `pytest` with `pytest-cov` for coverage reporting |
| Linter / Formatter | `ruff` (replaces flake8, isort, black)            |
| Type checker       | `mypy` with strict mode enabled                   |
| CI / CD            | GitHub Actions (`.github/workflows/ci.yml`)     |
| Build backend      | `hatchling` via `pyproject.toml`                |
| Package index      | PyPI (auto-publish on version tags)               |

---

## How to Extend

1. **New docstring style** (e.g., NumPy)
   - Add a new module under `src/pydoc2markdown/core/parsers/`.
   - Implement a style-specific parser class.
   - Register it in `DocstringParser` via configuration.

2. **New output format** (e.g., HTML)
   - Add a new generator class alongside `MarkdownGenerator`.
   - Abstract common logic into `BaseGenerator` if needed.

3. **New CLI flag**
   - Update `cli.py` argument parser.
   - Pass the new option through to the relevant core class.
   - Add tests in `tests/test_cli.py`.
