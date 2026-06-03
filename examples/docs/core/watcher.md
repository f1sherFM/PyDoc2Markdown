# watcher

File watcher for auto-regenerating documentation.

## Table of Contents

- [Functions](#functions)
  - [`watch_and_generate`](#watch_and_generate)

## Functions

### `watch_and_generate`
Watch source files and regenerate docs on change.

Args:
    source: Path to Python file or directory.
    output_dir: Output directory for Markdown files.
    recursive: Whether to scan subdirectories recursively.
    theme: Built-in theme name.
    template_path: Optional custom template path.
    readme_path: Optional README path to update with an API reference.
    navigation: Whether to generate the navigation-first docs layout.
    api_dir: Directory for API pages when navigation is enabled.
    include: Optional glob patterns for files to include.
    exclude: Optional glob patterns for files to exclude.
    source_link_template: Optional URL template for source links.

Returns:
    Exit code (0 for success, 1 for error).

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `source` | `Path` | *required* | Path to Python file or directory. |
| `output_dir` | `Path` | *required* | Output directory for Markdown files. |
| `recursive` | `bool` | *required* | Whether to scan subdirectories recursively. |
| `theme` | `str` | *required* | Built-in theme name. |
| `template_path` | `Path | None` | *required* | Optional custom template path. |
| `single_file` | `bool` | `False` | - |
| `readme_path` | `Path | None` | `None` | Optional README path to update with an API reference. |
| `navigation` | `bool` | `False` | Whether to generate the navigation-first docs layout. |
| `api_dir` | `Path` | `Path('api')` | Directory for API pages when navigation is enabled. |
| `include` | `list[str] | None` | `None` | Optional glob patterns for files to include. |
| `exclude` | `list[str] | None` | `None` | Optional glob patterns for files to exclude. |
| `source_link_template` | `str | None` | `None` | Optional URL template for source links. |

**Returns:** `int`
Exit code (0 for success, 1 for error).
