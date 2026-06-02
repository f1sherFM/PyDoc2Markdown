"""Markdown documentation generator."""

import logging
from collections.abc import Iterable
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from pydoc2markdown.core.parser import ModuleDoc

logger = logging.getLogger(__name__)

README_START_MARKER = "<!-- pydoc2markdown:start -->"
README_END_MARKER = "<!-- pydoc2markdown:end -->"


def _write_markdown_lines(path: Path, lines: list[str]) -> None:
    """Write Markdown lines with a final newline."""
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class MarkdownGenerator:
    """Generate Markdown files from parsed Python documentation."""

    def __init__(
        self,
        template_path: Path | None = None,
        theme: str = "default",
    ) -> None:
        """Initialize the generator with an optional custom template or theme."""
        self._template_path = template_path
        self._theme = theme
        self._env = self._create_environment()

    def _create_environment(self) -> Environment:
        """Create and configure the Jinja2 environment."""
        from pydoc2markdown.core.type_hints import format_type_hint

        if self._template_path and self._template_path.exists():
            env = Environment(
                loader=FileSystemLoader(str(self._template_path.parent)),
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        else:
            env = Environment(
                loader=PackageLoader("pydoc2markdown", "templates"),
                autoescape=select_autoescape(),
                trim_blocks=True,
                lstrip_blocks=True,
            )
        from pydoc2markdown.core.crossref import link_type_filter

        env.filters["format_type_hint"] = format_type_hint
        env.filters["link_type"] = link_type_filter
        return env

    def _resolve_template_name(self) -> str:
        """Resolve the template file name based on theme or custom path."""
        if self._template_path:
            return self._template_path.name
        if self._theme == "default":
            return "module.md"
        return f"{self._theme}.md"

    def generate(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
    ) -> list[Path]:
        """Generate Markdown files for the given modules."""
        generated = self._write_module_docs(modules, output_dir)

        index_path = self._generate_index(modules, output_dir)
        if index_path:
            generated.append(index_path)

        return generated

    def generate_navigation(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
        api_dir: Path = Path("api"),
    ) -> list[Path]:
        """Generate a navigation-first docs layout with API pages under api_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = self._write_module_docs(modules, output_dir / api_dir)

        package_pages = self._generate_package_pages(modules, output_dir, api_dir)
        generated.extend(package_pages)

        index_path = self._generate_navigation_index(modules, output_dir, api_dir)
        if index_path:
            generated.append(index_path)

        return generated

    def _write_module_docs(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
    ) -> list[Path]:
        """Render module documentation files into output_dir."""
        from pydoc2markdown.core.crossref import TypeIndex

        output_dir.mkdir(parents=True, exist_ok=True)
        generated: list[Path] = []

        template_name = self._resolve_template_name()
        logger.debug("Using template: %s", template_name)
        template = self._env.get_template(template_name)
        type_index = TypeIndex.from_modules(modules)

        for module in modules:
            output_path = self._module_output_path(module, output_dir)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug("Generating %s", output_path)
            content = template.render(module=module, type_index=type_index)
            output_path.write_text(content, encoding="utf-8")
            generated.append(output_path)

        return generated

    def _module_output_path(self, module: ModuleDoc, output_dir: Path) -> Path:
        """Return the Markdown output path for a module."""
        if module.package:
            return output_dir / module.package.replace(".", "/") / f"{module.name}.md"
        return output_dir / f"{module.name}.md"

    def _module_link(self, module: ModuleDoc, api_dir: Path) -> str:
        """Return a POSIX-style relative link to a module API page."""
        return self._module_output_path(module, api_dir).as_posix()

    def _public_modules(self, modules: Iterable[ModuleDoc]) -> list[ModuleDoc]:
        """Return modules that should be shown in indexes."""
        return sorted(
            (module for module in modules if module.name != "__init__"),
            key=lambda m: (m.package, m.name),
        )

    def _generate_index(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
    ) -> Path | None:
        """Generate an index.md with links to all module docs, grouped by package."""
        if not modules:
            return None

        from collections import OrderedDict

        groups: OrderedDict[str, list[ModuleDoc]] = OrderedDict()
        for module in sorted(modules, key=lambda m: (m.package, m.name)):
            groups.setdefault(module.package, []).append(module)

        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) for m in modules)

        lines = ["# Documentation Index", ""]
        lines.append(
            f"**Overview:** {len(modules)} modules, "
            f"{total_classes} classes, "
            f"{total_functions} functions."
        )
        lines.append("")

        for package, mods in groups.items():
            if package:
                lines.append(f"## Package `{package}`")
                # Try to find __init__ module for package description
                init_mod = next((m for m in mods if m.name == "__init__"), None)
                if init_mod and init_mod.docstring:
                    first_line = init_mod.docstring.strip().split("\n")[0]
                    lines.append(f"\n{first_line}\n")
            else:
                lines.append("## Modules")
                lines.append("")

            for module in mods:
                if module.name == "__init__":
                    continue
                rel_path = (
                    f"{module.package.replace('.', '/')}/{module.name}.md"
                    if module.package
                    else f"{module.name}.md"
                )
                stats_parts: list[str] = []
                if module.classes:
                    stats_parts.append(f"{len(module.classes)} class(es)")
                if module.functions:
                    stats_parts.append(f"{len(module.functions)} function(s)")
                stats = f" — {', '.join(stats_parts)}" if stats_parts else ""
                lines.append(f"- [{module.name}]({rel_path}){stats}")
                if module.docstring:
                    first_line = module.docstring.strip().split("\n")[0]
                    lines.append(f"  > {first_line}")
            lines.append("")

        index_path = output_dir / "index.md"
        logger.debug("Generating %s", index_path)
        _write_markdown_lines(index_path, lines)
        return index_path

    def _generate_navigation_index(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
        api_dir: Path,
    ) -> Path | None:
        """Generate a navigation landing page for docs output."""
        public_modules = self._public_modules(modules)
        if not public_modules:
            return None

        package_pages = self._package_page_map(public_modules)
        total_classes = sum(len(m.classes) for m in modules)
        total_functions = sum(len(m.functions) for m in modules)

        lines = ["# Documentation", ""]
        lines.append(
            f"**Overview:** {len(public_modules)} modules, "
            f"{total_classes} classes, "
            f"{total_functions} functions."
        )
        lines.append("")
        lines.append("## Navigation")
        lines.append("")
        for package_name, page_name in package_pages.items():
            label = package_name or "Modules"
            lines.append(f"- [{label}]({page_name})")
        lines.append("")
        lines.append("## API Reference")
        lines.append("")

        for module in public_modules:
            stats = self._module_stats(module)
            package_prefix = f"{module.package}." if module.package else ""
            lines.append(
                f"- [`{package_prefix}{module.name}`]({self._module_link(module, api_dir)}){stats}"
            )
            if module.docstring:
                lines.append(f"  > {self._first_doc_line(module)}")

        index_path = output_dir / "index.md"
        logger.debug("Generating %s", index_path)
        _write_markdown_lines(index_path, lines)
        return index_path

    def _generate_package_pages(
        self,
        modules: list[ModuleDoc],
        output_dir: Path,
        api_dir: Path,
    ) -> list[Path]:
        """Generate package landing pages for navigation output."""
        public_modules = self._public_modules(modules)
        if not public_modules:
            return []

        pages: list[Path] = []
        groups: dict[str, list[ModuleDoc]] = {}
        for module in public_modules:
            groups.setdefault(self._top_level_package(module), []).append(module)

        for package_name, page_name in self._package_page_map(public_modules).items():
            package_modules = groups[package_name]
            title = package_name or "Modules"
            lines = [f"# {title}", ""]
            lines.append(
                f"**Overview:** {len(package_modules)} modules, "
                f"{sum(len(m.classes) for m in package_modules)} classes, "
                f"{sum(len(m.functions) for m in package_modules)} functions."
            )
            lines.append("")
            lines.append("## Modules")
            lines.append("")

            for module in package_modules:
                stats = self._module_stats(module)
                package_prefix = f"{module.package}." if module.package else ""
                lines.append(
                    f"- [`{package_prefix}{module.name}`]({self._module_link(module, api_dir)})"
                    f"{stats}"
                )
                if module.docstring:
                    lines.append(f"  > {self._first_doc_line(module)}")

            page_path = output_dir / page_name
            logger.debug("Generating %s", page_path)
            _write_markdown_lines(page_path, lines)
            pages.append(page_path)

        return pages

    def _package_page_map(self, modules: list[ModuleDoc]) -> dict[str, str]:
        """Return top-level package names mapped to navigation page names."""
        package_names = sorted({self._top_level_package(module) for module in modules})
        return {
            package_name: f"{package_name}.md" if package_name else "modules.md"
            for package_name in package_names
        }

    def _top_level_package(self, module: ModuleDoc) -> str:
        """Return the top-level package label for a module."""
        if module.package:
            return module.package.split(".", 1)[0]
        return ""

    def _module_stats(self, module: ModuleDoc) -> str:
        """Return compact class/function counts for navigation links."""
        stats_parts: list[str] = []
        if module.classes:
            stats_parts.append(f"{len(module.classes)} class(es)")
        if module.functions:
            stats_parts.append(f"{len(module.functions)} function(s)")
        return f" — {', '.join(stats_parts)}" if stats_parts else ""

    def _first_doc_line(self, module: ModuleDoc) -> str:
        """Return the first line of a module docstring."""
        return module.docstring.strip().split("\n")[0] if module.docstring else ""

    def _generate_api_summary(self, modules: list[ModuleDoc]) -> str:
        """Generate a compact API summary suitable for README files."""
        lines = [README_START_MARKER, "", "_Generated by PyDoc2Markdown._", ""]

        for module in sorted(modules, key=lambda m: (m.package, m.name)):
            if module.name == "__init__":
                continue

            module_name = f"{module.package}.{module.name}" if module.package else module.name
            lines.append(f"### `{module_name}`")
            lines.append("")

            if module.docstring:
                lines.append(module.docstring.strip().split("\n")[0])
                lines.append("")

            if module.classes:
                lines.append("**Classes:**")
                for class_doc in module.classes:
                    lines.append(f"- `{class_doc.name}`")
                lines.append("")

            if module.functions:
                lines.append("**Functions:**")
                for func_doc in module.functions:
                    lines.append(f"- `{func_doc.name}`")
                lines.append("")

        lines.append(README_END_MARKER)
        return "\n".join(lines)

    def update_readme(
        self,
        modules: list[ModuleDoc],
        readme_path: Path,
    ) -> Path:
        """Create or update the generated API section in a README file."""
        generated = self._generate_api_summary(modules)
        section = f"## API Reference\n\n{generated}\n"

        if not readme_path.exists():
            readme_path.parent.mkdir(parents=True, exist_ok=True)
            readme_path.write_text(f"# API Reference\n\n{generated}\n", encoding="utf-8")
            logger.info("Created README API reference: %s", readme_path)
            return readme_path

        content = readme_path.read_text(encoding="utf-8")
        has_start_marker = README_START_MARKER in content
        has_end_marker = README_END_MARKER in content
        if has_start_marker != has_end_marker:
            msg = (
                "README contains only one PyDoc2Markdown marker; "
                "add both markers or remove the partial block."
            )
            raise ValueError(msg)

        if has_start_marker and has_end_marker:
            start = content.index(README_START_MARKER)
            end = content.index(README_END_MARKER) + len(README_END_MARKER)
            updated = content[:start] + generated + content[end:]
        else:
            separator = "" if not content or content.endswith("\n") else "\n"
            updated = f"{content}{separator}\n{section}"

        readme_path.write_text(updated, encoding="utf-8")
        logger.info("Updated README API reference: %s", readme_path)
        return readme_path

    def generate_single_file(
        self,
        modules: list[ModuleDoc],
        output_path: Path,
    ) -> Path:
        """Generate a single combined Markdown file for all modules.

        Args:
            modules: List of parsed modules.
            output_path: File path for the combined Markdown output.

        Returns:
            Path to the generated file.
        """
        from pydoc2markdown.core.crossref import TypeIndex

        output_path.parent.mkdir(parents=True, exist_ok=True)

        template_name = self._resolve_template_name()
        template = self._env.get_template(template_name)
        type_index = TypeIndex.from_modules(modules)

        lines: list[str] = ["# Documentation", ""]

        # Table of contents for all modules
        if modules:
            lines.append("## Modules")
            for module in sorted(modules, key=lambda m: (m.package, m.name)):
                lines.append(f"- {module.name}")
            lines.append("")

        # Render each module and concatenate
        for module in sorted(modules, key=lambda m: (m.package, m.name)):
            content = template.render(module=module, type_index=type_index)
            lines.append(content)
            lines.append("---")
            lines.append("")

        _write_markdown_lines(output_path, lines)
        logger.info("Generated single file: %s", output_path)
        return output_path

    def generate_string(self, module: ModuleDoc) -> str:
        """Generate Markdown content as a string for a single module."""
        from pydoc2markdown.core.crossref import TypeIndex

        template_name = self._resolve_template_name()
        template = self._env.get_template(template_name)
        type_index = TypeIndex.from_modules([module])
        return template.render(module=module, type_index=type_index)
