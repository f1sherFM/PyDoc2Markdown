# Contributing to PyDoc2Markdown

Thanks for helping improve PyDoc2Markdown. This guide covers the development
setup, commit conventions, release flow, and the checks we expect before a PR
is merged.

## Development Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/f1sherFM/PyDoc2Markdown.git
   cd PyDoc2Markdown
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate     # Windows
   ```

3. **Install the project in development mode**

   ```bash
   pip install -e ".[dev]"
   ```

   The `dev` extra already includes the watcher dependency used in local
   development. If you only need runtime `--watch` support outside a dev setup,
   install:

   ```bash
   pip install pydoc2markdown[watch]
   ```

## Conventional Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/). Use a
clear prefix in each commit message:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Formatting and style-only changes
- `refactor:` - Internal code restructuring without behavior changes
- `test:` - Adding or updating tests
- `chore:` - Tooling, automation, and maintenance work

Example:

```bash
git commit -m "feat: add support for NumPy-style docstrings"
```

## Automated Releases

This project uses
[release-please](https://github.com/googleapis/release-please) to automate
versioning and publishing.

1. When a PR with releasable commits is merged into `main`, release-please
   analyzes the commit history.
2. If a release is needed, it opens a **Release PR** that updates:
   - `pyproject.toml`
   - `src/pydoc2markdown/__init__.py`
   - `CHANGELOG.md`
3. Merging that Release PR creates a GitHub Release and triggers PyPI
   publishing through Trusted Publishing.

### Version bumping rules

- `feat:` normally bumps the **minor** version, for example `0.1.0 -> 0.2.0`
- `fix:` normally bumps the **patch** version, for example `0.1.0 -> 0.1.1`
- `BREAKING CHANGE:` bumps the **major** version

### Project version policy

This repository uses a slightly stricter versioning policy for user-facing
releases:

- `x.1.x` - a large feature or fairly large update
- `x.x.1` - a small feature, bug fix, minor improvement, or a collected set of
  microfixes
- `x.x.x.1` - microfixes
- `1.x.x` - a major milestone release after at least four `x.1.x` versions

Because release-please follows standard semantic versioning, small features may
occasionally need their Release PR adjusted from a minor bump to a patch bump.
When that happens, update the version files and PR title only. Do not replace
the release-please PR body, because release-please parses that body when it
creates the GitHub Release.

## Code Quality

Before opening or updating a PR, run:

```bash
ruff check src tests
ruff format --check src tests
mypy src
pytest
```

## Pull Request Checklist

Before you ask for review, make sure:

1. The change is focused and intentionally scoped.
2. Tests cover new behavior or bug fixes when appropriate.
3. Documentation is updated when the user experience changes.
4. Commit messages follow Conventional Commits.
5. Local checks pass.

## Questions

Open an [issue](https://github.com/f1sherFM/PyDoc2Markdown/issues) or start a
[discussion](https://github.com/f1sherFM/PyDoc2Markdown/discussions).
