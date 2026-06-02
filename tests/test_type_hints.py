"""Tests for type hint formatting."""

import pytest

from pydoc2markdown.core.type_hints import format_type_hint


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("str", "str"),
        ("int", "int"),
        ("Optional[str]", "str | None"),
        ("typing.Optional[str]", "str | None"),
        ("Union[str, int]", "str | int"),
        ("typing.Union[str, int]", "str | int"),
        ("Union[str, int, None]", "str | int | None"),
        ("List[str]", "list[str]"),
        ("typing.List[str]", "list[str]"),
        ("Dict[str, int]", "dict[str, int]"),
        ("Tuple[str, int]", "tuple[str, int]"),
        ("Set[str]", "set[str]"),
        ("FrozenSet[int]", "frozenset[int]"),
        ("Any", "Any"),
        ("typing.Any", "Any"),
        ("", ""),
        ("Optional[List[str]]", "list[str] | None"),
        ("Union[List[str], Dict[str, int]]", "list[str] | dict[str, int]"),
        ('Optional[Literal["foo", "bar"]]', 'Literal["foo", "bar"] | None'),
        ('Union[Literal["foo,bar"], Literal["baz"]]', 'Literal["foo,bar"] | Literal["baz"]'),
    ],
)
def test_format_type_hint(raw: str, expected: str) -> None:
    assert format_type_hint(raw) == expected
