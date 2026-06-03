# cli

Command-line interface for PyDoc2Markdown.

## Table of Contents

- [Functions](#functions)
  - [`create_parser`](#create_parser)
  - [`_setup_logging`](#_setup_logging)
  - [`_log_cli_error`](#_log_cli_error)
  - [`_split_patterns`](#_split_patterns)
  - [`init_config`](#init_config)
  - [`run_demo`](#run_demo)
  - [`_different_files`](#_different_files)
  - [`_check_readme`](#_check_readme)
  - [`_manifest_path`](#_manifest_path)
  - [`_write_manifest`](#_write_manifest)
  - [`_read_manifest`](#_read_manifest)
  - [`_find_stale_managed_files`](#_find_stale_managed_files)
  - [`prune_stale_files`](#prune_stale_files)
  - [`check_generated_docs`](#check_generated_docs)
  - [`_validate_single_file_output`](#_validate_single_file_output)
  - [`_source_link_template`](#_source_link_template)
  - [`main`](#main)

## Functions

### `create_parser`
Create and configure the argument parser.

**Returns:** `argparse.ArgumentParser`
### `_setup_logging`
Configure logging level based on verbosity count.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `verbosity` | `int` | *required* | - |

### `_log_cli_error`
Log a user-facing CLI error and optional next step.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `str` | *required* | - |
| `hint` | `str | None` | `None` | - |

**Returns:** `int`
### `_split_patterns`
Split comma-separated CLI glob patterns.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `raw` | `str | None` | *required* | - |

**Returns:** `list[str] | None`
### `init_config`
Create or update [tool.pydoc2markdown] in pyproject.toml.

Returns:
    0 on success, 1 on error.

**Returns:** `int`
0 on success, 1 on error.

### `run_demo`
Create a demo project and generate documentation for it.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output_dir` | `Path` | *required* | - |

**Returns:** `int`
### `_different_files`
Return generated files whose current output is missing, outdated, or stale.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `expected_dir` | `Path` | *required* | - |
| `actual_dir` | `Path` | *required* | - |
| `expected_paths` | `list[Path]` | *required* | - |

**Returns:** `list[Path]`
### `_check_readme`
Return README path when its generated API section is missing or outdated.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `generator` | `[MarkdownGenerator](#markdowngenerator)` | *required* | - |
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `readme_path` | `Path` | *required* | - |
| `temp_dir` | `Path` | *required* | - |

**Returns:** `list[Path]`
### `_manifest_path`
Return the manifest path for generated Markdown files.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |

**Returns:** `Path`
### `_write_manifest`
Persist generated Markdown paths for future prune operations.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `generated_paths` | `list[Path]` | *required* | - |

### `_read_manifest`
Load previously generated Markdown paths from the prune manifest.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |

**Returns:** `set[Path]`
### `_find_stale_managed_files`
Return stale generated Markdown files tracked by the prune manifest.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `generator` | `[MarkdownGenerator](#markdowngenerator)` | *required* | - |
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `navigation` | `bool` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `list[Path]`
### `prune_stale_files`
Remove or preview stale generated Markdown files from the output directory.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `generator` | `[MarkdownGenerator](#markdowngenerator)` | *required* | - |
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
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
| `generator` | `[MarkdownGenerator](#markdowngenerator)` | *required* | - |
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `readme` | `bool` | *required* | - |
| `readme_path` | `Path` | *required* | - |
| `navigation` | `bool` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `int`
### `_validate_single_file_output`
Return a CLI error when --single-file output is not an explicit file path.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output` | `Path` | *required* | - |

**Returns:** `int`
### `_source_link_template`
Resolve source-link CLI options into a URL template.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `source_link` | `str | None` | *required* | - |
| `source_repo` | `str | None` | *required* | - |

**Returns:** `str | None`
### `main`
Main entry point for the CLI.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `args` | `list[str] | None` | `None` | - |

**Returns:** `int`
