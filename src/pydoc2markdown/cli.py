"""Command-line interface for PyDoc2Markdown."""

import argparse
import logging
import sys
from pathlib import Path

from pydoc2markdown import __version__
from pydoc2markdown.core.config import load_config
from pydoc2markdown.core.generator import MarkdownGenerator
from pydoc2markdown.core.parser import DocstringParser
from pydoc2markdown.core.watcher import watch_and_generate

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = """[tool.pydoc2markdown]
output = "docs"
theme = "default"
recursive = true
"""


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    defaults = load_config()
    parser = argparse.ArgumentParser(
        prog="pydoc2markdown",
        description="Convert Python docstrings to Markdown documentation.",
    )
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Path to a Python file or directory to process.",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        default=False,
        help="Create or update [tool.pydoc2markdown] in pyproject.toml.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(str(defaults.get("output", "docs"))),
        help="Output directory (or file when --single-file is used).",
    )
    parser.add_argument(
        "--single-file",
        action="store_true",
        default=False,
        help="Generate a single combined Markdown file instead of separate files.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        default=defaults.get("recursive", False),
        help="Recursively process subdirectories.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to a custom Jinja2 template for Markdown generation.",
    )
    parser.add_argument(
        "--theme",
        choices=["default", "minimal"],
        default=defaults.get("theme", "default"),
        help="Built-in theme/template to use (default: default).",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch source files and regenerate docs on change.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def _setup_logging(verbosity: int) -> None:
    """Configure logging level based on verbosity count."""
    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO
    logging.basicConfig(
        level=level,
        format="%(name)s - %(levelname)s - %(message)s",
    )


def init_config() -> int:
    """Create or update [tool.pydoc2markdown] in pyproject.toml.

    Returns:
        0 on success, 1 on error.
    """
    try:
        import tomllib
    except ModuleNotFoundError:
        import tomli as tomllib

    pyproject = Path.cwd() / "pyproject.toml"

    if not pyproject.exists():
        # Create minimal pyproject.toml with just our section
        pyproject.write_text(_DEFAULT_CONFIG, encoding="utf-8")
        logger.info("Created pyproject.toml with [tool.pydoc2markdown] defaults.")
        return 0

    # File exists — parse it
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
    except Exception:
        logger.error("Failed to parse pyproject.toml — file exists but is not valid TOML.")
        return 1

    # Check if section already exists
    if "tool" in data and "pydoc2markdown" in data["tool"]:
        logger.info(
            "[tool.pydoc2markdown] already exists in pyproject.toml — nothing to change. "
            "Edit it manually if you want to override defaults."
        )
        return 0

    # Section doesn't exist — append it
    existing = pyproject.read_text(encoding="utf-8")
    if existing and not existing.endswith("\n"):
        existing += "\n"
    existing += "\n" + _DEFAULT_CONFIG
    pyproject.write_text(existing, encoding="utf-8")
    logger.info("Added [tool.pydoc2markdown] to existing pyproject.toml.")
    return 0


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    _setup_logging(parsed_args.verbose)

    if parsed_args.init:
        return init_config()

    if parsed_args.source is None:
        parser.error("the following arguments are required: source")

    if not parsed_args.source.exists():
        logger.error("Source path does not exist: %s", parsed_args.source)
        return 1

    if parsed_args.watch:
        return watch_and_generate(
            source=parsed_args.source,
            output_dir=parsed_args.output,
            recursive=parsed_args.recursive,
            theme=parsed_args.theme,
            template_path=parsed_args.template,
            single_file=parsed_args.single_file,
        )

    logger.info("Parsing source: %s (recursive=%s)", parsed_args.source, parsed_args.recursive)
    doc_parser = DocstringParser()
    md_generator = MarkdownGenerator(
        template_path=parsed_args.template,
        theme=parsed_args.theme,
    )

    try:
        modules = doc_parser.parse(
            source=parsed_args.source,
            recursive=parsed_args.recursive,
        )
        logger.info("Parsed %d module(s)", len(modules))
        if parsed_args.single_file:
            single_path = md_generator.generate_single_file(
                modules=modules,
                output_path=parsed_args.output,
            )
            logger.info("Generated single Markdown file: %s", single_path)
        else:
            generated = md_generator.generate(
                modules=modules,
                output_dir=parsed_args.output,
            )
            logger.info("Generated %d Markdown file(s) in %s", len(generated), parsed_args.output)
    except Exception:
        logger.exception("Documentation generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
