# PyDoc2Markdown

[![CI](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/f1sherFM/PyDoc2Markdown/branch/main/graph/badge.svg)](https://codecov.io/gh/f1sherFM/PyDoc2Markdown)
[![PyPI](https://img.shields.io/pypi/v/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)
[![Python versions](https://img.shields.io/pypi/pyversions/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)
[![License](https://img.shields.io/pypi/l/pydoc2markdown)](https://github.com/f1sherFM/PyDoc2Markdown/blob/main/LICENSE)

> Convert Python docstrings into clean, structured Markdown documentation.

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

## Installation

```bash
pip install pydoc2markdown
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

> See [`examples/docs/`](examples/docs/) for a sample of the generated output.

### Library Usage

```python
from pathlib import Path
from pydoc2markdown import DocstringParser, MarkdownGenerator

parser = DocstringParser()
modules = parser.parse(Path("src/my_package"), recursive=True)

generator = MarkdownGenerator(theme="default")
generator.generate(modules, output_dir=Path("docs"))
```

## Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Project Structure](PROJECT_STRUCTURE.md)

## License

MIT License — see [LICENSE](LICENSE) for details.
