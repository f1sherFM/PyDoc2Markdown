"""Configuration loader for PyDoc2Markdown."""

import logging
from pathlib import Path
from typing import Any, cast

logger = logging.getLogger(__name__)


def load_config(
    cwd: Path | None = None,
) -> dict[str, Any]:
    """Load [tool.pydoc2markdown] from pyproject.toml.

    Args:
        cwd: Directory to search for pyproject.toml. Defaults to current dir.

    Returns:
        Dictionary with parsed config values.
    """
    import tomllib

    if cwd is None:
        cwd = Path.cwd()

    pyproject = cwd / "pyproject.toml"
    if not pyproject.exists():
        return {}

    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
        return cast(dict[str, Any], data.get("tool", {}).get("pydoc2markdown", {}))
    except Exception:
        logger.warning("Failed to load pyproject.toml config")
        return {}
