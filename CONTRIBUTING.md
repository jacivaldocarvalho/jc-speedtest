# Contributing to jc-speedtest

Thank you for your interest! Here is how to contribute.

## Development setup

1. Fork and clone the repository.
2. Create a virtual environment: `python -m venv .venv && source .venv/bin/activate`.
3. Install with dev extras: `pip install -e ".[dev]"`.
4. Install pre-commit hooks: `pre-commit install`.

## Running checks

- Lint: `ruff check .`
- Format: `ruff format .`
- Type check: `mypy src`
- Tests: `pytest`
- Integration tests (network): `pytest -m integration`

## Pull requests

- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Ensure `ruff`, `mypy`, and `pytest` pass before pushing.
- Reference any related issue in the PR description.