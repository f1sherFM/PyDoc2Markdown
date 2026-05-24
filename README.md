# PyDoc2Markdown

[![CI](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml/badge.svg)](https://github.com/f1sherFM/PyDoc2Markdown/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/f1sherFM/PyDoc2Markdown/branch/main/graph/badge.svg)](https://codecov.io/gh/f1sherFM/PyDoc2Markdown)
[![PyPI](https://img.shields.io/pypi/v/pydoc2markdown)](https://pypi.org/project/pydoc2markdown/)

> Convert Python docstrings into clean, structured Markdown documentation.

## Features

- **Docstring parsing** — Extract Google, NumPy, and reStructuredText style docstrings.
- **Markdown generation** — Produce beautiful Markdown files with customizable Jinja2 templates.
- **CLI & API** — Use via command line or import as a Python library.
- **Recursive processing** — Scan entire packages in one command.
- **Type-aware** — Respects type hints and annotations.

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

# Use a custom template
pydoc2markdown src/my_package --recursive --template custom.md.j2 -o docs
```

### Library Usage

```python
from pathlib import Path
from pydoc2markdown import DocstringParser, MarkdownGenerator

parser = DocstringParser()
modules = parser.parse(Path("src/my_package"), recursive=True)

generator = MarkdownGenerator()
generator.generate(modules, output_dir=Path("docs"))
```

## Documentation

- [Contributing Guide](CONTRIBUTING.md)
- [Project Structure](PROJECT_STRUCTURE.md)

## License

MIT License — see [LICENSE](LICENSE) for details.
