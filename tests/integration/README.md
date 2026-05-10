# Integration tests

These tests submit jobs to real backends and only run when the
corresponding credentials are present in the environment. The
`conftest.py` in the project root auto-skips them otherwise.

Run only integration tests:

```bash
uv run pytest -m integration
```

Mark a test with `needs_ibm`, `needs_aws`, or `needs_oqtopus` to gate
it on a specific provider's credentials.
