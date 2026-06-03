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
    - [`_should_parse_file`](#docstringparser-_should_parse_file)
    - [`_path_matches`](#docstringparser-_path_matches)
    - [`_parse_file`](#docstringparser-_parse_file)
    - [`_extract_module`](#docstringparser-_extract_module)
    - [`_source_relative_path`](#docstringparser-_source_relative_path)
    - [`_extract_class`](#docstringparser-_extract_class)
    - [`_extract_function`](#docstringparser-_extract_function)
    - [`_extract_ast_params`](#docstringparser-_extract_ast_params)
    - [`_positional_defaults`](#docstringparser-_positional_defaults)
    - [`_merge_param_descriptions`](#docstringparser-_merge_param_descriptions)
    - [`_extract_returns`](#docstringparser-_extract_returns)
    - [`_extract_raises`](#docstringparser-_extract_raises)
    - [`_extract_attributes`](#docstringparser-_extract_attributes)
    - [`_format_base`](#docstringparser-_format_base)
    - [`_extract_decorator_names`](#docstringparser-_extract_decorator_names)
    - [`_resolve_class_type`](#docstringparser-_resolve_class_type)
    - [`_is_protocol`](#docstringparser-_is_protocol)
    - [`_is_abstract`](#docstringparser-_is_abstract)
    - [`_is_pydantic_model`](#docstringparser-_is_pydantic_model)
    - [`_extract_pydantic_fields`](#docstringparser-_extract_pydantic_fields)
    - [`_parse_pydantic_field`](#docstringparser-_parse_pydantic_field)
    - [`_extract_field_description`](#docstringparser-_extract_field_description)
    - [`_extract_public_api`](#docstringparser-_extract_public_api)

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

### `PydanticField` (dataclass)
Represents a Pydantic model field.

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

<a id="docstringparser-parse"></a>

##### `parse`
Parse a file or directory and return extracted documentation.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `source` | `Path` | *required* | - |
| `recursive` | `bool` | `False` | - |
| `include` | `list[str] | None` | `None` | - |
| `exclude` | `list[str] | None` | `None` | - |

**Returns:** `list[[ModuleDoc](#moduledoc)]`
<a id="docstringparser-_should_parse_file"></a>

##### `_should_parse_file`
Return whether a source file passes include/exclude filters.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |
| `include` | `list[str] | None` | *required* | - |
| `exclude` | `list[str] | None` | *required* | - |

**Returns:** `bool`
<a id="docstringparser-_path_matches"></a>

##### `_path_matches`
Match a path against a glob pattern using source-relative POSIX paths.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |
| `pattern` | `str` | *required* | - |

**Returns:** `bool`
<a id="docstringparser-_parse_file"></a>

##### `_parse_file`
Parse a single Python file.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |

<a id="docstringparser-_extract_module"></a>

##### `_extract_module`
Extract module-level documentation.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |
| `tree` | `ast.AST` | *required* | - |

**Returns:** `[ModuleDoc](#moduledoc)`
<a id="docstringparser-_source_relative_path"></a>

##### `_source_relative_path`
Return a POSIX source path relative to the parse root.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |

**Returns:** `str`
<a id="docstringparser-_extract_class"></a>

##### `_extract_class`
Extract documentation from a class definition.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.ClassDef` | *required* | - |
| `source_path` | `str` | *required* | - |

**Returns:** `[ClassDoc](#classdoc)`
<a id="docstringparser-_extract_function"></a>

##### `_extract_function`
Extract documentation from a function definition.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.FunctionDef | ast.AsyncFunctionDef` | *required* | - |
| `is_method` | `bool` | `False` | - |
| `source_path` | `str | None` | `None` | - |

**Returns:** `[FunctionDoc](#functiondoc)`
<a id="docstringparser-_extract_ast_params"></a>

##### `_extract_ast_params`
Extract parameter names and type hints from AST.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.FunctionDef | ast.AsyncFunctionDef` | *required* | - |

**Returns:** `list[[Parameter](#parameter)]`
<a id="docstringparser-_positional_defaults"></a>

##### `_positional_defaults`
Return defaults right-aligned to positional arguments.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `args` | `list[ast.arg]` | *required* | - |
| `defaults` | `list[ast.expr]` | *required* | - |

**Returns:** `list[str | None]`
<a id="docstringparser-_merge_param_descriptions"></a>

##### `_merge_param_descriptions`
Merge docstring parameter descriptions into AST-extracted parameters.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `params` | `list[[Parameter](#parameter)]` | *required* | - |
| `parsed` | `ParsedDocstring` | *required* | - |

<a id="docstringparser-_extract_returns"></a>

##### `_extract_returns`
Extract structured return info from parsed docstring.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `parsed` | `ParsedDocstring` | *required* | - |

**Returns:** `[ReturnsInfo](#returnsinfo) | None`
<a id="docstringparser-_extract_raises"></a>

##### `_extract_raises`
Extract structured raises info from parsed docstring.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `parsed` | `ParsedDocstring` | *required* | - |

**Returns:** `list[[RaisesInfo](#raisesinfo)]`
<a id="docstringparser-_extract_attributes"></a>

##### `_extract_attributes`
Extract instance attributes from __init__ method.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `init_node` | `ast.FunctionDef | ast.AsyncFunctionDef` | *required* | - |

**Returns:** `list[[Parameter](#parameter)]`
<a id="docstringparser-_format_base"></a>

##### `_format_base`
Format a base class expression as a string.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `base` | `ast.expr` | *required* | - |

**Returns:** `str`
<a id="docstringparser-_extract_decorator_names"></a>

##### `_extract_decorator_names`
Extract decorator names from a function or class definition.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef` | *required* | - |

**Returns:** `list[str]`
<a id="docstringparser-_resolve_class_type"></a>

##### `_resolve_class_type`
Determine if a class is a dataclass, enum, typeddict, or plain class.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.ClassDef` | *required* | - |
| `bases` | `list[str]` | *required* | - |

**Returns:** `str`
<a id="docstringparser-_is_protocol"></a>

##### `_is_protocol`
Check if the class inherits from typing.Protocol.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bases` | `list[str]` | *required* | - |

**Returns:** `bool`
<a id="docstringparser-_is_abstract"></a>

##### `_is_abstract`
Check if the class inherits from ABC.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bases` | `list[str]` | *required* | - |

**Returns:** `bool`
<a id="docstringparser-_is_pydantic_model"></a>

##### `_is_pydantic_model`
Check if the class inherits from pydantic.BaseModel.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `bases` | `list[str]` | *required* | - |

**Returns:** `bool`
<a id="docstringparser-_extract_pydantic_fields"></a>

##### `_extract_pydantic_fields`
Extract Pydantic field definitions from a class body.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.ClassDef` | *required* | - |

**Returns:** `list[[PydanticField](#pydanticfield)]`
<a id="docstringparser-_parse_pydantic_field"></a>

##### `_parse_pydantic_field`
Parse a single AnnAssign node as a Pydantic field.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.AnnAssign` | *required* | - |

**Returns:** `[PydanticField](#pydanticfield) | None`
<a id="docstringparser-_extract_field_description"></a>

##### `_extract_field_description`
Extract description keyword from a Field() call.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.Call` | *required* | - |

**Returns:** `str | None`
<a id="docstringparser-_extract_public_api"></a>

##### `_extract_public_api`
Extract names from __all__ assignment.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `node` | `ast.Assign | ast.AnnAssign` | *required* | - |

**Returns:** `list[str]`
---
