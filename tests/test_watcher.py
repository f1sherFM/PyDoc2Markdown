"""Tests for watch mode error paths."""

import builtins
import json
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from pydoc2markdown.core.watcher import watch_and_generate


def _install_idle_watchdog(monkeypatch: pytest.MonkeyPatch) -> None:
    events_module = cast(Any, ModuleType("watchdog.events"))
    observers_module = cast(Any, ModuleType("watchdog.observers"))

    class FakeFileSystemEvent:
        is_directory = False
        src_path = ""

    class FakeFileSystemEventHandler:
        pass

    class FakeObserver:
        def schedule(self, *_args: object, **_kwargs: object) -> None:
            pass

        def start(self) -> None:
            pass

        def is_alive(self) -> bool:
            return False

        def join(self, _timeout: float | None = None) -> None:
            pass

        def stop(self) -> None:
            pass

    events_module.FileSystemEvent = FakeFileSystemEvent
    events_module.FileSystemEventHandler = FakeFileSystemEventHandler
    observers_module.Observer = FakeObserver

    monkeypatch.setitem(sys.modules, "watchdog.events", events_module)
    monkeypatch.setitem(sys.modules, "watchdog.observers", observers_module)


def test_watch_and_generate_missing_watchdog(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    real_import = builtins.__import__

    def _fake_import(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name.startswith("watchdog"):
            raise ImportError("watchdog is unavailable")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _fake_import)

    with caplog.at_level(logging.ERROR):
        result = watch_and_generate(
            source=tmp_path,
            output_dir=tmp_path / "docs",
            recursive=False,
            theme="default",
            template_path=None,
        )

    assert result == 1
    assert "watchdog is required for --watch" in caplog.text


def test_watch_and_generate_initial_generation_failure_is_logged(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    events_module = cast(Any, ModuleType("watchdog.events"))
    observers_module = cast(Any, ModuleType("watchdog.observers"))

    class FakeFileSystemEvent:
        is_directory = False
        src_path = ""

    class FakeFileSystemEventHandler:
        pass

    class FakeObserver:
        def schedule(self, *_args: object, **_kwargs: object) -> None:
            pass

        def start(self) -> None:
            pass

        def is_alive(self) -> bool:
            return False

        def join(self, _timeout: float | None = None) -> None:
            pass

        def stop(self) -> None:
            pass

    events_module.FileSystemEvent = FakeFileSystemEvent
    events_module.FileSystemEventHandler = FakeFileSystemEventHandler
    observers_module.Observer = FakeObserver

    monkeypatch.setitem(sys.modules, "watchdog.events", events_module)
    monkeypatch.setitem(sys.modules, "watchdog.observers", observers_module)

    with caplog.at_level(logging.ERROR):
        result = watch_and_generate(
            source=tmp_path / "missing.py",
            output_dir=tmp_path / "docs",
            recursive=False,
            theme="default",
            template_path=None,
        )

    assert result == 0
    assert "Initial generation failed" in caplog.text


def test_watch_and_generate_schedules_with_recursive_flag(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events_module = cast(Any, ModuleType("watchdog.events"))
    observers_module = cast(Any, ModuleType("watchdog.observers"))
    scheduled: dict[str, object] = {}

    class FakeFileSystemEvent:
        is_directory = False
        src_path = ""

    class FakeFileSystemEventHandler:
        pass

    class FakeObserver:
        def schedule(self, handler: object, path: str, *, recursive: bool) -> None:
            scheduled["handler"] = handler
            scheduled["path"] = path
            scheduled["recursive"] = recursive

        def start(self) -> None:
            pass

        def is_alive(self) -> bool:
            return False

        def join(self, _timeout: float | None = None) -> None:
            pass

        def stop(self) -> None:
            pass

    events_module.FileSystemEvent = FakeFileSystemEvent
    events_module.FileSystemEventHandler = FakeFileSystemEventHandler
    observers_module.Observer = FakeObserver

    source = tmp_path / "pkg"
    source.mkdir()
    (source / "module.py").write_text('"""Module."""\n', encoding="utf-8")

    monkeypatch.setitem(sys.modules, "watchdog.events", events_module)
    monkeypatch.setitem(sys.modules, "watchdog.observers", observers_module)

    result = watch_and_generate(
        source=source,
        output_dir=tmp_path / "docs",
        recursive=False,
        theme="default",
        template_path=None,
    )

    assert result == 0
    assert scheduled["path"] == str(source)
    assert scheduled["recursive"] is False


def test_watch_and_generate_writes_prune_manifest(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_idle_watchdog(monkeypatch)
    source = tmp_path / "src"
    source.mkdir()
    (source / "module.py").write_text('"""Module docs."""\n', encoding="utf-8")
    output_dir = tmp_path / "docs"

    result = watch_and_generate(
        source=source,
        output_dir=output_dir,
        recursive=True,
        theme="default",
        template_path=None,
    )

    manifest = json.loads((output_dir / ".pydoc2markdown.json").read_text(encoding="utf-8"))
    assert result == 0
    assert manifest["single_file"] is False
    assert set(manifest["files"]) == {"index.md", "module.md"}


def test_watch_and_generate_readme_links_to_navigation_docs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_idle_watchdog(monkeypatch)
    source = tmp_path / "src"
    source.mkdir()
    (source / "module.py").write_text(
        '''"""Module docs."""

class Widget:
    """Example widget."""
''',
        encoding="utf-8",
    )
    output_dir = tmp_path / "docs"
    readme_path = tmp_path / "README.md"

    result = watch_and_generate(
        source=source,
        output_dir=output_dir,
        recursive=True,
        theme="default",
        template_path=None,
        readme_path=readme_path,
        navigation=True,
    )

    content = readme_path.read_text(encoding="utf-8")
    assert result == 0
    assert "### [`module`](docs/api/module.md)" in content
    assert "### `module`" not in content


def test_watch_and_generate_debounces_file_events(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events_module = cast(Any, ModuleType("watchdog.events"))
    observers_module = cast(Any, ModuleType("watchdog.observers"))
    generated: list[Path] = []
    now = 0.0

    class FakeFileSystemEvent:
        def __init__(self, src_path: str) -> None:
            self.is_directory = False
            self.src_path = src_path

    class FakeFileSystemEventHandler:
        pass

    class FakeObserver:
        def __init__(self) -> None:
            self.handler: Any | None = None
            self._alive_calls = 0

        def schedule(self, handler: object, _path: str, *, recursive: bool) -> None:
            self.handler = handler

        def start(self) -> None:
            assert self.handler is not None
            self.handler.on_any_event(FakeFileSystemEvent(str(tmp_path / "one.py")))
            self.handler.on_any_event(FakeFileSystemEvent(str(tmp_path / "two.py")))

        def is_alive(self) -> bool:
            self._alive_calls += 1
            return self._alive_calls <= 2

        def join(self, _timeout: float | None = None) -> None:
            nonlocal now
            now += 0.5

        def stop(self) -> None:
            pass

    class FakeParser:
        def __init__(self, *, inherit_docstrings: bool = False) -> None:
            self.inherit_docstrings = inherit_docstrings

        def parse(
            self,
            source: Path,
            recursive: bool,
            include: list[str] | None = None,
            exclude: list[str] | None = None,
        ) -> list[object]:
            return [object()]

    class FakeGenerator:
        def __init__(self, **_kwargs: object) -> None:
            pass

        def generate(self, modules: list[object], output_dir: Path) -> list[Path]:
            generated.append(output_dir)
            return []

    events_module.FileSystemEvent = FakeFileSystemEvent
    events_module.FileSystemEventHandler = FakeFileSystemEventHandler
    observers_module.Observer = FakeObserver

    monkeypatch.setitem(sys.modules, "watchdog.events", events_module)
    monkeypatch.setitem(sys.modules, "watchdog.observers", observers_module)
    monkeypatch.setattr("time.monotonic", lambda: now)
    monkeypatch.setattr("pydoc2markdown.core.parser.DocstringParser", FakeParser)
    monkeypatch.setattr("pydoc2markdown.core.generator.MarkdownGenerator", FakeGenerator)

    result = watch_and_generate(
        source=tmp_path,
        output_dir=tmp_path / "docs",
        recursive=True,
        theme="default",
        template_path=None,
    )

    assert result == 0
    assert generated == [tmp_path / "docs", tmp_path / "docs"]
