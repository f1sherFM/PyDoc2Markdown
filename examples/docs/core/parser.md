# parser

Python docstring parser with structured docstring support.

## Table of Contents

- [Classes](#classes)

  - [`Parameter`](#parameter)

  - [`ReturnsInfo`](#returnsinfo)

  - [`RaisesInfo`](#raisesinfo)

  - [`FunctionDoc`](#functiondoc)

  - [`ClassDoc`](#classdoc)

  - [`ModuleDoc`](#moduledoc)

  - [`DocstringParser`](#docstringparser)

    - [`parse`](#parse)

    - [`_parse_file`](#_parse_file)

    - [`_extract_module`](#_extract_module)

    - [`_extract_class`](#_extract_class)

    - [`_extract_function`](#_extract_function)

    - [`_extract_ast_params`](#_extract_ast_params)

    - [`_merge_param_descriptions`](#_merge_param_descriptions)

    - [`_extract_returns`](#_extract_returns)

    - [`_extract_raises`](#_extract_raises)

    - [`_extract_attributes`](#_extract_attributes)

    - [`_format_base`](#_format_base)

    - [`_extract_decorator_names`](#_extract_decorator_names)

    - [`_resolve_class_type`](#_resolve_class_type)

    - [`_extract_public_api`](#_extract_public_api)

## Classes

### `Parameter` (dataclass)

Represents a function/method parameter.

---

### `ReturnsInfo` (dataclass)

Structured return type and description.

---

### `RaisesInfo` (dataclass)

Structured exception type and description.

---

### `FunctionDoc` (dataclass)

Represents extracted documentation for a function or method.

---

### `ClassDoc` (dataclass)

Represents extracted documentation for a class.

---

### `ModuleDoc` (dataclass)

Represents extracted documentation for a module.

---

### `DocstringParser`

Parse Python source files and extract structured docstrings.

#### Attributes

| Name | Type | Description |
|------|------|-------------|
| `_modules` | `list[[ModuleDoc](#moduledoc)]` | - |

| `_source` | `Path` | - |

#### Methods

##### `parse`

Parse a file or directory and return extracted documentation.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `source` | `Path` | - |

| `recursive` | `bool` | - |

**Returns:** `list[[ModuleDoc](#moduledoc)]`

##### `_parse_file`

Parse a single Python file.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `path` | `Path` | - |

**Returns:** `None`

##### `_extract_module`

Extract module-level documentation.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `path` | `Path` | - |

| `tree` | `ast.AST` | - |

**Returns:** `[ModuleDoc](#moduledoc)`

##### `_extract_class`

Extract documentation from a class definition.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node` | `ast.ClassDef` | - |

**Returns:** `[ClassDoc](#classdoc)`

##### `_extract_function`

Extract documentation from a function definition.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node` | `ast.FunctionDef | ast.AsyncFunctionDef` | - |

| `is_method` | `bool` | - |

**Returns:** `[FunctionDoc](#functiondoc)`

##### `_extract_ast_params`

Extract parameter names and type hints from AST.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node` | `ast.FunctionDef | ast.AsyncFunctionDef` | - |

**Returns:** `list[[Parameter](#parameter)]`

##### `_merge_param_descriptions`

Merge docstring parameter descriptions into AST-extracted parameters.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `params` | `list[[Parameter](#parameter)]` | - |

| `parsed` | `ParsedDocstring` | - |

**Returns:** `None`

##### `_extract_returns`

Extract structured return info from parsed docstring.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `parsed` | `ParsedDocstring` | - |

**Returns:** `[ReturnsInfo](#returnsinfo) | None`

##### `_extract_raises`

Extract structured raises info from parsed docstring.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `parsed` | `ParsedDocstring` | - |

**Returns:** `list[[RaisesInfo](#raisesinfo)]`

##### `_extract_attributes`

Extract instance attributes from __init__ method.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `init_node` | `ast.FunctionDef | ast.AsyncFunctionDef` | - |

**Returns:** `list[[Parameter](#parameter)]`

##### `_format_base`

Format a base class expression as a string.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `base` | `ast.expr` | - |

**Returns:** `str`

##### `_extract_decorator_names`

Extract decorator names from a function or class definition.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node` | `ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef` | - |

**Returns:** `list[str]`

##### `_resolve_class_type`

Determine if a class is a dataclass, enum, typeddict, or plain class.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node` | `ast.ClassDef` | - |

| `bases` | `list[str]` | - |

**Returns:** `str`

##### `_extract_public_api`

Extract names from __all__ assignment.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `node` | `ast.Assign | ast.AnnAssign` | - |

**Returns:** `list[str]`

---
