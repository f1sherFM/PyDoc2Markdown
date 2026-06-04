"""Tests for configuration loading."""

import logging
from pathlib import Path

import pytest

from pydoc2markdown.core.config import load_config


def test_load_config_reads_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[tool.pydoc2markdown]\n"
        'output = "build_docs"\n'
        'theme = "minimal"\n'
        "show_toc = false\n"
        "compact_sections = true\n"
        'readme_mode = "detailed"\n',
        encoding="utf-8",
    )
    config = load_config(cwd=tmp_path)
    assert config["output"] == "build_docs"
    assert config["theme"] == "minimal"
    assert config["show_toc"] is False
    assert config["compact_sections"] is True
    assert config["readme_mode"] == "detailed"


def test_load_config_missing_file(tmp_path: Path) -> None:
    config = load_config(cwd=tmp_path)
    assert config == {}


def test_load_config_invalid_pyproject_returns_empty(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text("[tool.pydoc2markdown\n", encoding="utf-8")

    with caplog.at_level(logging.WARNING):
        config = load_config(cwd=tmp_path)

    assert config == {}
    assert "Failed to load pyproject.toml config" in caplog.text
