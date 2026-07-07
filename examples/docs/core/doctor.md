# doctor

Project diagnostics for PyDoc2Markdown onboarding.

## Table of Contents

- [Classes](#classes)
  - [`DoctorOptions`](#doctoroptions)
- [Functions](#functions)
  - [`format_doctor_report`](#format_doctor_report)

## Classes

### `DoctorOptions` (dataclass)
Context used to render a project diagnostics report.

#### Attributes
| Name | Type | Description |
|------|------|-------------|
| `source` | `Path` | - |
| `recursive` | `bool` | - |
| `output` | `Path` | - |
| `readme_path` | `Path` | - |
| `cwd` | `Path` | - |
| `filter_options` | `object \| None` | - |

---
## Functions

### `format_doctor_report`
Return a human-readable diagnostics report for a Python documentation surface.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `modules` | `list[ModuleDoc]` | *required* | - |
| `options` | `[DoctorOptions](#doctoroptions)` | *required* | - |

**Returns:** `str`
