# Contributing

Thanks for your interest in improving **blockhead-clikit**.

## Setup

This project uses [uv](https://docs.astral.sh/uv/). Python 3.12+ is required.

```bash
git clone https://github.com/mojo5000/blockhead-clikit
cd blockhead-clikit
uv sync --all-extras   # runtime + dev deps (pytest, ruff, coverage) + django extra
```

### Pre-commit hooks (recommended)

Install the git hooks once so ruff, mypy, and gitleaks run automatically on
every commit — the same gates CI enforces:

```bash
uv run pre-commit install
```

## Development loop

```bash
uv run pytest                 # run the suite
uv run pytest --cov           # with coverage
uv run ruff check .           # lint
uv run ruff format .          # format
uv run mypy                   # type check (config in [tool.mypy])
```

CI runs secret scanning (gitleaks), lint + format + type check, the test matrix
(Python 3.12 & 3.13), and a build on every PR — please make sure `ruff check`,
`ruff format --check`, `mypy`, and `pytest` all pass locally first.

## Guidelines

- **Keep the public API stable.** The import name `cli_kit` and the symbols in
  `cli_kit/__init__.py` are a contract; breaking changes need a major version
  bump and a `CHANGELOG` note.
- **Add tests** for new behavior — the suite lives in `cli_kit/tests/`.
- **Type everything.** The package ships `py.typed`; new code should carry
  type hints.
- **Update the docs** (`README.md`, `cli_kit/README.md`) and **`CHANGELOG.md`**
  (under `## [Unreleased]`) when you change behavior.

## Releasing (maintainers)

1. Move the `## [Unreleased]` entries into a new versioned section in
   `CHANGELOG.md` and bump `version` in `pyproject.toml`.
2. Tag the commit (`git tag vX.Y.Z && git push --tags`).
3. Publish a GitHub Release for that tag — the `release` workflow builds and
   publishes to PyPI via trusted publishing.

## Reporting bugs / requesting features

Open an issue using the templates in the "New issue" flow.
