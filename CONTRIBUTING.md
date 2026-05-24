# Contributing to PyDoc2Markdown

Thank you for your interest in contributing! This document provides guidelines to help you get started.

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/f1sherFM/PyDoc2Markdown.git
   cd PyDoc2Markdown
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate      # Windows
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

## Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Prefix your commit messages:

- `feat:` — New features
- `fix:` — Bug fixes
- `docs:` — Documentation changes
- `style:` — Code style changes (formatting, semicolons, etc.)
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Build process or auxiliary tool changes

Example:
```bash
git commit -m "feat: add support for NumPy-style docstrings"
```

## Code Quality

Before submitting a PR, ensure all checks pass:

```bash
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Make your changes with clear, focused commits.
3. Add or update tests for any new functionality.
4. Update documentation if needed.
5. Open a PR with a descriptive title and summary.

## Questions?

Open an [issue](https://github.com/f1sherFM/PyDoc2Markdown/issues) or start a [discussion](https://github.com/f1sherFM/PyDoc2Markdown/discussions).
