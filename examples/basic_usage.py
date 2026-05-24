"""Basic usage example for PyDoc2Markdown library API."""

from pathlib import Path

from pydoc2markdown import DocstringParser, MarkdownGenerator


def main() -> None:
    # Path to your Python package or module
    source = Path("src/my_awesome_project")

    # Parse docstrings from source files
    parser = DocstringParser()
    modules = parser.parse(source, recursive=True)
    print(f"Parsed {len(modules)} module(s)")

    # Generate Markdown documentation
    output_dir = Path("docs")
    generator = MarkdownGenerator()
    generated = generator.generate(modules, output_dir)
    print(f"Generated {len(generated)} Markdown file(s) in {output_dir}")

    # Or generate a single module as a string
    if modules:
        md_content = generator.generate_string(modules[0])
        print("\n--- Sample output ---\n")
        print(md_content[:500])


if __name__ == "__main__":
    main()
