"""Tests for CLI."""

import json
import logging
from pathlib import Path
from typing import cast

import pytest

from pydoc2markdown import __version__
from pydoc2markdown.cli import main
from pydoc2markdown.core.generator import OutputOptions


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
    assert "Analysis:" in help_text
    assert "Demo:" in help_text
    assert "Examples:" in help_text
    assert "--dry-run" in help_text
    assert "--include" in help_text
    assert "--exclude" in help_text
    assert "pydoc2markdown --demo" in help_text
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


def test_cli_recursive_filters_include_exclude(tmp_path: Path) -> None:
    source = tmp_path / "pkg"
    api = source / "api"
    internal = source / "internal"
    api.mkdir(parents=True)
    internal.mkdir()
    (api / "public.py").write_text('"""Public API."""\n', encoding="utf-8")
    (api / "generated.py").write_text('"""Generated API."""\n', encoding="utf-8")
    (internal / "secret.py").write_text('"""Internal module."""\n', encoding="utf-8")

    output = tmp_path / "docs"
    result = main(
        [
            str(source),
            "--recursive",
            "--include",
            "api/*",
            "--exclude",
            "*/generated.py",
            "-o",
            str(output),
        ]
    )

    assert result == 0
    assert (output / "api" / "public.md").exists()
    assert not (output / "api" / "generated.md").exists()
    assert not (output / "internal" / "secret.md").exists()


def test_cli_source_repo_generates_source_links(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    result = main(
        [
            str(sample_module),
            "--source-repo",
            "acme/app",
            "-o",
            str(output),
        ]
    )

    assert result == 0
    content = (output / "sample_module.md").read_text(encoding="utf-8")
    assert "[source](https://github.com/acme/app/blob/main/sample_module.py#L" in content


def test_cli_source_link_rejects_source_repo(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_module),
                "--source-link",
                "https://example.com/{path}#L{line}",
                "--source-repo",
                "acme/app",
                "-o",
                str(tmp_path / "docs"),
            ]
        )

    assert result == 1
    assert "--source-link cannot be combined with --source-repo." in caplog.text


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
            "--include",
            "pkg/*",
            "--exclude",
            "pkg/internal/*",
            "--source-repo",
            "acme/app",
            "--readme",
            "--readme-path",
            str(tmp_path / "README.md"),
            "--public-only",
            "--show-private-members",
            "--show-dunder-members",
            "--member-include",
            "Widget,Widget.run",
            "--member-exclude",
            "Widget._debug",
            "-o",
            str(tmp_path / "docs"),
        ]
    )

    assert result == 0
    assert calls[0]["navigation"] is True
    assert calls[0]["api_dir"] == Path("reference")
    assert calls[0]["include"] == ["pkg/*"]
    assert calls[0]["exclude"] == ["pkg/internal/*"]
    assert (
        calls[0]["source_link_template"] == "https://github.com/acme/app/blob/main/{path}#L{line}"
    )
    assert calls[0]["readme_path"] == tmp_path / "README.md"
    assert calls[0]["readme_mode"] == "summary"
    assert calls[0]["readme_title"] == "API Reference"
    output_options = cast(OutputOptions, calls[0]["output_options"])
    assert output_options.show_toc is True
    assert output_options.public_only is True
    assert output_options.show_private_members is True
    assert output_options.show_dunder_members is True
    assert output_options.member_include == ("Widget", "Widget.run")
    assert output_options.member_exclude == ("Widget._debug",)


def test_cli_single_file(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "combined.md"
    result = main([str(sample_package), "--recursive", "--single-file", "-o", str(output)])
    assert result == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "# Documentation" in content
    assert "math_utils" in content


def test_cli_single_file_requires_file_output(
    sample_package: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_package), "--recursive", "--single-file"])

    assert result == 1
    assert "--single-file output points to a directory" in caplog.text


def test_cli_single_file_rejects_output_without_markdown_suffix(
    sample_package: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_package),
                "--recursive",
                "--single-file",
                "-o",
                str(tmp_path / "combined"),
            ]
        )

    assert result == 1
    assert "--single-file requires --output to be a Markdown file path." in caplog.text


def test_cli_single_file_rejects_existing_output_dir(
    sample_package: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    output.mkdir()

    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_package),
                "--recursive",
                "--single-file",
                "-o",
                str(output),
            ]
        )

    assert result == 1
    assert "--single-file output points to a directory" in caplog.text


def test_cli_check_passes_when_docs_are_current(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_module), "-o", str(output)]) == 0

    result = main([str(sample_module), "-o", str(output), "--check"])

    assert result == 0


def test_cli_check_fails_when_docs_are_outdated(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_module), "-o", str(output)]) == 0
    generated = output / "sample_module.md"
    generated.write_text("stale docs\n", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "-o", str(output), "--check"])

    assert result == 1
    assert "Generated documentation is out of date." in caplog.text
    assert str(generated) in caplog.text
    assert generated.read_text(encoding="utf-8") == "stale docs\n"


def test_cli_check_fails_when_stale_generated_file_remains(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = tmp_path / "pkg"
    source.mkdir()
    initial = source / "sample_module.py"
    initial.write_text('"""First module."""\n', encoding="utf-8")
    output = tmp_path / "docs"
    assert main([str(initial), "-o", str(output)]) == 0

    renamed = source / "renamed_module.py"
    initial.rename(renamed)
    renamed.write_text('"""Renamed module."""\n', encoding="utf-8")
    stale = output / "sample_module.md"

    with caplog.at_level(logging.ERROR):
        result = main([str(renamed), "-o", str(output), "--check"])

    assert result == 1
    assert "Generated documentation is out of date." in caplog.text
    assert str(stale) in caplog.text


def test_cli_check_detects_outdated_generated_content(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    module = tmp_path / "stale_content.py"
    module.write_text('"""Fresh docs."""\n', encoding="utf-8")
    output = tmp_path / "docs"
    assert main([str(module), "-o", str(output)]) == 0

    generated = output / "stale_content.md"
    generated.write_text("stale docs\n", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = main([str(module), "-o", str(output), "--check"])

    assert result == 1
    assert "Generated documentation is out of date." in caplog.text
    assert str(generated) in caplog.text


def test_cli_check_keeps_non_generated_markdown_files(
    sample_module: Path,
    tmp_path: Path,
) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_module), "-o", str(output)]) == 0
    (output / "guide.md").write_text("# Manual guide\n", encoding="utf-8")

    result = main([str(sample_module), "-o", str(output), "--check"])

    assert result == 0


def test_cli_check_single_file(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "combined.md"
    assert main([str(sample_package), "--recursive", "--single-file", "-o", str(output)]) == 0

    result = main(
        [
            str(sample_package),
            "--recursive",
            "--single-file",
            "-o",
            str(output),
            "--check",
        ]
    )

    assert result == 0


def test_cli_check_navigation_layout(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_package), "--recursive", "--nav", "-o", str(output)]) == 0

    result = main([str(sample_package), "--recursive", "--nav", "-o", str(output), "--check"])

    assert result == 0


def test_cli_check_readme_fails_when_api_section_is_outdated(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    readme_path = tmp_path / "README.md"
    assert (
        main(
            [
                str(sample_module),
                "-o",
                str(output),
                "--readme",
                "--readme-path",
                str(readme_path),
            ]
        )
        == 0
    )
    readme_path.write_text("# Project\n\nOld API docs.\n", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_module),
                "-o",
                str(output),
                "--readme",
                "--readme-path",
                str(readme_path),
                "--check",
            ]
        )

    assert result == 1
    assert str(readme_path) in caplog.text
    assert readme_path.read_text(encoding="utf-8") == "# Project\n\nOld API docs.\n"


def test_cli_check_rejects_watch(sample_module: Path, tmp_path: Path) -> None:
    result = main([str(sample_module), "-o", str(tmp_path / "docs"), "--watch", "--check"])

    assert result == 1


def test_cli_demo_creates_project(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "demo"
    result = main(["--demo", "--demo-output", str(output)])

    assert result == 0
    assert (output / "README.md").exists()
    assert (output / "src" / "shop_demo" / "inventory.py").exists()
    assert (output / "docs" / "index.md").exists()
    assert (output / "docs" / "api" / "shop_demo" / "orders.md").exists()

    readme = (output / "README.md").read_text(encoding="utf-8")
    assert "This small shop package shows what PyDoc2Markdown creates" in readme
    assert "### [`shop_demo.inventory`](docs/api/shop_demo/inventory.md)" in readme
    assert "### [`shop_demo.orders`](docs/api/shop_demo/orders.md)" in readme
    assert "pydoc2markdown src --recursive --nav --readme --check -o docs" in readme

    out = capsys.readouterr().out
    assert "Created demo project:" in out
    assert "Next steps:" in out
    assert "Inspect the README:" in out
    assert "Inspect the docs index:" in out
    assert "pydoc2markdown src --recursive --nav --readme --check -o docs" in out


def test_cli_demo_rejects_non_empty_output(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "demo"
    output.mkdir()
    (output / "existing.txt").write_text("keep me", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = main(["--demo", "--demo-output", str(output)])

    assert result == 1
    assert "Demo output directory is not empty" in caplog.text
    assert "--demo-output" in caplog.text
    assert (output / "existing.txt").read_text(encoding="utf-8") == "keep me"


def test_cli_demo_rejects_source_argument(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main(
            [
                str(sample_module),
                "--demo",
                "--demo-output",
                str(tmp_path / "demo"),
            ]
        )

    assert result == 1
    assert "--demo does not accept a source path." in caplog.text


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
    assert "### [`sample_module`](docs/sample_module.md)" in content
    assert "_Includes: 1 class(es), 1 function(s)._" in content
    assert "- `Calculator`: A simple calculator class." in content
    assert "- `greet`: Greet a person." in content
    assert "Calculator" in content
    assert "greet" in content


def test_cli_readme_detailed_mode(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    readme_path = tmp_path / "README.md"

    result = main(
        [
            str(sample_module),
            "-o",
            str(output),
            "--readme",
            "--readme-mode",
            "detailed",
            "--readme-path",
            str(readme_path),
        ]
    )

    assert result == 0
    content = readme_path.read_text(encoding="utf-8")
    assert "### sample_module" in content
    assert "##### `Calculator`" in content


def test_cli_readme_uses_custom_title(sample_module: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    readme_path = tmp_path / "README.md"

    result = main(
        [
            str(sample_module),
            "-o",
            str(output),
            "--readme",
            "--readme-title",
            "Developer API",
            "--readme-path",
            str(readme_path),
        ]
    )

    assert result == 0
    content = readme_path.read_text(encoding="utf-8")
    assert "# Developer API" in content
    assert "# API Reference" not in content


def test_cli_readme_links_to_navigation_docs(sample_package: Path, tmp_path: Path) -> None:
    output = tmp_path / "docs"
    readme_path = tmp_path / "README.md"

    result = main(
        [
            str(sample_package),
            "--recursive",
            "--nav",
            "--readme",
            "--readme-path",
            str(readme_path),
            "-o",
            str(output),
        ]
    )

    assert result == 0
    content = readme_path.read_text(encoding="utf-8")
    assert "### [`math_utils`](docs/api/math_utils.md)" in content


def test_cli_respects_configured_output_toggles(
    sample_module: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        "[tool.pydoc2markdown]\n"
        "show_toc = false\n"
        "show_source_links = false\n"
        "show_returns = false\n"
        'readme_mode = "detailed"\n'
        'readme_title = "Developer API"\n',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    output = tmp_path / "docs"

    result = main([str(sample_module), "-o", str(output), "--readme"])

    assert result == 0
    module_content = (output / "sample_module.md").read_text(encoding="utf-8")
    assert "## Table of Contents" not in module_content
    assert "**Returns:**" not in module_content
    readme_content = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "# Developer API" in readme_content
    assert "### sample_module" in readme_content


def test_cli_hides_selected_sections_with_flags(tmp_path: Path) -> None:
    source = tmp_path / "feature_module.py"
    source.write_text(
        '''"""Feature module."""

__all__ = ["Gadget", "helper"]

class Gadget:
    """Example gadget."""

    def __init__(self, name: str) -> None:
        """Create a gadget.

        Args:
            name: Gadget name.
        """
        self.name: str = name

    def run(self, value: int) -> int:
        """Run the gadget.

        Args:
            value: Input value.

        Returns:
            Processed value.

        Raises:
            ValueError: If the input is invalid.
        """
        if value < 0:
            raise ValueError("invalid")
        return value

def helper() -> int:
    """Help the gadget.

    Returns:
        Static result.
    """
    return 1
''',
        encoding="utf-8",
    )

    output = tmp_path / "docs"
    result = main(
        [
            str(source),
            "-o",
            str(output),
            "--no-show-public-api",
            "--no-show-attributes",
            "--no-show-returns",
            "--no-show-raises",
        ]
    )

    assert result == 0
    content = (output / "feature_module.md").read_text(encoding="utf-8")
    assert "**Public API:**" not in content
    assert "**Attributes:**" not in content
    assert "#### Attributes" not in content
    assert "**Returns:**" not in content
    assert "**Raises:**" not in content


def test_cli_member_filtering_flags_apply_to_docs_output(tmp_path: Path) -> None:
    source = tmp_path / "filtered_cli.py"
    source.write_text(
        '''"""CLI filtering sample."""

__all__ = ["Widget", "exported_helper"]

class Widget:
    """Public widget."""

    def run(self) -> None:
        """Run the widget."""

    def _debug(self) -> None:
        """Debug helper."""

    def __repr__(self) -> str:
        """Render the widget."""
        return "Widget()"

class _InternalWidget:
    """Internal widget."""

def exported_helper() -> None:
    """Exported helper."""

def public_helper() -> None:
    """Non-exported helper."""
''',
        encoding="utf-8",
    )

    output = tmp_path / "docs"
    result = main([str(source), "-o", str(output), "--public-only"])

    assert result == 0
    content = (output / "filtered_cli.md").read_text(encoding="utf-8")
    assert "### `Widget`" in content
    assert "### `exported_helper`" in content
    assert "_debug" not in content
    assert "__repr__" not in content
    assert "_InternalWidget" not in content
    assert "public_helper" not in content


def test_cli_can_show_private_and_dunder_members(tmp_path: Path) -> None:
    source = tmp_path / "visible_cli.py"
    source.write_text(
        '''"""CLI visible filtering sample."""

class Widget:
    """Public widget."""

    def _debug(self) -> None:
        """Debug helper."""

    def __repr__(self) -> str:
        """Render the widget."""
        return "Widget()"

def _private_helper() -> None:
    """Private helper."""
''',
        encoding="utf-8",
    )

    output = tmp_path / "docs"
    result = main(
        [
            str(source),
            "-o",
            str(output),
            "--show-private-members",
            "--show-dunder-members",
        ]
    )

    assert result == 0
    content = (output / "visible_cli.md").read_text(encoding="utf-8")
    assert "`_debug`" in content
    assert "`__repr__`" in content
    assert "### `_private_helper`" in content


def test_cli_member_include_and_exclude_patterns(tmp_path: Path) -> None:
    source = tmp_path / "pattern_cli.py"
    source.write_text(
        '''"""CLI pattern filtering sample."""

class Widget:
    """Public widget."""

    def run(self) -> None:
        """Run the widget."""

    def helper(self) -> None:
        """Helper method."""

class Service:
    """Background service."""

    def run(self) -> None:
        """Run the service."""

def public_helper() -> None:
    """Public helper."""

def backup() -> None:
    """Backup helper."""
''',
        encoding="utf-8",
    )

    output = tmp_path / "docs"
    result = main(
        [
            str(source),
            "-o",
            str(output),
            "--member-include",
            "Widget,Service.run,public_*",
            "--member-exclude",
            "Widget.helper",
        ]
    )

    assert result == 0
    content = (output / "pattern_cli.md").read_text(encoding="utf-8")
    assert "### `Widget`" in content
    assert "`helper`" not in content
    assert "### `Service`" in content
    assert "Run the service." in content
    assert "### `public_helper`" in content
    assert "### `backup`" not in content


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
    assert "show_private_members = false" in content
    assert "show_dunder_members = false" in content
    assert "public_only = false" in content
    assert "member_include = []" in content
    assert "member_exclude = []" in content
    assert 'readme_mode = "summary"' in content


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


def test_cli_prune_removes_stale_files(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = tmp_path / "pkg"
    source.mkdir()
    initial = source / "sample_module.py"
    initial.write_text('"""First module."""\n', encoding="utf-8")

    output = tmp_path / "docs"
    assert main([str(initial), "-o", str(output)]) == 0

    renamed = source / "renamed_module.py"
    initial.rename(renamed)
    renamed.write_text('"""Renamed module."""\n', encoding="utf-8")

    stale = output / "sample_module.md"
    assert stale.exists()

    with caplog.at_level(logging.INFO):
        result = main([str(renamed), "-o", str(output), "--prune"])

    assert result == 0
    assert not stale.exists()
    assert f"Removed stale generated file: {stale}" in caplog.text
    assert "1 stale generated file(s) removed." in caplog.text
    assert (output / "index.md").exists()


def test_cli_prune_keeps_current_files(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_module), "-o", str(output)]) == 0

    with caplog.at_level(logging.INFO):
        result = main([str(sample_module), "-o", str(output), "--prune"])

    assert result == 0
    assert "No stale generated files found." in caplog.text
    assert (output / "sample_module.md").exists()


def test_cli_prune_keeps_non_generated_markdown_files(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_module), "-o", str(output)]) == 0

    guide = output / "guide.md"
    guide.write_text("# Manual guide\n", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        result = main([str(sample_module), "-o", str(output), "--prune"])

    assert result == 0
    assert guide.exists()
    assert "Removed stale generated file:" not in caplog.text


def test_cli_prune_nav_layout(
    sample_package: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    assert main([str(sample_package), "--recursive", "--nav", "-o", str(output)]) == 0

    stale = output / "api" / "math_utils.md"
    assert stale.exists()
    (sample_package / "math_utils.py").rename(sample_package / "helpers.py")
    (sample_package / "helpers.py").write_text(
        '''"""Math utilities."""

def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y
''',
        encoding="utf-8",
    )

    with caplog.at_level(logging.INFO):
        result = main([str(sample_package), "--recursive", "--nav", "-o", str(output), "--prune"])

    assert result == 0
    assert not stale.exists()
    assert (output / "index.md").exists()
    assert (output / "api").exists()


def test_cli_prune_on_empty_directory(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "docs"
    output.mkdir(parents=True, exist_ok=True)

    with caplog.at_level(logging.INFO):
        result = main([str(sample_module), "-o", str(output), "--prune"])

    assert result == 0
    assert "No stale generated files found." in caplog.text


def test_cli_prune_single_file_keeps_outdated_current_output(
    sample_package: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    output = tmp_path / "combined.md"
    assert main([str(sample_package), "--recursive", "--single-file", "-o", str(output)]) == 0
    output.write_text("# stale single file\n", encoding="utf-8")

    with caplog.at_level(logging.INFO):
        result = main(
            [
                str(sample_package),
                "--recursive",
                "--single-file",
                "-o",
                str(output),
                "--prune",
            ]
        )

    assert result == 0
    assert output.exists()
    assert output.read_text(encoding="utf-8") == "# stale single file\n"
    assert "Removed stale generated file:" not in caplog.text


def test_cli_prune_dry_run_reports_without_deleting(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    source = tmp_path / "pkg"
    source.mkdir()
    initial = source / "sample_module.py"
    initial.write_text('"""First module."""\n', encoding="utf-8")

    output = tmp_path / "docs"
    assert main([str(initial), "-o", str(output)]) == 0

    renamed = source / "renamed_module.py"
    initial.rename(renamed)
    renamed.write_text('"""Renamed module."""\n', encoding="utf-8")
    stale = output / "sample_module.md"

    with caplog.at_level(logging.INFO):
        result = main([str(renamed), "-o", str(output), "--prune", "--dry-run"])

    assert result == 0
    assert stale.exists()
    assert f"Would remove stale generated file: {stale}" in caplog.text
    assert "1 stale generated file(s) would be removed." in caplog.text


def test_cli_dry_run_requires_prune(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "-o", str(tmp_path / "docs"), "--dry-run"])

    assert result == 1
    assert "--dry-run currently works only with --prune." in caplog.text


def test_cli_prune_rejects_check(sample_module: Path, tmp_path: Path) -> None:
    result = main([str(sample_module), "-o", str(tmp_path / "docs"), "--prune", "--check"])
    assert result == 1


def test_cli_prune_rejects_watch(sample_module: Path, tmp_path: Path) -> None:
    result = main([str(sample_module), "-o", str(tmp_path / "docs"), "--prune", "--watch"])
    assert result == 1


def test_cli_report_prints_summary(
    sample_module: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main([str(sample_module), "--report"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Documentation Coverage Report" in output
    assert "Scanned 1 module(s), 1 class(es), and 1 function(s)." in output
    assert "Overall coverage:" in output
    assert "Coverage by category:" in output
    assert "Modules without docstrings: 0" in output


def test_cli_report_finds_coverage_gaps(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_sample.py"
    module.write_text(
        '''class MissingDocs:
    def run(self, value: int) -> None:
        """Run something."""

def helper(value: int, other: int) -> None:
    """Help with something.

    Args:
        value: First value.
    """

__all__ = ["MissingDocs", "helper", "missing_export"]
''',
        encoding="utf-8",
    )

    result = main([str(module), "--report"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Modules without docstrings: 1" in output
    assert "Classes without docstrings: 1" in output
    assert "Undocumented public API exports: 2" in output
    assert "Parameters missing descriptions: 2" in output
    assert "- coverage_sample.MissingDocs" in output
    assert "- coverage_sample.missing_export" in output


def test_cli_report_summary_only_hides_individual_findings(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_summary.py"
    module.write_text(
        '''class MissingDocs:
    def run(self, value: int) -> None:
        """Run something."""

def helper(value: int, other: int) -> None:
    """Help with something.

    Args:
        value: First value.
    """
''',
        encoding="utf-8",
    )

    result = main([str(module), "--report", "--report-summary-only"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Parameters missing descriptions: 2" in output
    assert "- coverage_summary.MissingDocs" not in output
    assert "- coverage_summary.helper(other)" not in output


def test_cli_report_categories_filters_text_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_categories.py"
    module.write_text(
        '''class MissingDocs:
    def run(self, value: int) -> None:
        """Run something."""

def helper(value: int, other: int) -> None:
    """Help with something.

    Args:
        value: First value.
    """

__all__ = ["MissingDocs", "helper", "missing_export"]
''',
        encoding="utf-8",
    )

    result = main([str(module), "--report", "--report-categories", "modules,params"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Modules without docstrings:" in output
    assert "Parameters missing descriptions:" in output
    assert "Classes without docstrings:" not in output
    assert "Undocumented public API exports:" not in output


def test_cli_report_json_output(
    sample_module: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main([str(sample_module), "--report", "--report-format", "json"])

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["module_count"] == 1
    assert payload["summary"]["class_count"] == 1
    assert payload["summary"]["overall_percentage"] == 75.0
    assert payload["counts"]["modules"] == 0
    assert payload["counts"]["functions"] == 0
    assert payload["percentages"]["params"] == 60.0


def test_cli_report_respects_member_filtering_flags(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_filtering.py"
    module.write_text(
        '''"""Coverage filtering sample."""

__all__ = ["public_helper"]

def public_helper(value: int, other: int) -> None:
    """Public helper.

    Args:
        value: First value.
    """

def public_not_exported() -> None:
    pass

def _private_helper() -> None:
    pass
''',
        encoding="utf-8",
    )

    result = main([str(module), "--report", "--public-only"])

    assert result == 0
    output = capsys.readouterr().out
    assert "Scanned 1 module(s), 0 class(es), and 1 function(s)." in output
    assert "Functions without docstrings: 0" in output
    assert "Undocumented public API exports: 0" in output
    assert "Parameters missing descriptions: 1" in output
    assert "public_not_exported" not in output
    assert "_private_helper" not in output


def test_cli_report_respects_member_include_and_exclude_patterns(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_patterns.py"
    module.write_text(
        '''"""Coverage pattern sample."""

class Widget:
    """Public widget."""

    def run(self) -> None:
        """Run the widget."""

class Service:
    """Background service."""

    def run(self) -> None:
        pass

def public_helper() -> None:
    """Public helper."""

def backup() -> None:
    pass
''',
        encoding="utf-8",
    )

    result = main(
        [
            str(module),
            "--report",
            "--member-include",
            "Widget,Service.run,public_*",
            "--member-exclude",
            "Service.run",
        ]
    )

    assert result == 0
    output = capsys.readouterr().out
    assert "Scanned 1 module(s), 1 class(es), and 1 function(s)." in output
    assert "Classes without docstrings: 0" in output
    assert "Functions without docstrings: 0" in output
    assert "Service" not in output
    assert "backup" not in output


def test_cli_member_filters_apply_to_attributes_and_fields(tmp_path: Path) -> None:
    source = tmp_path / "field_cli.py"
    source.write_text(
        '''"""CLI field filtering sample."""

from pydantic import BaseModel, Field

class Widget:
    """Widget with internal state."""

    def __init__(self, name: str, secret: str) -> None:
        """Create widget.

        Args:
            name: Public name.
            secret: Internal secret.
        """
        self.name: str = name
        self._secret: str = secret

class Config(BaseModel):
    """Pydantic config."""

    debug: bool = False
    _token: str = Field(default="", description="Internal token")
''',
        encoding="utf-8",
    )

    output = tmp_path / "docs"
    result = main(
        [
            str(source),
            "-o",
            str(output),
            "--member-exclude",
            "Config.debug",
        ]
    )

    assert result == 0
    content = (output / "field_cli.md").read_text(encoding="utf-8")
    assert "| `name` | `str` | Public name. |" in content
    assert "_secret" not in content
    assert "`debug`" not in content
    assert "_token" not in content


def test_cli_report_json_output_respects_selected_categories(
    sample_module: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = main(
        [
            str(sample_module),
            "--report",
            "--report-format",
            "json",
            "--report-categories",
            "modules,params",
        ]
    )

    assert result == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["summary"]["selected_categories"] == ["modules", "params"]
    assert sorted(payload["counts"]) == ["modules", "params"]
    assert sorted(payload["findings"]) == ["modules", "params"]


def test_cli_report_fail_on_selected_categories(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_fail.py"
    module.write_text(
        '''"""Coverage fail sample."""

def helper(value: int, other: int) -> None:
    """Help with something.

    Args:
        value: First value.
    """
''',
        encoding="utf-8",
    )

    assert main([str(module), "--report", "--fail-on", "modules"]) == 0
    capsys.readouterr()

    result = main([str(module), "--report", "--fail-on", "params"])

    assert result == 1
    assert "Parameters missing descriptions: 1" in capsys.readouterr().out


def test_cli_report_fail_on_any(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_any.py"
    module.write_text("def helper() -> None:\n    pass\n", encoding="utf-8")

    result = main([str(module), "--report", "--fail-on", "any"])

    assert result == 1
    assert "Modules without docstrings: 1" in capsys.readouterr().out


def test_cli_report_fail_under(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    module = tmp_path / "coverage_threshold.py"
    module.write_text(
        '''"""Coverage threshold sample."""

def helper(value: int, other: int) -> None:
    """Help with something.

    Args:
        value: First value.
    """
''',
        encoding="utf-8",
    )

    assert main([str(module), "--report", "--fail-under", "70"]) == 0
    capsys.readouterr()

    result = main([str(module), "--report", "--fail-under", "80"])

    assert result == 1
    assert "Overall coverage:" in capsys.readouterr().out


def test_cli_report_writes_output_file(
    sample_module: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    report_path = tmp_path / "reports" / "coverage.json"

    result = main(
        [
            str(sample_module),
            "--report",
            "--report-format",
            "json",
            "--report-output",
            str(report_path),
        ]
    )

    assert result == 0
    stdout_payload = json.loads(capsys.readouterr().out)
    file_payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert stdout_payload == file_payload
    assert file_payload["summary"]["overall_percentage"] == 75.0


def test_cli_report_rejects_invalid_fail_on(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report", "--fail-on", "widgets"])

    assert result == 1
    assert "Unsupported --fail-on categories" in caplog.text


def test_cli_report_rejects_invalid_report_categories(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report", "--report-categories", "widgets"])

    assert result == 1
    assert "Unsupported --report-categories values" in caplog.text


def test_cli_fail_on_requires_report(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--fail-on", "modules"])

    assert result == 1
    assert "--fail-on can be used only with --report." in caplog.text


def test_cli_report_format_requires_report(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report-format", "json"])

    assert result == 1
    assert "--report-format can be used only with --report." in caplog.text


def test_cli_report_output_requires_report(
    sample_module: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report-output", str(tmp_path / "report.txt")])

    assert result == 1
    assert "--report-output can be used only with --report." in caplog.text


def test_cli_fail_under_requires_report(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--fail-under", "90"])

    assert result == 1
    assert "--fail-under can be used only with --report." in caplog.text


def test_cli_report_categories_requires_report(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report-categories", "modules,params"])

    assert result == 1
    assert "--report-categories can be used only with --report." in caplog.text


def test_cli_report_summary_only_requires_report(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report-summary-only"])

    assert result == 1
    assert "--report-summary-only can be used only with --report." in caplog.text


def test_cli_report_rejects_invalid_fail_under(
    sample_module: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        result = main([str(sample_module), "--report", "--fail-under", "120"])

    assert result == 1
    assert "--fail-under must be between 0 and 100." in caplog.text


@pytest.mark.parametrize(
    "flag",
    ["--watch", "--readme", "--nav", "--single-file", "--check", "--prune"],
)
def test_cli_report_rejects_incompatible_flags(
    sample_module: Path,
    tmp_path: Path,
    flag: str,
) -> None:
    args = [str(sample_module), "--report", flag]
    if flag == "--readme":
        args.extend(["--readme-path", str(tmp_path / "README.md")])
    if flag == "--single-file":
        args.extend(["-o", str(tmp_path / "combined.md")])
    elif flag in {"--nav", "--prune"}:
        args.extend(["-o", str(tmp_path / "docs")])

    result = main(args)

    assert result == 1


def test_cli_init_invalid_toml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text("not valid toml {{{", encoding="utf-8")
    result = main(["--init"])
    assert result == 1
