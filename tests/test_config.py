"""Tests for configuration loading."""

from pathlib import Path

from pydoc2markdown.core.config import load_config


def test_load_config_reads_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[tool.pydoc2markdown]\noutput = "build_docs"\ntheme = "minimal"\n',
        encoding="utf-8",
    )
    config = load_config(cwd=tmp_path)
    assert config["output"] == "build_docs"
    assert config["theme"] == "minimal"


def test_load_config_missing_file(tmp_path: Path) -> None:
    config = load_config(cwd=tmp_path)
    assert config == {}
