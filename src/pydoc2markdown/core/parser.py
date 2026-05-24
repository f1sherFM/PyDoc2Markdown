"""Python docstring parser."""

import ast
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Parameter:
    """Represents a function/method parameter."""

    name: str
    type_hint: str | None = None
    default: str | None = None
    description: str | None = None


@dataclass
class FunctionDoc:
    """Represents extracted documentation for a function or method."""

    name: str
    docstring: str | None = None
    params: list[Parameter] = field(default_factory=list)
    returns: str | None = None
    raises: list[str] = field(default_factory=list)
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
    """Parse Python source files and extract docstrings."""

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
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            source = path.read_text(encoding="latin-1")

        tree = ast.parse(source)
        module_doc = self._extract_module(path, tree)
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
        return FunctionDoc(
            name=node.name,
            docstring=ast.get_docstring(node),
            is_method=is_method,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    def _extract_attributes(
        self, init_node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[Parameter]:
        """Extract instance attributes from __init__ method."""
        attributes: list[Parameter] = []
        for node in ast.walk(init_node):
            if (
                isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Attribute)
                and isinstance(node.target.value, ast.Name)
                and node.target.value.id == "self"
            ):
                attr = Parameter(
                    name=node.target.attr,
                    type_hint=ast.unparse(node.annotation) if node.annotation else None,
                )
                attributes.append(attr)
        return attributes

    def _format_base(self, base: ast.expr) -> str:
        """Format a base class expression as a string."""
        return ast.unparse(base)
