# Contributing

Thanks for your interest in qrouter! This document covers the local
workflow.

## Setup

```bash
# Install uv: https://github.com/astral-sh/uv
uv sync --all-extras
uv run pre-commit install
```

## Common commands

```bash
uv run pytest -m unit              # fast unit tests
uv run pytest -m integration       # real backends; needs credentials
uv run ruff check . && uv run ruff format --check .
uv run mypy src
```

## Adding a new SDK

1. Add a module under `src/qrouter/adapters/`.
2. Implement the `CircuitAdapter` protocol (`name`, `to_ir`, `from_ir`).
3. Register it in `src/qrouter/adapters/__init__.py` *or* expose it via a
   `qrouter.adapters` entry point in your own package.
4. Add round-trip property tests under `tests/property/`.

## Adding a new backend

1. Add a module under `src/qrouter/backends/`.
2. Implement the `Backend` protocol and a `BackendCapabilities`
   descriptor.
3. Read credentials from `qrouter.config` only — never accept tokens as
   constructor arguments.
4. Add an integration test marked `integration` and gated by
   `needs_<provider>`.

## License

By contributing you agree that your contributions are licensed under
Apache License 2.0.
