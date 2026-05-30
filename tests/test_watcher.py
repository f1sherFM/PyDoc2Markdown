"""Tests for watch mode error paths."""

import builtins
import logging
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import pytest

from pydoc2markdown.core.watcher import watch_and_generate


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
