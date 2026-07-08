"""Command-line interface for PyDoc2Markdown."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from pydoc2markdown import __version__
from pydoc2markdown.core.config import load_config
from pydoc2markdown.core.doctor import DoctorOptions, format_doctor_report
from pydoc2markdown.core.generator import (
    DEFAULT_README_TITLE,
    README_RENDER_MODES,
    MarkdownGenerator,
    OutputOptions,
)
from pydoc2markdown.core.parser import DocstringParser, ModuleDoc
from pydoc2markdown.core.report import (
    REPORT_CATEGORY_ORDER,
    analyze_modules,
    format_report,
    format_report_json,
)
from pydoc2markdown.core.watcher import watch_and_generate

logger = logging.getLogger(__name__)
_MANIFEST_VERSION = 1
_REPORT_CATEGORIES = REPORT_CATEGORY_ORDER

_DEFAULT_CONFIG = """[tool.pydoc2markdown]
output = "docs"
theme = "default"
recursive = true
show_toc = true
show_source_links = true
compact_sections = false
show_class_metadata = true
show_public_api = true
show_attributes = true
show_returns = true
show_raises = true
show_private_members = false
show_dunder_members = false
public_only = false
inherit_docstrings = false
member_include = []
member_exclude = []
readme_mode = "summary"
readme_title = "API Reference"
"""

_DEMO_FILES = {
    "src/shop_demo/__init__.py": '''"""Small shop demo package for PyDoc2Markdown examples."""

from shop_demo.inventory import Inventory, Product
from shop_demo.orders import Order, OrderStatus, calculate_total

__all__ = [
    "Inventory",
    "Order",
    "OrderStatus",
    "Product",
    "calculate_total",
]
''',
    "src/shop_demo/inventory.py": '''"""Inventory models and helpers for the sample shop."""

from dataclasses import dataclass

__all__ = ["Product", "Inventory"]


@dataclass
class Product:
    """A product available in the shop.

    Args:
        sku: Stable product identifier.
        name: Human-readable product name.
        price: Unit price in the shop currency.
        stock: Number of available units.
    """

    sku: str
    name: str
    price: float
    stock: int = 0

    @property
    def available(self) -> bool:
        """Whether the product can be purchased."""
        return self.stock > 0


class Inventory:
    """In-memory product inventory.

    Args:
        products: Initial products keyed by SKU.
    """

    def __init__(self, products: dict[str, Product] | None = None) -> None:
        self._products = products or {}

    def add(self, product: Product) -> None:
        """Add or replace a product.

        Args:
            product: Product to store.
        """
        self._validate_product(product)
        self._products[product.sku] = product

    def get(self, sku: str) -> Product:
        """Return a product by SKU.

        Args:
            sku: Product identifier.

        Returns:
            Matching product.

        Raises:
            KeyError: If the SKU is unknown.
        """
        return self._products[_coerce_sku(sku)]

    def _validate_product(self, product: Product) -> None:
        """Validate product input before it enters the inventory."""
        if not product.sku:
            raise ValueError("product sku must not be empty")


def _coerce_sku(value: str) -> str:
    """Normalize an SKU key used for in-memory lookups."""
    return value.strip().upper()
''',
    "src/shop_demo/orders.py": '''"""Order models and pricing helpers."""

from dataclasses import dataclass
from enum import Enum

from shop_demo.inventory import Product

__all__ = ["OrderStatus", "Order", "calculate_total"]


class OrderStatus(Enum):
    """Lifecycle status for an order."""

    DRAFT = "draft"
    PAID = "paid"
    SHIPPED = "shipped"


@dataclass
class Order:
    """A customer order.

    Args:
        order_id: Public order identifier.
        items: Products included in the order.
        status: Current order status.
    """

    order_id: str
    items: list[Product]
    status: OrderStatus = OrderStatus.DRAFT

    def mark_paid(self) -> None:
        """Mark the order as paid."""
        self.status = OrderStatus.PAID


def calculate_total(items: list[Product], discount: float = 0.0) -> float:
    """Calculate the discounted order total.

    Args:
        items: Products to include in the total.
        discount: Discount ratio between 0 and 1.

    Returns:
        Total price after discount.

    Raises:
        ValueError: If discount is outside the accepted range.
    """
    discount = _normalize_discount(discount)
    subtotal = sum(item.price for item in items)
    return subtotal * (1 - discount)


def _normalize_discount(value: float) -> float:
    """Validate and normalize a discount ratio."""
    if not 0 <= value <= 1:
        raise ValueError("discount must be between 0 and 1")
    return value
''',
    "README.md": """# PyDoc2Markdown Demo

This small shop package shows what PyDoc2Markdown creates from normal Python
source files and docstrings.

The generated output includes:

- a README API section below
- a browsable docs entrypoint at `docs/index.md`
- per-module API pages under `docs/api/`

Inspect the demo without writing files:

```bash
pydoc2markdown src --recursive --doctor
```

Regenerate the demo docs from this directory with:

```bash
pydoc2markdown src --recursive --nav --readme -o docs
```

Check whether the generated docs are current with:

```bash
pydoc2markdown src --recursive --nav --readme --check -o docs
```

## API Reference

<!-- pydoc2markdown:start -->
<!-- pydoc2markdown:end -->
""",
}


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    defaults = load_config()
    parser = argparse.ArgumentParser(
        prog="pydoc2markdown",
        description=(
            "Convert Python docstrings into Markdown docs, README API sections, "
            "or a navigation-ready docs layout."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  pydoc2markdown src/my_package --recursive -o docs
  pydoc2markdown src/my_package --recursive --nav -o docs
  pydoc2markdown src/my_package --recursive --readme
  pydoc2markdown --demo
  pydoc2markdown --init
""",
    )
    input_group = parser.add_argument_group("Input")
    output_group = parser.add_argument_group("Output")
    readme_group = parser.add_argument_group("README integration")
    config_group = parser.add_argument_group("Configuration")
    demo_group = parser.add_argument_group("Demo")
    analysis_group = parser.add_argument_group("Analysis")
    watch_group = parser.add_argument_group("Watch mode")
    logging_group = parser.add_argument_group("Logging")

    input_group.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="Path to a Python file or directory to process.",
    )
    input_group.add_argument(
        "--recursive",
        action="store_true",
        default=defaults.get("recursive", False),
        help="Recursively process subdirectories.",
    )
    input_group.add_argument(
        "--include",
        default=None,
        help="Comma-separated glob patterns for files to include.",
    )
    input_group.add_argument(
        "--exclude",
        default=None,
        help="Comma-separated glob patterns for files to exclude.",
    )
    config_group.add_argument(
        "--init",
        action="store_true",
        default=False,
        help="Create or update [tool.pydoc2markdown] in pyproject.toml.",
    )
    config_group.add_argument(
        "--template",
        type=Path,
        default=None,
        help="Path to a custom Jinja2 template for Markdown generation.",
    )
    config_group.add_argument(
        "--theme",
        choices=["default", "minimal"],
        default=defaults.get("theme", "default"),
        help="Built-in theme/template to use (default: default).",
    )
    config_group.add_argument(
        "--show-toc",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_toc", True),
        help="Show or hide the module table of contents in built-in output.",
    )
    config_group.add_argument(
        "--show-source-links",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_source_links", True),
        help="Show or hide source links in built-in output.",
    )
    config_group.add_argument(
        "--compact-sections",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "compact_sections", False),
        help="Use a tighter built-in Markdown layout with less section chrome.",
    )
    config_group.add_argument(
        "--show-class-metadata",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_class_metadata", True),
        help="Show or hide built-in class metadata like bases and status markers.",
    )
    config_group.add_argument(
        "--show-public-api",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_public_api", True),
        help="Show or hide the Public API block derived from __all__.",
    )
    config_group.add_argument(
        "--show-attributes",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_attributes", True),
        help="Show or hide built-in attribute and model field tables.",
    )
    config_group.add_argument(
        "--show-returns",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_returns", True),
        help="Show or hide Returns sections in built-in output.",
    )
    config_group.add_argument(
        "--show-raises",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_raises", True),
        help="Show or hide Raises sections in built-in output.",
    )
    config_group.add_argument(
        "--show-private-members",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_private_members", False),
        help="Show or hide private members such as _helper in generated output.",
    )
    config_group.add_argument(
        "--show-dunder-members",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "show_dunder_members", False),
        help="Show or hide dunder members such as __repr__ in generated output.",
    )
    config_group.add_argument(
        "--public-only",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "public_only", False),
        help="When __all__ is present, document only that exported top-level surface.",
    )
    config_group.add_argument(
        "--inherit-docstrings",
        action=argparse.BooleanOptionalAction,
        default=_config_bool(defaults, "inherit_docstrings", False),
        help="Fill missing subclass and override method docs from parsed base classes.",
    )
    config_group.add_argument(
        "--member-include",
        default=",".join(_config_patterns(defaults, "member_include")) or None,
        help=(
            "Comma-separated glob patterns for member names to include, such as "
            "'Widget,public_helper,Client.*,pkg.module.Service.run'."
        ),
    )
    config_group.add_argument(
        "--member-exclude",
        default=",".join(_config_patterns(defaults, "member_exclude")) or None,
        help=(
            "Comma-separated glob patterns for member names to exclude, such as "
            "'*_internal,_debug,Client.__repr__'."
        ),
    )
    demo_group.add_argument(
        "--demo",
        action="store_true",
        default=False,
        help="Create a small demo project and generate docs for it.",
    )
    demo_group.add_argument(
        "--demo-output",
        type=Path,
        default=Path("pydoc2markdown-demo"),
        help="Directory created by --demo.",
    )
    output_group.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(str(defaults.get("output", "docs"))),
        help="Output directory (or file when --single-file is used).",
    )
    output_group.add_argument(
        "--single-file",
        action="store_true",
        default=False,
        help="Generate one combined Markdown file; --output must be a .md file path.",
    )
    output_group.add_argument(
        "--nav",
        action="store_true",
        default=False,
        help="Generate a navigation-first docs layout with API pages under api/.",
    )
    output_group.add_argument(
        "--check",
        action="store_true",
        default=False,
        help="Check whether generated docs are up to date without writing files.",
    )
    output_group.add_argument(
        "--prune",
        action="store_true",
        default=False,
        help="Remove stale generated Markdown files from the output directory.",
    )
    output_group.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview prune actions without deleting files; use with --prune.",
    )
    output_group.add_argument(
        "--api-dir",
        type=Path,
        default=Path("api"),
        help="Directory for API pages when --nav is used.",
    )
    output_group.add_argument(
        "--source-link",
        default=None,
        help="URL template for source links, using {path}, {file}, and {line}.",
    )
    output_group.add_argument(
        "--source-repo",
        default=None,
        help="GitHub repository shorthand for source links, for example user/repo.",
    )
    readme_group.add_argument(
        "--readme",
        action="store_true",
        default=False,
        help="Create or update an API reference section in README.md.",
    )
    readme_group.add_argument(
        "--readme-path",
        type=Path,
        default=Path("README.md"),
        help="Path to the README file updated by --readme.",
    )
    readme_group.add_argument(
        "--readme-mode",
        choices=README_RENDER_MODES,
        default=_config_choice(defaults, "readme_mode", "summary", README_RENDER_MODES),
        help="README rendering mode: summary (default) or detailed.",
    )
    readme_group.add_argument(
        "--readme-title",
        default=_config_string(defaults, "readme_title", DEFAULT_README_TITLE),
        help="Section title used for generated README content.",
    )
    analysis_group.add_argument(
        "--report",
        action="store_true",
        default=False,
        help="Print a documentation coverage report instead of generating Markdown files.",
    )
    analysis_group.add_argument(
        "--doctor",
        action="store_true",
        default=False,
        help="Inspect a project and suggest useful PyDoc2Markdown commands.",
    )
    analysis_group.add_argument(
        "--report-categories",
        default=None,
        help=(
            "Comma-separated report categories to include in output: "
            "modules, classes, functions, public_api, params."
        ),
    )
    analysis_group.add_argument(
        "--report-format",
        choices=["text", "json"],
        default="text",
        help="Output format for --report (default: text).",
    )
    analysis_group.add_argument(
        "--report-output",
        type=Path,
        default=None,
        help="Also write the report output to a file.",
    )
    analysis_group.add_argument(
        "--fail-on",
        default=None,
        help=(
            "Comma-separated report categories that should return exit code 1 when findings "
            "exist. Supported values: modules, classes, functions, public_api, params, any."
        ),
    )
    analysis_group.add_argument(
        "--fail-under",
        type=float,
        default=None,
        help="Return exit code 1 when overall report coverage falls below this percentage.",
    )
    analysis_group.add_argument(
        "--report-summary-only",
        action="store_true",
        default=False,
        help="Print report totals and counts without listing every finding.",
    )
    watch_group.add_argument(
        "--watch",
        action="store_true",
        help="Watch source files and regenerate docs on change.",
    )
    logging_group.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for INFO, -vv for DEBUG).",
    )
    logging_group.add_argument(
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


def _log_cli_error(message: str, *, hint: str | None = None) -> int:
    """Log a user-facing CLI error and optional next step."""
    logger.error(message)
    if hint:
        logger.error("Hint: %s", hint)
    return 1


def _split_patterns(raw: str | None) -> list[str] | None:
    """Split comma-separated CLI glob patterns."""
    if raw is None:
        return None
    patterns = [pattern.strip() for pattern in raw.split(",") if pattern.strip()]
    return patterns or None


def _config_bool(config: dict[str, Any], key: str, default: bool) -> bool:
    """Return a boolean config value or a safe default."""
    value = config.get(key, default)
    return value if isinstance(value, bool) else default


def _config_choice(
    config: dict[str, Any],
    key: str,
    default: str,
    choices: tuple[str, ...],
) -> str:
    """Return a validated string config choice or a safe default."""
    value = config.get(key, default)
    return value if isinstance(value, str) and value in choices else default


def _config_string(
    config: dict[str, Any],
    key: str,
    default: str,
) -> str:
    """Return a validated non-empty string config value or a safe default."""
    value = config.get(key, default)
    return value.strip() if isinstance(value, str) and value.strip() else default


def _config_patterns(config: dict[str, Any], key: str) -> tuple[str, ...]:
    """Return validated member-filtering patterns from config."""
    value = config.get(key)
    if isinstance(value, str):
        return tuple(pattern.strip() for pattern in value.split(",") if pattern.strip())
    if isinstance(value, list):
        return tuple(
            pattern.strip() for pattern in value if isinstance(pattern, str) and pattern.strip()
        )
    return ()


def _output_options_from_args(parsed_args: argparse.Namespace) -> OutputOptions:
    """Build generator output options from parsed CLI arguments."""
    return OutputOptions(
        show_toc=parsed_args.show_toc,
        show_source_links=parsed_args.show_source_links,
        compact_sections=parsed_args.compact_sections,
        show_class_metadata=parsed_args.show_class_metadata,
        show_public_api=parsed_args.show_public_api,
        show_attributes=parsed_args.show_attributes,
        show_returns=parsed_args.show_returns,
        show_raises=parsed_args.show_raises,
        show_private_members=parsed_args.show_private_members,
        show_dunder_members=parsed_args.show_dunder_members,
        public_only=parsed_args.public_only,
        member_include=tuple(_split_patterns(parsed_args.member_include) or ()),
        member_exclude=tuple(_split_patterns(parsed_args.member_exclude) or ()),
    )


def _parse_fail_on(raw: str | None) -> set[str] | None:
    """Parse --fail-on into a validated category set."""
    if raw is None:
        return None

    categories = {value.strip().lower() for value in raw.split(",") if value.strip()}
    if not categories:
        return None
    if "any" in categories:
        return set(_REPORT_CATEGORIES)

    invalid = categories - set(_REPORT_CATEGORIES)
    if invalid:
        invalid_text = ", ".join(sorted(invalid))
        valid_text = ", ".join((*_REPORT_CATEGORIES, "any"))
        raise ValueError(
            f"Unsupported --fail-on categories: {invalid_text}. Supported values: {valid_text}."
        )
    return categories


def _validate_fail_under(value: float | None) -> float | None:
    """Validate --fail-under percentage."""
    if value is None:
        return None
    if 0 <= value <= 100:
        return value
    raise ValueError("--fail-under must be between 0 and 100.")


def _parse_report_categories(raw: str | None) -> tuple[str, ...] | None:
    """Parse --report-categories into a validated ordered category tuple."""
    if raw is None:
        return None

    selected = {value.strip().lower() for value in raw.split(",") if value.strip()}
    if not selected:
        return None

    invalid = selected - set(_REPORT_CATEGORIES)
    if invalid:
        invalid_text = ", ".join(sorted(invalid))
        valid_text = ", ".join(_REPORT_CATEGORIES)
        raise ValueError(
            "Unsupported --report-categories values: "
            f"{invalid_text}. Supported values: {valid_text}."
        )
    return tuple(category for category in _REPORT_CATEGORIES if category in selected)


def _write_report_output(output_path: Path | None, content: str) -> None:
    """Write report output to a file when requested."""
    if output_path is None:
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def _readme_module_links(
    modules: list[ModuleDoc],
    *,
    output: Path,
    readme_path: Path,
    single_file: bool,
    navigation: bool,
    api_dir: Path,
) -> dict[str, str]:
    """Build README links to generated module docs for the current run."""
    if single_file:
        return {}

    links: dict[str, str] = {}
    readme_dir = readme_path.resolve().parent
    docs_root = output / api_dir if navigation else output
    for module in modules:
        if module.name == "__init__":
            continue
        module_name = f"{module.package}.{module.name}" if module.package else module.name
        module_path = (
            docs_root / module.package.replace(".", "/") / f"{module.name}.md"
            if module.package
            else docs_root / f"{module.name}.md"
        )
        links[module_name] = Path(
            os.path.relpath(module_path.resolve(), start=readme_dir)
        ).as_posix()
    return links


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

    # File exists - parse it
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
    except Exception:
        logger.error("Failed to parse pyproject.toml - file exists but is not valid TOML.")
        return 1

    # Check if section already exists
    if "tool" in data and "pydoc2markdown" in data["tool"]:
        logger.info(
            "[tool.pydoc2markdown] already exists in pyproject.toml - nothing to change. "
            "Edit it manually if you want to override defaults."
        )
        return 0

    # Section doesn't exist - append it
    existing = pyproject.read_text(encoding="utf-8")
    if existing and not existing.endswith("\n"):
        existing += "\n"
    existing += "\n" + _DEFAULT_CONFIG
    pyproject.write_text(existing, encoding="utf-8")
    logger.info("Added [tool.pydoc2markdown] to existing pyproject.toml.")
    return 0


def run_demo(output_dir: Path) -> int:
    """Create a demo project and generate documentation for it."""
    if output_dir.exists() and any(output_dir.iterdir()):
        return _log_cli_error(
            f"Demo output directory is not empty: {output_dir}",
            hint="Choose another directory with --demo-output, or remove the existing directory.",
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    for relative_path, content in _DEMO_FILES.items():
        path = output_dir / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    source = output_dir / "src"
    docs = output_dir / "docs"
    readme = output_dir / "README.md"

    modules = DocstringParser().parse(source, recursive=True)
    generator = MarkdownGenerator(
        readme_mode="summary",
        readme_module_links=_readme_module_links(
            modules,
            output=docs,
            readme_path=readme,
            single_file=False,
            navigation=True,
            api_dir=Path("api"),
        ),
    )
    generated = generator.generate_navigation(modules, docs)
    _write_manifest(docs, single_file=False, generated_paths=generated)
    generator.update_readme(modules, readme)

    print(f"Created demo project: {output_dir}")
    print(f"Generated {len(generated)} docs file(s): {docs}")
    print(f"Updated README API section: {readme}")
    print("")
    print("Next steps:")
    print(f"  Inspect the README: {readme}")
    print(f"  Inspect the docs index: {docs / 'index.md'}")
    print("  Regenerate from inside the demo:")
    print("    pydoc2markdown src --recursive --nav --readme -o docs")
    print("  Check freshness from inside the demo:")
    print("    pydoc2markdown src --recursive --nav --readme --check -o docs")
    return 0


def _different_files(
    expected_dir: Path,
    actual_dir: Path,
    expected_paths: list[Path],
) -> list[Path]:
    """Return generated files whose current output is missing or outdated."""
    different: list[Path] = []

    for expected_path in expected_paths:
        relative_path = expected_path.relative_to(expected_dir)
        actual_path = actual_dir / relative_path
        if not actual_path.exists():
            different.append(actual_path)
            continue
        if expected_path.read_text(encoding="utf-8") != actual_path.read_text(encoding="utf-8"):
            different.append(actual_path)

    return different


def _check_readme(
    generator: MarkdownGenerator,
    modules: list[ModuleDoc],
    readme_path: Path,
    temp_dir: Path,
) -> list[Path]:
    """Return README path when its generated API section is missing or outdated."""
    expected_readme = temp_dir / "README.md"
    if readme_path.exists():
        expected_readme.write_text(readme_path.read_text(encoding="utf-8"), encoding="utf-8")

    generator.update_readme(modules, expected_readme)
    if not readme_path.exists():
        return [readme_path]
    if expected_readme.read_text(encoding="utf-8") != readme_path.read_text(encoding="utf-8"):
        return [readme_path]
    return []


def _manifest_path(output: Path, *, single_file: bool) -> Path:
    """Return the manifest path for generated Markdown files."""
    if single_file:
        return output.parent / f".{output.name}.pydoc2markdown.json"
    return output / ".pydoc2markdown.json"


def _write_manifest(output: Path, *, single_file: bool, generated_paths: list[Path]) -> None:
    """Persist generated Markdown paths for future prune operations."""
    manifest_path = _manifest_path(output, single_file=single_file)
    base_dir = output.parent if single_file else output
    payload = {
        "version": _MANIFEST_VERSION,
        "single_file": single_file,
        "files": sorted(str(path.relative_to(base_dir).as_posix()) for path in generated_paths),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _read_manifest(output: Path, *, single_file: bool) -> set[Path]:
    """Load previously generated Markdown paths from the prune manifest."""
    manifest_path = _manifest_path(output, single_file=single_file)
    if not manifest_path.exists():
        return set()

    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logger.warning("Ignoring invalid prune manifest: %s", manifest_path)
        return set()

    if (
        payload.get("version") != _MANIFEST_VERSION
        or payload.get("single_file") is not single_file
        or not isinstance(payload.get("files"), list)
    ):
        logger.warning("Ignoring incompatible prune manifest: %s", manifest_path)
        return set()

    managed_paths: set[Path] = set()
    for value in payload["files"]:
        if isinstance(value, str):
            relative_path = Path(value)
            if _is_safe_relative_path(relative_path):
                managed_paths.add(relative_path)
            else:
                logger.warning("Ignoring unsafe manifest path: %s", value)
    return managed_paths


def _find_stale_managed_files(
    generator: MarkdownGenerator,
    modules: list[ModuleDoc],
    *,
    output: Path,
    single_file: bool,
    navigation: bool,
    api_dir: Path,
) -> list[Path]:
    """Return stale generated Markdown files tracked by the prune manifest."""
    with TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        expected_paths: list[Path] = []
        base_dir = output.parent if single_file else output

        if single_file:
            expected_output = temp_dir / output.name
            generator.generate_single_file(modules, expected_output)
            expected_paths = [expected_output]
        elif navigation:
            expected_output_dir = temp_dir / "docs"
            expected_paths = generator.generate_navigation(
                modules,
                expected_output_dir,
                api_dir=api_dir,
            )
        else:
            expected_output_dir = temp_dir / "docs"
            expected_paths = generator.generate(modules, expected_output_dir)

        if single_file:
            expected_relative_paths = {path.relative_to(temp_dir) for path in expected_paths}
        else:
            expected_relative_paths = {
                path.relative_to(expected_output_dir) for path in expected_paths
            }
        managed_relative_paths = _read_manifest(output, single_file=single_file)

        stale_paths: list[Path] = []
        for relative_path in sorted(managed_relative_paths - expected_relative_paths):
            actual_path = _safe_managed_file(base_dir, relative_path)
            if actual_path is None:
                continue
            if actual_path.exists():
                stale_paths.append(actual_path)

    return stale_paths


def prune_stale_files(
    generator: MarkdownGenerator,
    modules: list[ModuleDoc],
    *,
    output: Path,
    single_file: bool,
    navigation: bool,
    api_dir: Path,
    dry_run: bool,
) -> list[Path]:
    """Remove or preview stale generated Markdown files from the output directory."""
    stale_paths = _find_stale_managed_files(
        generator,
        modules,
        output=output,
        single_file=single_file,
        navigation=navigation,
        api_dir=api_dir,
    )

    if dry_run:
        return stale_paths

    output_root = (output.parent if single_file else output).resolve()
    for stale_path in stale_paths:
        resolved_path = stale_path.resolve()
        if not resolved_path.is_relative_to(output_root) or stale_path.is_symlink():
            logger.warning("Skipping unsafe stale generated file: %s", stale_path)
            continue
        stale_path.unlink()

    return stale_paths


def check_generated_docs(
    generator: MarkdownGenerator,
    modules: list[ModuleDoc],
    *,
    output: Path,
    single_file: bool,
    readme: bool,
    readme_path: Path,
    navigation: bool,
    api_dir: Path,
) -> int:
    """Check whether generated documentation matches the current files."""
    with TemporaryDirectory() as temp_name:
        temp_dir = Path(temp_name)
        stale_paths: list[Path] = []

        if single_file:
            expected_output = temp_dir / output.name
            generator.generate_single_file(modules, expected_output)
            if not output.exists() or (
                expected_output.read_text(encoding="utf-8") != output.read_text(encoding="utf-8")
            ):
                stale_paths.append(output)
        elif navigation:
            expected_output_dir = temp_dir / "docs"
            expected_paths = generator.generate_navigation(
                modules,
                expected_output_dir,
                api_dir=api_dir,
            )
            stale_paths.extend(_different_files(expected_output_dir, output, expected_paths))
            stale_paths.extend(
                _find_stale_managed_files(
                    generator,
                    modules,
                    output=output,
                    single_file=False,
                    navigation=True,
                    api_dir=api_dir,
                )
            )
        else:
            expected_output_dir = temp_dir / "docs"
            expected_paths = generator.generate(modules, expected_output_dir)
            stale_paths.extend(_different_files(expected_output_dir, output, expected_paths))
            stale_paths.extend(
                _find_stale_managed_files(
                    generator,
                    modules,
                    output=output,
                    single_file=False,
                    navigation=False,
                    api_dir=api_dir,
                )
            )

        if readme:
            try:
                stale_paths.extend(_check_readme(generator, modules, readme_path, temp_dir))
            except ValueError as exc:
                return _log_cli_error(
                    str(exc),
                    hint=(
                        "Keep both <!-- pydoc2markdown:start --> and "
                        "<!-- pydoc2markdown:end --> in the README, or remove both markers."
                    ),
                )

    if stale_paths:
        logger.error("Generated documentation is out of date.")
        for path in stale_paths:
            logger.error("Outdated: %s", path)
        logger.error("Run the same command without --check to update generated files.")
        return 1

    logger.info("Generated documentation is up to date.")
    return 0


def _validate_single_file_output(output: Path) -> int:
    """Return a CLI error when --single-file output is not an explicit file path."""
    if output.exists() and output.is_dir():
        return _log_cli_error(
            f"--single-file output points to a directory: {output}",
            hint="Pass a Markdown file path, for example: --single-file -o docs/api.md",
        )
    if output.suffix.lower() not in {".md", ".markdown"}:
        return _log_cli_error(
            "--single-file requires --output to be a Markdown file path.",
            hint="Pass a file path such as -o docs/api.md instead of the default docs directory.",
        )
    return 0


def _is_safe_relative_path(path: Path) -> bool:
    """Return whether path is relative and cannot escape through parent segments."""
    return not path.is_absolute() and ".." not in path.parts


def _safe_managed_file(base_dir: Path, relative_path: Path) -> Path | None:
    """Resolve a managed manifest path only when it stays inside base_dir."""
    if not _is_safe_relative_path(relative_path):
        logger.warning("Ignoring unsafe manifest path: %s", relative_path)
        return None

    output_root = base_dir.resolve()
    actual_path = base_dir / relative_path
    resolved_path = actual_path.resolve()
    if not resolved_path.is_relative_to(output_root):
        logger.warning("Ignoring manifest path outside output directory: %s", relative_path)
        return None
    if actual_path.is_symlink():
        logger.warning("Ignoring symlinked manifest path: %s", relative_path)
        return None
    return actual_path


def _validate_api_dir(api_dir: Path) -> int:
    """Return a CLI error when --api-dir can escape the output directory."""
    if not _is_safe_relative_path(api_dir):
        return _log_cli_error(
            "--api-dir must be a relative path inside --output.",
            hint="Use a path like 'api' or 'reference/api', without '..' or an absolute root.",
        )
    return 0


def _source_link_template(source_link: str | None, source_repo: str | None) -> str | None:
    """Resolve source-link CLI options into a URL template."""
    if source_link and source_repo:
        raise ValueError("--source-link cannot be combined with --source-repo.")
    if source_link:
        return source_link
    if source_repo:
        return f"https://github.com/{source_repo}/blob/main/{{path}}#L{{line}}"
    return None


def main(args: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    _setup_logging(parsed_args.verbose)

    if parsed_args.init:
        return init_config()

    if parsed_args.demo:
        if parsed_args.source is not None:
            return _log_cli_error(
                "--demo does not accept a source path.",
                hint="Run 'pydoc2markdown --demo', or remove --demo to process your own source.",
            )
        return run_demo(parsed_args.demo_output)

    if parsed_args.source is None:
        return _log_cli_error(
            "Missing source path.",
            hint="Run 'pydoc2markdown --help' for examples, or use '--init' to create config.",
        )

    if not parsed_args.source.exists():
        return _log_cli_error(
            f"Source path does not exist: {parsed_args.source}",
            hint=(
                "Pass a Python file or package directory, for example: "
                "pydoc2markdown src --recursive -o docs"
            ),
        )

    if parsed_args.nav and parsed_args.single_file:
        return _log_cli_error(
            "--nav cannot be combined with --single-file.",
            hint="Use --nav for a docs directory, or --single-file for one combined Markdown file.",
        )

    if parsed_args.check and parsed_args.watch:
        return _log_cli_error(
            "--check cannot be combined with --watch.",
            hint="Use --check in CI, or --watch while editing locally.",
        )

    if parsed_args.prune and parsed_args.check:
        return _log_cli_error(
            "--prune cannot be combined with --check.",
            hint="Use --check to detect stale files, or --prune to remove them.",
        )

    if parsed_args.prune and parsed_args.watch:
        return _log_cli_error(
            "--prune cannot be combined with --watch.",
            hint="Use --prune to clean stale files, or --watch for continuous regeneration.",
        )

    if parsed_args.report and parsed_args.watch:
        return _log_cli_error(
            "--report cannot be combined with --watch.",
            hint="Use --report to inspect coverage, or --watch to regenerate files continuously.",
        )

    doctor_conflicts = {
        "--report": parsed_args.report,
        "--watch": parsed_args.watch,
        "--readme": parsed_args.readme,
        "--nav": parsed_args.nav,
        "--single-file": parsed_args.single_file,
        "--check": parsed_args.check,
        "--prune": parsed_args.prune,
    }
    active_doctor_conflicts = [
        flag for flag, enabled in doctor_conflicts.items() if parsed_args.doctor and enabled
    ]
    if active_doctor_conflicts:
        return _log_cli_error(
            f"--doctor cannot be combined with {', '.join(active_doctor_conflicts)}.",
            hint=(
                "Use --doctor for a read-only project diagnosis, or remove it to run another mode."
            ),
        )

    if parsed_args.dry_run and not parsed_args.prune:
        return _log_cli_error(
            "--dry-run currently works only with --prune.",
            hint="Use --prune --dry-run to preview stale generated files without deleting them.",
        )

    if parsed_args.report and parsed_args.readme:
        return _log_cli_error(
            "--report cannot be combined with --readme.",
            hint="Use --report for analysis only, or remove it to update the README.",
        )

    if parsed_args.report and parsed_args.nav:
        return _log_cli_error(
            "--report cannot be combined with --nav.",
            hint="Use --report for analysis only, or remove it to generate navigation docs.",
        )

    if parsed_args.report and parsed_args.single_file:
        return _log_cli_error(
            "--report cannot be combined with --single-file.",
            hint="Use --report for analysis only, or remove it to generate one Markdown file.",
        )

    if parsed_args.report and parsed_args.check:
        return _log_cli_error(
            "--report cannot be combined with --check.",
            hint="Use --report to inspect coverage, or --check to validate generated docs.",
        )

    if parsed_args.report and parsed_args.prune:
        return _log_cli_error(
            "--report cannot be combined with --prune.",
            hint="Use --report to inspect coverage, or --prune to remove stale generated files.",
        )

    if parsed_args.fail_on and not parsed_args.report:
        return _log_cli_error(
            "--fail-on can be used only with --report.",
            hint="Add --report to enable coverage analysis output and failure thresholds.",
        )

    if parsed_args.report_format != "text" and not parsed_args.report:
        return _log_cli_error(
            "--report-format can be used only with --report.",
            hint="Add --report to print a coverage report in text or JSON format.",
        )

    if parsed_args.report_output is not None and not parsed_args.report:
        return _log_cli_error(
            "--report-output can be used only with --report.",
            hint="Add --report to write a coverage report to a file.",
        )

    if parsed_args.fail_under is not None and not parsed_args.report:
        return _log_cli_error(
            "--fail-under can be used only with --report.",
            hint="Add --report to enforce a minimum documentation coverage percentage.",
        )

    if parsed_args.report_categories and not parsed_args.report:
        return _log_cli_error(
            "--report-categories can be used only with --report.",
            hint="Add --report to filter coverage output categories.",
        )

    if parsed_args.report_summary_only and not parsed_args.report:
        return _log_cli_error(
            "--report-summary-only can be used only with --report.",
            hint="Add --report to print a summary-only coverage report.",
        )

    try:
        fail_on_categories = _parse_fail_on(parsed_args.fail_on)
        fail_under = _validate_fail_under(parsed_args.fail_under)
        report_categories = _parse_report_categories(parsed_args.report_categories)
    except ValueError as exc:
        return _log_cli_error(str(exc))

    try:
        source_link_template = _source_link_template(
            parsed_args.source_link,
            parsed_args.source_repo,
        )
    except ValueError as exc:
        return _log_cli_error(str(exc))

    if parsed_args.single_file:
        single_file_error = _validate_single_file_output(parsed_args.output)
        if single_file_error:
            return single_file_error

    if parsed_args.nav:
        api_dir_error = _validate_api_dir(parsed_args.api_dir)
        if api_dir_error:
            return api_dir_error

    if parsed_args.watch:
        return watch_and_generate(
            source=parsed_args.source,
            output_dir=parsed_args.output,
            recursive=parsed_args.recursive,
            theme=parsed_args.theme,
            template_path=parsed_args.template,
            single_file=parsed_args.single_file,
            readme_path=parsed_args.readme_path if parsed_args.readme else None,
            readme_mode=parsed_args.readme_mode,
            readme_title=parsed_args.readme_title,
            navigation=parsed_args.nav,
            api_dir=parsed_args.api_dir,
            include=_split_patterns(parsed_args.include),
            exclude=_split_patterns(parsed_args.exclude),
            source_link_template=source_link_template,
            output_options=_output_options_from_args(parsed_args),
            inherit_docstrings=parsed_args.inherit_docstrings,
        )

    logger.info("Parsing source: %s (recursive=%s)", parsed_args.source, parsed_args.recursive)
    doc_parser = DocstringParser(inherit_docstrings=parsed_args.inherit_docstrings)

    try:
        modules = doc_parser.parse(
            source=parsed_args.source,
            recursive=parsed_args.recursive,
            include=_split_patterns(parsed_args.include),
            exclude=_split_patterns(parsed_args.exclude),
        )
        logger.info("Parsed %d module(s)", len(modules))
        output_options = _output_options_from_args(parsed_args)
        if parsed_args.doctor:
            sys.stdout.write(
                format_doctor_report(
                    modules,
                    DoctorOptions(
                        source=parsed_args.source,
                        recursive=parsed_args.recursive,
                        output=parsed_args.output,
                        readme_path=parsed_args.readme_path,
                        cwd=Path.cwd(),
                        filter_options=output_options,
                    ),
                )
            )
            return 0

        md_generator = MarkdownGenerator(
            template_path=parsed_args.template,
            theme=parsed_args.theme,
            source_link_template=source_link_template,
            output_options=output_options,
            readme_mode=parsed_args.readme_mode,
            readme_title=parsed_args.readme_title,
            readme_module_links=(
                _readme_module_links(
                    modules,
                    output=parsed_args.output,
                    readme_path=parsed_args.readme_path,
                    single_file=parsed_args.single_file,
                    navigation=parsed_args.nav,
                    api_dir=parsed_args.api_dir,
                )
                if parsed_args.readme
                else None
            ),
        )
        if parsed_args.report:
            report = analyze_modules(modules, filter_options=output_options)
            content = (
                format_report_json(report, categories=report_categories)
                if parsed_args.report_format == "json"
                else format_report(
                    report,
                    categories=report_categories,
                    summary_only=parsed_args.report_summary_only,
                )
            )
            sys.stdout.write(content)
            _write_report_output(parsed_args.report_output, content)
            if parsed_args.report_format == "json":
                logger.info("Generated JSON coverage report.")
            if parsed_args.report_output is not None:
                logger.info("Wrote coverage report to %s", parsed_args.report_output)
            if fail_on_categories and report.has_findings(fail_on_categories):
                logger.error("Coverage report failed due to --fail-on conditions.")
                return 1
            if fail_under is not None and report.overall_percentage() < fail_under:
                logger.error(
                    "Coverage report failed: overall coverage %.1f%% is below %.1f%%.",
                    report.overall_percentage(),
                    fail_under,
                )
                return 1
            return 0
        if parsed_args.prune:
            stale_paths = prune_stale_files(
                md_generator,
                modules,
                output=parsed_args.output,
                single_file=parsed_args.single_file,
                navigation=parsed_args.nav,
                api_dir=parsed_args.api_dir,
                dry_run=parsed_args.dry_run,
            )
            if not stale_paths:
                logger.info(
                    "No stale generated files found. "
                    "PyDoc2Markdown only prunes files tracked in its manifest."
                )
            else:
                action = "Would remove" if parsed_args.dry_run else "Removed"
                for stale_path in stale_paths:
                    logger.info("%s stale generated file: %s", action, stale_path)
                suffix = "would be removed" if parsed_args.dry_run else "removed"
                logger.info("%d stale generated file(s) %s.", len(stale_paths), suffix)
            return 0
        if parsed_args.check:
            return check_generated_docs(
                md_generator,
                modules,
                output=parsed_args.output,
                single_file=parsed_args.single_file,
                readme=parsed_args.readme,
                readme_path=parsed_args.readme_path,
                navigation=parsed_args.nav,
                api_dir=parsed_args.api_dir,
            )
        if parsed_args.single_file:
            single_path = md_generator.generate_single_file(
                modules=modules,
                output_path=parsed_args.output,
            )
            _write_manifest(
                parsed_args.output,
                single_file=True,
                generated_paths=[single_path],
            )
            logger.info("Generated single Markdown file: %s", single_path)
        elif parsed_args.nav:
            generated = md_generator.generate_navigation(
                modules=modules,
                output_dir=parsed_args.output,
                api_dir=parsed_args.api_dir,
            )
            _write_manifest(
                parsed_args.output,
                single_file=False,
                generated_paths=generated,
            )
            logger.info(
                "Generated %d navigation docs file(s) in %s",
                len(generated),
                parsed_args.output,
            )
        else:
            generated = md_generator.generate(
                modules=modules,
                output_dir=parsed_args.output,
            )
            _write_manifest(
                parsed_args.output,
                single_file=False,
                generated_paths=generated,
            )
            logger.info("Generated %d Markdown file(s) in %s", len(generated), parsed_args.output)
        if parsed_args.readme:
            try:
                readme_path = md_generator.update_readme(
                    modules=modules,
                    readme_path=parsed_args.readme_path,
                )
            except ValueError as exc:
                return _log_cli_error(
                    str(exc),
                    hint=(
                        "Keep both <!-- pydoc2markdown:start --> and "
                        "<!-- pydoc2markdown:end --> in the README, or remove both markers."
                    ),
                )
            logger.info("Updated README API reference: %s", readme_path)
    except Exception:
        logger.exception("Documentation generation failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
