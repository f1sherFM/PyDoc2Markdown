"""File watcher for auto-regenerating documentation."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def watch_and_generate(
    source: Path,
    output_dir: Path,
    recursive: bool,
    theme: str,
    template_path: Path | None,
) -> int:
    """Watch source files and regenerate docs on change.

    Args:
        source: Path to Python file or directory.
        output_dir: Output directory for Markdown files.
        recursive: Whether to scan subdirectories recursively.
        theme: Built-in theme name.
        template_path: Optional custom template path.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    try:
        from watchdog.events import FileSystemEvent, FileSystemEventHandler
        from watchdog.observers import Observer
    except ImportError:
        logger.error(
            "watchdog is required for --watch. Install it with: pip install pydoc2markdown[watch]"
        )
        return 1

    from pydoc2markdown.core.generator import MarkdownGenerator
    from pydoc2markdown.core.parser import DocstringParser

    generator = MarkdownGenerator(
        template_path=template_path,
        theme=theme,
    )

    class _RebuildHandler(FileSystemEventHandler):
        def __init__(self) -> None:
            self._parser = DocstringParser()

        def on_any_event(self, event: FileSystemEvent) -> None:
            if event.is_directory:
                return
            src = getattr(event, "src_path", "")
            if isinstance(src, str) and not src.endswith(".py"):
                return
            logger.info("Change detected, regenerating docs...")
            try:
                modules = self._parser.parse(source, recursive=recursive)
                generator.generate(modules, output_dir)
                logger.info("Docs regenerated in %s", output_dir)
            except Exception:
                logger.exception("Regeneration failed")

    handler = _RebuildHandler()
    watch_path = source if source.is_dir() else source.parent
    observer = Observer()
    observer.schedule(handler, str(watch_path), recursive=True)
    observer.start()

    logger.info("Watching %s for changes. Press Ctrl+C to stop.", watch_path)

    # Generate once before watching
    try:
        modules = handler._parser.parse(source, recursive=recursive)
        generator.generate(modules, output_dir)
        logger.info("Initial docs generated in %s", output_dir)
    except Exception:
        logger.exception("Initial generation failed")

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
    finally:
        observer.stop()
        observer.join()

    return 0
