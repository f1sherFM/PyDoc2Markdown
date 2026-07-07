# cli

Command-line interface for PyDoc2Markdown.

## Table of Contents

- [Functions](#functions)
  - [`create_parser`](#create_parser)
  - [`init_config`](#init_config)
  - [`run_demo`](#run_demo)
  - [`prune_stale_files`](#prune_stale_files)
  - [`check_generated_docs`](#check_generated_docs)
  - [`main`](#main)

## Functions

### `create_parser`
Create and configure the argument parser.

**Returns:** `argparse.ArgumentParser`
### `init_config`
Create or update [tool.pydoc2markdown] in pyproject.toml.

**Returns:** `int`
0 on success, 1 on error.

### `run_demo`
Create a demo project and generate documentation for it.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output_dir` | `Path` | *required* | - |

**Returns:** `int`
### `prune_stale_files`
Remove or preview stale generated Markdown files from the output directory.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `generator` | `MarkdownGenerator` | *required* | - |
| `modules` | `list[ModuleDoc]` | *required* | - |
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `navigation` | `bool` | *required* | - |
| `api_dir` | `Path` | *required* | - |
| `dry_run` | `bool` | *required* | - |

**Returns:** `list[Path]`
### `check_generated_docs`
Check whether generated documentation matches the current files.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `generator` | `MarkdownGenerator` | *required* | - |
| `modules` | `list[ModuleDoc]` | *required* | - |
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `readme` | `bool` | *required* | - |
| `readme_path` | `Path` | *required* | - |
| `navigation` | `bool` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `int`
### `main`
Main entry point for the CLI.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `args` | `list[str] \| None` | `None` | - |

**Returns:** `int`
