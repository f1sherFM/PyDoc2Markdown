"""Type hint formatting utilities."""

import re


def _find_closing_bracket(s: str, start: int = 0) -> int:
    """Find the index of the closing bracket matching an opening bracket at start."""
    depth = 0
    for i, ch in enumerate(s[start:], start=start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return i
    return -1


def _split_top_level(text: str, delimiter: str = ",") -> list[str]:
    """Split text by delimiter respecting nested brackets."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for ch in text:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        elif ch == delimiter and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return parts


def format_type_hint(type_str: str) -> str:
    """Format a type hint string using modern Python syntax.

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
    """
    if not type_str:
        return type_str

    type_str = type_str.strip()

    # Handle Optional[...]
    match = re.match(r"^(typing\.)?Optional\[(.*)\]$", type_str, re.DOTALL)
    if match:
        inner = match.group(2).strip()
        return f"{format_type_hint(inner)} | None"

    # Handle Union[...]
    match = re.match(r"^(typing\.)?Union\[(.*)\]$", type_str, re.DOTALL)
    if match:
        inner = match.group(2).strip()
        parts = _split_top_level(inner, ",")
        return " | ".join(format_type_hint(p) for p in parts)

    # Handle generic aliases from typing module
    alias_map = {
        "List": "list",
        "Dict": "dict",
        "Tuple": "tuple",
        "Set": "set",
        "FrozenSet": "frozenset",
        "Sequence": "collections.abc.Sequence",
        "Iterable": "collections.abc.Iterable",
        "Iterator": "collections.abc.Iterator",
        "Callable": "collections.abc.Callable",
        "Mapping": "collections.abc.Mapping",
        "MutableMapping": "collections.abc.MutableMapping",
        "Collection": "collections.abc.Collection",
    }

    for old, new in alias_map.items():
        pattern = rf"^(typing\.)?{re.escape(old)}(\[.*\])?$"
        m = re.match(pattern, type_str, re.DOTALL)
        if m:
            suffix = m.group(2) or ""
            return f"{new}{format_type_hint(suffix)}"

    # Strip typing. prefix for simple names (e.g. typing.Any → Any)
    if type_str.startswith("typing."):
        type_str = type_str[7:]

    return type_str
