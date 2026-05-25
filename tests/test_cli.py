"""Tests for CLI."""

from pathlib import Path

import pytest

from pydoc2markdown.cli import main


def test_cli_version() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0


def test_cli_missing_source() -> None:
    result = main(["nonexistent.py"])
    assert result == 1


def test_cli_success(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    result = main([str(sample_module), "-o", str(output)])
    assert result == 0
    assert output.exists()
    assert (output / "sample_module.md").exists()


def test_cli_recursive(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    result = main([str(sample_package), "--recursive", "-o", str(output)])
    assert result == 0
    assert (output / "math_utils.md").exists()


def test_cli_verbose(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    result = main([str(sample_module), "-o", str(output), "-v"])
    assert result == 0
    assert (output / "sample_module.md").exists()


def test_cli_watch(sample_module: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[object]] = []

    def _fake_watch(**kwargs: object) -> int:
        calls.append(list(kwargs.values()))
        return 0

    monkeypatch.setattr("pydoc2markdown.cli.watch_and_generate", _fake_watch)
    output = tmp_path / "docs"
    result = main([str(sample_module), "-o", str(output), "--watch"])
    assert result == 0
    assert len(calls) == 1
    assert calls[0][0] == sample_module
    assert calls[0][1] == output
