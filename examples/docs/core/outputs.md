# outputs

Shared helpers for generated documentation outputs.

## Table of Contents

- [Functions](#functions)
  - [`manifest_path`](#manifest_path)
  - [`write_manifest`](#write_manifest)
  - [`readme_module_links`](#readme_module_links)

## Functions

### `manifest_path`
Return the manifest path for generated Markdown files.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |

**Returns:** `Path`
### `write_manifest`
Persist generated Markdown paths for future prune operations.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `output` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `generated_paths` | `list[Path]` | *required* | - |

### `readme_module_links`
Build README links to generated module docs for the current run.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `output` | `Path` | *required* | - |
| `readme_path` | `Path` | *required* | - |
| `single_file` | `bool` | *required* | - |
| `navigation` | `bool` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `dict[str, str]`
