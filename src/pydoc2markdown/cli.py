"""Command-line interface for PyDoc2Markdown."""

import argparse
import sys
from pathlib import Path

from pydoc2markdown.core.generator import MarkdownGenerator
from pydoc2markdown.core.parser import DocstringParser


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
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )
    return parser


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.source.exists():
        print(f"Error: Source path does not exist: {parsed_args.source}", file=sys.stderr)
        return 1

    doc_parser = DocstringParser()
    md_generator = MarkdownGenerator(template_path=parsed_args.template)

    try:
        modules = doc_parser.parse(
            source=parsed_args.source,
            recursive=parsed_args.recursive,
        )
        md_generator.generate(
            modules=modules,
            output_dir=parsed_args.output,
        )
        print(f"Documentation generated successfully in {parsed_args.output}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
