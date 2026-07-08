# watcher

File watcher for auto-regenerating documentation.

## Table of Contents

- [Functions](#functions)
  - [`watch_and_generate`](#watch_and_generate)

## Functions

### `watch_and_generate`
Watch source files and regenerate docs on change.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `source` | `Path` | *required* | Path to Python file or directory. |
| `output_dir` | `Path` | *required* | Output directory for Markdown files. |
| `recursive` | `bool` | *required* | Whether to scan subdirectories recursively. |
| `theme` | `str` | *required* | Built-in theme name. |
| `template_path` | `Path \| None` | *required* | Optional custom template path. |
| `single_file` | `bool` | `False` | - |
| `readme_path` | `Path \| None` | `None` | Optional README path to update with an API reference. |
| `readme_mode` | `str` | `'summary'` | README rendering mode when readme_path is provided. |
| `readme_title` | `str` | `'API Reference'` | Section title used for generated README content. |
| `navigation` | `bool` | `False` | Whether to generate the navigation-first docs layout. |
| `api_dir` | `Path` | `Path('api')` | Directory for API pages when navigation is enabled. |
| `include` | `list[str] \| None` | `None` | Optional glob patterns for files to include. |
| `exclude` | `list[str] \| None` | `None` | Optional glob patterns for files to exclude. |
| `source_link_template` | `str \| None` | `None` | Optional URL template for source links. |
| `output_options` | `OutputOptions \| None` | `None` | Optional built-in Markdown rendering toggles. |
| `inherit_docstrings` | `bool` | `False` | Fill missing docs from parsed base classes. |

**Returns:** `int`
Exit code (0 for success, 1 for error).
