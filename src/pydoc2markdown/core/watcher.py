"""File watcher for auto-regenerating documentation."""

import logging
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_DEBOUNCE_SECONDS = 0.25


def watch_and_generate(
    source: Path,
    output_dir: Path,
    recursive: bool,
    theme: str,
    template_path: Path | None,
    single_file: bool = False,
    readme_path: Path | None = None,
    navigation: bool = False,
    api_dir: Path = Path("api"),
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    source_link_template: str | None = None,
) -> int:
    """Watch source files and regenerate docs on change.

    Args:
        source: Path to Python file or directory.
        output_dir: Output directory for Markdown files.
        recursive: Whether to scan subdirectories recursively.
        theme: Built-in theme name.
        template_path: Optional custom template path.
        readme_path: Optional README path to update with an API reference.
        navigation: Whether to generate the navigation-first docs layout.
        api_dir: Directory for API pages when navigation is enabled.
        include: Optional glob patterns for files to include.
        exclude: Optional glob patterns for files to exclude.
        source_link_template: Optional URL template for source links.

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
        source_link_template=source_link_template,
    )
    parser = DocstringParser()

    def _generate_docs(message: str) -> None:
        modules = parser.parse(
            source,
            recursive=recursive,
            include=include,
            exclude=exclude,
        )
        if single_file:
            generator.generate_single_file(modules, output_dir)
        elif navigation:
            generator.generate_navigation(modules, output_dir, api_dir)
        else:
            generator.generate(modules, output_dir)
        if readme_path:
            generator.update_readme(modules, readme_path)
        logger.info(message, output_dir)

    class _RebuildHandler(FileSystemEventHandler):
        def __init__(self) -> None:
            self._pending_since: float | None = None

        def on_any_event(self, event: FileSystemEvent) -> None:
            if event.is_directory:
                return
            src = getattr(event, "src_path", "")
            if isinstance(src, str) and not src.endswith(".py"):
                return
            self._pending_since = time.monotonic()
            logger.debug("Change detected, scheduling docs regeneration...")

        def maybe_rebuild(self) -> None:
            if self._pending_since is None:
                return
            if time.monotonic() - self._pending_since < _DEBOUNCE_SECONDS:
                return
            self._pending_since = None
            logger.info("Change detected, regenerating docs...")
            try:
                _generate_docs("Docs regenerated in %s")
            except Exception:
                logger.exception("Regeneration failed")

    handler = _RebuildHandler()
    watch_path = source if source.is_dir() else source.parent
    observer = Observer()
    observer.schedule(handler, str(watch_path), recursive=recursive if source.is_dir() else False)
    observer.start()

    logger.info("Watching %s for changes. Press Ctrl+C to stop.", watch_path)

    # Generate once before watching
    try:
        _generate_docs("Initial docs generated in %s")
    except Exception:
        logger.exception("Initial generation failed")

    try:
        while observer.is_alive():
            observer.join(_DEBOUNCE_SECONDS)
            handler.maybe_rebuild()
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
    finally:
        observer.stop()
        observer.join()

    return 0
