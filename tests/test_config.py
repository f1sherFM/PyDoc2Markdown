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
        "show_public_api = false\n"
        "show_returns = false\n"
        "show_private_members = true\n"
        "show_dunder_members = true\n"
        "public_only = true\n"
        "inherit_docstrings = true\n"
        'member_include = ["Widget", "Service.*"]\n'
        'member_exclude = ["Service._debug"]\n'
        'readme_mode = "detailed"\n'
        'readme_title = "Developer API"\n',
        encoding="utf-8",
    )
    config = load_config(cwd=tmp_path)
    assert config["output"] == "build_docs"
    assert config["theme"] == "minimal"
    assert config["show_toc"] is False
    assert config["compact_sections"] is True
    assert config["show_public_api"] is False
    assert config["show_returns"] is False
    assert config["show_private_members"] is True
    assert config["show_dunder_members"] is True
    assert config["public_only"] is True
    assert config["inherit_docstrings"] is True
    assert config["member_include"] == ["Widget", "Service.*"]
    assert config["member_exclude"] == ["Service._debug"]
    assert config["readme_mode"] == "detailed"
    assert config["readme_title"] == "Developer API"


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
