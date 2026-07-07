# crossref

Cross-referencing utilities for linking project-defined types.

## Table of Contents

- [Classes](#classes)
  - [`TypeRef`](#typeref)
  - [`TypeIndex`](#typeindex)
    - [@classmethod `from_modules`](#typeindex-from_modules)
    - [`link`](#typeindex-link)
- [Functions](#functions)
  - [`link_type_filter`](#link_type_filter)

## Classes

### `TypeRef` (dataclass)
A project-defined type target.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `anchor` | `str` | - |
| `module` | `str \| None` | - |

---
### `TypeIndex` (dataclass)
Index of project-defined types for cross-referencing.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `types` | `dict[str, [TypeRef](#typeref) \| str]` | Mapping from type name to a Markdown target. |

#### Methods
<a id="typeindex-from_modules"></a>

##### @classmethod `from_modules`
Build an index from a list of parsed modules.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |

**Returns:** `[TypeIndex](#typeindex)`
<a id="typeindex-link"></a>

##### `link`
Replace project-defined type names with Markdown hyperlinks.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `type_str` | `str` | *required* | A type hint string (preferably already formatted). |
| `current_module` | `str \| None` | `None` | Module key for local-only links. When provided,
types from other modules are left as plain text. |

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
