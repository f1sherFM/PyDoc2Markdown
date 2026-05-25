"""Python docstring parser with structured docstring support."""

import ast
import contextlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

import docstring_parser
from docstring_parser import Docstring as ParsedDocstring

logger = logging.getLogger(__name__)


@dataclass
class Parameter:
    """Represents a function/method parameter."""

    name: str
    type_hint: str | None = None
    default: str | None = None
    description: str | None = None


@dataclass
class ReturnsInfo:
    """Structured return type and description."""

    type_hint: str | None = None
    description: str | None = None


@dataclass
class RaisesInfo:
    """Structured exception type and description."""

    type_name: str | None = None
    description: str | None = None


@dataclass
class FunctionDoc:
    """Represents extracted documentation for a function or method."""

    name: str
    docstring: str | None = None
    params: list[Parameter] = field(default_factory=list)
    returns: ReturnsInfo | None = None
    raises: list[RaisesInfo] = field(default_factory=list)
    is_method: bool = False
    is_async: bool = False


@dataclass
class ClassDoc:
    """Represents extracted documentation for a class."""

    name: str
    docstring: str | None = None
    methods: list[FunctionDoc] = field(default_factory=list)
    attributes: list[Parameter] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)


@dataclass
class ModuleDoc:
    """Represents extracted documentation for a module."""

    name: str
    path: Path
    docstring: str | None = None
    classes: list[ClassDoc] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)


class DocstringParser:
    """Parse Python source files and extract structured docstrings."""

    def __init__(self) -> None:
        self._modules: list[ModuleDoc] = []

    def parse(
        self,
        source: Path,
        recursive: bool = False,
    ) -> list[ModuleDoc]:
        """Parse a file or directory and return extracted documentation."""
        self._modules.clear()

        if source.is_file() and source.suffix == ".py":
            self._parse_file(source)
        elif source.is_dir():
            pattern = "**/*.py" if recursive else "*.py"
            for file_path in sorted(source.glob(pattern)):
                self._parse_file(file_path)
        else:
            raise ValueError(f"Invalid source: {source}")

        return self._modules

    def _parse_file(self, path: Path) -> None:
        """Parse a single Python file."""
        logger.debug("Parsing file: %s", path)
        try:
            source_text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source_text = path.read_text(encoding="latin-1")

        tree = ast.parse(source_text)
        module_doc = self._extract_module(path, tree)
        logger.debug(
            "Extracted %d classes and %d functions from %s",
            len(module_doc.classes),
            len(module_doc.functions),
            path,
        )
        self._modules.append(module_doc)

    def _extract_module(self, path: Path, tree: ast.AST) -> ModuleDoc:
        """Extract module-level documentation."""
        assert isinstance(tree, ast.Module)
        module = ModuleDoc(
            name=path.stem,
            path=path,
            docstring=ast.get_docstring(tree),
        )

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                module.classes.append(self._extract_class(node))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                module.functions.append(self._extract_function(node))

        return module

    def _extract_class(self, node: ast.ClassDef) -> ClassDoc:
        """Extract documentation from a class definition."""
        class_doc = ClassDoc(
            name=node.name,
            docstring=ast.get_docstring(node),
            bases=[self._format_base(base) for base in node.bases],
        )

        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name == "__init__":
                    class_doc.attributes.extend(self._extract_attributes(item))
                else:
                    class_doc.methods.append(self._extract_function(item, is_method=True))

        return class_doc

    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_method: bool = False,
    ) -> FunctionDoc:
        """Extract documentation from a function definition."""
        raw_docstring = ast.get_docstring(node)
        params = self._extract_ast_params(node)
        returns: ReturnsInfo | None = None
        raises: list[RaisesInfo] = []

        if raw_docstring:
            with contextlib.suppress(Exception):
                parsed = docstring_parser.parse(raw_docstring)
                self._merge_param_descriptions(params, parsed)
                returns = self._extract_returns(parsed)
                raises = self._extract_raises(parsed)

        # Fallback to AST return annotation if docstring did not provide type
        ast_return_type = ast.unparse(node.returns) if node.returns else None
        if returns is None:
            returns = ReturnsInfo(type_hint=ast_return_type)
        elif ast_return_type and not returns.type_hint:
            returns.type_hint = ast_return_type

        return FunctionDoc(
            name=node.name,
            docstring=raw_docstring,
            params=params,
            returns=returns,
            raises=raises,
            is_method=is_method,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    def _extract_ast_params(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> list[Parameter]:
        """Extract parameter names and type hints from AST."""
        params: list[Parameter] = []
        args = node.args

        # Determine start index (skip self/cls for methods)
        start = 0
        if args.args and args.args[0].arg in ("self", "cls"):
            start = 1

        # Positional args
        for _idx, arg in enumerate(args.args[start:], start=start):
            param = Parameter(
                name=arg.arg,
                type_hint=ast.unparse(arg.annotation) if arg.annotation else None,
            )
            params.append(param)

        # *args
        if args.vararg:
            params.append(
                Parameter(
                    name=f"*{args.vararg.arg}",
                    type_hint=ast.unparse(args.vararg.annotation)
                    if args.vararg.annotation
                    else None,
                ),
            )

        # Keyword-only args
        for arg in args.kwonlyargs:
            params.append(
                Parameter(
                    name=arg.arg,
                    type_hint=ast.unparse(arg.annotation) if arg.annotation else None,
                ),
            )

        # **kwargs
        if args.kwarg:
            params.append(
                Parameter(
                    name=f"**{args.kwarg.arg}",
                    type_hint=ast.unparse(args.kwarg.annotation) if args.kwarg.annotation else None,
                ),
            )

        return params

    def _merge_param_descriptions(
        self,
        params: list[Parameter],
        parsed: ParsedDocstring,
    ) -> None:
        """Merge docstring parameter descriptions into AST-extracted parameters."""
        for param in params:
            doc_param = next(
                (p for p in parsed.params if p.arg_name == param.name.lstrip("*")),
                None,
            )
            if doc_param and doc_param.description:
                param.description = doc_param.description

    def _extract_returns(self, parsed: ParsedDocstring) -> ReturnsInfo | None:
        """Extract structured return info from parsed docstring."""
        if parsed.returns:
            return ReturnsInfo(
                type_hint=parsed.returns.type_name,
                description=parsed.returns.description,
            )
        return None

    def _extract_raises(self, parsed: ParsedDocstring) -> list[RaisesInfo]:
        """Extract structured raises info from parsed docstring."""
        return [
            RaisesInfo(
                type_name=r.type_name,
                description=r.description,
            )
            for r in parsed.raises
        ]

    def _extract_attributes(
        self,
        init_node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> list[Parameter]:
        """Extract instance attributes from __init__ method."""
        attributes: list[Parameter] = []

        # Try to enrich with __init__ docstring parameter descriptions
        init_docstring = ast.get_docstring(init_node)
        parsed_init: ParsedDocstring | None = None
        if init_docstring:
            with contextlib.suppress(Exception):
                parsed_init = docstring_parser.parse(init_docstring)

        for node in ast.walk(init_node):
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Attribute)
                and isinstance(node.target.value, ast.Name)
                and node.target.value.id == "self"
            ):
                attr_name = node.target.attr
                attr = Parameter(
                    name=attr_name,
                    type_hint=ast.unparse(node.annotation) if node.annotation else None,
                )
                if parsed_init:
                    doc_attr = next(
                        (p for p in parsed_init.params if p.arg_name == attr_name),
                        None,
                    )
                    if doc_attr and doc_attr.description:
                        attr.description = doc_attr.description
                attributes.append(attr)

        return attributes

    def _format_base(self, base: ast.expr) -> str:
        """Format a base class expression as a string."""
        return ast.unparse(base)
