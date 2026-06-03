# Documentation Index

This directory contains a generated documentation snapshot for the
PyDoc2Markdown codebase itself. It works as a small showcase of the default
Markdown output: package grouping, module landing pages, tables of contents,
and API sections built directly from Python source.

**Overview:** 11 modules, 9 classes, 12 functions.

## Start Here

If you just want a quick feel for the output, these are the most useful pages:

- [cli](cli.md) for the command-line entrypoint
- [core/generator](core/generator.md) for the main Markdown rendering surface
- [core/parser](core/parser.md) for the structured parsing models
- [utils/helpers](utils/helpers.md) for a compact utility-module example

## Modules

- [cli](cli.md) - 3 function(s)
  > Command-line interface for PyDoc2Markdown.

## Package `core`

Core logic for PyDoc2Markdown.

- [config](core/config.md) - 1 function(s)
  > Configuration loader for PyDoc2Markdown.
- [crossref](core/crossref.md) - 1 class(es), 2 function(s)
  > Cross-referencing utilities for linking project-defined types.
- [generator](core/generator.md) - 1 class(es)
  > Markdown documentation generator.
- [parser](core/parser.md) - 7 class(es)
  > Python docstring parser with structured docstring support.
- [type_hints](core/type_hints.md) - 3 function(s)
  > Type hint formatting utilities.
- [watcher](core/watcher.md) - 1 function(s)
  > File watcher for auto-regenerating documentation.

## Package `utils`

Utility modules for PyDoc2Markdown.

- [helpers](utils/helpers.md) - 2 function(s)
  > Helper utilities for PyDoc2Markdown.
