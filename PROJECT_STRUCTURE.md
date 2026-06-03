# PyDoc2Markdown Project Structure

This document is a quick map of the repository so contributors can find the
right place to work without reverse-engineering the project first.

## Repository Layout

```text
PyDoc2Markdown/
|-- .github/workflows/
|   |-- ci.yml
|   `-- release.yml
|-- docs/
|   `-- .gitkeep
|-- examples/
|   |-- basic_usage.py
|   |-- custom_template.md.j2
|   |-- docs/
|   `-- sample_project/
|-- src/pydoc2markdown/
|   |-- cli.py
|   |-- __init__.py
|   |-- core/
|   |-- templates/
|   `-- utils/
|-- tests/
|   |-- conftest.py
|   |-- test_cli.py
|   |-- test_config.py
|   |-- test_crossref.py
|   |-- test_examples.py
|   |-- test_generator.py
|   |-- test_parser.py
|   |-- test_type_hints.py
|   `-- test_watcher.py
|-- CHANGELOG.md
|-- CONTRIBUTING.md
|-- LICENSE
|-- PROJECT_STRUCTURE.md
|-- README.md
`-- pyproject.toml
```

## What Lives Where

### `src/pydoc2markdown/`

The library and CLI implementation.

- [src/pydoc2markdown/cli.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/cli.py)
  handles argument parsing, config loading, check/prune flows, README updates,
  navigation generation, and demo project creation.
- [src/pydoc2markdown/__init__.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/__init__.py)
  exposes the public API and package version.

### `src/pydoc2markdown/core/`

The main documentation pipeline.

- [config.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/config.py) reads
  `[tool.pydoc2markdown]` defaults from `pyproject.toml`.
- [parser.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/parser.py) parses
  Python files into structured documentation models.
- [generator.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/generator.py)
  renders Markdown, README API blocks, single-file output, and navigation docs.
- [crossref.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/crossref.py)
  builds cross-links between documented objects.
- [type_hints.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/type_hints.py)
  normalizes and formats type hint strings.
- [watcher.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/watcher.py)
  powers `--watch`.

### `src/pydoc2markdown/templates/`

Built-in Markdown themes.

- [module.md](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/templates/module.md) is
  the default detailed output.
- [minimal.md](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/templates/minimal.md)
  is the shorter built-in variant.

### `src/pydoc2markdown/utils/`

Shared helper functions used across parsing and rendering.

### `tests/`

The automated test suite.

- `test_cli.py` covers command-line behavior and integration-style flows.
- `test_generator.py`, `test_parser.py`, `test_crossref.py`, and
  `test_type_hints.py` cover the core rendering and parsing logic.
- `test_config.py`, `test_examples.py`, and `test_watcher.py` cover supporting
  behavior and example workflows.

### `examples/`

Real usage examples and generated output.

- [examples/basic_usage.py](/abs/path/C:/PyDoc2Md/examples/basic_usage.py)
  shows the library API in a small script.
- [examples/custom_template.md.j2](/abs/path/C:/PyDoc2Md/examples/custom_template.md.j2)
  is a custom template example.
- [examples/sample_project/](/abs/path/C:/PyDoc2Md/examples/sample_project/)
  is the best end-to-end demo: source code, generated docs, and README sync in
  one place.
- [examples/docs/](/abs/path/C:/PyDoc2Md/examples/docs/) contains pre-generated
  documentation for this repository.

### `docs/`

Reserved as the default generated output directory in local workflows. The
tracked `.gitkeep` keeps the directory present in the repository without
committing generated docs there by default.

## Common Contributor Paths

If you are working on:

- **CLI behavior**: start in
  [cli.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/cli.py) and
  [test_cli.py](/abs/path/C:/PyDoc2Md/tests/test_cli.py)
- **Docstring parsing**: start in
  [parser.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/parser.py) and
  [test_parser.py](/abs/path/C:/PyDoc2Md/tests/test_parser.py)
- **Rendered Markdown output**: start in
  [generator.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/generator.py),
  the templates directory, and
  [test_generator.py](/abs/path/C:/PyDoc2Md/tests/test_generator.py)
- **Type formatting or links**: start in
  [type_hints.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/type_hints.py),
  [crossref.py](/abs/path/C:/PyDoc2Md/src/pydoc2markdown/core/crossref.py), and
  their matching tests
- **Docs and onboarding**: start in
  [README.md](/abs/path/C:/PyDoc2Md/README.md),
  [CONTRIBUTING.md](/abs/path/C:/PyDoc2Md/CONTRIBUTING.md),
  [PROJECT_STRUCTURE.md](/abs/path/C:/PyDoc2Md/PROJECT_STRUCTURE.md), and the
  `examples/` directory

## Release and Tooling Notes

- [pyproject.toml](/abs/path/C:/PyDoc2Md/pyproject.toml) is the single source
  of truth for packaging metadata, dependencies, tool config, and default
  PyDoc2Markdown settings.
- [CHANGELOG.md](/abs/path/C:/PyDoc2Md/CHANGELOG.md) is maintained through the
  release workflow.
- GitHub Actions in `.github/workflows/` handle CI, release preparation, and
  publishing.
