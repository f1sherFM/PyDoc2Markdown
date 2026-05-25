"""Command-line interface for PyDoc2Markdown."""

import argparse
import logging
import sys
from pathlib import Path

from pydoc2markdown.core.generator import MarkdownGenerator
from pydoc2markdown.core.parser import DocstringParser

logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog="pydoc2markdown",
        description="Convert Python docstrings to Markdown documentation.",
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Path to a Python file or directory to process.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("docs"),
        help="Output directory for generated Markdown files (default: docs).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively process subdirectories.",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to a custom Jinja2 template for Markdown generation.",
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
        version="%(prog)s 0.1.0",
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


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    _setup_logging(parsed_args.verbose)

    if not parsed_args.source.exists():
        logger.error("Source path does not exist: %s", parsed_args.source)
        return 1

    logger.info("Parsing source: %s (recursive=%s)", parsed_args.source, parsed_args.recursive)
    doc_parser = DocstringParser()
    md_generator = MarkdownGenerator(template_path=parsed_args.template)

    try:
        modules = doc_parser.parse(
            source=parsed_args.source,
            recursive=parsed_args.recursive,
        )
        logger.info("Parsed %d module(s)", len(modules))
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
