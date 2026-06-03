# config

Configuration loader for PyDoc2Markdown.

## Table of Contents

- [Functions](#functions)

  - [`load_config`](#load_config)

## Functions

### `load_config`

Load [tool.pydoc2markdown] from pyproject.toml.

Args:
    cwd: Directory to search for pyproject.toml. Defaults to current dir.

Returns:
    Dictionary with parsed config values.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `cwd` | `Path | None` | Directory to search for pyproject.toml. Defaults to current dir. |

**Returns:** `dict[str, Any]`

Dictionary with parsed config values.
