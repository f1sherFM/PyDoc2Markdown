# config

Configuration loader for PyDoc2Markdown.

## Table of Contents

- [Functions](#functions)
  - [`load_config`](#load_config)

## Functions

### `load_config`
Load [tool.pydoc2markdown] from pyproject.toml.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `cwd` | `Path \| None` | `None` | Directory to search for pyproject.toml. Defaults to current dir. |

**Returns:** `dict[str, Any]`
Dictionary with parsed config values.
