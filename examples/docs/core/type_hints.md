# type_hints

Type hint formatting utilities.

## Table of Contents

- [Functions](#functions)
  - [`format_type_hint`](#format_type_hint)

## Functions

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

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `type_str` | `str` | *required* | Raw type hint string. |

**Returns:** `str`
Formatted type hint string.
