# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-07-28

### Added
- Menu shortcut keys are now functional hotkeys: pressing an item's key selects
  it, and the accelerator renders inline in the label (e.g. `(C)onfigure`).
  Reserved keys (quit/back) and type-to-filter menus are left untouched.
- `prompts.select` gained a `shortcuts` map powering the above.
- A `CLAUDE.md` project guide and a `build-cli-kit-app` Claude Code skill.
- A menu screenshot in the README.

### Changed
- Reworked the runnable example (`samples/` → `examples/`) to demonstrate the
  full surface: click CLI commands via `expose`, questionary input, a submenu
  with Back, and the `clay` theme by default.
- README overhaul: Prerequisites, split menu/CLI run instructions, and a note
  that `python` is optional under `uv run`.
- README leads with the PyPI install; git install kept as an option for
  unreleased fixes / branch pinning.

### Added (type checking & tooling)
- Static type checking: `mypy` config (`disallow_untyped_defs`) + a CI step;
  annotated the remaining untyped functions in the package.
- Secret scanning via `gitleaks` (CI job + pre-commit hook) with a
  `.gitleaks.toml` allowlist.
- `.pre-commit-config.yaml` (ruff, mypy, gitleaks, generic safety hooks) and
  `.editorconfig` for cross-editor consistency.
- Expanded the ruff ruleset to the house standard (adds `N`, `S`, `C90`, `T20`).

### Added (earlier)
- Public-repo scaffolding: MIT `LICENSE`, CI workflow (lint + test matrix on
  Python 3.12/3.13 + build), PyPI trusted-publishing release workflow, ruff
  and coverage configuration, `CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`,
  issue/PR templates, and Dependabot.
- Packaging metadata: authors, license, keywords, classifiers, and project URLs.

## [0.1.0] - 2026-07-19

### Added
- Initial extraction of `cli_kit` as the standalone `blockhead-clikit` package.
- `theme` (blockhead/clay/zigablocks/mono + `register_theme`), `ui`, `prompts`,
  `sh`, `Menu`, `registry.expose`, and the optional Django `ActionCommand`
  bridge.

[Unreleased]: https://github.com/mojo5000/blockhead-clikit/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/mojo5000/blockhead-clikit/compare/v0.1.0...v0.1.3
[0.1.0]: https://github.com/mojo5000/blockhead-clikit/releases/tag/v0.1.0
