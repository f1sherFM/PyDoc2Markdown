"""Helper utilities for PyDoc2Markdown."""

import re


def clean_docstring(docstring: str | None) -> str | None:
    """Clean and normalize a docstring."""
    if not docstring:
        return None
    lines = docstring.expandtabs().splitlines()
    if not lines:
        return None

    # Find minimum indentation
    indent = None
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            line_indent = len(line) - len(stripped)
            if indent is None or line_indent < indent:
                indent = line_indent

    if indent:
        lines[1:] = [line[indent:] for line in lines[1:]]

    return "\n".join(lines).strip()


def slugify(text: str) -> str:
    """Convert text to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)
