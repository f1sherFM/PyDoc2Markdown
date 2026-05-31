# PyDoc2Markdown

[![CI](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/f1sherFM/PyDoc2Markdown/branch/main/graph/badge.svg)](https://codecov.io/gh/f1sherFM/PyDoc2Markdown)
[![PyPI](https://img.shields.io/pypi/v/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)
[![License](https://img.shields.io/pypi/l/pydoc2markdown)](https://github.com/f1sherFM/PyDoc2Markdown/blob/main/LICENSE)

> Convert Python docstrings into clean, structured Markdown documentation.

## Table of Contents

- [Why PyDoc2Markdown?](#why-pydoc2markdown)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [CLI Usage](#cli-usage)
  - [Library Usage](#library-usage)
- [CLI Reference](#cli-reference)
- [Configuration](#configuration)
- [README API Sections](#readme-api-sections)
- [Navigation Docs Layout](#navigation-docs-layout)
- [Library API](#library-api)
- [Supported Docstring Formats](#supported-docstring-formats)
- [Example Output](#example-output)
- [Documentation](#documentation)
- [License](#license)

## Why PyDoc2Markdown?

Documentation generators like **Sphinx** are powerful but require significant configuration — themes, `conf.py`, extensions, and often custom builders to get clean output. **pdoc** and **mkdocstrings** are easier but still depend on a full documentation framework.

PyDoc2Markdown takes a different approach: **zero configuration, zero framework dependencies, pure Markdown output.** Point it at your Python project and get structured Markdown files that work anywhere — GitHub, GitLab, MkDocs, or any Markdown renderer.

- **No `conf.py`** — works out of the box
- **No framework lock-in** — generates plain `.md` files
- **Minimal dependencies** — Jinja2 + docstring-parser

## Features

- **Docstring parsing** — Extract Google and NumPy style docstrings, with basic reStructuredText field support via `docstring-parser`.
- **Markdown generation** — Produce beautiful Markdown files with customizable Jinja2 templates.
- **README API sections** — Create or update a generated API reference block in README files.
- **Auto-generated index & TOC** — Each module gets a Table of Contents; an `index.md` with package grouping is created automatically.
- **Navigation layout** — Generate a docs entrypoint with package pages and API files under `api/`.
- **Package grouping** — Output files are organized into subdirectories matching the package structure.
- **Built-in themes** — Choose between `default` (detailed) and `minimal` themes, or supply your own template.
- **CLI & API** — Use via command line or import as a Python library.
- **Recursive processing** — Scan entire packages in one command.
- **Type-aware** — Respects type hints and annotations.
- **Advanced constructs** — Supports `property`, `classmethod`, `staticmethod`, `dataclass`, `Enum`, `TypedDict`, `Protocol`, `ABC`, `Pydantic`, and `__all__`.

## Requirements

- Python >= 3.10
- Dependencies: [Jinja2](https://jinja.palletsprojects.com/), [docstring-parser](https://github.com/rr-/docstring-parser)
- Optional: [watchdog](https://github.com/argoslabs/python-watchdog) (for `--watch` mode)

## Installation

```bash
# Base installation
pip install pydoc2markdown

# With file watcher support
pip install pydoc2markdown[watch]
```

## Quick Start

### CLI Usage

```bash
# Initialize default configuration in pyproject.toml
pydoc2markdown --init

# Generate docs for a single file
pydoc2markdown my_module.py -o docs

# Recursively process a package
pydoc2markdown src/my_package --recursive -o docs

# Use a built-in theme
pydoc2markdown src/my_package --recursive --theme minimal -o docs

# Use a custom template
pydoc2markdown src/my_package --recursive --template custom.md.j2 -o docs

# Single combined file
pydoc2markdown src/my_package --recursive --single-file -o docs/README.md

# Update the API section in README.md
pydoc2markdown src/my_package --recursive --readme

# Generate a navigation-first docs layout
pydoc2markdown src/my_package --recursive --nav -o docs

# Watch mode — auto-regenerate on changes
pydoc2markdown src/my_package --recursive --watch -o docs

# Enable verbose logging
pydoc2markdown src/my_package --recursive -vv -o docs
```

### Library Usage

```python
from pathlib import Path
from pydoc2markdown import DocstringParser, MarkdownGenerator

parser = DocstringParser()
modules = parser.parse(Path("src/my_package"), recursive=True)

generator = MarkdownGenerator(theme="default")
generator.generate(modules, output_dir=Path("docs"))
```

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `source` | *(required unless `--init` is used)* | Path to a Python file or directory to process |
| `--init` | `False` | Create or update `[tool.pydoc2markdown]` in `pyproject.toml` |
| `-o`, `--output` | `docs` / value from `pyproject.toml` | Output directory (or file path when `--single-file` is used) |
| `--recursive` | `False` / value from `pyproject.toml` | Recursively process subdirectories |
| `--theme` | `default` / value from `pyproject.toml` | Built-in theme: `default` (detailed) or `minimal` |
| `--template` | `None` | Path to a custom Jinja2 template for Markdown generation |
| `--single-file` | `False` | Generate a single combined Markdown file instead of separate files |
| `--readme` | `False` | Create or update an API reference section in README.md |
| `--readme-path` | `README.md` | Path to the README file updated by `--readme` |
| `--nav` | `False` | Generate a navigation-first docs layout with API pages under `api/` |
| `--api-dir` | `api` | Directory for API pages when `--nav` is used |
| `--watch` | `False` | Watch source files and regenerate docs on change |
| `-v`, `--verbose` | `0` | Increase verbosity (`-v` = INFO, `-vv` = DEBUG) |
| `--version` | — | Show version and exit |

**Configuration priority:** CLI flags > `[tool.pydoc2markdown]` in `pyproject.toml` > built-in defaults.

## Configuration

You can initialize default configuration with:

```bash
pydoc2markdown --init
```

This creates or appends a `[tool.pydoc2markdown]` section in `pyproject.toml`.
If the section already exists, it is left unchanged.

You can also set default values manually in your `pyproject.toml`:

```toml
[tool.pydoc2markdown]
output = "docs"
theme = "default"
recursive = true
```

Any values set here serve as defaults and can be overridden by CLI flags.

## README API Sections

Use `--readme` to create or update a compact API reference in your README:

```bash
pydoc2markdown src/my_package --recursive --readme
```

By default, PyDoc2Markdown updates `README.md`. Use `--readme-path` to target a
different file:

```bash
pydoc2markdown src/my_package --recursive --readme --readme-path docs/index.md
```

When the file already contains PyDoc2Markdown markers, only the generated block
between the markers is replaced:

```markdown
## API Reference

<!-- pydoc2markdown:start -->
<!-- pydoc2markdown:end -->
```

If the markers are missing, a new `## API Reference` section is appended. If the
README does not exist, it is created.

## Navigation Docs Layout

Use `--nav` when you want a docs directory that is ready to browse from a single
entrypoint:

```bash
pydoc2markdown src/my_package --recursive --nav -o docs
```

This creates a layout like:

```text
docs/
├── index.md
├── modules.md
└── api/
    ├── package.md
    └── utils.md
```

The root `index.md` links to package landing pages and every generated API page.
Use `--api-dir` to change where module pages are written:

```bash
pydoc2markdown src/my_package --recursive --nav --api-dir reference -o docs
```

## Library API

### DocstringParser

```python
from pathlib import Path
from pydoc2markdown import DocstringParser

parser = DocstringParser()
modules = parser.parse(Path("src/my_package"), recursive=True)
```

### MarkdownGenerator

```python
from pathlib import Path
from pydoc2markdown import DocstringParser, MarkdownGenerator

# Parse modules
parser = DocstringParser()
modules = parser.parse(Path("src/my_package"), recursive=True)

# Default theme, separate files
gen = MarkdownGenerator(theme="default")
gen.generate(modules, output_dir=Path("docs"))

# Minimal theme
gen_min = MarkdownGenerator(theme="minimal")
gen_min.generate(modules, output_dir=Path("docs_minimal"))

# Custom template
gen_tmpl = MarkdownGenerator(template_path=Path("my_template.md.j2"))
gen_tmpl.generate(modules, output_dir=Path("docs_custom"))

# Single combined file
gen.generate_single_file(modules, output_path=Path("docs/README.md"))

# README API section
gen.update_readme(modules, readme_path=Path("README.md"))

# Navigation docs layout
gen.generate_navigation(modules, output_dir=Path("docs"))

# Markdown string for a single module
md_string = gen.generate_string(modules[0])
```

## Supported Docstring Formats

PyDoc2Markdown uses [docstring-parser](https://github.com/rr-/docstring-parser) and supports common structured docstring sections:

| Style | Support | Notes |
|-------|---------|-------|
| **Google** | ✅ Full | Args, Returns, Raises, Attributes, Examples |
| **NumPy** | ✅ Full | Parameters, Returns, Raises, Attributes, Examples |
| **reStructuredText (reST)** | ⚠️ Basic | Field-style metadata via `docstring-parser`, including `:param:`, `:returns:`, and `:raises:` |

## Example Output

Given this source file:

```python
from pydantic import BaseModel, Field


class User(BaseModel):
    """A user in the system."""

    id: int = Field(description="Unique identifier")
    email: str = Field(default="", description="Email address")
    is_active: bool = True


class UserService:
    """Service for managing users."""

    def get_user(self, user_id: int) -> User:
        """Fetch a user by ID.

        Args:
            user_id: The user's unique identifier.

        Returns:
            The requested User instance.

        Raises:
            ValueError: If the user does not exist.
        """
        ...
```

Running `pydoc2markdown src/users.py -o docs` produces:

```markdown
# users

## Table of Contents

- [Classes](#classes)
  - [`User`](#user)
  - [`UserService`](#userservice)

## Classes

### `User` *(Pydantic)*

A user in the system.

#### Pydantic Fields

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `id` | `int` | *required* | Unique identifier |
| `email` | `str` | `""` | Email address |
| `is_active` | `bool` | `True` | - |

### `UserService`

Service for managing users.

#### Methods

##### `get_user`

Fetch a user by ID.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `user_id` | `int` | *required* | The user's unique identifier. |

**Returns:** `User`

**Raises:**

- `ValueError` — If the user does not exist.
```

For a complete small project, see [examples/sample_project/](examples/sample_project/).
It includes source code, a generated README API section, and a navigation-first
docs layout generated by PyDoc2Markdown. You can also see pre-built
documentation for this repository in [examples/docs/](examples/docs/).

## Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Project Structure](PROJECT_STRUCTURE.md)

## License

MIT License — see [LICENSE](LICENSE) for details.
