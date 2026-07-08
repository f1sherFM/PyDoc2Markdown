# parser

Python docstring parser with structured docstring support.

## Table of Contents

- [Classes](#classes)
  - [`Parameter`](#parameter)
  - [`ReturnsInfo`](#returnsinfo)
  - [`RaisesInfo`](#raisesinfo)
  - [`FunctionDoc`](#functiondoc)
  - [`PydanticField`](#pydanticfield)
  - [`ClassDoc`](#classdoc)
  - [`ModuleDoc`](#moduledoc)
  - [`DocstringParser`](#docstringparser)
    - [`parse`](#docstringparser-parse)

## Classes

### `Parameter` (dataclass)
Represents a function/method parameter.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | - |
| `type_hint` | `str \| None` | - |
| `default` | `str \| None` | - |
| `description` | `str \| None` | - |

---
### `ReturnsInfo` (dataclass)
Structured return type and description.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `type_hint` | `str \| None` | - |
| `description` | `str \| None` | - |

---
### `RaisesInfo` (dataclass)
Structured exception type and description.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `type_name` | `str \| None` | - |
| `description` | `str \| None` | - |

---
### `FunctionDoc` (dataclass)
Represents extracted documentation for a function or method.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | - |
| `docstring` | `str \| None` | - |
| `params` | `list[[Parameter](#parameter)]` | - |
| `returns` | `[ReturnsInfo](#returnsinfo) \| None` | - |
| `raises` | `list[[RaisesInfo](#raisesinfo)]` | - |
| `is_method` | `bool` | - |
| `is_async` | `bool` | - |
| `is_property` | `bool` | - |
| `is_classmethod` | `bool` | - |
| `is_staticmethod` | `bool` | - |
| `source_path` | `str \| None` | - |
| `line_number` | `int \| None` | - |

---
### `PydanticField` (dataclass)
Represents a Pydantic model field.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | - |
| `type_hint` | `str \| None` | - |
| `default` | `str \| None` | - |
| `description` | `str \| None` | - |
| `required` | `bool` | - |

---
### `ClassDoc` (dataclass)
Represents extracted documentation for a class.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | - |
| `docstring` | `str \| None` | - |
| `constructor_params` | `list[[Parameter](#parameter)]` | - |
| `methods` | `list[[FunctionDoc](#functiondoc)]` | - |
| `attributes` | `list[[Parameter](#parameter)]` | - |
| `bases` | `list[str]` | - |
| `class_type` | `str` | - |
| `is_protocol` | `bool` | - |
| `is_abstract` | `bool` | - |
| `is_pydantic_model` | `bool` | - |
| `pydantic_fields` | `list[[PydanticField](#pydanticfield)]` | - |
| `source_path` | `str \| None` | - |
| `line_number` | `int \| None` | - |

---
### `ModuleDoc` (dataclass)
Represents extracted documentation for a module.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `name` | `str` | - |
| `path` | `Path` | - |
| `docstring` | `str \| None` | - |
| `attributes` | `list[[Parameter](#parameter)]` | - |
| `classes` | `list[[ClassDoc](#classdoc)]` | - |
| `functions` | `list[[FunctionDoc](#functiondoc)]` | - |
| `public_api` | `list[str]` | - |
| `package` | `str` | - |

---
### `DocstringParser`
Parse Python source files and extract structured docstrings.

#### Constructor Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `inherit_docstrings` | `bool` | `False` | Fill missing class and method documentation from parsed base classes when possible. |

#### Methods
<a id="docstringparser-parse"></a>

##### `parse`
Parse a file or directory and return extracted documentation.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `source` | `Path` | *required* | - |
| `recursive` | `bool` | `False` | - |
| `include` | `list[str] \| None` | `None` | - |
| `exclude` | `list[str] \| None` | `None` | - |

**Returns:** `list[[ModuleDoc](#moduledoc)]`
---
