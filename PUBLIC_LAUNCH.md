# Public Launch Kit

This document collects launch-ready copy for introducing PyDoc2Markdown to new
users. Keep it practical, transparent, and focused on what the tool can do today.

## One-line Pitch

PyDoc2Markdown generates clean Markdown API docs from Python docstrings without
making you adopt a full documentation framework.

## Short Description

PyDoc2Markdown is a lightweight CLI and library for Python projects that want
API documentation to stay close to the code. It can generate Markdown files,
maintain an API section in `README.md`, create navigation-ready docs trees, and
report documentation coverage for CI.

It is meant for the middle ground between copy-pasted README docs and a full
Sphinx-style documentation site: libraries, internal tools, services, and small
packages where plain Markdown is enough.

## Key Points To Mention

- Generates plain Markdown files from Python docstrings.
- Works as both a CLI and a library.
- Supports README API sections, navigation docs, source links, output toggles,
  watch mode, stale-file pruning, and documentation coverage reports.
- Includes a safe `--doctor` mode for inspecting a project before writing docs.
- Ships with a `--demo` command and a real sample project.
- Targets Python 3.10, 3.11, and 3.12.
- Has CI, tests, Codecov, release notes, and a PyPI package.

## Reddit Post

Title:

```text
I built a small Python tool that turns docstrings into plain Markdown docs
```

Body:

```text
Hi! I have been working on PyDoc2Markdown, a lightweight Python documentation
tool that generates clean Markdown API docs from Python docstrings.

The idea is simple: point it at a package and get normal `.md` files that can be
committed, reviewed, and published anywhere. It can also maintain an API section
inside README.md, generate a navigation-ready docs tree, add source links, and
produce a documentation coverage report for CI.

It is not trying to replace Sphinx for large documentation sites. I built it for
the middle ground: small libraries, internal tools, services, and packages where
plain Markdown is enough and setup should stay boring.

Quick try:

    pip install pydoc2markdown
    pydoc2markdown --demo

For an existing project:

    pydoc2markdown src/my_package --recursive --doctor
    pydoc2markdown src/my_package --recursive --nav --readme -o docs

What it supports today:

- Google-style docstrings, with partial NumPy/reST support through docstring-parser
- README API section generation
- navigation docs layout
- source links
- output toggles for public/private members and sections
- documented attributes
- docstring inheritance
- watch mode
- `--check`, `--prune`, and `--report` for CI workflows

Repo: https://github.com/f1sherFM/PyDoc2Markdown
PyPI: https://pypi.org/project/pydoc2markdown/

I would love feedback from people who maintain small Python packages or internal
tools. The most useful question for me right now is: what would make this fit
better into your existing docs workflow?
```

## Short Social Post

```text
I released PyDoc2Markdown, a small Python CLI/library for generating plain
Markdown API docs from docstrings.

It can update README API sections, create navigation-ready docs, add source
links, run doc coverage reports, and inspect a project with `--doctor` before
writing anything.

Try it:

pip install pydoc2markdown
pydoc2markdown --demo

https://github.com/f1sherFM/PyDoc2Markdown
```

## GitHub Discussion Or Issue Post

```text
I am preparing PyDoc2Markdown for broader public feedback and would like to make
sure it solves the right documentation problems for real Python projects.

The tool currently generates Markdown API docs from docstrings, can maintain a
README API section, create a docs navigation layout, add source links, and report
documentation coverage in CI.

I would especially appreciate feedback on:

1. The generated Markdown structure.
2. The README API workflow.
3. What should be configurable by default.
4. Missing patterns from real-world Python projects.
5. Whether `--doctor` and `--demo` make onboarding clear enough.
```

## Suggested Places To Share

- `r/Python`
- `r/learnpython`, if the post is framed as a practical docs workflow
- `r/opensource`
- Python Discord or community chats where project showcases are welcome
- GitHub Discussions in related documentation/tooling communities
- Personal GitHub profile README or pinned repository

Check each community's self-promotion rules before posting.

## Pre-launch Checklist

- Confirm the latest PyPI version matches the latest GitHub release.
- Confirm CI is green on `main`.
- Run `pydoc2markdown --demo` from a clean directory.
- Open the sample project README and generated docs links.
- Check README badges.
- Check the first screen of the GitHub repository on mobile and desktop.
- Prepare one honest "known limitations" answer:
  PyDoc2Markdown is intentionally lighter than Sphinx and currently relies on
  `docstring-parser` for docstring format support, so NumPy and reST support are
  useful but not as exhaustive as dedicated documentation frameworks.
