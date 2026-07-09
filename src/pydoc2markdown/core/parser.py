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
    constructor_params: list[Parameter] = field(default_factory=list)
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
    attributes: list[Parameter] = field(default_factory=list)
    classes: list[ClassDoc] = field(default_factory=list)
    functions: list[FunctionDoc] = field(default_factory=list)
    public_api: list[str] = field(default_factory=list)
    package: str = ""


class DocstringParser:
    """Parse Python source files and extract structured docstrings."""

    def __init__(self, inherit_docstrings: bool = False) -> None:
        """Initialize the parser.

        Args:
            inherit_docstrings: Fill missing class and method documentation from
                parsed base classes when possible.
        """
        self._modules: list[ModuleDoc] = []
        self._source: Path = Path()
        self._inherit_docstrings = inherit_docstrings

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

        if self._inherit_docstrings:
            self._apply_docstring_inheritance()

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

    def _apply_docstring_inheritance(self) -> None:
        """Fill missing class and method docs from parsed base classes."""
        class_index = self._class_index()
        resolved: set[int] = set()
        for module in self._modules:
            for class_doc in module.classes:
                self._inherit_class_docs(class_doc, class_index, resolved, set())

    def _class_index(self) -> dict[str, ClassDoc | None]:
        """Return class lookup keys, marking duplicate short names as ambiguous."""
        index: dict[str, ClassDoc | None] = {}
        for module in self._modules:
            module_name = f"{module.package}.{module.name}" if module.package else module.name
            for class_doc in module.classes:
                qualified_name = f"{module_name}.{class_doc.name}"
                index[qualified_name] = class_doc
                if class_doc.name in index:
                    index[class_doc.name] = None
                else:
                    index[class_doc.name] = class_doc
        return index

    def _inherit_class_docs(
        self,
        class_doc: ClassDoc,
        class_index: dict[str, ClassDoc | None],
        resolved: set[int],
        resolving: set[int],
    ) -> None:
        """Apply inherited docs to one class, resolving its bases first."""
        class_id = id(class_doc)
        if class_id in resolved:
            return
        if class_id in resolving:
            return
        resolving.add(class_id)

        for base_doc in self._base_classes(class_doc, class_index):
            self._inherit_class_docs(base_doc, class_index, resolved, resolving)
            self._inherit_from_base(class_doc, base_doc)

        resolving.remove(class_id)
        resolved.add(class_id)

    def _base_classes(
        self,
        class_doc: ClassDoc,
        class_index: dict[str, ClassDoc | None],
    ) -> list[ClassDoc]:
        """Return parsed base classes for a class, ignoring unknown or ambiguous bases."""
        bases: list[ClassDoc] = []
        for base_name in class_doc.bases:
            for candidate in self._base_lookup_keys(base_name):
                base_doc = class_index.get(candidate)
                if base_doc is not None:
                    bases.append(base_doc)
                    break
        return bases

    def _base_lookup_keys(self, base_name: str) -> tuple[str, ...]:
        """Return lookup keys for a base class expression."""
        normalized = base_name.split("[", 1)[0].strip()
        if not normalized:
            return ()
        return (normalized, normalized.rsplit(".", 1)[-1])

    def _inherit_from_base(self, class_doc: ClassDoc, base_doc: ClassDoc) -> None:
        """Copy missing class and method docs from one base class."""
        if not class_doc.docstring and base_doc.docstring:
            class_doc.docstring = base_doc.docstring

        base_methods = {method.name: method for method in base_doc.methods}
        for method in class_doc.methods:
            base_method = base_methods.get(method.name)
            if base_method is not None:
                self._inherit_method_docs(method, base_method)

    def _inherit_method_docs(
        self,
        method: FunctionDoc,
        base_method: FunctionDoc,
    ) -> None:
        """Copy missing method docs from a base method."""
        if not method.docstring and base_method.docstring:
            method.docstring = base_method.docstring
        if method.returns is None and base_method.returns is not None:
            method.returns = ReturnsInfo(
                type_hint=base_method.returns.type_hint,
                description=base_method.returns.description,
            )
        elif method.returns is not None and base_method.returns is not None:
            if not method.returns.type_hint:
                method.returns.type_hint = base_method.returns.type_hint
            if not method.returns.description:
                method.returns.description = base_method.returns.description
        if not method.raises and base_method.raises:
            method.raises = [
                RaisesInfo(type_name=raise_info.type_name, description=raise_info.description)
                for raise_info in base_method.raises
            ]

        base_params = {param.name.lstrip("*"): param for param in base_method.params}
        for param in method.params:
            base_param = base_params.get(param.name.lstrip("*"))
            if base_param and base_param.description and not param.description:
                param.description = base_param.description

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
        aliases = self._extract_import_aliases(tree)
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
                module.classes.append(self._extract_class(node, source_path, aliases))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                module.functions.append(
                    self._extract_function(
                        node,
                        source_path=source_path,
                        aliases=aliases,
                    )
                )
            elif isinstance(node, ast.Assign | ast.AnnAssign):
                module.public_api.extend(self._extract_public_api(node))

        module.attributes = self._extract_documented_name_attributes(tree.body)
        return module

    def _source_relative_path(self, path: Path) -> str:
        """Return a POSIX source path relative to the parse root."""
        source_root = self._source if self._source.is_dir() else self._source.parent
        try:
            return path.relative_to(source_root).as_posix()
        except ValueError:
            return path.as_posix()

    def _extract_class(
        self,
        node: ast.ClassDef,
        source_path: str,
        aliases: dict[str, str],
    ) -> ClassDoc:
        """Extract documentation from a class definition."""
        raw_docstring = ast.get_docstring(node)
        parsed_docstring = self._parse_docstring(raw_docstring)
        bases = [self._format_base(base) for base in node.bases]
        canonical_bases = [self._canonical_name(base, aliases) for base in bases]
        is_pydantic = self._is_pydantic_model(canonical_bases)
        class_doc = ClassDoc(
            name=node.name,
            docstring=raw_docstring,
            bases=bases,
            class_type=self._resolve_class_type(node, canonical_bases, aliases),
            is_protocol=self._is_protocol(canonical_bases),
            is_abstract=self._is_abstract(canonical_bases),
            is_pydantic_model=is_pydantic,
            source_path=source_path,
            line_number=node.lineno,
        )

        documented_class_attrs = self._extract_documented_name_attributes(
            node.body,
            include_undocumented_annassign=class_doc.class_type
            in ("attrs", "dataclass", "typeddict"),
        )
        if is_pydantic:
            class_doc.pydantic_fields = self._extract_pydantic_fields(node, aliases)
            self._merge_pydantic_field_descriptions(
                class_doc.pydantic_fields,
                documented_class_attrs,
            )
        else:
            class_doc.attributes.extend(documented_class_attrs)

        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                if item.name == "__init__":
                    class_doc.constructor_params = self._extract_ast_params(item)
                    init_docstring = self._parse_docstring(ast.get_docstring(item))
                    if init_docstring:
                        self._merge_param_descriptions(
                            class_doc.constructor_params,
                            init_docstring,
                        )
                    class_doc.attributes.extend(self._extract_attributes(item))
                else:
                    class_doc.methods.append(
                        self._extract_function(
                            item,
                            is_method=True,
                            source_path=source_path,
                            aliases=aliases,
                        )
                    )

        if parsed_docstring:
            self._merge_param_descriptions(class_doc.constructor_params, parsed_docstring)
            self._merge_param_descriptions(class_doc.attributes, parsed_docstring)
            if self._class_docstring_params_are_rendered(class_doc, parsed_docstring):
                class_doc.docstring = self._docstring_description(parsed_docstring)

        return class_doc

    def _extract_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        is_method: bool = False,
        source_path: str | None = None,
        aliases: dict[str, str] | None = None,
    ) -> FunctionDoc:
        """Extract documentation from a function definition."""
        raw_docstring = ast.get_docstring(node)
        parsed_docstring = self._parse_docstring(raw_docstring)
        params = self._extract_ast_params(node)
        returns: ReturnsInfo | None = None
        raises: list[RaisesInfo] = []
        description = raw_docstring

        if parsed_docstring:
            description = self._docstring_description(parsed_docstring)
            self._merge_param_descriptions(params, parsed_docstring)
            returns = self._extract_returns(parsed_docstring)
            raises = self._extract_raises(parsed_docstring)

        # Fallback to AST return annotation if docstring did not provide type
        ast_return_type = ast.unparse(node.returns) if node.returns else None
        if returns is None and ast_return_type and ast_return_type != "None":
            returns = ReturnsInfo(type_hint=ast_return_type)
        elif returns and ast_return_type and ast_return_type != "None" and not returns.type_hint:
            returns.type_hint = ast_return_type
        if returns and returns.type_hint == "None" and not returns.description:
            returns = None

        decorators = self._extract_decorator_names(node, aliases or {})
        is_property = any(
            d.rsplit(".", 1)[-1] in ("property", "cached_property") for d in decorators
        )
        is_classmethod = "classmethod" in decorators
        is_staticmethod = "staticmethod" in decorators

        return FunctionDoc(
            name=node.name,
            docstring=description,
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

    def _parse_docstring(self, docstring: str | None) -> ParsedDocstring | None:
        """Parse a docstring into structured sections when possible."""
        if not docstring:
            return None
        with contextlib.suppress(Exception):
            return docstring_parser.parse(docstring)
        return None

    def _docstring_description(self, parsed: ParsedDocstring) -> str | None:
        """Return the narrative part of a parsed docstring without structured fields."""
        parts = [
            part.strip()
            for part in (parsed.short_description, parsed.long_description)
            if part and part.strip()
        ]
        return "\n\n".join(parts) if parts else None

    def _class_docstring_params_are_rendered(
        self,
        class_doc: ClassDoc,
        parsed: ParsedDocstring,
    ) -> bool:
        """Return whether class docstring params are represented in rendered fields."""
        param_names = {param.arg_name for param in parsed.params if param.arg_name}
        if not param_names:
            return True

        rendered_names = {attr.name for attr in class_doc.attributes}
        rendered_names.update(param.name for param in class_doc.constructor_params)
        rendered_names.update(field.name for field in class_doc.pydantic_fields)
        return param_names <= rendered_names

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
            if doc_param and doc_param.description and not param.description:
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
        attributes_by_name = {
            attr.name: attr for attr in self._extract_documented_instance_attributes(init_node.body)
        }

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
                attr = attributes_by_name.setdefault(
                    node.target.attr,
                    Parameter(
                        name=node.target.attr,
                        type_hint=ast.unparse(node.annotation) if node.annotation else None,
                    ),
                )
                if node.annotation and not attr.type_hint:
                    attr.type_hint = ast.unparse(node.annotation)
                if parsed_init:
                    doc_attr = next(
                        (p for p in parsed_init.params if p.arg_name == attr.name),
                        None,
                    )
                    if doc_attr and doc_attr.description and not attr.description:
                        attr.description = doc_attr.description

        return list(attributes_by_name.values())

    def _extract_documented_name_attributes(
        self,
        body: list[ast.stmt],
        *,
        include_undocumented_annassign: bool = False,
    ) -> list[Parameter]:
        """Extract documented module/class attributes from adjacent string literals."""
        attributes: list[Parameter] = []
        descriptions = self._adjacent_docstrings(body)

        for item in body:
            for name, type_hint, default in self._name_assignment_targets(item):
                if name == "__all__":
                    continue
                description = descriptions.get(item)
                if description or (
                    include_undocumented_annassign and isinstance(item, ast.AnnAssign)
                ):
                    attributes.append(
                        Parameter(
                            name=name,
                            type_hint=type_hint,
                            default=default,
                            description=description,
                        )
                    )
        return attributes

    def _extract_documented_instance_attributes(self, body: list[ast.stmt]) -> list[Parameter]:
        """Extract documented self attributes from adjacent string literals."""
        attributes: list[Parameter] = []
        descriptions = self._adjacent_docstrings(body)

        for item in body:
            for name, type_hint, default in self._self_assignment_targets(item):
                description = descriptions.get(item)
                if description:
                    attributes.append(
                        Parameter(
                            name=name,
                            type_hint=type_hint,
                            default=default,
                            description=description,
                        )
                    )
        return attributes

    def _adjacent_docstrings(self, body: list[ast.stmt]) -> dict[ast.stmt, str]:
        """Return string literals that immediately document the previous statement."""
        descriptions: dict[ast.stmt, str] = {}
        for index, item in enumerate(body[:-1]):
            next_item = body[index + 1]
            if (
                isinstance(next_item, ast.Expr)
                and isinstance(next_item.value, ast.Constant)
                and isinstance(next_item.value.value, str)
            ):
                descriptions[item] = next_item.value.value.strip()
        return descriptions

    def _name_assignment_targets(
        self,
        node: ast.stmt,
    ) -> list[tuple[str, str | None, str | None]]:
        """Return simple top-level assignment targets with type hints and defaults."""
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            return [
                (
                    node.target.id,
                    ast.unparse(node.annotation) if node.annotation else None,
                    ast.unparse(node.value) if node.value else None,
                )
            ]
        if isinstance(node, ast.Assign):
            return [
                (target.id, None, ast.unparse(node.value))
                for target in node.targets
                if isinstance(target, ast.Name)
            ]
        return []

    def _self_assignment_targets(
        self,
        node: ast.stmt,
    ) -> list[tuple[str, str | None, str | None]]:
        """Return self attribute assignment targets with type hints and defaults."""
        if isinstance(node, ast.AnnAssign) and self._is_self_attribute(node.target):
            assert isinstance(node.target, ast.Attribute)
            return [
                (
                    node.target.attr,
                    ast.unparse(node.annotation) if node.annotation else None,
                    ast.unparse(node.value) if node.value else None,
                )
            ]
        if isinstance(node, ast.Assign):
            targets: list[tuple[str, str | None, str | None]] = []
            for target in node.targets:
                if isinstance(target, ast.Attribute) and self._is_self_attribute(target):
                    targets.append((target.attr, None, ast.unparse(node.value)))
            return targets
        return []

    def _is_self_attribute(self, node: ast.expr) -> bool:
        """Return whether a node targets an attribute on self."""
        return (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "self"
        )

    def _merge_pydantic_field_descriptions(
        self,
        fields: list[PydanticField],
        documented_attrs: list[Parameter],
    ) -> None:
        """Fill missing Pydantic field descriptions from adjacent attribute docs."""
        descriptions = {
            attr.name: attr.description for attr in documented_attrs if attr.description
        }
        for pydantic_field in fields:
            if not pydantic_field.description:
                pydantic_field.description = descriptions.get(pydantic_field.name)

    def _format_base(self, base: ast.expr) -> str:
        """Format a base class expression as a string."""
        return ast.unparse(base)

    def _extract_import_aliases(self, tree: ast.Module) -> dict[str, str]:
        """Return import aliases that can affect semantic class detection."""
        aliases: dict[str, str] = {}
        for node in tree.body:
            if isinstance(node, ast.Import):
                for item in node.names:
                    aliases[item.asname or item.name] = item.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                module = "." * node.level + node.module if node.level else node.module
                for item in node.names:
                    if item.name == "*":
                        continue
                    aliases[item.asname or item.name] = f"{module}.{item.name}"
        return aliases

    def _canonical_name(self, name: str, aliases: dict[str, str]) -> str:
        """Expand the first segment of an imported alias when known."""
        head, separator, tail = name.partition(".")
        target = aliases.get(head)
        if target is None:
            return name
        return f"{target}{separator}{tail}" if separator else target

    def _extract_decorator_names(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef,
        aliases: dict[str, str],
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
        return [self._canonical_name(name, aliases) for name in names]

    def _resolve_class_type(
        self,
        node: ast.ClassDef,
        bases: list[str],
        aliases: dict[str, str],
    ) -> str:
        """Determine if a class is an attrs class, dataclass, enum, typeddict, or plain class."""
        decorators = self._extract_decorator_names(node, aliases)
        if any(d in ("dataclass", "dataclasses.dataclass") for d in decorators):
            return "dataclass"
        if any(self._is_attrs_decorator(decorator) for decorator in decorators):
            return "attrs"
        if any(base.rsplit(".", 1)[-1] in ("Enum", "IntEnum", "Flag", "IntFlag") for base in bases):
            return "enum"
        if any(base.rsplit(".", 1)[-1] in ("TypedDict", "typing.TypedDict") for base in bases):
            return "typeddict"
        return "class"

    def _is_attrs_decorator(self, decorator: str) -> bool:
        """Return whether a decorator marks an attrs-powered class."""
        return decorator in {
            "attr.s",
            "attr.attrs",
            "attr.define",
            "attr.mutable",
            "attr.frozen",
            "attr.dataclass",
            "attrs.define",
            "attrs.mutable",
            "attrs.frozen",
            "attrs.dataclass",
        }

    def _is_protocol(self, bases: list[str]) -> bool:
        """Check if the class inherits from typing.Protocol."""
        return any(base.rsplit(".", 1)[-1] in ("Protocol", "typing.Protocol") for base in bases)

    def _is_abstract(self, bases: list[str]) -> bool:
        """Check if the class inherits from ABC."""
        return any(base.rsplit(".", 1)[-1] in ("ABC", "abc.ABC") for base in bases)

    def _is_pydantic_model(self, bases: list[str]) -> bool:
        """Check if the class inherits from pydantic.BaseModel."""
        return any(base.rsplit(".", 1)[-1] in ("BaseModel", "pydantic.BaseModel") for base in bases)

    def _extract_pydantic_fields(
        self,
        node: ast.ClassDef,
        aliases: dict[str, str],
    ) -> list[PydanticField]:
        """Extract Pydantic field definitions from a class body."""
        fields: list[PydanticField] = []
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                field = self._parse_pydantic_field(item, aliases)
                if field is not None:
                    fields.append(field)
        return fields

    def _parse_pydantic_field(
        self,
        node: ast.AnnAssign,
        aliases: dict[str, str],
    ) -> PydanticField | None:
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
                description = self._extract_field_description(node.value, aliases)
            else:
                default = ast.unparse(node.value)

        return PydanticField(
            name=name,
            type_hint=type_hint,
            default=default,
            description=description,
            required=required,
        )

    def _extract_field_description(
        self,
        node: ast.Call,
        aliases: dict[str, str],
    ) -> str | None:
        """Extract description keyword from a Field() call."""
        if not isinstance(node.func, ast.Name | ast.Attribute):
            return None
        func_name = ast.unparse(node.func)
        canonical_name = self._canonical_name(func_name, aliases)
        if canonical_name.rsplit(".", 1)[-1] != "Field":
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
