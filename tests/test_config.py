"""Tests for configuration loading."""

import logging
from pathlib import Path

import pytest

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
