# generator

Markdown documentation generator.

## Table of Contents

- [Classes](#classes)

  - [`MarkdownGenerator`](#markdowngenerator)

    - [`_create_environment`](#_create_environment)

    - [`_resolve_template_name`](#_resolve_template_name)

    - [`generate`](#generate)

    - [`_generate_index`](#_generate_index)

    - [`generate_single_file`](#generate_single_file)

    - [`generate_string`](#generate_string)

## Classes

### `MarkdownGenerator`

Generate Markdown files from parsed Python documentation.

#### Methods

##### `_create_environment`

Create and configure the Jinja2 environment.

**Returns:** `Environment`

##### `_resolve_template_name`

Resolve the template file name based on theme or custom path.

**Returns:** `str`

##### `generate`

Generate Markdown files for the given modules.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | - |

| `output_dir` | `Path` | - |

**Returns:** `list[Path]`

##### `_generate_index`

Generate an index.md with links to all module docs, grouped by package.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | - |

| `output_dir` | `Path` | - |

**Returns:** `Path | None`

##### `generate_single_file`

Generate a single combined Markdown file for all modules.

Args:
    modules: List of parsed modules.
    output_path: File path for the combined Markdown output.

Returns:
    Path to the generated file.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | List of parsed modules. |

| `output_path` | `Path` | File path for the combined Markdown output. |

**Returns:** `Path`

Path to the generated file.

##### `generate_string`

Generate Markdown content as a string for a single module.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | - |

**Returns:** `str`

---
