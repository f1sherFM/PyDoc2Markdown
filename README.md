# PyDoc2Markdown

[![CI](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/f1sherFM/PyDoc2Markdown/branch/main/graph/badge.svg)](https://codecov.io/gh/f1sherFM/PyDoc2Markdown)
[![PyPI](https://img.shields.io/pypi/v/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)
[![License](https://img.shields.io/pypi/l/pydoc2markdown)](https://github.com/f1sherFM/PyDoc2Markdown/blob/main/LICENSE)

> Convert Python docstrings into clean, structured Markdown documentation.

PyDoc2Markdown is a lightweight documentation tool for Python projects that want
plain Markdown output without adopting a full documentation framework. It works
as both a CLI and a library: point it at your source code, and it generates
module docs, a navigation-ready docs directory, or an API section inside your
README.

It is built for projects that want documentation to stay close to the code while
remaining easy to publish on GitHub, GitLab, MkDocs, or any Markdown renderer.

## Table of Contents

- [Why PyDoc2Markdown?](#why-pydoc2markdown)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Try It In 30 Seconds](#try-it-in-30-seconds)
- [Sample Project](#sample-project)
- [Before And After](#before-and-after)
- [Common Commands](#common-commands)
- [Quick Start](#quick-start)
  - [CLI Usage](#cli-usage)
  - [Library Usage](#library-usage)
- [CLI Reference](#cli-reference)
- [Configuration](#configuration)
- [Module Filtering](#module-filtering)
- [Source Links](#source-links)
- [README API Sections](#readme-api-sections)
- [Navigation Docs Layout](#navigation-docs-layout)
- [CI Checks](#ci-checks)
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
- **Practical defaults** — useful CLI output before you write any config

## Features

- **Docstring parsing** — Extract Google and NumPy style docstrings, with basic reStructuredText field support via `docstring-parser`.
- **Markdown generation** — Produce beautiful Markdown files with customizable Jinja2 templates.
- **README API sections** — Create or update a generated API reference block in README files.
- **Auto-generated index & TOC** — Each module gets a Table of Contents; an `index.md` with package grouping is created automatically.
- **Navigation layout** — Generate a docs entrypoint with package pages and API files under `api/`.
- **CI-friendly checks** — Verify generated docs are up to date with `--check`.
- **Module filtering** — Include or exclude source files with glob patterns.
- **Parameter defaults** — Show which function arguments are required or optional.
- **Source links** — Link generated classes, functions, and methods back to source code.
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

## Try It In 30 Seconds

Clone the repository and run PyDoc2Markdown against the included sample project:

```bash
pydoc2markdown examples/sample_project/src --recursive --nav --readme \
  --readme-path examples/sample_project/README.md \
  -o examples/sample_project/docs
```

That command updates the sample project's README API block and creates a
navigation-first docs layout:

```text
examples/sample_project/
├── README.md
├── src/shop_demo/
└── docs/
    ├── index.md
    ├── shop_demo.md
    └── api/shop_demo/
        ├── inventory.md
        └── orders.md
```

## Sample Project

The [sample project](examples/sample_project/) is a tiny shop package with
dataclasses, an enum, typed functions, properties, and Google-style docstrings.
It exists so you can inspect both sides of the workflow:

- [source code](examples/sample_project/src/shop_demo/)
- [generated docs index](examples/sample_project/docs/index.md)
- [README API section](examples/sample_project/README.md)

You can also create a local copy of the same style of demo project:

```bash
pydoc2markdown --demo
```

By default this writes to `pydoc2markdown-demo/`. Use `--demo-output` to choose
another directory. Existing non-empty directories are not overwritten.

## Before And After

Start with normal Python code and docstrings:

```python
def calculate_total(items: list[Product], discount: float = 0.0) -> float:
    """Calculate the discounted order total.

    Args:
        items: Products to include in the total.
        discount: Discount ratio between 0 and 1.

    Returns:
        Total price after discount.

    Raises:
        ValueError: If discount is outside the accepted range.
    """
```

PyDoc2Markdown turns it into Markdown with headings, parameter tables, return
types, and raised exceptions:

```markdown
### `calculate_total`

Calculate the discounted order total.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `items` | `list[Product]` | Products to include in the total. |
| `discount` | `float` | Discount ratio between 0 and 1. |

**Returns:** `float`
Total price after discount.

**Raises:**
- `ValueError`: If discount is outside the accepted range.
```

## Common Commands

Start with the command that matches how you want to publish docs:

| Goal | Command |
|------|---------|
| Generate module docs | `pydoc2markdown src/my_package --recursive -o docs` |
| Generate a docs index and API pages | `pydoc2markdown src/my_package --recursive --nav -o docs` |
| Update the API section in README.md | `pydoc2markdown src/my_package --recursive --readme` |
| Skip private/internal modules | `pydoc2markdown src/my_package --recursive --exclude "tests/*,*/internal/*,*_private.py"` |
| Add GitHub source links | `pydoc2markdown src/my_package --recursive --source-repo user/repo -o docs` |
| Check generated docs in CI | `pydoc2markdown src/my_package --recursive --nav --readme --check -o docs` |
| Preview stale generated docs cleanup | `pydoc2markdown src/my_package --recursive --prune --dry-run -o docs` |
| Remove stale generated docs | `pydoc2markdown src/my_package --recursive --prune -o docs` |
| Generate one combined Markdown file | `pydoc2markdown src/my_package --recursive --single-file -o docs/api.md` |
| Watch source files while editing | `pydoc2markdown src/my_package --recursive --watch -o docs` |
| Create default pyproject config | `pydoc2markdown --init` |
| Create a local demo project | `pydoc2markdown --demo` |

Use `--theme minimal` for shorter output, or `--template path/to/template.md.j2`
when a project needs custom Markdown.

## Quick Start

### CLI Usage

```bash
# Generate docs for a single file
pydoc2markdown my_module.py -o docs

# Recursively process a package
pydoc2markdown src/my_package --recursive -o docs

# Skip internal and test modules
pydoc2markdown src/my_package --recursive --exclude "tests/*,*/internal/*,*_test.py" -o docs

# Generate a navigation-first docs layout
pydoc2markdown src/my_package --recursive --nav -o docs

# Add GitHub source links next to documented objects
pydoc2markdown src/my_package --recursive --source-repo user/repo -o docs

# Check whether generated docs are current without writing files
pydoc2markdown src/my_package --recursive --nav --check -o docs

# Preview stale generated Markdown files before removing them
pydoc2markdown src/my_package --recursive --prune --dry-run -o docs

# Remove stale generated Markdown files tracked by PyDoc2Markdown
pydoc2markdown src/my_package --recursive --prune -o docs

# Initialize default configuration in pyproject.toml
pydoc2markdown --init
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
| `--include` | `None` | Comma-separated glob patterns for files to include |
| `--exclude` | `None` | Comma-separated glob patterns for files to exclude |
| `--theme` | `default` / value from `pyproject.toml` | Built-in theme: `default` (detailed) or `minimal` |
| `--template` | `None` | Path to a custom Jinja2 template for Markdown generation |
| `--single-file` | `False` | Generate a single combined Markdown file; `--output` must be a `.md` or `.markdown` file path |
| `--check` | `False` | Check whether generated docs are up to date without writing files |
| `--prune` | `False` | Remove stale generated Markdown files tracked by PyDoc2Markdown |
| `--dry-run` | `False` | Preview `--prune` results without deleting files |
| `--readme` | `False` | Create or update an API reference section in README.md |
| `--readme-path` | `README.md` | Path to the README file updated by `--readme` |
| `--nav` | `False` | Generate a navigation-first docs layout with API pages under `api/` |
| `--api-dir` | `api` | Directory for API pages when `--nav` is used |
| `--source-link` | `None` | URL template for source links, using `{path}`, `{file}`, and `{line}` |
| `--source-repo` | `None` | GitHub repository shorthand for source links, for example `user/repo` |
| `--watch` | `False` | Watch source files and regenerate docs on change |
| `--demo` | `False` | Create a small demo project and generate docs for it |
| `--demo-output` | `pydoc2markdown-demo` | Directory created by `--demo` |
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

## Module Filtering

Use `--include` and `--exclude` with `--recursive` to control which Python files
are documented:

```bash
pydoc2markdown src/my_package --recursive --exclude "tests/*,*/internal/*,*_private.py"
```

Patterns use standard shell-style globs and are matched against paths relative
to the scanned source root. Patterns without a directory separator also match
file names in any package directory, so `conftest.py` or `*_test.py` work as
convenient basename filters.

When both flags are used, PyDoc2Markdown applies `--include` first and then
removes anything matched by `--exclude`:

```bash
pydoc2markdown src/my_package --recursive --include "api/*,core/*" --exclude "*/generated.py"
```

## Source Links

Use `--source-repo` to add GitHub source links next to generated class,
function, and method headings:

```bash
pydoc2markdown src/my_package --recursive --source-repo user/repo -o docs
```

This expands to a GitHub URL template using the `main` branch:

```text
https://github.com/user/repo/blob/main/{path}#L{line}
```

For GitLab, another branch, or a custom host, pass the full template with
`--source-link`:

```bash
pydoc2markdown src/my_package --recursive \
  --source-link "https://gitlab.com/user/repo/-/blob/develop/{path}#L{line}" \
  -o docs
```

Available template variables are `{path}` for the source-root-relative Python
file path, `{file}` for the filename, and `{line}` for the 1-indexed definition
line.

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

## CI Checks

Use `--check` in CI to fail when generated documentation is missing or stale:

```bash
pydoc2markdown src/my_package --recursive --nav --readme --check -o docs
```

The command compares the files PyDoc2Markdown would generate with the files
already on disk. It exits with `0` when docs are current and `1` when any
generated output needs to be updated. It does not write files in check mode.

`--check` works with normal multi-file output, `--nav`, `--single-file`, and
README API sections. It cannot be combined with `--watch`.

## Prune Stale Docs

Use `--prune` to remove stale generated Markdown files that were tracked by
PyDoc2Markdown in a previous run but are no longer expected for the current
source tree:

```bash
pydoc2markdown src/my_package --recursive --prune -o docs
```

To preview the cleanup first, add `--dry-run`:

```bash
pydoc2markdown src/my_package --recursive --prune --dry-run -o docs
```

`--prune` only affects generated Markdown files recorded in the PyDoc2Markdown
manifest. It does not try to delete unrelated hand-written Markdown files that
may live in the same docs directory.

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
