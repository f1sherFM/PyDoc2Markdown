"""Tests for cross-reference link generation."""

from pathlib import Path

from pydoc2markdown.core.crossref import TypeIndex
from pydoc2markdown.core.parser import DocstringParser


def test_type_index_does_not_relink_existing_markdown_links() -> None:
    index = TypeIndex({"User": "user"})

    linked = index.link("[User](#user)")

    assert linked == "[User](#user)"


def test_type_index_links_plain_project_types() -> None:
    index = TypeIndex({"User": "user"})

    linked = index.link("list[User]")

    assert linked == "list[[User](#user)]"


def test_type_index_links_local_type_when_names_overlap(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "a.py").write_text(
        '''"""Module A."""

class User:
    """User from A."""

def get_user() -> User:
    """Get a user."""
    return User()
''',
        encoding="utf-8",
    )
    (package / "b.py").write_text(
        '''"""Module B."""

class User:
    """User from B."""
''',
        encoding="utf-8",
    )

    index = TypeIndex.from_modules(DocstringParser().parse(package, recursive=True))

    assert index.link("User", current_module="a") == "[User](#user)"
    assert index.link("User", current_module="b") == "[User](#user)"
    assert index.link("User", current_module="other") == "User"


def test_type_index_skips_ambiguous_global_type_links(tmp_path: Path) -> None:
    package = tmp_path / "pkg"
    package.mkdir()
    (package / "a.py").write_text(
        '''"""Module A."""

class User:
    """User from A."""
''',
        encoding="utf-8",
    )
    (package / "b.py").write_text(
        '''"""Module B."""

class User:
    """User from B."""
''',
        encoding="utf-8",
    )

    index = TypeIndex.from_modules(DocstringParser().parse(package, recursive=True))

    assert index.link("User") == "User"
