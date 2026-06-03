# crossref

Cross-referencing utilities for linking project-defined types.

## Table of Contents

- [Classes](#classes)
  - [`TypeIndex`](#typeindex)
    - [@classmethod `from_modules`](#typeindex-from_modules)
    - [`link`](#typeindex-link)
- [Functions](#functions)
  - [`link_type_filter`](#link_type_filter)
  - [`_to_anchor`](#_to_anchor)

## Classes

### `TypeIndex` (dataclass)
Index of project-defined types for cross-referencing.

#### Methods

<a id="typeindex-from_modules"></a>

##### @classmethod `from_modules`
Build an index from a list of parsed modules.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |

**Returns:** `[TypeIndex](#typeindex)`
<a id="typeindex-link"></a>

##### `link`
Replace project-defined type names with Markdown hyperlinks.

Args:
    type_str: A type hint string (preferably already formatted).

Returns:
    Markdown string with hyperlinks for known types.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `type_str` | `str` | *required* | A type hint string (preferably already formatted). |

**Returns:** `str`
Markdown string with hyperlinks for known types.

---

## Functions

### `link_type_filter`
Jinja2 filter that auto-links project-defined types.

Expects ``type_index`` in the render context.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `ctx` | `dict` | *required* | - |
| `type_str` | `str` | *required* | - |

**Returns:** `str`
### `_to_anchor`
Convert a name to a Markdown anchor.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `name` | `str` | *required* | - |

**Returns:** `str`
