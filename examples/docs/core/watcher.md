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

Returns:
    Exit code (0 for success, 1 for error).

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `source` | `Path` | Path to Python file or directory. |

| `output_dir` | `Path` | Output directory for Markdown files. |

| `recursive` | `bool` | Whether to scan subdirectories recursively. |

| `theme` | `str` | Built-in theme name. |

| `template_path` | `Path | None` | Optional custom template path. |

| `single_file` | `bool` | - |

**Returns:** `int`

Exit code (0 for success, 1 for error).
