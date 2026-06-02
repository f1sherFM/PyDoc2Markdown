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

   The `dev` extra includes watcher dependencies for local development. Use
   `pip install pydoc2markdown[watch]` when installing only the runtime package
   with `--watch` support.

## Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Prefix your commit messages:

- `feat:` — New features (triggers **MINOR** version bump)
- `fix:` — Bug fixes (triggers **PATCH** version bump)
- `docs:` — Documentation changes
- `style:` — Code style changes (formatting, semicolons, etc.)
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Build process or auxiliary tool changes

Example:
```bash
git commit -m "feat: add support for NumPy-style docstrings"
```

## Automated Releases

This project uses [release-please](https://github.com/googleapis/release-please) to automate versioning and publishing:

1. When a PR with conventional commits is merged to `main`, release-please analyzes the commit history.
2. If there are releasable changes, release-please opens a **Release PR** containing:
   - Bumped version in `pyproject.toml`
   - Updated `CHANGELOG.md`
3. Merging the Release PR creates a **GitHub Release** and triggers a PyPI publish via Trusted Publishing.

**Version bumping rules:**
- `feat:` commits bump the **minor** version (e.g. `0.1.0` → `0.2.0`)
- `fix:` commits bump the **patch** version (e.g. `0.1.0` → `0.1.1`)
- A commit footer with `BREAKING CHANGE:` bumps the **major** version

Commits with prefixes `docs:`, `style:`, `refactor:`, `test:`, `chore:` do not trigger a release by themselves.

**Project version policy:**
- `x.1.x` is for a large feature or a fairly large update.
- `x.x.1` is for a small feature, bug fix, minor improvement, or a collected set of microfixes.
- `x.x.x.1` is for microfixes.
- `1.x.x` is reserved for a major, user-visible milestone after at least four `x.1.x` releases.

Because release-please follows conventional semver by default, small features
may need their Release PR version adjusted from a minor bump to a patch bump.
When adjusting a Release PR, edit the version files and PR title only. Do not
replace the release-please PR body: release-please parses that body when it
creates the GitHub Release, and a custom body can prevent PyPI publishing.

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
