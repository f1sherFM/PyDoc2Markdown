# filtering

Helpers for filtering documented module members before rendering or reporting.

## Table of Contents

- [Functions](#functions)
  - [`filter_modules`](#filter_modules)

## Functions

### `filter_modules`
Return module docs filtered by the configured member-visibility options.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `options` | `object \| None` | `None` | - |

**Returns:** `list[ModuleDoc]`
