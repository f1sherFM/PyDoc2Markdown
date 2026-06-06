"""Tests for repository examples."""

from pathlib import Path
from shutil import copytree

from pydoc2markdown.cli import main


def test_sample_project_command_generates_expected_docs(tmp_path: Path) -> None:
    sample_root = Path("examples/sample_project")
    source = tmp_path / "src"
    readme = tmp_path / "README.md"
    docs = tmp_path / "docs"

    copytree(sample_root / "src", source)
    readme.write_text(
        "# Sample Project\n\n"
        "## API Reference\n\n"
        "<!-- pydoc2markdown:start -->\n"
        "<!-- pydoc2markdown:end -->\n",
        encoding="utf-8",
    )

    result = main(
        [
            str(source),
            "--recursive",
            "--nav",
            "--readme",
            "--readme-path",
            str(readme),
            "-o",
            str(docs),
        ]
    )

    assert result == 0
    assert (docs / "index.md").exists()
    assert (docs / "shop_demo.md").exists()
    assert (docs / "api" / "shop_demo" / "inventory.md").exists()
    assert (docs / "api" / "shop_demo" / "orders.md").exists()

    index_content = (docs / "index.md").read_text(encoding="utf-8")
    assert "[`shop_demo.inventory`](api/shop_demo/inventory.md)" in index_content
    assert "[`shop_demo.orders`](api/shop_demo/orders.md)" in index_content

    readme_content = readme.read_text(encoding="utf-8")
    assert "**Overview:** 2 modules, 4 classes, 1 functions." in readme_content
    assert "**Quick links:**" in readme_content
    assert "### [`shop_demo.inventory`](docs/api/shop_demo/inventory.md)" in readme_content
    assert "### [`shop_demo.orders`](docs/api/shop_demo/orders.md)" in readme_content
