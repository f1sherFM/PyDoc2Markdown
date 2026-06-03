# type_hints

Type hint formatting utilities.

## Table of Contents

- [Functions](#functions)

  - [`_find_closing_bracket`](#_find_closing_bracket)

  - [`_split_top_level`](#_split_top_level)

  - [`format_type_hint`](#format_type_hint)

## Functions

### `_find_closing_bracket`

Find the index of the closing bracket matching an opening bracket at start.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `s` | `str` | - |

| `start` | `int` | - |

**Returns:** `int`

### `_split_top_level`

Split text by delimiter respecting nested brackets.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | - |

| `delimiter` | `str` | - |

**Returns:** `list[str]`

### `format_type_hint`

Format a type hint string using modern Python syntax.

Transformations:
- ``Optional[X]`` → ``X | None``
- ``Union[X, Y]`` → ``X | Y``
- ``typing.List[X]`` → ``list[X]``
- ``typing.Dict[X, Y]`` → ``dict[X, Y]``
- ``typing.Tuple[X, ...]`` → ``tuple[X, ...]``
- ``typing.Set[X]`` → ``set[X]``
- ``typing.FrozenSet[X]`` → ``frozenset[X]``
- ``typing.Any`` → ``Any`` (drop typing prefix)

Args:
    type_str: Raw type hint string.

Returns:
    Formatted type hint string.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `type_str` | `str` | Raw type hint string. |

**Returns:** `str`

Formatted type hint string.
