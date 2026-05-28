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
- **Cross-references** — automatic type linking within your project

## Features

- **Docstring parsing** — Extract Google, NumPy, and reStructuredText style docstrings with structured params, returns, and raises.
- **Markdown generation** — Produce beautiful Markdown files with customizable Jinja2 templates.
- **Auto-generated index & TOC** — Each module gets a Table of Contents; an `index.md` with package grouping is created automatically.
- **Package grouping** — Output files are organized into subdirectories matching the package structure.
- **Built-in themes** — Choose between `default` (detailed) and `minimal` themes, or supply your own template.
- **CLI & API** — Use via command line or import as a Python library.
- **Recursive processing** — Scan entire packages in one command.
- **Type-aware** — Respects type hints and annotations.
- **Advanced constructs** — Supports `property`, `classmethod`, `staticmethod`, `dataclass`, `Enum`, `TypedDict`, `Protocol`, `ABC`, and `__all__`.

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
| `source` | *(required)* | Path to a Python file or directory to process |
| `-o`, `--output` | `docs` / value from `pyproject.toml` | Output directory (or file path when `--single-file` is used) |
| `--recursive` | `False` / value from `pyproject.toml` | Recursively process subdirectories |
| `--theme` | `default` / value from `pyproject.toml` | Built-in theme: `default` (detailed) or `minimal` |
| `--template` | `None` | Path to a custom Jinja2 template for Markdown generation |
| `--single-file` | `False` | Generate a single combined Markdown file instead of separate files |
| `--watch` | `False` | Watch source files and regenerate docs on change |
| `-v`, `--verbose` | `0` | Increase verbosity (`-v` = INFO, `-vv` = DEBUG) |
| `--version` | — | Show version and exit |

**Configuration priority:** CLI flags > `[tool.pydoc2markdown]` in `pyproject.toml` > built-in defaults.

## Configuration

You can set default values in your `pyproject.toml` under the `[tool.pydoc2markdown]` section:

```toml
[tool.pydoc2markdown]
output = "docs"
theme = "default"
recursive = true
```

Any values set here serve as defaults and can be overridden by CLI flags.

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

# Markdown string for a single module
md_string = gen.generate_string(modules[0])
```

**Methods available on `MarkdownGenerator`:**

| Method | Description |
|--------|-------------|
| `generate(modules, output_dir)` → `list[Path]` | Generate separate Markdown files for each module |
| `generate_single_file(modules, output_path)` → `Path` | Generate a single combined Markdown file |
| `generate_string(module)` → `str` | Return Markdown as a string for a single module |

## Supported Docstring Formats

PyDoc2Markdown uses [docstring-parser](https://github.com/rr-/docstring-parser) and supports:

| Style | Support | Notes |
|-------|---------|-------|
| **Google** | ✅ Full | Args, Returns, Raises, Attributes, Examples |
| **NumPy** | ✅ Full | Parameters, Returns, Raises, Attributes, Examples |
| **reStructuredText (reST)** | ⚠️ Partial | Basic structure via `docstring-parser`; `:param:`, `:returns:`, `:raises:` fields |

## Example Output

Running `pydoc2markdown examples/basic_usage.py -o docs` produces:

```markdown
# basic_usage

Basic usage example for PyDoc2Markdown library API.

## Table of Contents

- [Functions](#functions)
  - [`main`](#main)

## Functions

### `main`

**Returns:** `None`
```

For a more complete example, see the [examples/](examples/) directory in this repository.

## Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Project Structure](PROJECT_STRUCTURE.md)

## License

MIT License — see [LICENSE](LICENSE) for details.
