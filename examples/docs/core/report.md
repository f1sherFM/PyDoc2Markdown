# report

Documentation coverage analysis and terminal reporting.

## Table of Contents

- [Classes](#classes)
  - [`CoverageReport`](#coveragereport)
    - [`category_counts`](#coveragereport-category_counts)
    - [`category_totals`](#coveragereport-category_totals)
    - [`category_documented`](#coveragereport-category_documented)
    - [`category_percentages`](#coveragereport-category_percentages)
    - [`total_findings`](#coveragereport-total_findings)
    - [`total_checks`](#coveragereport-total_checks)
    - [`overall_percentage`](#coveragereport-overall_percentage)
    - [`has_findings`](#coveragereport-has_findings)
    - [`findings_by_category`](#coveragereport-findings_by_category)
    - [`to_dict`](#coveragereport-to_dict)
- [Functions](#functions)
  - [`analyze_modules`](#analyze_modules)
  - [`format_report`](#format_report)
  - [`format_report_json`](#format_report_json)

## Classes

### `CoverageReport` (dataclass)
Structured documentation coverage findings.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `module_count` | `int` | - |
| `class_count` | `int` | - |
| `function_count` | `int` | - |
| `undocumented_modules` | `list[str]` | - |
| `undocumented_classes` | `list[str]` | - |
| `undocumented_functions` | `list[str]` | - |
| `undocumented_public_api` | `list[str]` | - |
| `params_missing_descriptions` | `list[str]` | - |
| `public_api_count` | `int` | - |
| `parameter_count` | `int` | - |

#### Methods
<a id="coveragereport-category_counts"></a>

##### `category_counts`
Return finding counts keyed by report category.

**Returns:** `dict[str, int]`
<a id="coveragereport-category_totals"></a>

##### `category_totals`
Return total documentable items keyed by report category.

**Returns:** `dict[str, int]`
<a id="coveragereport-category_documented"></a>

##### `category_documented`
Return documented counts keyed by report category.

**Returns:** `dict[str, int]`
<a id="coveragereport-category_percentages"></a>

##### `category_percentages`
Return coverage percentages keyed by report category.

**Returns:** `dict[str, float]`
<a id="coveragereport-total_findings"></a>

##### `total_findings`
Return the total number of report findings.

**Returns:** `int`
<a id="coveragereport-total_checks"></a>

##### `total_checks`
Return the total number of documentable checks in the report.

**Returns:** `int`
<a id="coveragereport-overall_percentage"></a>

##### `overall_percentage`
Return overall documentation coverage as a percentage.

**Returns:** `float`
<a id="coveragereport-has_findings"></a>

##### `has_findings`
Return whether any findings exist in the selected categories.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `categories` | `set[str] \| None` | `None` | - |

**Returns:** `bool`
<a id="coveragereport-findings_by_category"></a>

##### `findings_by_category`
Return findings keyed by report category.

**Returns:** `dict[str, list[str]]`
<a id="coveragereport-to_dict"></a>

##### `to_dict`
Return a machine-readable representation of the report.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `categories` | `tuple[str, ...] \| None` | `None` | - |

**Returns:** `dict[str, object]`
---
## Functions

### `analyze_modules`
Inspect parsed modules and return coverage findings.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `filter_options` | `object \| None` | `None` | - |

**Returns:** `[CoverageReport](#coveragereport)`
### `format_report`
Format a human-readable terminal report.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `report` | `[CoverageReport](#coveragereport)` | *required* | - |
| `categories` | `tuple[str, ...] \| None` | `None` | - |
| `summary_only` | `bool` | `False` | - |

**Returns:** `str`
### `format_report_json`
Format a machine-readable JSON coverage report.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `report` | `[CoverageReport](#coveragereport)` | *required* | - |
| `categories` | `tuple[str, ...] \| None` | `None` | - |

**Returns:** `str`
