# Changelog

## [0.6.3](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.6.2...v0.6.3) (2026-06-03)


### Bug Fixes

* normalize generated markdown output ([021a85f](https://github.com/f1sherFM/PyDoc2Markdown/commit/021a85f29db3a1e8de2561f972b0e8f877085e97))
* normalize init config messages ([7250846](https://github.com/f1sherFM/PyDoc2Markdown/commit/7250846b22d9d233226e5d2989f1439992d503c5))


### Documentation

* add README visual assets ([543b043](https://github.com/f1sherFM/PyDoc2Markdown/commit/543b043c42c3cb7e5586b29c82bfcd371b14a42a))
* improve onboarding guides ([83751b3](https://github.com/f1sherFM/PyDoc2Markdown/commit/83751b37e6405c712e9bb6358f8f5d2feac3857d))
* polish project presentation ([7efe3bc](https://github.com/f1sherFM/PyDoc2Markdown/commit/7efe3bcb567db82a2a3dc1d44a44dcf49a195336))
* polish showcase index ([7e0f951](https://github.com/f1sherFM/PyDoc2Markdown/commit/7e0f951ea191145523dcc96fc5275397888255c2))
* tighten showcase markdown ([ac54f6c](https://github.com/f1sherFM/PyDoc2Markdown/commit/ac54f6cc4e47c1904a7274a35c8051f25a56f7e6))

## [0.7.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.6.1...v0.7.0) (2026-06-03)


### Features

* **cli:** add --prune flag to remove stale generated files ([#36](https://github.com/f1sherFM/PyDoc2Markdown/issues/36)) ([fcdec44](https://github.com/f1sherFM/PyDoc2Markdown/commit/fcdec441cbb30c3f25a6fb0af0ef5ce9aa91127c))


### Bug Fixes

* improve prune cli feedback ([ebcbd39](https://github.com/f1sherFM/PyDoc2Markdown/commit/ebcbd39ad21ab8ea02fca7d00c3bdfcc80d6ea82))

## [0.6.1](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.6.0...v0.6.1) (2026-06-03)


### Bug Fixes

* tighten check output and method rendering ([400d7c2](https://github.com/f1sherFM/PyDoc2Markdown/commit/400d7c2dcdf3c966c3b6ce08a74309cfda554d78))

## [0.6.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.6...v0.6.0) (2026-06-02)


### Features

0.6.0 focuses on making generated API docs more practical for real Python projects:
users can now decide exactly which modules should be documented, generated
parameter tables show whether arguments are required or optional, and Markdown
output can link every documented class, function, and method back to source code.

* add `--include` and `--exclude` glob filters for recursive documentation runs, with include patterns applied first and exclude patterns removing unwanted matches afterward ([0392582](https://github.com/f1sherFM/PyDoc2Markdown/commit/039258294edb89380a06f2f5c7e377e40de8c91f))
* add parameter defaults to generated function and method tables, marking required arguments explicitly and showing defaults for optional positional and keyword-only parameters ([0392582](https://github.com/f1sherFM/PyDoc2Markdown/commit/039258294edb89380a06f2f5c7e377e40de8c91f))
* add source links via `--source-repo` for GitHub projects and `--source-link` for custom URL templates using `{path}`, `{file}`, and `{line}` ([0392582](https://github.com/f1sherFM/PyDoc2Markdown/commit/039258294edb89380a06f2f5c7e377e40de8c91f))
* document the new workflow in the README and update the sample project docs so users can see the new output format immediately ([0392582](https://github.com/f1sherFM/PyDoc2Markdown/commit/039258294edb89380a06f2f5c7e377e40de8c91f))

## [0.5.6](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.5...v0.5.6) (2026-06-02)


### Bug Fixes

* preserve final newline in generated docs ([cae4e24](https://github.com/f1sherFM/PyDoc2Markdown/commit/cae4e242973b9d61ed1b2d1ec1b34d37814c94e0))

## [0.5.5](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.4...v0.5.5) (2026-06-02)


### Bug Fixes

* stabilize docs output edge cases ([7d45f7c](https://github.com/f1sherFM/PyDoc2Markdown/commit/7d45f7c8bae1505370c1057ab7b79ea4b1e858ce))

## [0.5.4](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.3...v0.5.4) (2026-06-02)


### Bug Fixes

* add generated docs check mode ([03a02c9](https://github.com/f1sherFM/PyDoc2Markdown/commit/03a02c9325102052601db120902019d68a367239))

## [0.5.3](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.2...v0.5.3) (2026-06-01)


### Features

* add CLI demo command ([30357c3](https://github.com/f1sherFM/PyDoc2Markdown/commit/30357c3f3bfc24c200fc4d18ef516a982056ad35))


### Documentation

* add common CLI commands ([203b86f](https://github.com/f1sherFM/PyDoc2Markdown/commit/203b86fb7923bc388148abff899cdb10c3d98463))

## [0.5.2](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.1...v0.5.2) (2026-06-01)


### Bug Fixes

* improve CLI help and errors ([93da13b](https://github.com/f1sherFM/PyDoc2Markdown/commit/93da13babed643856797f6fd5540a38fbf6f8ea6))


### Documentation

* improve README first impression ([89aa6fd](https://github.com/f1sherFM/PyDoc2Markdown/commit/89aa6fdead8d8dd919329049820416f7315c9fa5))

## [0.5.1](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.5.0...v0.5.1) (2026-06-01)


### Bug Fixes

* clean generated markdown spacing ([11ee206](https://github.com/f1sherFM/PyDoc2Markdown/commit/11ee2062cea12d46418b6c6f56bc40c21c7c1603))


### Documentation

* add sample project example ([cb2d7f5](https://github.com/f1sherFM/PyDoc2Markdown/commit/cb2d7f57b25593006241ee51ba2980476494270b))

## [0.5.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.4.3...v0.5.0) (2026-05-31)


### Features

* add README and navigation docs generation ([30ca8a8](https://github.com/f1sherFM/PyDoc2Markdown/commit/30ca8a8c5b123b3057b5ef8a5d20f6051715a68c))

## [0.5.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.4.3...v0.5.0) (2026-05-31)


### Features

* add README API section generation with marker-based updates
* add navigation-first docs layout with API pages under `api/`

## [0.4.3](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.4.2...v0.4.3) (2026-05-30)


### Features

* add init command for pyproject config ([0804433](https://github.com/f1sherFM/PyDoc2Markdown/commit/08044332f861d44390dcf3731d83e5ac0997cf96))

## [0.4.2](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.4.1...v0.4.2) (2026-05-30)


### Bug Fixes

* align `generate_string()` type formatting and cross-reference rendering with file generation ([fde8f7a](https://github.com/f1sherFM/PyDoc2Markdown/commit/fde8f7a))
* render `generate_string()` through the configured Jinja2 template instead of a duplicated built-in template ([24a97fc](https://github.com/f1sherFM/PyDoc2Markdown/commit/24a97fc))
* read the CLI `--version` value from package `__version__` instead of hardcoding it


### Continuous Integration

* pass `CODECOV_TOKEN` to `codecov-action` so coverage uploads work on `main` ([7e95f03](https://github.com/f1sherFM/PyDoc2Markdown/commit/7e95f03))


### Documentation

* clarify `docstring-parser` support for Google, NumPy, and basic reStructuredText fields
* document that the `dev` extra already includes watcher dependencies


### Tests

* add CLI version output coverage
* add invalid `pyproject.toml` config error-path coverage
* add watcher missing-dependency and initial-generation failure coverage

## [0.4.1](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.4.0...v0.4.1) (2026-05-28)


### Documentation

* improve README with richer Example Output and cleaner Library API ([410f2f8](https://github.com/f1sherFM/PyDoc2Markdown/commit/410f2f808a98b3d7bf359331922689308a3633c1))

## [0.4.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.3.0...v0.4.0) (2026-05-28)


### Features

* add Pydantic BaseModel support with field extraction ([9d01b51](https://github.com/f1sherFM/PyDoc2Markdown/commit/9d01b5115b2c29ad62902463993ff055c0991c88))


### Documentation

* improve README with TOC, CLI reference, config, and API docs ([ec7e275](https://github.com/f1sherFM/PyDoc2Markdown/commit/ec7e2758e5b920d08a00cef227e4d5c2df047957))

## [0.3.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.2.0...v0.3.0) (2026-05-26)


### Features

* add cross-referencing hyperlinks for project-defined types ([7576075](https://github.com/f1sherFM/PyDoc2Markdown/commit/7576075f0cdd756ed8f7fdf3e489d04e35c9ca59))
* add modern type hint formatting ([53c2a11](https://github.com/f1sherFM/PyDoc2Markdown/commit/53c2a11049a4eaa99c3ad4f05c8b600f95f7fa6e))
* add Protocol and ABC support with badges in generated docs ([19c766e](https://github.com/f1sherFM/PyDoc2Markdown/commit/19c766ee7876ee64d8f8061de8088070a4856b3c))
* enhance index.md with overview stats and package descriptions ([fe149d2](https://github.com/f1sherFM/PyDoc2Markdown/commit/fe149d2adf89baf04ea86731f1b160a48b21fc8a))

## [0.2.0](https://github.com/f1sherFM/PyDoc2Markdown/compare/v0.1.0...v0.2.0) (2026-05-26)


### Features

* add --single-file mode for combined Markdown output ([60e3561](https://github.com/f1sherFM/PyDoc2Markdown/commit/60e3561b6fd0c859e47631111274c6b5da80cb6c))


### Bug Fixes

* add mypy override for tomli ([be58be8](https://github.com/f1sherFM/PyDoc2Markdown/commit/be58be8424b67da367928fee91a6712173a2f2ba))


### Documentation

* add shields, issue/PR templates, and Dependabot config ([173241b](https://github.com/f1sherFM/PyDoc2Markdown/commit/173241bb041a990cbc09a8d7b48abb6c21f0ac30))

## 0.1.0 (2026-05-26)


### Features

* add --theme support with default and minimal built-in themes ([d4db85a](https://github.com/f1sherFM/PyDoc2Markdown/commit/d4db85a110bb60e6c73c80c37525af8b106a6e63))
* add --watch mode, pyproject.toml config, release-please CI workflow ([29cb01c](https://github.com/f1sherFM/PyDoc2Markdown/commit/29cb01c96cae5f9cdbdfd635bdba505d06397844))
* add property, classmethod, staticmethod, dataclass, enum, typeddict, __all__ parsing ([8f3b548](https://github.com/f1sherFM/PyDoc2Markdown/commit/8f3b54865e118ab8b00817d18cbf8f3a359b8f6c))
* add TOC and auto-generated index.md ([9616e8a](https://github.com/f1sherFM/PyDoc2Markdown/commit/9616e8a3cdfafd37e1789bba409f3ea1720e972d))
* group output by package and create nested directories ([fe7d629](https://github.com/f1sherFM/PyDoc2Markdown/commit/fe7d6293e537163a7c2305c24a8044f1396badef))
* initial project structure for PyDoc2Markdown ([07a480d](https://github.com/f1sherFM/PyDoc2Markdown/commit/07a480d72f95cea98151c736b50b6867e9627706))
* initial release on PyPI ([fc612f5](https://github.com/f1sherFM/PyDoc2Markdown/commit/fc612f52185ed53dd84f49aaa0969b4c61152b15))
* integrate docstring-parser, add verbose logging, setup pre-commit hooks ([acd4ab6](https://github.com/f1sherFM/PyDoc2Markdown/commit/acd4ab61c2de458095e58f8ffbc2b9dfd41f1241))


### Bug Fixes

* Python 3.10 compat for tomllib, downgrade release-please to v3 ([e9f5cce](https://github.com/f1sherFM/PyDoc2Markdown/commit/e9f5cce27a70d1c7994b2991b220b8c424c0024b))


### Documentation

* update CONTRIBUTING.md with release-please and versioning info ([a82ba61](https://github.com/f1sherFM/PyDoc2Markdown/commit/a82ba61fe55a249139dd40875195fcfcafc6e374))
* update README with new features and usage examples ([ca47680](https://github.com/f1sherFM/PyDoc2Markdown/commit/ca476807eeddf3f36442f02373f67eb83a9823df))
