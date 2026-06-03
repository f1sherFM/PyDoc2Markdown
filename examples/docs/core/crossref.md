# crossref

Cross-referencing utilities for linking project-defined types.

## Table of Contents

- [Classes](#classes)

  - [`TypeIndex`](#typeindex)

    - [
@classmethod

`from_modules`](#from_modules)

    - [`link`](#link)

- [Functions](#functions)

  - [`link_type_filter`](#link_type_filter)

  - [`_to_anchor`](#_to_anchor)

## Classes

### `TypeIndex` (dataclass)

Index of project-defined types for cross-referencing.

#### Methods

##### @classmethod `from_modules`

Build an index from a list of parsed modules.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | - |

**Returns:** `[TypeIndex](#typeindex)`

##### `link`

Replace project-defined type names with Markdown hyperlinks.

Args:
    type_str: A type hint string (preferably already formatted).

Returns:
    Markdown string with hyperlinks for known types.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `type_str` | `str` | A type hint string (preferably already formatted). |

**Returns:** `str`

Markdown string with hyperlinks for known types.

---

## Functions

### `link_type_filter`

Jinja2 filter that auto-links project-defined types.

Expects ``type_index`` in the render context.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `ctx` | `dict` | - |

| `type_str` | `str` | - |

**Returns:** `str`

### `_to_anchor`

Convert a name to a Markdown anchor.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | - |

**Returns:** `str`
