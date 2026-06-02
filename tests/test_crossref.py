"""Tests for cross-reference link generation."""

from pydoc2markdown.core.crossref import TypeIndex


def test_type_index_does_not_relink_existing_markdown_links() -> None:
    index = TypeIndex({"User": "user"})

    linked = index.link("[User](#user)")

    assert linked == "[User](#user)"


def test_type_index_links_plain_project_types() -> None:
    index = TypeIndex({"User": "user"})

    linked = index.link("list[User]")

    assert linked == "list[[User](#user)]"
