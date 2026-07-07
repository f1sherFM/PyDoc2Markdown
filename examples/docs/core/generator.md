# generator

Markdown documentation generator.

## Table of Contents

- [Classes](#classes)
  - [`OutputOptions`](#outputoptions)
  - [`MarkdownGenerator`](#markdowngenerator)
    - [`generate`](#markdowngenerator-generate)
    - [`generate_navigation`](#markdowngenerator-generate_navigation)
    - [`update_readme`](#markdowngenerator-update_readme)
    - [`generate_single_file`](#markdowngenerator-generate_single_file)
    - [`generate_string`](#markdowngenerator-generate_string)

## Classes

### `OutputOptions` (dataclass)
Rendering options for built-in Markdown output.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `show_toc` | `bool` | - |
| `show_source_links` | `bool` | - |
| `compact_sections` | `bool` | - |
| `show_class_metadata` | `bool` | - |
| `show_public_api` | `bool` | - |
| `show_attributes` | `bool` | - |
| `show_returns` | `bool` | - |
| `show_raises` | `bool` | - |
| `show_private_members` | `bool` | - |
| `show_dunder_members` | `bool` | - |
| `public_only` | `bool` | - |
| `member_include` | `tuple[str, ...]` | - |
| `member_exclude` | `tuple[str, ...]` | - |

---
### `MarkdownGenerator`
Generate Markdown files from parsed Python documentation.

#### Constructor Parameters
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `template_path` | `Path \| None` | `None` | - |
| `theme` | `str` | `'default'` | - |
| `source_link_template` | `str \| None` | `None` | - |
| `output_options` | `[OutputOptions](#outputoptions) \| None` | `None` | - |
| `readme_mode` | `str` | `'summary'` | - |
| `readme_title` | `str` | `DEFAULT_README_TITLE` | - |
| `readme_module_links` | `dict[str, str] \| None` | `None` | - |

#### Methods
<a id="markdowngenerator-generate"></a>

##### `generate`
Generate Markdown files for the given modules.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `output_dir` | `Path` | *required* | - |

**Returns:** `list[Path]`
<a id="markdowngenerator-generate_navigation"></a>

##### `generate_navigation`
Generate a navigation-first docs layout with API pages under api_dir.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `output_dir` | `Path` | *required* | - |
| `api_dir` | `Path` | `Path('api')` | - |

**Returns:** `list[Path]`
<a id="markdowngenerator-update_readme"></a>

##### `update_readme`
Create or update the generated API section in a README file.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `readme_path` | `Path` | *required* | - |

**Returns:** `Path`
<a id="markdowngenerator-generate_single_file"></a>

##### `generate_single_file`
Generate a single combined Markdown file for all modules.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | List of parsed modules. |
| `output_path` | `Path` | *required* | File path for the combined Markdown output. |

**Returns:** `Path`
Path to the generated file.

<a id="markdowngenerator-generate_string"></a>

##### `generate_string`
Generate Markdown content as a string for a single module.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `module` | `ModuleDoc` | *required* | - |

**Returns:** `str`
---
