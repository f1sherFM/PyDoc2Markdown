"""Tests for CLI."""

import logging
from pathlib import Path

import pytest

from pydoc2markdown import __version__
from pydoc2markdown.cli import main


def test_cli_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out.strip() == f"pydoc2markdown {__version__}"


def test_cli_help_groups_options(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    help_text = capsys.readouterr().out
    assert "Input:" in help_text
    assert "Output:" in help_text
    assert "README integration:" in help_text
    assert "Examples:" in help_text
    assert "pydoc2markdown src/my_package --recursive --nav -o docs" in help_text


def test_cli_missing_source(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([])

    assert result == 1
    assert "Missing source path." in caplog.text
    assert "pydoc2markdown --help" in caplog.text


def test_cli_missing_source_path(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.ERROR):
        result = main(["nonexistent.py"])

    assert result == 1
    assert "Source path does not exist: nonexistent.py" in caplog.text
    assert "pydoc2markdown src --recursive -o docs" in caplog.text


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
    calls: list[dict[str, object]] = []

    def _fake_watch(**kwargs: object) -> int:
        calls.append(kwargs)
        return 0

    monkeypatch.setattr("pydoc2markdown.cli.watch_and_generate", _fake_watch)
    output = tmp_path / "docs"
    result = main([str(sample_module), "-o", str(output), "--watch"])
    assert result == 0
    assert len(calls) == 1
    assert calls[0]["source"] == sample_module
    assert calls[0]["output_dir"] == output


def test_cli_watch_passes_navigation_options(
    sample_module: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, object]] = []

    def _fake_watch(**kwargs: object) -> int:
        calls.append(kwargs)
        return 0

    monkeypatch.setattr("pydoc2markdown.cli.watch_and_generate", _fake_watch)
    result = main(
        [
            str(sample_module),
            "--watch",
            "--nav",
            "--api-dir",
            "reference",
            "--readme",
            "--readme-path",
            str(tmp_path / "README.md"),
            "-o",
            str(tmp_path / "docs"),
        ]
    )

    assert result == 0
    assert calls[0]["navigation"] is True
    assert calls[0]["api_dir"] == Path("reference")
    assert calls[0]["readme_path"] == tmp_path / "README.md"


def test_cli_single_file(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "combined.md"
    result = main([str(sample_package), "--recursive", "--single-file", "-o", str(output)])
    assert result == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "# Documentation" in content
    assert "math_utils" in content


def test_cli_nav_generates_navigation_layout(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    result = main([str(sample_package), "--recursive", "--nav", "-o", str(output)])

    assert result == 0
    assert (output / "index.md").exists()
    assert (output / "modules.md").exists()
    assert (output / "api" / "math_utils.md").exists()
    content = (output / "index.md").read_text(encoding="utf-8")
    assert "# Documentation" in content
    assert "[`math_utils`](api/math_utils.md)" in content


def test_cli_nav_uses_custom_api_dir(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    result = main(
        [
            str(sample_module),
            "--nav",
            "--api-dir",
            "reference",
            "-o",
            str(output),
        ]
    )

    assert result == 0
    assert (output / "reference" / "sample_module.md").exists()


def test_cli_nav_rejects_single_file(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_module),
                "--nav",
                "--single-file",
                "-o",
                str(tmp_path / "docs"),
            ]
        )

    assert result == 1
    assert "--nav cannot be combined with --single-file." in caplog.text
    assert "Use --nav for a docs directory" in caplog.text


def test_cli_readme_updates_custom_readme(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    readme_path = tmp_path / "README.md"

    result = main(
        [
            str(sample_module),
            "-o",
            str(output),
            "--readme",
            "--readme-path",
            str(readme_path),
        ]
    )

    assert result == 0
    assert (output / "sample_module.md").exists()
    content = readme_path.read_text(encoding="utf-8")
    assert "# API Reference" in content
    assert "Calculator" in content
    assert "greet" in content


def test_cli_readme_invalid_marker_block_returns_error(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    readme_path = tmp_path / "README.md"
    readme_path.write_text("<!-- pydoc2markdown:start -->\n", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_module),
                "-o",
                str(tmp_path / "docs"),
                "--readme",
                "--readme-path",
                str(readme_path),
            ]
        )

    assert result == 1
    assert "only one PyDoc2Markdown marker" in caplog.text
    assert "<!-- pydoc2markdown:end -->" in caplog.text


def test_cli_init_creates_pyproject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = main(["--init"])
    assert result == 0
    pyproject = tmp_path / "pyproject.toml"
    assert pyproject.exists()
    content = pyproject.read_text(encoding="utf-8")
    assert "[tool.pydoc2markdown]" in content
    assert 'output = "docs"' in content
    assert 'theme = "default"' in content
    assert "recursive = true" in content


def test_cli_init_appends_to_existing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    existing = "[project]\nname = 'my-app'\n"
    (tmp_path / "pyproject.toml").write_text(existing, encoding="utf-8")
    result = main(["--init"])
    assert result == 0
    content = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert "[project]" in content
    assert "name = 'my-app'" in content
    assert "[tool.pydoc2markdown]" in content
    # Original content preserved
    assert content.index("[project]") < content.index("[tool.pydoc2markdown]")


def test_cli_init_no_overwrite_existing_section(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    existing = '[tool.pydoc2markdown]\noutput = "custom"\n'
    (tmp_path / "pyproject.toml").write_text(existing, encoding="utf-8")
    result = main(["--init"])
    assert result == 0
    content = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    assert content == existing  # Not modified


def test_cli_init_invalid_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("not valid toml {{{", encoding="utf-8")
    result = main(["--init"])
    assert result == 1
