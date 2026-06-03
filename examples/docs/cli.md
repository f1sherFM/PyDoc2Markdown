# cli

Command-line interface for PyDoc2Markdown.

## Table of Contents

- [Functions](#functions)

  - [`create_parser`](#create_parser)

  - [`_setup_logging`](#_setup_logging)

  - [`main`](#main)

## Functions

### `create_parser`

Create and configure the argument parser.

**Returns:** `argparse.ArgumentParser`

### `_setup_logging`

Configure logging level based on verbosity count.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `verbosity` | `int` | - |

**Returns:** `None`

### `main`

Main entry point for the CLI.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `args` | `list[str] | None` | - |

**Returns:** `int`
