# generator

Markdown documentation generator.

## Table of Contents

- [Classes](#classes)
  - [`MarkdownGenerator`](#markdowngenerator)
    - [`_create_environment`](#markdowngenerator-_create_environment)
    - [`_method_anchor`](#markdowngenerator-_method_anchor)
    - [`_source_url`](#markdowngenerator-_source_url)
    - [`_resolve_template_name`](#markdowngenerator-_resolve_template_name)
    - [`generate`](#markdowngenerator-generate)
    - [`generate_navigation`](#markdowngenerator-generate_navigation)
    - [`_write_module_docs`](#markdowngenerator-_write_module_docs)
    - [`_module_output_path`](#markdowngenerator-_module_output_path)
    - [`_module_link`](#markdowngenerator-_module_link)
    - [`_public_modules`](#markdowngenerator-_public_modules)
    - [`_generate_index`](#markdowngenerator-_generate_index)
    - [`_generate_navigation_index`](#markdowngenerator-_generate_navigation_index)
    - [`_generate_package_pages`](#markdowngenerator-_generate_package_pages)
    - [`_package_page_map`](#markdowngenerator-_package_page_map)
    - [`_top_level_package`](#markdowngenerator-_top_level_package)
    - [`_module_stats`](#markdowngenerator-_module_stats)
    - [`_first_doc_line`](#markdowngenerator-_first_doc_line)
    - [`_generate_api_summary`](#markdowngenerator-_generate_api_summary)
    - [`update_readme`](#markdowngenerator-update_readme)
    - [`generate_single_file`](#markdowngenerator-generate_single_file)
    - [`generate_string`](#markdowngenerator-generate_string)
- [Functions](#functions)
  - [`_anchorize`](#_anchorize)
  - [`_write_markdown_lines`](#_write_markdown_lines)
  - [`_normalize_markdown`](#_normalize_markdown)
  - [`_write_utf8_text`](#_write_utf8_text)

## Classes

### `MarkdownGenerator`
Generate Markdown files from parsed Python documentation.

#### Methods

<a id="markdowngenerator-_create_environment"></a>

##### `_create_environment`
Create and configure the Jinja2 environment.

**Returns:** `Environment`
<a id="markdowngenerator-_method_anchor"></a>

##### `_method_anchor`
Return a unique anchor for a class method heading.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `class_name` | `str` | *required* | - |
| `method_name` | `str` | *required* | - |

**Returns:** `str`
<a id="markdowngenerator-_source_url"></a>

##### `_source_url`
Render a source URL for a documented object.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `str | None` | *required* | - |
| `line` | `int | None` | *required* | - |

**Returns:** `str | None`
<a id="markdowngenerator-_resolve_template_name"></a>

##### `_resolve_template_name`
Resolve the template file name based on theme or custom path.

**Returns:** `str`
<a id="markdowngenerator-generate"></a>

##### `generate`
Generate Markdown files for the given modules.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output_dir` | `Path` | *required* | - |

**Returns:** `list[Path]`
<a id="markdowngenerator-generate_navigation"></a>

##### `generate_navigation`
Generate a navigation-first docs layout with API pages under api_dir.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output_dir` | `Path` | *required* | - |
| `api_dir` | `Path` | `Path('api')` | - |

**Returns:** `list[Path]`
<a id="markdowngenerator-_write_module_docs"></a>

##### `_write_module_docs`
Render module documentation files into output_dir.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output_dir` | `Path` | *required* | - |

**Returns:** `list[Path]`
<a id="markdowngenerator-_module_output_path"></a>

##### `_module_output_path`
Return the Markdown output path for a module.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | *required* | - |
| `output_dir` | `Path` | *required* | - |

**Returns:** `Path`
<a id="markdowngenerator-_module_link"></a>

##### `_module_link`
Return a POSIX-style relative link to a module API page.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `str`
<a id="markdowngenerator-_public_modules"></a>

##### `_public_modules`
Return modules that should be shown in indexes.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `collections.abc.Iterable[[ModuleDoc](#moduledoc)]` | *required* | - |

**Returns:** `list[[ModuleDoc](#moduledoc)]`
<a id="markdowngenerator-_generate_index"></a>

##### `_generate_index`
Generate an index.md with links to all module docs, grouped by package.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output_dir` | `Path` | *required* | - |

**Returns:** `Path | None`
<a id="markdowngenerator-_generate_navigation_index"></a>

##### `_generate_navigation_index`
Generate a navigation landing page for docs output.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output_dir` | `Path` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `Path | None`
<a id="markdowngenerator-_generate_package_pages"></a>

##### `_generate_package_pages`
Generate package landing pages for navigation output.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `output_dir` | `Path` | *required* | - |
| `api_dir` | `Path` | *required* | - |

**Returns:** `list[Path]`
<a id="markdowngenerator-_package_page_map"></a>

##### `_package_page_map`
Return top-level package names mapped to navigation page names.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |

**Returns:** `dict[str, str]`
<a id="markdowngenerator-_top_level_package"></a>

##### `_top_level_package`
Return the top-level package label for a module.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | *required* | - |

**Returns:** `str`
<a id="markdowngenerator-_module_stats"></a>

##### `_module_stats`
Return compact class/function counts for navigation links.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | *required* | - |

**Returns:** `str`
<a id="markdowngenerator-_first_doc_line"></a>

##### `_first_doc_line`
Return the first line of a module docstring.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | *required* | - |

**Returns:** `str`
<a id="markdowngenerator-_generate_api_summary"></a>

##### `_generate_api_summary`
Generate a compact API summary suitable for README files.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |

**Returns:** `str`
<a id="markdowngenerator-update_readme"></a>

##### `update_readme`
Create or update the generated API section in a README file.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | - |
| `readme_path` | `Path` | *required* | - |

**Returns:** `Path`
<a id="markdowngenerator-generate_single_file"></a>

##### `generate_single_file`
Generate a single combined Markdown file for all modules.

Args:
    modules: List of parsed modules.
    output_path: File path for the combined Markdown output.

Returns:
    Path to the generated file.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[[ModuleDoc](#moduledoc)]` | *required* | List of parsed modules. |
| `output_path` | `Path` | *required* | File path for the combined Markdown output. |

**Returns:** `Path`
Path to the generated file.

<a id="markdowngenerator-generate_string"></a>

##### `generate_string`
Generate Markdown content as a string for a single module.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `[ModuleDoc](#moduledoc)` | *required* | - |

**Returns:** `str`
---

## Functions

### `_anchorize`
Return a Markdown heading-style anchor fragment.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `value` | `str` | *required* | - |

**Returns:** `str`
### `_write_markdown_lines`
Write Markdown lines with a final newline.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |
| `lines` | `list[str]` | *required* | - |

### `_normalize_markdown`
Tighten rendered Markdown spacing without changing semantics.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `content` | `str` | *required* | - |

**Returns:** `str`
### `_write_utf8_text`
Write UTF-8 text with LF newlines for stable generated output.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `path` | `Path` | *required* | - |
| `content` | `str` | *required* | - |
