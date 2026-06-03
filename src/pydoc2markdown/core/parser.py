"""Python docstring parser with structured docstring support."""

import ast
import contextlib
import fnmatch
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
    is_property: bool = False
    is_classmethod: bool = False
    is_staticmethod: bool = False
    source_path: str | None = None
    line_number: int | None = None


@dataclass
class PydanticField:
    """Represents a Pydantic model field."""

    name: str
    type_hint: str | None = None
    default: str | None = None
    description: str | None = None
    required: bool = True


@dataclass
class ClassDoc:
    """Represents extracted documentation for a class."""

    name: str
    docstring: str | None = None
    methods: list[FunctionDoc] = field(default_factory=list)
    attributes: list[Parameter] = field(default_factory=list)
    bases: list[str] = field(default_factory=list)
    class_type: str = "class"
    is_protocol: bool = False
    is_abstract: bool = False
    is_pydantic_model: bool = False
    pydantic_fields: list[PydanticField] = field(default_factory=list)
    source_path: str | None = None
    line_number: int | None = None


@dataclass
class ModuleDoc:
    """Represents extracted documentation for a module."""

    name: str
    path: Path
    docstring: str | None = None
    classes: list[ClassDoc] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)
    public_api: list[str] = field(default_factory=list)
    package: str = ""


class DocstringParser:
    """Parse Python source files and extract structured docstrings."""

    def __init__(self) -> None:
        self._modules: list[ModuleDoc] = []
        self._source: Path = Path()

    def parse(
        self,
        source: Path,
        recursive: bool = False,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> list[ModuleDoc]:
        """Parse a file or directory and return extracted documentation."""
        self._modules.clear()
        self._source = source

        if source.is_file() and source.suffix == ".py":
            if self._should_parse_file(source, include, exclude):
                self._parse_file(source)
        elif source.is_dir():
            pattern = "**/*.py" if recursive else "*.py"
            for file_path in sorted(source.glob(pattern)):
                if self._should_parse_file(file_path, include, exclude):
                    self._parse_file(file_path)
        else:
            raise ValueError(f"Invalid source: {source}")

        return self._modules

    def _should_parse_file(
        self,
        path: Path,
        include: list[str] | None,
        exclude: list[str] | None,
    ) -> bool:
        """Return whether a source file passes include/exclude filters."""
        if include and not any(self._path_matches(path, pattern) for pattern in include):
            return False
        return not (exclude and any(self._path_matches(path, pattern) for pattern in exclude))

    def _path_matches(self, path: Path, pattern: str) -> bool:
        """Match a path against a glob pattern using source-relative POSIX paths."""
        source_root = self._source if self._source.is_dir() else self._source.parent
        try:
            relative = path.relative_to(source_root)
        except ValueError:
            relative = path

        relative_text = relative.as_posix()
        normalized_pattern = pattern.replace("\\", "/")
        if fnmatch.fnmatch(relative_text, normalized_pattern):
            return True
        if "/" not in normalized_pattern:
            return fnmatch.fnmatch(path.name, normalized_pattern)
        return False

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
        package = ""
        source_path = self._source_relative_path(path)
        if self._source.is_dir():
            try:
                rel = path.parent.relative_to(self._source)
                if rel != Path("."):
                    package = str(rel).replace("\\", ".").replace("/", ".")
            except ValueError:
                package = ""
        module = ModuleDoc(
            name=path.stem,
            path=path,
            docstring=ast.get_docstring(tree),
            package=package,
        )

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                module.classes.append(self._extract_class(node, source_path))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                module.functions.append(self._extract_function(node, source_path=source_path))
            elif isinstance(node, ast.Assign | ast.AnnAssign):
                module.public_api.extend(self._extract_public_api(node))

        return module

    def _source_relative_path(self, path: Path) -> str:
        """Return a POSIX source path relative to the parse root."""
        source_root = self._source if self._source.is_dir() else self._source.parent
        try:
            return path.relative_to(source_root).as_posix()
        except ValueError:
            return path.as_posix()

    def _extract_class(self, node: ast.ClassDef, source_path: str) -> ClassDoc:
        """Extract documentation from a class definition."""
        bases = [self._format_base(base) for base in node.bases]
        is_pydantic = self._is_pydantic_model(bases)
        class_doc = ClassDoc(
            name=node.name,
            docstring=ast.get_docstring(node),
            bases=bases,
            class_type=self._resolve_class_type(node, bases),
            is_protocol=self._is_protocol(bases),
            is_abstract=self._is_abstract(bases),
            is_pydantic_model=is_pydantic,
            source_path=source_path,
            line_number=node.lineno,
        )

        if is_pydantic:
            class_doc.pydantic_fields = self._extract_pydantic_fields(node)

        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name == "__init__":
                    class_doc.attributes.extend(self._extract_attributes(item))
                else:
                    class_doc.methods.append(
                        self._extract_function(
                            item,
                            is_method=True,
                            source_path=source_path,
                        )
                    )

        return class_doc

    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_method: bool = False,
        source_path: str | None = None,
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
        if returns is None and ast_return_type and ast_return_type != "None":
            returns = ReturnsInfo(type_hint=ast_return_type)
        elif returns and ast_return_type and ast_return_type != "None" and not returns.type_hint:
            returns.type_hint = ast_return_type
        if returns and returns.type_hint == "None" and not returns.description:
            returns = None

        decorators = self._extract_decorator_names(node)
        is_property = any(d in ("property", "cached_property") for d in decorators)
        is_classmethod = "classmethod" in decorators
        is_staticmethod = "staticmethod" in decorators

        return FunctionDoc(
            name=node.name,
            docstring=raw_docstring,
            params=params,
            returns=returns,
            raises=raises,
            is_method=is_method,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            is_property=is_property,
            is_classmethod=is_classmethod,
            is_staticmethod=is_staticmethod,
            source_path=source_path,
            line_number=node.lineno,
        )

    def _extract_ast_params(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> list[Parameter]:
        """Extract parameter names and type hints from AST."""
        params: list[Parameter] = []
        args = node.args
        positional_args = [*args.posonlyargs, *args.args]
        positional_defaults = self._positional_defaults(positional_args, args.defaults)

        # Determine start index (skip self/cls for methods)
        start = 0
        if positional_args and positional_args[0].arg in ("self", "cls"):
            start = 1

        # Positional args
        for idx, arg in enumerate(positional_args[start:], start=start):
            param = Parameter(
                name=arg.arg,
                type_hint=ast.unparse(arg.annotation) if arg.annotation else None,
                default=positional_defaults[idx],
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
        for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
            params.append(
                Parameter(
                    name=arg.arg,
                    type_hint=ast.unparse(arg.annotation) if arg.annotation else None,
                    default=ast.unparse(default) if default else None,
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

    def _positional_defaults(
        self,
        args: list[ast.arg],
        defaults: list[ast.expr],
    ) -> list[str | None]:
        """Return defaults right-aligned to positional arguments."""
        required_count = len(args) - len(defaults)
        return [None] * required_count + [ast.unparse(default) for default in defaults]

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

    def _extract_decorator_names(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
    ) -> list[str]:
        """Extract decorator names from a function or class definition."""
        names: list[str] = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                names.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                names.append(f"{ast.unparse(dec.value)}.{dec.attr}")
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    names.append(dec.func.id)
                elif isinstance(dec.func, ast.Attribute):
                    names.append(f"{ast.unparse(dec.func.value)}.{dec.func.attr}")
        return names

    def _resolve_class_type(
        self,
        node: ast.ClassDef,
        bases: list[str],
    ) -> str:
        """Determine if a class is a dataclass, enum, typeddict, or plain class."""
        decorators = self._extract_decorator_names(node)
        if any(d in ("dataclass", "dataclasses.dataclass") for d in decorators):
            return "dataclass"
        if any(base.rsplit(".", 1)[-1] in ("Enum", "IntEnum", "Flag", "IntFlag") for base in bases):
            return "enum"
        if any(base.rsplit(".", 1)[-1] in ("TypedDict", "typing.TypedDict") for base in bases):
            return "typeddict"
        return "class"

    def _is_protocol(self, bases: list[str]) -> bool:
        """Check if the class inherits from typing.Protocol."""
        return any(base.rsplit(".", 1)[-1] in ("Protocol", "typing.Protocol") for base in bases)

    def _is_abstract(self, bases: list[str]) -> bool:
        """Check if the class inherits from ABC."""
        return any(base.rsplit(".", 1)[-1] in ("ABC", "abc.ABC") for base in bases)

    def _is_pydantic_model(self, bases: list[str]) -> bool:
        """Check if the class inherits from pydantic.BaseModel."""
        return any(base.rsplit(".", 1)[-1] in ("BaseModel", "pydantic.BaseModel") for base in bases)

    def _extract_pydantic_fields(self, node: ast.ClassDef) -> list[PydanticField]:
        """Extract Pydantic field definitions from a class body."""
        fields: list[PydanticField] = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                field = self._parse_pydantic_field(item)
                if field is not None:
                    fields.append(field)
        return fields

    def _parse_pydantic_field(self, node: ast.AnnAssign) -> PydanticField | None:
        """Parse a single AnnAssign node as a Pydantic field."""
        if not isinstance(node.target, ast.Name):
            return None

        name = node.target.id
        type_hint = ast.unparse(node.annotation) if node.annotation else None
        default: str | None = None
        description: str | None = None
        required = True

        if node.value is not None:
            required = False
            if isinstance(node.value, ast.Call):
                default = ast.unparse(node.value)
                description = self._extract_field_description(node.value)
            else:
                default = ast.unparse(node.value)

        return PydanticField(
            name=name,
            type_hint=type_hint,
            default=default,
            description=description,
            required=required,
        )

    def _extract_field_description(self, node: ast.Call) -> str | None:
        """Extract description keyword from a Field() call."""
        if not isinstance(node.func, ast.Name | ast.Attribute):
            return None
        func_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        if func_name != "Field":
            return None
        for kw in node.keywords:
            if (
                kw.arg == "description"
                and isinstance(kw.value, ast.Constant)
                and isinstance(kw.value.value, str)
            ):
                return kw.value.value
        return None

    def _extract_public_api(
        self,
        node: ast.Assign | ast.AnnAssign,
    ) -> list[str]:
        """Extract names from __all__ assignment."""
        target = node.targets[0] if isinstance(node, ast.Assign) else node.target
        if not (isinstance(target, ast.Name) and target.id == "__all__"):
            return []

        value = node.value
        if value is None:
            return []

        names: list[str] = []
        if isinstance(value, (ast.List, ast.Tuple)):
            for elt in value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    names.append(elt.value)
                elif hasattr(ast, "Str") and isinstance(elt, ast.Str):  # noqa: UP023
                    names.append(str(elt.s))
        return names
