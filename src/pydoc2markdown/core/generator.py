"""Markdown documentation generator."""

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from pydoc2markdown.core.parser import ModuleDoc

if TYPE_CHECKING:
    from pydoc2markdown.core.parser import ClassDoc, FunctionDoc

logger = logging.getLogger(__name__)

README_START_MARKER = "<!-- pydoc2markdown:start -->"
README_END_MARKER = "<!-- pydoc2markdown:end -->"
README_RENDER_MODES = ("summary", "detailed")
DEFAULT_README_TITLE = "API Reference"


@dataclass(frozen=True)
class OutputOptions:
    """Rendering options for built-in Markdown output."""

    show_toc: bool = True
    show_source_links: bool = True
    compact_sections: bool = False
    show_class_metadata: bool = True
    show_public_api: bool = True
    show_attributes: bool = True
    show_returns: bool = True
    show_raises: bool = True


def _anchorize(value: str) -> str:
    """Return a Markdown heading-style anchor fragment."""
    return value.lower().replace(" ", "-")


def _write_markdown_lines(path: Path, lines: list[str]) -> None:
    """Write Markdown lines with a final newline."""
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def _normalize_markdown(content: str) -> str:
    """Tighten rendered Markdown spacing without changing semantics."""
    content = content.replace("\r\n", "\n").strip()
    content = re.sub(r"- \[\s*`([^`]+)`\]\((#[^)]+)\)", r"- [`\1`](\2)", content)

    previous = None
    while previous != content:
        previous = content
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = re.sub(r"(^\s*[-*] [^\n]+\n)\n(?=\s*[-*] )", r"\1", content, flags=re.MULTILINE)
        content = re.sub(
            r"(^\s*[-*] [^\n]+\n)\n(?=\s{2,}[-*] )",
            r"\1",
            content,
            flags=re.MULTILINE,
        )
        content = re.sub(r"(\|[^\n]+\|)\n\n(?=\|)", r"\1\n", content)

    return content


def _write_utf8_text(path: Path, content: str) -> None:
    """Write UTF-8 text with LF newlines for stable generated output."""
    path.write_text(content, encoding="utf-8", newline="\n")


class MarkdownGenerator:
    """Generate Markdown files from parsed Python documentation."""

    def __init__(
        self,
        template_path: Path | None = None,
        theme: str = "default",
        source_link_template: str | None = None,
        output_options: OutputOptions | None = None,
        readme_mode: str = "summary",
        readme_title: str = DEFAULT_README_TITLE,
        readme_module_links: dict[str, str] | None = None,
    ) -> None:
        """Initialize the generator with an optional custom template or theme."""
        if readme_mode not in README_RENDER_MODES:
            msg = f"Unsupported readme_mode: {readme_mode}"
            raise ValueError(msg)
        self._template_path = template_path
        self._theme = theme
        self._source_link_template = source_link_template
        self._output_options = output_options or OutputOptions()
        self._active_output_options = self._output_options
        self._readme_mode = readme_mode
        self._readme_title = readme_title.strip() or DEFAULT_README_TITLE
        self._readme_module_links = readme_module_links or {}
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
        env.globals["anchorize"] = _anchorize
        env.globals["method_anchor"] = self._method_anchor
        env.globals["source_url"] = self._source_url
        return env

    def _method_anchor(self, class_name: str, method_name: str) -> str:
        """Return a unique anchor for a class method heading."""
        return _anchorize(f"{class_name}-{method_name}")

    def _source_url(self, path: str | None, line: int | None) -> str | None:
        """Render a source URL for a documented object."""
        if not (
            self._active_output_options.show_source_links
            and self._source_link_template
            and path
            and line
        ):
            return None
        return self._source_link_template.format(
            path=path,
            file=Path(path).name,
            line=line,
        )

    def _render_module_content(
        self,
        module: ModuleDoc,
        *,
        type_index: object,
        output_options: OutputOptions | None = None,
    ) -> str:
        """Render a single module using the configured Jinja template."""
        template_name = self._resolve_template_name()
        template = self._env.get_template(template_name)
        render_options = output_options or self._output_options
        previous_options = self._active_output_options
        self._active_output_options = render_options
        try:
            return _normalize_markdown(
                template.render(
                    module=module,
                    type_index=type_index,
                    render_options=render_options,
                )
            )
        finally:
            self._active_output_options = previous_options

    def _readme_render_options(self) -> OutputOptions:
        """Return rendering options for detailed README output."""
        return replace(self._output_options, show_toc=False)

    def _demote_headings(self, content: str, levels: int = 2) -> str:
        """Shift Markdown heading levels down for README embedding."""
        demoted_lines: list[str] = []
        for line in content.splitlines():
            if line.startswith("#"):
                hashes, _, rest = line.partition(" ")
                if rest:
                    demoted_lines.append(f"{hashes}{'#' * levels} {rest}")
                    continue
            demoted_lines.append(line)
        return "\n".join(demoted_lines)

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
        type_index = TypeIndex.from_modules(modules)

        for module in modules:
            output_path = self._module_output_path(module, output_dir)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug("Generating %s", output_path)
            content = self._render_module_content(module, type_index=type_index)
            _write_utf8_text(output_path, content + "\n")
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
                stats = f" - {', '.join(stats_parts)}" if stats_parts else ""
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
        return f" - {', '.join(stats_parts)}" if stats_parts else ""

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
            lines.append(self._readme_module_heading(module_name))
            lines.append("")

            if module.docstring:
                lines.append(self._first_doc_line(module))
                lines.append("")

            stats_parts: list[str] = []
            if module.classes:
                stats_parts.append(f"{len(module.classes)} class(es)")
            if module.functions:
                stats_parts.append(f"{len(module.functions)} function(s)")
            if module.public_api:
                stats_parts.append(f"{len(module.public_api)} export(s)")
            if stats_parts:
                lines.append(f"_Includes: {', '.join(stats_parts)}._")
                lines.append("")

            public_entries, remaining_classes, remaining_functions, undocumented_exports = (
                self._readme_public_api_sections(module)
            )
            if public_entries:
                lines.append("**Public API:**")
                lines.extend(public_entries)
                lines.append("")

            if undocumented_exports:
                lines.append("**Additional exports:**")
                lines.extend(f"- `{name}`" for name in undocumented_exports)
                lines.append("")

            if remaining_classes:
                lines.append("**Other classes:**")
                for class_doc in remaining_classes:
                    lines.append(self._readme_object_line(class_doc.name, class_doc.docstring))
                lines.append("")

            if remaining_functions:
                lines.append("**Other functions:**")
                for func_doc in remaining_functions:
                    lines.append(self._readme_object_line(func_doc.name, func_doc.docstring))
                lines.append("")

        lines.append(README_END_MARKER)
        return "\n".join(lines)

    def _generate_detailed_readme(self, modules: list[ModuleDoc]) -> str:
        """Generate a richer README API section using detailed module rendering."""
        from pydoc2markdown.core.crossref import TypeIndex

        lines = [README_START_MARKER, "", "_Generated by PyDoc2Markdown._", ""]
        type_index = TypeIndex.from_modules(modules)
        rendered_modules: list[str] = []

        for module in sorted(modules, key=lambda m: (m.package, m.name)):
            if module.name == "__init__":
                continue
            content = self._render_module_content(
                module,
                type_index=type_index,
                output_options=self._readme_render_options(),
            )
            rendered_modules.append(self._demote_headings(content))

        for index, content in enumerate(rendered_modules):
            if index:
                lines.extend(["", "---", ""])
            lines.append(content)

        lines.extend(["", README_END_MARKER])
        return "\n".join(lines)

    def update_readme(
        self,
        modules: list[ModuleDoc],
        readme_path: Path,
    ) -> Path:
        """Create or update the generated API section in a README file."""
        if self._readme_mode == "detailed":
            generated = self._generate_detailed_readme(modules)
        else:
            generated = self._generate_api_summary(modules)
        section = f"## {self._readme_title}\n\n{generated}\n"

        if not readme_path.exists():
            readme_path.parent.mkdir(parents=True, exist_ok=True)
            _write_utf8_text(readme_path, f"# {self._readme_title}\n\n{generated}\n")
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

        _write_utf8_text(readme_path, updated)
        logger.info("Updated README API reference: %s", readme_path)
        return readme_path

    def _short_doc_line(self, docstring: str | None) -> str:
        """Return the first non-empty docstring line, if any."""
        if not docstring:
            return ""
        return docstring.strip().split("\n")[0]

    def _readme_module_heading(self, module_name: str) -> str:
        """Return a README heading for one module, with a link when available."""
        target = self._readme_module_links.get(module_name)
        if target:
            return f"### [`{module_name}`]({target})"
        return f"### `{module_name}`"

    def _readme_object_line(self, name: str, docstring: str | None) -> str:
        """Return one compact README bullet for a documented object."""
        summary = self._short_doc_line(docstring)
        if summary:
            return f"- `{name}`: {summary}"
        return f"- `{name}`"

    def _readme_public_api_sections(
        self,
        module: ModuleDoc,
    ) -> tuple[list[str], list["ClassDoc"], list["FunctionDoc"], list[str]]:
        """Split module objects into public API and remaining README summary buckets."""
        class_map = {class_doc.name: class_doc for class_doc in module.classes}
        function_map = {func_doc.name: func_doc for func_doc in module.functions}
        public_entries: list[str] = []
        public_class_names: set[str] = set()
        public_function_names: set[str] = set()
        undocumented_exports: list[str] = []

        for export_name in module.public_api:
            if export_name in class_map:
                public_entries.append(
                    self._readme_object_line(export_name, class_map[export_name].docstring)
                )
                public_class_names.add(export_name)
            elif export_name in function_map:
                public_entries.append(
                    self._readme_object_line(export_name, function_map[export_name].docstring)
                )
                public_function_names.add(export_name)
            else:
                undocumented_exports.append(export_name)

        remaining_classes = [
            class_doc for class_doc in module.classes if class_doc.name not in public_class_names
        ]
        remaining_functions = [
            func_doc for func_doc in module.functions if func_doc.name not in public_function_names
        ]
        return public_entries, remaining_classes, remaining_functions, undocumented_exports

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
            content = self._render_module_content(module, type_index=type_index)
            lines.append(content)
            lines.append("---")
            lines.append("")

        _write_markdown_lines(output_path, lines)
        logger.info("Generated single file: %s", output_path)
        return output_path

    def generate_string(self, module: ModuleDoc) -> str:
        """Generate Markdown content as a string for a single module."""
        from pydoc2markdown.core.crossref import TypeIndex

        type_index = TypeIndex.from_modules([module])
        return self._render_module_content(module, type_index=type_index)
