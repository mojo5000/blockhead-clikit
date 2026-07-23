# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Public-repo scaffolding: MIT `LICENSE`, CI workflow (lint + test matrix on
  Python 3.12/3.13 + build), PyPI trusted-publishing release workflow, ruff
  and coverage configuration, `CONTRIBUTING`, `SECURITY`, `CODE_OF_CONDUCT`,
  issue/PR templates, and Dependabot.
- Packaging metadata: authors, license, keywords, classifiers, and project URLs.

### Changed
- README leads with the PyPI install; git install kept as an option for
  unreleased fixes / branch pinning.

## [0.1.0] - 2026-07-19

### Added
- Initial extraction of `cli_kit` as the standalone `blockhead-clikit` package.
- `theme` (blockhead/clay/zigablocks/mono + `register_theme`), `ui`, `prompts`,
  `sh`, `Menu`, `registry.expose`, and the optional Django `ActionCommand`
  bridge.

[Unreleased]: https://github.com/mojo5000/blockhead-clikit/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mojo5000/blockhead-clikit/releases/tag/v0.1.0
